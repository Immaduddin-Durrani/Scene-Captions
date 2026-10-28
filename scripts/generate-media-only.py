"""Explicit experimental full-film NIM generation. Never imported by the player.

No source captions, transcripts, titles, plots or hand-authored scene context are
read as inference input. Raw responses are cached; quality is NOT certified.
Run with the existing isolated scenecaptions-nim-asr Python environment.
"""
import argparse
import concurrent.futures
import hashlib
import json
import math
import re
import subprocess
import sys
import time
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'diagnostics'))
from phase1_nim import audio_part, run_one
from nim_client import ROOT, MODEL, api_key, parse_json, rate_limit, _retry_delay

VERSION = 'media-only-experimental-v2'
WINDOW = 15
FILMS = {
    'big-buck-bunny': ('Big Buck Bunny', 'https://peach.blender.org/about/', '2008 Blender Foundation / peach.blender.org'),
    'sintel': ('Sintel', 'https://durian.blender.org/about/', '2010 Blender Foundation / durian.blender.org'),
    'tears-of-steel': ('Tears of Steel', 'https://mango.blender.org/', '2012 Blender Foundation / mango.blender.org'),
}
PROMPT = '''Describe the non-speech sounds audible in this {duration:.3f}-second recording.
Answer in one factual sentence of at most 30 words. Include music or effects if
audible. Do not transcribe spoken words or describe a visual scene, story, emotion
or imagined cause. If no non-speech sounds are identifiable, say so. No JSON.'''


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def validate_sounds(value, duration):
    if not isinstance(value, dict) or set(value) != {'cues'} or not isinstance(value['cues'], list) or len(value['cues']) > 12:
        raise ValueError('Expected a bounded cues array')
    for cue in value['cues']:
        if not isinstance(cue, dict) or set(cue) != {'start_s', 'end_s', 'essential', 'balanced', 'detailed'}:
            raise ValueError('Unexpected cue fields')
        a, b = cue['start_s'], cue['end_s']
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) for t in (a, b)) or not 0 <= a < b <= duration:
            raise ValueError('Cue outside its exact audio window')
        for key in ('essential', 'balanced', 'detailed'):
            text = cue[key]
            if not isinstance(text, str) or not text.strip() or len(text.strip()) > 278 or any(c in text for c in '[]<>\n\r'):
                raise ValueError('Invalid caption text')
    return value['cues']


def dialogue_cues(response, offset, duration):
    """Group reported Parakeet word times. No reference/estimated ASR timing fallback."""
    cues, rejected = [], []
    for result in response.get('results', []):
        alternatives = result.get('alternatives', [])
        if not alternatives:
            continue
        alt = alternatives[0]
        text = alt.get('transcript', '').strip()
        if not text:
            continue
        if re.search(r'<[^>]*>|\[[^]]*\]|[♪♫]', text) or not re.search('[A-Za-z]', text):
            rejected.append('nonlexical/unknown-token transcript')
            continue
        words = alt.get('words', [])
        # Do not silently omit words that have zero-length/out-of-window offsets.
        if not words:
            rejected.append('transcript without word timestamps')
            continue
        if any(not 0 <= w.get('start_time', 0) / 1000 <= w.get('end_time', 0) / 1000 <= duration for w in words):
            rejected.append('word outside clip duration')
            continue
        group = []

        def flush():
            if not group:
                return
            a = group[0].get('start_time', 0) / 1000
            b = max(w.get('end_time', 0) / 1000 for w in group)
            phrase = ' '.join(w['word'].strip() for w in group).strip()
            if b > a and phrase and len(phrase) <= 1000:
                cues.append({'start_s': round(offset + a, 3), 'end_s': round(offset + b, 3), 'text': phrase})
            else:
                rejected.append('zero-duration/empty word group')
            group.clear()

        for word in words:
            if not isinstance(word.get('word'), str) or not word['word'].strip() or re.search('[<>♪♫]', word['word']):
                rejected.append('invalid word text')
                flush()
                continue
            if group and (word.get('end_time', 0) / 1000 - group[0].get('start_time', 0) / 1000 > 6
                          or word.get('start_time', 0) / 1000 - group[-1].get('end_time', 0) / 1000 > .8
                          or len(' '.join(w['word'] for w in group)) + len(word['word']) > 84):
                flush()
            group.append(word)
            if re.search(r'[.!?]$', word['word']):
                flush()
        flush()
    return cues, rejected


