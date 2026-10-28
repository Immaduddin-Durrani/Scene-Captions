"""Offline integrity and stage assessment; no inference or playback installation."""
import hashlib
import array
import json
import statistics
import wave
from collections import Counter
from pathlib import Path

from google.protobuf.json_format import ParseDict
from riva.client.proto import riva_asr_pb2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASR = ['asr-access', 'asr-controls', 'parakeet-timing', 'parakeet-absence', 'parakeet-raw-pcm']
HTTP = {'sounds': 'sounds', 'sounds-p04-retry': 'sounds-p04-retry',
        'sounds-p05-retry': 'sounds-p05-retry', 'renderer': 'renderer'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def text(call):
    return ' '.join(r.get('alternatives', [{}])[0].get('transcript', '')
                    for r in call.get('response', {}).get('results', [])).strip()


def pcm(path):
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000)
        return array.array('h', w.readframes(w.getnframes()))


def main():
    out = HERE / 'assessment.json'
    assert not out.exists()
    asr_jobs = {j['case']: j for j in json.loads((HERE / 'inputs/asr.json').read_text())}
    # Independently reconstruct controlled mixtures, rather than trusting file names.
    art = ROOT / 'artifacts/nim-pipeline-2026-10-27'
    recent = ROOT / 'artifacts/nim-recognition-2026-10-27'
    speech = pcm(recent / 'q07.wav')
    assert pcm(art / 'p01.wav') == speech
    assert not any(pcm(art / 'p02.wav'))
    original = pcm(recent / 'q01.wav')
    indices = [i for i, value in enumerate(original) if value]
    burst = original[indices[0]:indices[-1] + 1]
    effects = array.array('h', [0]) * 160000
    for onset in range(1, 9):
        effects[onset * 16000:onset * 16000 + len(burst)] = burst
    assert effects == pcm(art / 'p03.wav')
    mixture = array.array('h', [0]) * 160000
    mixture[8000:8000 + len(speech)] = speech
    for onset in [4, 6, 8]:
        mixture[onset * 16000:onset * 16000 + len(burst)] = burst
    assert mixture == pcm(art / 'p04.wav')
    asr_rows, http_rows = [], []
    by_run = {}
    for name in ASR:
        report = json.loads((HERE / 'reports' / (name + '.json')).read_text())
        assert report['manifest_sha256'] == sha((HERE / 'inputs/asr.json').read_bytes())
        by_run[name] = {call['case']: call for call in report['calls']}
        for call in report['calls']:
            media = ROOT / call['fixture']['file']; raw = media.read_bytes()
            assert sha(raw) == call['fixture']['sha256'] == asr_jobs[call['case']]['sha256']
            if call.get('wire_audio_format') == 'raw PCM16':
                with wave.open(str(media), 'rb') as w:
                    raw = w.readframes(w.getnframes())
            config = ParseDict(call['config'], riva_asr_pb2.RecognitionConfig())
            request = riva_asr_pb2.RecognizeRequest(config=config, audio=raw)
            assert sha(request.SerializeToString()) == call['request_sha256']
            transcript = text(call)
            asr_rows.append({'run': name, 'case': call['case'], 'status': call['grpc_status'],
                'model_function_id': call['function_id'], 'text_prefix': transcript[:150],
                'text_length': len(transcript), 'unknown_token_count': transcript.count('<unk>'),
                'word_count': sum(len(r.get('alternatives', [{}])[0].get('words', []))
                                  for r in call.get('response', {}).get('results', []))})
    for name, manifest in HTTP.items():
        report = json.loads((HERE / 'reports' / (name + '.json')).read_text())
        assert report['manifest_sha256'] == sha((HERE / 'inputs' / (manifest + '.json')).read_bytes())
        for call in report['calls']:
            for media in call.get('fixtures', []):
                assert sha((ROOT / media['file']).read_bytes()) == media['sha256']
            choice = (call.get('response', {}).get('choices') or [{}])[0]
            http_rows.append({'run': name, 'case': call['case'], 'http_status': call.get('http_status'),
                'finish_reason': choice.get('finish_reason'), 'text': choice.get('message', {}).get('content'),
                'error': call.get('error')})
    source = by_run['parakeet-timing']
    words = {k: v['response']['results'][0]['alternatives'][0]['words'] for k, v in source.items()}
    a, b = words['p01'], words['p04']
    assert len(a) == len(b) == 8
    shifts = [(y.get('start_time', 0) - x.get('start_time', 0)) / 1000 for x, y in zip(a, b)]
    timing = {'expected_speech_shift_s': .5, 'observed_word_onset_shifts_s': shifts,
        'median_onset_shift_s': statistics.median(shifts),
        'zero_duration_words': {case: [w['word'] for w in entries if w.get('start_time', 0) == w.get('end_time', 0)]
                                for case, entries in words.items()},
        'last_word_end_s': {case: entries[-1]['end_time'] / 1000 for case, entries in words.items()},
        'constructed_mixed_speech_pcm_support_end_s': 3.09,
        'mixed_last_word_end_overrun_into_known_speech_silence_s': round(b[-1]['end_time'] / 1000 - 3.09, 4),
        'interpretation': 'Offsets supplied; median shift tracks constructed delay, but zero-length words and endpoint overrun prevent an unqualified timing pass.'}
    total = len(asr_rows) + len(http_rows)
    assert total == 18
    guards = json.loads((HERE / 'asr-guards.json').read_text())
    assert guards['p02']['digital_zero'] and guards['p02']['candidate_speech_text'] is None
    assert guards['p03']['candidate_speech_text'] is None
    renderer = json.loads((HERE / 'renderer-assessment.json').read_text())
    assert renderer['structure_and_identity_pass'] and not renderer['accepted_for_playback']
    result = {'total_inference_attempts': total,
        'grpc_status_counts': dict(Counter(r['status'] for r in asr_rows)),
        'http_status_counts': dict(Counter(str(r['http_status']) for r in http_rows)),
        'asr_rows': asr_rows, 'chat_rows': http_rows, 'speech_timing': timing,
        'stages': {'whisper_transcription': 'Clean and mixed expected phrase correct; raw absence controls fail; no word offsets returned.',
            'parakeet_transcription_and_timing': 'Expected phrase correct, word offsets partial; empty dog transcript; silence degenerates to unknown tokens on both WAV and raw PCM.',
            'preprocessing': 'Exact-zero and ASR-markup guards work on tested cells; no general speech detector or semantic truth guarantee.',
            'non_speech_grounding': 'FAILED: dog source becomes metallic clinks; fabricated tone on repeated-bark control.',
            'renderer': 'Structure/IDs/dialogue pass; wording faithfully propagates incorrect source observation.',
            'end_to_end_caption_quality': 'FAILED, no accepted or timed movie-caption output'},
        'integrity': {'all_manifest_and_fixture_hashes_match': True, 'grpc_request_bytes_reconstructed': True,
            'raw_pcm_variant_uses_same_source_samples': True, 'control_mixtures_independently_reconstructed': True},
        'renderer_output': renderer['output'], 'automatic_installation': False, 'failed_gate_cleared': False,
        'limits': ['Tiny synthetic/ESC-10 pilot, not full-film accuracy or DHH usability evidence.',
            'Raw BBB siren/beep description is unreviewed, not accepted ground truth.',
            'No inference was run through Qwen3-ASR; no applicable hosted NIM route was verified.',
            'Manual assessment in the main session; not an independent listening review.']}
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'requests': total, 'grpc': result['grpc_status_counts'], 'http': result['http_status_counts'],
        'renderer_contract': 'pass', 'end_to_end_sound_quality': 'failed'}, indent=2))


if __name__ == '__main__':
    main()
