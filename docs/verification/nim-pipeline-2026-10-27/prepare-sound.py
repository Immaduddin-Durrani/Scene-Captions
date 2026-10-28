"""Prepare sound-stage jobs from actual audio and our own uncertain ASR output."""
import json
import re
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
helpers = run_path(str(HERE / 'prepare.py'))
ROOT, sha, samples = helpers['ROOT'], helpers['sha'], helpers['samples']


def transcript(call):
    return ' '.join(r.get('alternatives', [{}])[0].get('transcript', '')
                    for r in call.get('response', {}).get('results', [])).strip()


def guarded_speech(raw, digital_zero):
    raw = raw.strip()
    markup = bool(re.fullmatch(r'\*[^*]+\*|\[[^\]]+\]', raw)) or not re.search(r'[A-Za-z0-9]', raw)
    unknown = '<unk>' in raw.lower()
    return None if digital_zero or markup or unknown or not raw else raw


def main():
    out = HERE / 'inputs/sounds.json'
    assert not out.exists()
    jobs = json.loads((HERE / 'inputs/asr.json').read_text())
    calls = [c for name in ['asr-access', 'asr-controls']
             for c in json.loads((HERE / 'reports' / (name + '.json')).read_text())['calls']]
    indexed = {c['case']: c for c in calls}
    prepared, guards = [], {}
    for fixture in jobs:
        case = fixture['case']; path = ROOT / fixture['file']; pcm = samples(path)
        assert sha(path) == fixture['sha256']
        call = indexed.get(case)
        raw = transcript(call) if call and call.get('grpc_status') == 'OK' else ''
        zero = not any(pcm)
        markup = bool(re.fullmatch(r'\*[^*]+\*|\[[^\]]+\]', raw)) or not re.search(r'[A-Za-z0-9]', raw)
        usable = guarded_speech(raw, zero)
        guards[case] = {'raw_asr_text': raw, 'candidate_speech_text': usable,
            'digital_zero': zero, 'asr_markup_or_empty': markup,
            'status': 'candidate, not independent ground truth' if usable else 'speech not established'}
        if zero:
            guards[case]['sound_stage'] = 'bypassed locally: all PCM samples zero; no cloud sound events'
            continue
        prompt = ('Listen to the recording and describe ONLY audible non-speech sounds, including music, '
            'environmental effects and non-word vocalizations. Do not describe visible or imagined scenes. '
            'A separate speech recognizer proposed the following words, which may be wrong: '
            + (json.dumps(usable) if usable else 'No lexical speech transcript was established.')
            + '\nUse that only to separate dialogue from effects; it does not establish any sound source. '
            'Base all sound observations on the attached audio. Do not repeat spoken words. '
            'Give a concise factual description. If no non-speech event is audible, reply NO_NON_SPEECH_EVENTS. '
            'Do not guess uncertain sound identities or attributes. No timestamps or JSON are required.')
        prepared.append({'case': case, 'hypothesis': 'Separate ASR from non-speech observations; own ASR is uncertain context, never fetched captions.',
            'payload': {'model': 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning',
                'messages': [{'role': 'user', 'content': [{'type': 'local_wav', 'path': fixture['file']},
                                                       {'type': 'text', 'text': prompt}]}],
                'temperature': .2, 'top_k': 1, 'max_tokens': 512, 'stream': False,
                'chat_template_kwargs': {'enable_thinking': False}}})
    out.write_text(json.dumps(prepared, indent=2) + '\n')
    (HERE / 'asr-guards.json').write_text(json.dumps(guards, indent=2) + '\n')
    (HERE / 'sound-protocol.json').write_text(json.dumps({'created_before_sound_inference': True,
        'manifest_sha256': sha(out), 'calls': len(prepared), 'digital_zero_bypass': ['p02'],
        'purpose': 'Test separation of speech transcription and sound descriptions with own ASR as uncertain context.',
        'expected_labels_sent': False, 'reference_captions_or_plot_sent': False,
        'criteria': {'p01': 'No invented non-speech events on the clean synthetic phrase.',
            'p03': 'Dog vocalizations; generic impacts are partial only.',
            'p04': 'Three dog-source bursts without inventing dialogue/effects.',
            'p05': 'Unreviewed actual BBB window; no established accuracy claim.'},
        'limits': ['Raw ASR can hallucinate. Markup is not acoustic ground truth.',
            'Local zero check protects only exact digital silence, not arbitrary noise/music.',
            'No sound times requested; unresolved times must stay null during rendering.']}, indent=2) + '\n')
    (HERE / 'timing-protocol.json').write_text(json.dumps({'created_before_parakeet_inference': True,
        'trigger': 'Whisper transcribed positive controls but returned no words/timestamps despite the offset flag.',
        'model': 'nvidia/parakeet-tdt-0.6b-v2', 'function_id': 'd3fe9151-442b-4204-a70d-5fcc597fd610',
        'source': 'https://build.nvidia.com/nvidia/parakeet-tdt-0_6b-v2/api',
        'cases': ['p01', 'p04'], 'max_initial_calls': 2,
        'criteria': 'Match the expected words, return finite ordered word offsets within clip bounds; compare +0.5s speech shift.',
        'limits': 'Separate dedicated ASR model; not proof of Omni or non-speech timing.'}, indent=2) + '\n')
    print('Prepared four sound jobs; exact-zero and ASR-markup guards recorded. No inference.')


if __name__ == '__main__':
    main()