def asr(wav):
    import grpc
    import riva.client
    from google.protobuf.json_format import MessageToDict
    from riva.client.proto import riva_asr_pb2
    key = api_key()
    function = 'd3fe9151-442b-4204-a70d-5fcc597fd610'
    auth = riva.client.Auth(use_ssl=True, uri='grpc.nvcf.nvidia.com:443', metadata_args=[
        ['function-id', function], ['authorization', 'Bearer ' + key]])
    config = riva.client.RecognitionConfig(language_code='en-US', sample_rate_hertz=16000,
        audio_channel_count=1, max_alternatives=1, enable_automatic_punctuation=True,
        enable_word_time_offsets=True)
    config.encoding = riva.client.AudioEncoding.LINEAR_PCM
    with wave.open(str(wav), 'rb') as w:
        raw = w.readframes(w.getnframes())
    request = riva_asr_pb2.RecognizeRequest(config=config, audio=raw)
    row = {'endpoint': 'grpc.nvcf.nvidia.com:443', 'function_id': function, 'model': 'parakeet-tdt-0_6b-v2',
           'request_sha256': hashlib.sha256(request.SerializeToString()).hexdigest(),
           'audio_sha256': hashlib.sha256(raw).hexdigest(),
           'config': MessageToDict(config, preserving_proto_field_name=True)}
    rate_limit()
    started = time.monotonic()
    try:
        response, rpc = riva.client.ASRService(auth).stub.Recognize.with_call(request, timeout=90,
            metadata=auth.get_auth_metadata(), wait_for_ready=False)
        row.update(grpc_status='OK', response=MessageToDict(response, preserving_proto_field_name=True))
        row['request_ids'] = {k: v for k, v in (rpc.initial_metadata() or []) if any(x in k.lower() for x in ('request-id', 'requestid', 'nvcf'))}
    except grpc.RpcError as error:
        row.update(grpc_status=error.code().name, error=error.details().replace(key, '[REDACTED]')[:1000])
    finally:
        auth.channel.close()
    row['seconds'] = round(time.monotonic() - started, 3)
    return row


