"""Freeze an audio-only recognition gate and documented preset comparison. No inference."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL = 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
LABELS = ['human_speech', 'dog_barking', 'bird_call', 'rainfall', 'running_water_or_waves',
          'music', 'tone_or_beep', 'impact_or_click', 'other_sound', 'silence', 'uncertain']
PROMPT = ('Listen to the recording. Which meaningful sound-event categories are actually audible? '
    'Use this same fixed vocabulary: ' + ', '.join(LABELS) + '. '
    'Choose all clearly supported categories; do not guess a category merely because it is listed. '
    'Do not count speech consonants as environmental impacts or voiced speech as an electronic tone. '
    'silence means no audible signal, not merely no speech. If uncertain about every category, '
    'choose uncertain. Return only a JSON array of category names, no explanation or timestamps.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (HERE / 'protocol.json').exists()
    recent = ROOT / 'artifacts/nim-recognition-2026-10-27'
    mixed = ROOT / 'artifacts/nim-pipeline-2026-10-27/p04.wav'
    frames = json.loads((ROOT / 'docs/verification/nim-frame-pipeline-2026-10-27/protocol.json').read_text())
    source_jobs = {j['case']: j for j in json.loads((ROOT / 'docs/verification/nim-pipeline-2026-10-27/inputs/asr.json').read_text())}
    rain_info = json.loads((ROOT / 'docs/verification/nim-recognition-2026-10-27/rain-protocol.json').read_text())
    dog_info = json.loads((ROOT / 'docs/verification/nim-recognition-2026-10-27/final-protocol.json').read_text())
    speech_info = json.loads((ROOT / 'docs/verification/nim-recognition-2026-10-27/speech-protocol.json').read_text())
    specs = {'k01': (recent / 'q07.wav', speech_info['wav_sha256'], ['human_speech']),
        'k02': (recent / 'q09.wav', dog_info['q09']['wav_sha256'], ['dog_barking']),
        'k03': (recent / 'q05.wav', rain_info['fixtures']['q05']['sha256'], ['rainfall']),
        'k04': (recent / 'q06.wav', rain_info['fixtures']['q06']['sha256'], ['silence']),
        'k05': (mixed, source_jobs['p04']['sha256'], ['human_speech', 'dog_barking']),
        'k06': (ROOT / frames['fixtures']['f02']['audio_file'], frames['fixtures']['f02']['audio_sha256'], None)}
    jobs, details = [], {}
    for case, (path, expected_hash, labels) in specs.items():
        assert sha(path) == expected_hash
        details[case] = {'file': str(path.relative_to(ROOT)), 'sha256': expected_hash,
            'evaluation_only_expected_labels': labels}
        payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': [
            {'type': 'local_wav', 'path': str(path.relative_to(ROOT))}, {'type': 'text', 'text': PROMPT}]}],
            'temperature': .2, 'top_k': 1, 'max_tokens': 1024, 'stream': False,
            'chat_template_kwargs': {'enable_thinking': False}}
        jobs.append({'case': case+'-instruct', 'hypothesis': 'Audio-only fixed-category evidence before visual source association.', 'payload': payload})
    for case in ['k02', 'k04']:
        payload = json.loads(json.dumps(next(j['payload'] for j in jobs if j['case'] == case+'-instruct')))
        payload.pop('top_k')
        payload.update(temperature=.6, top_p=.95, max_tokens=20480, reasoning_budget=16384,
                       chat_template_kwargs={'enable_thinking': True})
        jobs.append({'case': case+'-thinking', 'hypothesis': 'Documented hosted-compatible thinking preset, same audio and category prompt.', 'payload': payload})
    # Ensure both anchor presets are attempted early if the endpoint is available.
    order = ['k04-instruct', 'k04-thinking', 'k02-instruct', 'k02-thinking',
             'k01-instruct', 'k03-instruct', 'k05-instruct', 'k06-instruct']
    indexed = {j['case']: j for j in jobs}; jobs = [indexed[case] for case in order]
    manifest = HERE / 'inputs/audio.json'; manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    protocol = {'created_before_inference': True, 'date': '2026-10-27', 'fixtures': details,
        'manifest_sha256': sha(manifest), 'same_fixed_vocabulary_and_prompt_all_cases': True,
        'task': 'Closed-vocabulary classification; correct labels are evaluation-only. This is not an open-ended caption benchmark.',
        'labels': LABELS, 'reference_caption_or_plot_input': False,
        'preset_source': 'https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard',
        'reasoning_budget_source': 'https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer',
        'preset_limits': 'A bundle comparison, not an isolated thinking toggle. Server-only grace/context settings are not assumed configurable.',
        'criteria': {'complete': 'HTTP200, explicit stop, JSON list of distinct allowed labels.',
            'positive_controls': 'Exact expected label sets; false added labels counted separately. Empty/uncertain results are abstentions, not passes.',
            'rain': 'rainfall required; water/waves is only partial, not a weakened substitute.',
            'silence': 'Only silence, without asserted events.',
            'bbb': 'No human ground truth; do not score as correct from fluency or scene plausibility.',
            'visual': 'No new event IDs, no changes to acoustic facts, unresolved association when unsupported; empty ledgers must stay empty.'},
        'budget': {'maximum_total_requests': 14, 'initial_audio_requests': 8,
            'max_visual_requests': 4, 'optional_open_description_requests': 1,
            'budget_compatibility_retries': 'At most two, only if documented budget parameter is rejected; all requests count toward14.',
            'no_automatic_retries': True, 'stop_after_consecutive_capacity_errors_per_stage': 3,
            'per_request_timeout_s': 180},
        'conditional_plan': ['Test fixed categories and hosted-supported reasoning presets on known controls.',
            'If budget is rejected, remove only that parameter for one explicit follow-up per rejected thinking cell.',
            'Test vision as association-only with real/constructed ledgers clearly distinguished and matching/mismatched/silent controls.',
            'If a positive category passes, optionally test free audio description without the label vocabulary.',
            'Never clear the existing failed audio gate or install a track from bookkeeping/schema success.'],
        'limits': ['Tiny reused synthetic/ESC-10 controls; closed categories can make recognition easier without solving open discovery.',
            'No independent listening panel or DHH usability study.', 'Visual abstention alone is not a useful positive caption.',
            'Vision cannot repair an incorrect acoustic event ledger.']}
    (HERE / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    print('Eight audio jobs frozen; labels hidden per case, common vocabulary disclosed. No inference.')


if __name__ == '__main__':
    main()
