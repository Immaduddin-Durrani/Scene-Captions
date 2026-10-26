"""Prepare/score caption-free NIM controls. No inference, installation or gate changes."""
import argparse
import array
import hashlib
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nim_client import ROOT, parse_json

ART = ROOT / 'artifacts/nim-counterfactuals-2026-10-26'
EVIDENCE = ROOT / 'docs/verification/nim-counterfactuals-2026-10-26'
MODEL = 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
PROMPT = '''Describe only sounds actually audible in the supplied media, with their
approximate start and end times. If a video and separate audio are supplied, they
share the same zero-second origin; the separate audio is the sound evidence.
Do not infer sounds from visible actions or reconstruct a known story.
Include music, sound effects and non-word vocalizations in events. Put spoken words
in speech instead. Do not invent uncertain sources, instruments or acoustic traits.
If nothing is audible, return empty events and speech arrays. If timing is uncertain,
use null for both times instead of guessing. Times are relative to the media clip.
Return JSON with exactly: events (array), speech (array), limitations (array).
Each event: sound (short description), start_s (number or null), end_s (number or null).
Each speech item: text (verbatim), start_s (number or null), end_s (number or null).
At most 20 events. No markdown. Clip duration: 10 seconds.'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def pcm(path):
    with wave.open(str(path), 'rb') as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, 16000):
            raise ValueError('Expected mono 16-kHz PCM16')
        samples = array.array('h', w.readframes(w.getnframes()))
        return samples, w.getnframes() / w.getframerate()


def prepare():
    manifest = ART / 'manifest.json'
    if manifest.exists():
        raise ValueError('Prepared inputs already exist; preserve frozen evidence')
    ART.mkdir(parents=True, exist_ok=True)
    source_path = ART / 'sources.json'
    sources = json.loads(source_path.read_text())
    controls = {}
    for item in sources['clips']:
        path = ROOT / item['file']
        if digest(path) != item['sha256']:
            raise ValueError('Downloaded control changed')
        category = item['evaluation_only_metadata']['category']
        normalized = ART / (item['sha256'][:20] + '-16k.wav')
        ffmpeg('-i', path, '-map', '0:a:0', '-ac', 1, '-ar', 16000,
               '-c:a', 'pcm_s16le', '-map_metadata', '-1', normalized)
        controls[category] = normalized
    # The expected event names stay ONLY in evaluation metadata, never the requests.
    specs = [('c01', 'dog', 1), ('c02', 'dog', 4), ('c03', 'rain', 1)]
    metadata = {}
    for name, category, delay in specs:
        path = ART / (name + '.wav')
        ffmpeg('-i', controls[category], '-af', f'adelay={delay*1000}:all=1,apad',
               '-t', 10, '-ac', 1, '-ar', 16000, '-c:a', 'pcm_s16le', path)
        samples, duration = pcm(path)
        if len(samples) != 160000 or not any(samples):
            raise ValueError('Invalid padded control')
        # Prove digital-zero padding and the exact sample shift, not just durations.
        if any(samples[:delay*16000]) or any(samples[(delay+5)*16000:]):
            raise ValueError('Unexpected audio outside injected source interval')
        metadata[name] = {'file': str(path.relative_to(ROOT)), 'sha256': digest(path),
            'duration_s': duration, 'category': category, 'source_support_s': [delay, delay+5]}
    a, _ = pcm(ART/'c01.wav'); b, _ = pcm(ART/'c02.wav')
    if a[16000:96000] != b[64000:144000]:
        raise ValueError('Shifted source samples differ')
    muted = ART/'c00.wav'
    with wave.open(str(muted), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b'\0\0' * 160000)
    # Picture is independent of the sounds; no original soundtrack or text track.
    film = ROOT/'public/media/big-buck-bunny.mp4'
    silent_video = ART/'picture.mp4'
    ffmpeg('-ss', 0, '-i', film, '-t', 10, '-map', '0:v:0', '-an', '-sn', '-dn',
           '-vf', 'scale=512:-2,fps=2', '-c:v', 'libx264', '-crf', 24,
           '-map_metadata', '-1', '-map_chapters', '-1', '-movflags', '+faststart', silent_video)
    streams = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(silent_video)]))['streams']
    if len(streams) != 1 or streams[0]['codec_type'] != 'video':
        raise ValueError('The diagnostic picture must have only a video stream')
    jobs = []
    for mode in ['audio', 'split-av']:
        for name, _, _ in specs:
            content = [{'type':'local_wav','path':metadata[name]['file']}]
            if mode == 'split-av':
                content.append({'type':'local_mp4','path':str(silent_video.relative_to(ROOT))})
            content.append({'type':'text','text':PROMPT})
            jobs.append(job(name+'-'+mode, content,
                'Same audio/prompt with and without identical silent video. Names and known times are withheld.'))
    jobs.append(job('c00-split-av', [
        {'type':'local_wav','path':str(muted.relative_to(ROOT))},
        {'type':'local_mp4','path':str(silent_video.relative_to(ROOT))},
        {'type':'text','text':PROMPT}], 'Digital silence with identical picture must not yield sound or speech events.'))
    # Reuse the previously prepared novel speech fixture as transport/ASR control.
    nonce = ROOT/'artifacts/nim-phase1-2026-10-26/nonce.wav'
    jobs.append(job('c04-speech', [
        {'type':'local_wav','path':str(nonce.relative_to(ROOT))},
        {'type':'text','text':'Transcribe the speech in this recording exactly.'}],
        'Positive input control only; successful transcription does not establish sound recognition.'))
    assert_blind(jobs)
    manifest.write_text(json.dumps(jobs, indent=2)+'\n')
    protocol = {'created_before_inference':True, 'scope':'8 single-attempt NVIDIA requests; no source-caption input or playback installation',
        'cases':metadata, 'shift_samples':48000, 'shift_seconds':3,
        'picture_sha256':digest(silent_video), 'original_film_sha256':digest(film),
        'source_manifest_sha256':digest(source_path), 'manifest_sha256':digest(manifest),
        'same_picture_for_all_av_cases':True,'picture_streams':['video'],
        'caption_files_read':False,'plot_provided':False,
        'criteria':{'strict_categories':['dog','rain'],'water_without_rain':'partial only',
            'support_tolerance_s':.25,'relative_shift_tolerance_s':.5,
            'mute':'zero events and zero speech','speech':'seventeen/17 blue lanterns are beside the window'},
        'limits':['ESC-10 labels are clip-level, not exact event-onset annotations.',
            'Padding support and relative shift are known exactly; actual bark onset is not manually annotated.',
            'Small diagnostic only, not representative film accuracy or timing benchmark.',
            'Same WAV bytes in audio and split-AV; no AAC/PCM codec confound.',
            'A model may have seen public ESC-10 training audio; this is not a held-out generalization claim.']}
    (EVIDENCE/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (EVIDENCE/'inputs').mkdir(exist_ok=True)
    (EVIDENCE/'inputs/manifest.json').write_bytes(manifest.read_bytes())
    (EVIDENCE/'inputs/sources.json').write_bytes(source_path.read_bytes())
    print('Prepared 8 blinded requests; sample shift/padding and video-only stream checks passed. No inference.')


def job(name, content, hypothesis):
    return {'case':name,'hypothesis':hypothesis,'payload':{
        'model':MODEL,'messages':[{'role':'user','content':content}],
        'max_tokens':4096,'temperature':.2,'top_k':1,'stream':False,
        'chat_template_kwargs':{'enable_thinking':False}}}


def assert_blind(jobs):
    for item in jobs:
        if len(item['payload']['messages']) != 1:
            raise ValueError('No conversation history allowed')
        for part in item['payload']['messages'][0]['content']:
            if part['type']=='text' and re.search(r'\b(dog|rain|bark|rainfall|lanterns)\b',part['text'],re.I):
                raise ValueError('Expected content leaked into prompt')
            if part['type'].startswith('local_') and Path(part['path']).suffix.lower() not in ['.wav','.mp4']:
                raise ValueError('Only raw media allowed')


def validate_result(response, duration=10):
    result = parse_json(response)
    if not isinstance(result,dict) or set(result) != {'events','speech','limitations'} or any(not isinstance(result[k],list) for k in ['events','speech','limitations']):
        raise ValueError('Expected exactly events, speech and limitations arrays')
    if any(not isinstance(x,str) for x in result['limitations']):
        raise ValueError('Limitations must be strings')
    if len(result['events'])>20:
        raise ValueError('Too many events')
    for key, text_field in [('events','sound'),('speech','text')]:
        for event in result[key]:
            if not isinstance(event,dict) or not {text_field,'start_s','end_s'}<=set(event) or not isinstance(event.get(text_field),str) or not event[text_field].strip():
                raise ValueError('Missing event/speech text')
            a,b = event.get('start_s'),event.get('end_s')
            if a is None and b is None:continue
            if any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) for x in [a,b]) or not 0<=a<b<=duration+.05:
                raise ValueError('Invalid timestamps; null pairs permitted, fabricated zero-duration times rejected')
    return result


def category_present(sound, category):
    if re.search(r'\b(no|not|without|absent)\b',sound,re.I):
        return False
    pattern = r'\b(dog|dogs|bark\w*|woof\w*)\b' if category=='dog' else r'\brain(?:s|fall|drops|ing)?\b'
    return bool(re.search(pattern,sound,re.I))


def build_assessment(data, protocol):
    if not protocol.get('manifest_sha256') or data.get('manifest_sha256') != protocol['manifest_sha256']:
        raise ValueError('Report does not match the frozen experiment manifest')
    rows=[]
    for call in data['calls']:
        row={'case':call['case'],'http_status':call.get('http_status'),'seconds':call['seconds']}
        if call.get('http_status')!=200:
            row['status']='inconclusive-provider-or-transport';row['error']=call.get('error');rows.append(row);continue
        if call['case']=='c04-speech':
            choices=call['response'].get('choices') or []
            text=choices[0].get('message',{}).get('content') if choices else None
            if not choices or choices[0].get('finish_reason')!='stop' or not isinstance(text,str) or not text.strip():
                row.update(status='invalid-or-incomplete-output',error='Speech control did not finish with usable text')
                rows.append(row);continue
            normalized=re.sub(r'[^a-z0-9 ]','',text.lower()).strip().replace('seventeen','17')
            row.update(status='speech-positive-control',matches_expected=normalized=='17 blue lanterns are beside the window',text=text)
        else:
            try:result=validate_result(call['response'])
            except (ValueError,KeyError,TypeError) as e:
                row.update(status='invalid-or-incomplete-output',error=str(e));rows.append(row);continue
            row.update(status='complete-observation',observation=result)
            identity=call['case'].split('-')[0]
            if identity=='c00':
                row['mute_pass']=not result['events'] and not result['speech']
            else:
                expected=protocol['cases'][identity];events=[e for e in result['events'] if category_present(e['sound'],expected['category'])]
                row['strict_category_present']=bool(events)
                lo,hi=expected['source_support_s']
                row['known_silence_padding_respected']=all(e['start_s'] is not None and e['start_s']>=lo-.25 and e['end_s']<=hi+.25 for e in result['events']) if result['events'] else None
                row['target_onset_s']=min((e['start_s'] for e in events if e['start_s'] is not None),default=None)
        rows.append(row)
    shifts=[]
    indexed={r['case']:r for r in rows}
    for mode in ['audio','split-av']:
        a=indexed.get('c01-'+mode,{}).get('target_onset_s');b=indexed.get('c02-'+mode,{}).get('target_onset_s')
        shifts.append({'mode':mode,'observed_onset_shift_s':b-a if a is not None and b is not None else None,
            'expected_shift_s':3,'pass':abs((b-a)-3)<=.5 if a is not None and b is not None else None})
    return {'inference_calls':len(rows),'rows':rows,'timing_shift_checks':shifts,
        'automatic_installation':False,'model_gate_cleared':False,
        'interpretation':'Keyword recognition and timestamp bounds are narrow checks, not proof of correct full descriptions. Inspect raw responses; no aggregate film-quality claim.'}


def score(report):
    protocol=json.loads((EVIDENCE/'protocol.json').read_text())
    output=build_assessment(json.loads(report.read_text()),protocol)
    path=EVIDENCE/'assessment.json'
    if path.exists():raise ValueError('Assessment already exists')
    path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'calls':output['inference_calls'],
        'strict_category_hits':sum(r.get('strict_category_present',False) for r in output['rows']),
        'shifts':output['timing_shift_checks']},indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','score']);p.add_argument('--report',type=Path)
    a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.report:score(a.report)
    else:p.error('Provide --report')


if __name__=='__main__':main()