def process(job, report_dir, attempt_limit=2):
    identity, start, length, video, sha = job
    cache = ROOT / 'artifacts/media-only-2026-10-28' / identity / sha[:16]
    cache.mkdir(parents=True, exist_ok=True)
    wav = cache / f'sound15-{start:04d}.wav'
    if not wav.exists():
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start), '-i', str(video),
                        '-t', str(length), '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', '-y', str(wav)], check=True)
    part, fixture = audio_part(wav)
    length = fixture['duration_s']
    prompt = PROMPT.format(duration=length)
    payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': [part, {'type': 'text', 'text': prompt}]}],
               'temperature': .2, 'top_k': 1, 'max_tokens': 256, 'stream': False,
               'chat_template_kwargs': {'enable_thinking': False}}
    binding = {'version': VERSION, 'film_sha256': sha, 'fixture': fixture, 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}
    path = report_dir / identity / f'{start:04d}.json'
    saved = json.loads(path.read_text()) if path.exists() else {'binding': binding, 'sound_attempts': [], 'asr_attempts': []}
    if saved['binding'] != binding:
        raise ValueError('Stale or mismatched cached input')
    # Persistent attempt ceiling across resumes. Identical payload only.
    with wave.open(str(wav), 'rb') as w:
        zero = not any(w.readframes(w.getnframes()))
    if zero:
        saved.update(observation='', digital_zero=True)
        write(path, saved)
    for _ in range(attempt_limit - len(saved['sound_attempts'])):
        if 'observation' in saved:
            break
        if saved['sound_attempts']:
            previous = saved['sound_attempts'][-1]
            headers = previous.get('response_headers', {})
            advised = next((v for k, v in headers.items() if k.lower() == 'retry-after'), None)
            time.sleep(_retry_delay(len(saved['sound_attempts']) - 1, advised))
        row = run_one(payload)
        saved['sound_attempts'].append(row)
        try:
            if row.get('http_status') != 200:
                raise ValueError('Sound inference did not complete')
            choice = row['response']['choices'][0]
            text = choice['message']['content'].strip()
            if choice.get('finish_reason') != 'stop' or not 0 < len(text) <= 600 or any(t in text for t in ('<think>', '{', '}')):
                raise ValueError('No complete bounded plain-text observation')
            saved['observation'] = text
        except (ValueError, KeyError, TypeError) as error:
            row['validation_error'] = str(error)
        write(path, saved)
        if row.get('http_status') in (400, 401, 403, 404):
            raise RuntimeError('NVIDIA authorization/route/payload failure; stop, preserve cache')
    # Speech is independent of sound observations. Reuse prior exact-audio ASR
    # responses from the interrupted v1 run; never reuse its sound outputs.
    speech_wav = cache / f'{start:04d}.wav'
    if start % 30:
        saved.update(speech_cues=[], speech_rejections=[])
    else:
        if not speech_wav.exists():
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start), '-i', str(video),
                            '-t', '30', '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', '-y', str(speech_wav)], check=True)
        with wave.open(str(speech_wav), 'rb') as w:
            speech_length = w.getnframes() / 16000
            speech_raw = w.readframes(w.getnframes())
            speech_sha = hashlib.sha256(speech_raw).hexdigest()
        if not any(speech_raw):
            saved.update(speech_cues=[], speech_rejections=[], speech_digital_zero=True)
        old_path = report_dir.parent / identity / f'{start:04d}.json'
        if 'speech_cues' not in saved and old_path.exists():
            old = json.loads(old_path.read_text())
            for row in old.get('asr_attempts', []):
                if row.get('grpc_status') == 'OK' and row.get('audio_sha256') == speech_sha:
                    saved['asr_reused_from'] = str(old_path.relative_to(ROOT))
                    saved['speech_cues'], saved['speech_rejections'] = dialogue_cues(row['response'], start, speech_length)
                    break
    for _ in range(attempt_limit - len(saved['asr_attempts'])):
        if 'speech_cues' in saved:
            break
        row = asr(speech_wav)
        saved['asr_attempts'].append(row)
        if row.get('grpc_status') == 'OK':
            cues, rejected = dialogue_cues(row['response'], start, speech_length)
            saved.update(speech_cues=cues, speech_rejections=rejected)
        write(path, saved)
        if row.get('grpc_status') in ('UNAUTHENTICATED', 'PERMISSION_DENIED', 'NOT_FOUND', 'INVALID_ARGUMENT'):
            raise RuntimeError('NVIDIA ASR authorization/route/payload failure; stop, preserve cache')
    write(path, saved)
    ok = 'observation' in saved and 'speech_cues' in saved
    print(f'{identity} {start:04d}s: {"complete" if ok else "INCOMPLETE"}; dialogue={len(saved.get("speech_cues", []))}', flush=True)
    return identity, start, ok


def timestamp(value):
    n = round(value * 1000)
    return f'{n // 3600000:02d}:{n // 60000 % 60:02d}:{n // 1000 % 60:02d},{n % 1000:03d}'


def parse_render_response(response):
    """Accept a complete JSON object, or exact duplicate complete JSON objects.

    Some text responses repeat compact JSON as pretty JSON. Never pick a prefix,
    discard differing content, accept trailing prose or heal a truncated object.
    This compatibility rule is isolated to text rendering, not acoustic gates.
    """
    try:
        return parse_json(response)
    except json.JSONDecodeError as original:
        text = response['choices'][0]['message']['content'].strip()
        decoder, documents = json.JSONDecoder(), []
        while text:
            value, end = decoder.raw_decode(text)
            documents.append(value)
            if len(documents) > 3:
                raise original
            text = text[end:].strip()
        if len(documents) < 2 or any(v != documents[0] for v in documents[1:]):
            raise original
        return documents[0]


def validate_rendered(value, ids):
    if not isinstance(value, dict) or set(value) != {'captions'}:
        raise ValueError('Expected captions object')
    entries = value['captions']
    if not isinstance(entries, list) or len(entries) != len(ids) or any(not isinstance(e, dict) for e in entries) or {e.get('id') for e in entries} != set(ids):
        raise ValueError('Changed observation ids')
    for e in entries:
        if set(e) != {'id', 'essential', 'balanced', 'detailed'}:
            raise ValueError('Unexpected rendered fields')
        if all(e[k] is None for k in ('essential', 'balanced', 'detailed')):
            continue
        validate_sounds({'cues': [{'start_s': 0, 'end_s': 1, **{k: e[k] for k in ('essential', 'balanced', 'detailed')}}]}, 1)
    return entries


def export(identity, meta, jobs, report_dir):
    cues, dialogue, missing, rejections = [], [], [], []
    for _, start, _, _, _ in jobs:
        saved = json.loads((report_dir / identity / f'{start:04d}.json').read_text())
        if 'observation' not in saved or 'speech_cues' not in saved:
            missing.append(start)
            continue
        rendered = saved.get('rendered')
        if rendered is None:
            missing.append(start)
            continue
        for c in rendered:
            variants = [f'[{c[k].strip()}]' for k in ('essential', 'balanced', 'detailed')]
            cues.append({'cue_id': f'media-{start:04d}-{len(cues):04d}',
                'start_s': round(start + c['start_s'], 3), 'end_s': min(meta['duration'], round(start + c['end_s'], 3)),
                'original_text': variants[1], 'grid': {f'{d}-{e}': variants[d-1] for d in (1,2,3) for e in (1,2,3)},
                'scene_context': 'Experimental audio-only observation, reworded at three detail levels. This caption describes a 15-second analysis window, not a verified event interval. Sounds may be missing or invented; no reference captions or plot were supplied.',
                'sound_key': 'experimental-' + re.sub('[^a-z0-9]+', '-', c['essential'].lower()).strip('-')[:60],
                'scene_load': 'balanced', 'representations': {'plain': variants[0]}})
        dialogue.extend(saved['speech_cues'])
        rejections.extend({'window_start_s': start, 'reason': reason} for reason in saved.get('speech_rejections', []))
    summary = {'video_id': identity, 'duration_seconds': meta['duration'], 'video_sha256': meta['sha256'],
               'windows': len(jobs), 'completed': len(jobs) - len(missing), 'missing_windows': missing,
               'sound_cues': len(cues), 'dialogue_cues': len(dialogue), 'asr_rejections': rejections,
               'quality': 'UNVERIFIED; known sound-recognition controls failed; full processing is not full event recall'}
    write(report_dir / f'{identity}-summary.json', summary)
    if missing:
        return summary
    title, url, credit = FILMS[identity]
    cues.sort(key=lambda c: (c['start_s'], c['end_s'], c['cue_id']))
    dialogue.sort(key=lambda c: (c['start_s'], c['end_s']))
    for i, c in enumerate(dialogue):
        c['cue_id'] = f'asr-{i:04d}'
        c['end_s'] = min(meta['duration'], c['end_s'])
    result = {'schema_version': 1, 'video_id': identity, 'title': title, 'source_url': url, 'license': 'CC BY 3.0',
              'attribution': '© ' + credit + '. Experimental media-only captions by SceneCaptions; not creator-authored or reviewed.',
              'duration_seconds': meta['duration'], 'annotation_status': 'draft',
              'generated_with': {'kind': 'audio-derived', 'method': 'NVIDIA audio-only observations in nonoverlapping 15-second windows, reworded at three detail levels by Super VL; dedicated Parakeet word-timed speech in 30-second windows. Sound display intervals are analysis windows, NOT detected event boundaries. No fetched subtitles, plot, titles, scene descriptions or source cue timing supplied.',
                  'prompt_version': VERSION, 'model': MODEL + ' + nvidia/nemotron-3.5-super-vl-120b-a12b + nvidia/parakeet-tdt-0_6b-v2',
                  'source_sha256': meta['sha256'], 'quality_gate': 'unverified', 'experimental': True,
                  'acoustic_validation': 'failed', 'input_basis': 'media-only',
                  'expressiveness': 'conservative', 'scene_load_method': 'unreviewed'},
              'cues': cues, 'dialogue': dialogue}
    write(ROOT / 'data/experimental-captions' / f'{identity}.json', result)
    write(ROOT / 'public/research/media-only' / f'{identity}.json', result)
    for detail in (1,2,3):
        lines = sorted([{'start_s': c['start_s'], 'end_s': c['end_s'], 'text': c['grid'][f'{detail}-2']} for c in cues] + dialogue,
                       key=lambda c: (c['start_s'], c['end_s']))
        srt = '\n\n'.join(f'{i+1}\n{timestamp(c["start_s"])} --> {timestamp(c["end_s"])}\n{c["text"]}' for i,c in enumerate(lines)) + '\n'
        (ROOT / 'public/research/media-only' / f'{identity}-detail-{detail}.srt').write_text(srt)
    return summary


def render(identity, jobs, report_dir, attempt_limit=2):
    # Reuse complete, byte-bound text responses before making new requests.
    # Raw reports stay untouched; recovery is recorded on each observation.
    for report in (report_dir / identity).glob('render-*.json'):
        for row in json.loads(report.read_text()):
            try:
                if row.get('http_status') != 200:
                    continue
                payload = row['payload']
                observations = json.loads(payload['messages'][0]['content'].split('Observations:\n', 1)[1])
                if payload['model'] != 'nvidia/nemotron-3.5-super-vl-120b-a12b':
                    continue
                bound = []
                for observation in observations:
                    path = report_dir / identity / f'{int(observation["id"]):04d}.json'
                    saved = json.loads(path.read_text())
                    if saved.get('observation') != observation['observation']:
                        raise ValueError('Stale observation')
                    bound.append((path, saved, observation['id']))
                entries = validate_rendered(parse_render_response(row['response']), [o['id'] for o in observations])
                for path, saved, key in bound:
                    if 'rendered' in saved:
                        continue
                    e = next(e for e in entries if e['id'] == key)
                    saved['rendered'] = [] if e['essential'] is None else [{'start_s': 0, 'end_s': saved['binding']['fixture']['duration_s'], **{k: e[k] for k in ('essential', 'balanced', 'detailed')}}]
                    saved['render_report'] = str(report.relative_to(ROOT))
                    saved['render_recovery'] = 'Complete JSON; identical duplicate objects permitted, no divergent/truncated content discarded'
                    write(path, saved)
                break
            except (KeyError, TypeError, ValueError, OSError):
                continue
    pending = []
    for _, start, _, _, _ in jobs:
        path = report_dir / identity / f'{start:04d}.json'
        saved = json.loads(path.read_text())
        if 'observation' not in saved or 'rendered' in saved:
            continue
        if not saved['observation']:
            saved['rendered'] = []
            write(path, saved)
        else:
            pending.append((start, path, saved))
    for i in range(0, len(pending), 8):
        batch = pending[i:i+8]
        observations = [{'id': str(start), 'observation': saved['observation']} for start, _, saved in batch]
        prompt = '''Rewrite these unverified audio-model observations into non-speech captions
for Deaf/hard-of-hearing viewers. These observations are the ONLY factual input;
do not add sounds, source identities, emotion, visuals, plot or interpretations.
Do not treat observations as independently verified. Remove speculative causes
or moods. Preserve multiple audible sound types. Three texts per observation:
essential (short labels), balanced (brief description), detailed (more of the
already supplied acoustic detail, at most 25 words). All <= 278 characters, no
brackets, markup or newlines. If the observation explicitly reports no non-speech
sounds, return null texts for that id. Return only a JSON object with key captions,
an array of objects with EXACT keys id, essential, balanced, detailed. Preserve
every input id exactly once. Do not generate timestamps. Observations:\n''' + json.dumps(observations)
        payload = {'model': 'nvidia/nemotron-3.5-super-vl-120b-a12b',
                   'messages': [{'role': 'user', 'content': prompt}], 'temperature': .2,
                   'reasoning_effort': 'none', 'max_tokens': 4096, 'stream': False}
        batch_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]
        report = report_dir / identity / f'render-{batch[0][0]:04d}-{batch_hash}.json'
        attempts = json.loads(report.read_text()) if report.exists() else []
        accepted = None
        for _ in range(attempt_limit - len(attempts)):
            if attempts:
                time.sleep(_retry_delay(len(attempts) - 1))
            row = run_one(payload)
            attempts.append(row)
            try:
                if row.get('http_status') != 200:
                    raise ValueError('Rendering incomplete')
                accepted = validate_rendered(parse_render_response(row['response']), [o['id'] for o in observations])
            except (KeyError, TypeError, ValueError) as error:
                row['validation_error'] = str(error)
            write(report, attempts)
            if accepted is not None:
                break
        if accepted is None:
            continue
        for start, path, saved in batch:
            e = next(e for e in accepted if e['id'] == str(start))
            saved['rendered'] = [] if e['essential'] is None else [{'start_s': 0, 'end_s': saved['binding']['fixture']['duration_s'], **{k: e[k] for k in ('essential', 'balanced', 'detailed')}}]
            saved['render_report'] = str(report.relative_to(ROOT))
            write(path, saved)
        print(f'{identity}: rendered {len(batch)} observations at three detail levels', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experimental', action='store_true', required=True, help='Explicitly generate unverified experiments despite the failed acoustic gate; never install as default')
    p.add_argument('--films', nargs='+', choices=list(FILMS), default=list(FILMS))
    p.add_argument('--export-only', action='store_true')
    p.add_argument('--retry-incomplete', action='store_true', help='Bounded addendum: up to six total attempts per unfinished stage; no retry of completed observations')
    args = p.parse_args()
    report_dir = ROOT / 'docs/verification/media-only-2026-10-28/v2'
    metadata, jobs = {}, []
    for identity in dict.fromkeys(args.films):
        video = ROOT / 'public/media' / f'{identity}.mp4'
        duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video)], text=True))
        sha = digest(video)
        metadata[identity] = {'duration': duration, 'sha256': sha}
        jobs.extend((identity, start, min(WINDOW, duration-start), video, sha) for start in range(0, math.ceil(duration), WINDOW))
    protocol = {'version': VERSION, 'films': metadata, 'window_seconds': WINDOW, 'jobs': len(jobs),
                'max_inference_attempts': len(jobs)*4 + math.ceil(len(jobs)/8)*2, 'parallel_requests': 2, 'source_captions_as_input': False,
                'plot_or_scene_text_as_input': False, 'system_quality_gate_changed': False,
                'purpose': 'User-requested full-film experimental generation; opt-in, NOT validated subtitles',
                'prompt_template': PROMPT}
    path = report_dir / 'protocol.json'
    if path.exists() and json.loads(path.read_text()) != protocol:
        raise ValueError('Protocol mismatch; do not overwrite prior experiment')
    write(path, protocol)
    limit = 6 if args.retry_incomplete else 2
    if args.retry_incomplete:
        write(report_dir / 'retry-addendum.json', {'base_protocol_sha256': digest(path), 'total_attempt_limit_per_stage': limit,
            'max_total_inference_attempts': len(jobs)*12 + sum(math.ceil(sum(j[0] == identity for j in jobs)/8)*6 for identity in metadata),
            'scope': 'Only incomplete sound/ASR/render stages, unchanged payloads, complete cache reused. Supersedes initial attempt ceiling; no semantic quality approval.'})
    print(f'{len(jobs)} sound windows; speech processed separately every 30 seconds. Up to {limit} total attempts per stage. NVIDIA only; experimental, not quality approved.', flush=True)
    if not args.export_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for _ in pool.map(lambda job: process(job, report_dir, limit), jobs):
                pass
    for identity in metadata:
        render(identity, [j for j in jobs if j[0] == identity], report_dir, limit)
    summaries = [export(identity, metadata[identity], [j for j in jobs if j[0] == identity], report_dir) for identity in metadata]
    write(report_dir / 'summary.json', summaries)
    if any(s['missing_windows'] for s in summaries):
        raise SystemExit('Incomplete windows; no complete track exported for those films. See summaries.')
    print('All windows processed and experimental exports written. No default tracks/gates changed.', flush=True)


if __name__ == '__main__':
    main()
