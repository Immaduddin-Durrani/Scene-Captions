"""Verify saved report/media integrity and preserve a limited manual assessment. No inference."""
import array
import importlib.util
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('controls', HERE / 'prepare-controls.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

RUNS = ['recognition', 'rain', 'speech', 'speech-description', 'rain-retry', 'final-checks']
OUTCOMES = {
    'q01': ('failed-recognition', 'Expected dog; response asserted silence.'),
    'q02': ('failed-recognition', 'Expected dog; response asserted a door opening.'),
    'q03': ('failed-absence', 'Digital-zero PCM; response asserted a drum hit.'),
    'q04': ('partial-water-related', 'Dataset rain; response asserts waves/surf/ocean. Strict rain criterion not met.'),
    'q05': ('partial-water-related', 'Dataset rain; response describes flowing water. Strict rain criterion not met.'),
    'q06': ('passed-absence-control', 'Ten-second digital-zero PCM correctly described as silence.'),
    'q07': ('passed-speech-control', 'Fresh expected phrase transcribed exactly.'),
    'q08': ('failed-speech-presence', 'Same audible speech as q07; general description incorrectly asserts no sound.'),
    'q09': ('partial-repetition-recognition', 'Repeated short events described as percussive impacts; dog category not identified. Other acoustic claims unreviewed.')}


def main():
    output = HERE / 'assessment.json'
    assert not output.exists(), 'Preserve saved assessment'
    rows, last, requests = [], {}, {}
    counts = Counter()
    for run in RUNS:
        manifest = HERE / 'inputs' / (run + '.json')
        report = HERE / 'reports' / (run + '.json')
        data = json.loads(report.read_text())
        assert data['manifest_sha256'] == c.sha(manifest)
        jobs = json.loads(manifest.read_text())
        assert [j['case'] for j in jobs] == [r['case'] for r in data['calls']]
        for call in data['calls']:
            case = call['case']
            counts[str(call.get('http_status', 'no-http-status'))] += 1
            for fixture in call['fixtures']:
                assert c.sha(c.ROOT / fixture['file']) == fixture['sha256']
            if case in requests:
                assert call['wire_sha256'] == requests[case]['wire_sha256'], 'Retry payload changed'
            requests[case] = call
            choice = (call.get('response', {}).get('choices') or [{}])[0]
            text = choice.get('message', {}).get('content')
            complete = call.get('http_status') == 200 and choice.get('finish_reason') == 'stop' and isinstance(text, str) and bool(text.strip())
            status, rationale = OUTCOMES[case] if complete else ('inconclusive-provider-or-transport', call.get('error', 'Incomplete response'))
            row = {'run': run, 'case': case, 'http_status': call.get('http_status'),
                   'finish_reason': choice.get('finish_reason'), 'seconds': call['seconds'],
                   'text': text, 'status': status, 'rationale': rationale}
            rows.append(row)
            if complete:
                last[case] = row
    initial = json.loads((HERE / 'protocol.json').read_text())
    for case, fixture in initial['fixtures'].items():
        assert c.sha(c.ROOT / fixture['file']) == fixture['sha256']
    original = c.read_pcm(c.ART / 'q01.wav')
    source = c.ROOT / 'artifacts/nim-counterfactuals-2026-10-26/c01.wav'
    assert original == c.read_pcm(source)
    assert c.read_pcm(c.ART / 'q02.wav') == original[44000:68000]
    assert not any(c.read_pcm(c.ART / 'q03.wav'))
    assert not any(c.read_pcm(c.ART / 'q06.wav'))
    rain = c.read_pcm(c.ART / 'q04.wav')
    assert rain == c.read_pcm(c.ROOT / 'artifacts/nim-counterfactuals-2026-10-26/c03.wav')
    assert c.read_pcm(c.ART / 'q05.wav') == rain[16000:96000]
    nonzero = [i for i, value in enumerate(original) if value]
    burst = original[nonzero[0]:nonzero[-1] + 1]
    repeated = array.array('h', [0]) * 160000
    for onset in range(1, 9):
        repeated[onset * 16000:onset * 16000 + len(burst)] = burst
    assert repeated == c.read_pcm(c.ART / 'q09.wav')
    # The successful ASR and failed description differ only in the text instruction.
    a, b = deepcopy(requests['q07']['payload']), deepcopy(requests['q08']['payload'])
    a['messages'][0]['content'][1]['text'] = '<instruction removed for comparison>'
    b['messages'][0]['content'][1]['text'] = '<instruction removed for comparison>'
    assert a == b
    assert requests['q07']['fixtures'][0]['sha256'] == requests['q08']['fixtures'][0]['sha256']
    speech_protocol = json.loads((HERE / 'speech-protocol.json').read_text())
    assert last['q07']['text'] == speech_protocol['evaluation_only_expected_text']
    result = {'scope': 'Small NVIDIA-only endpoint diagnostic, not a film-caption benchmark.',
        'inference_attempts': len(rows), 'unique_cells': len(requests), 'http_outcomes': dict(counts),
        'review_method': 'Manual text interpretation in the main session against dataset labels and constructed controls; no independent listening panel.',
        'rows': rows, 'last_complete_observation_by_cell': last,
        'integrity': {'manifest_hashes_match': True, 'fixture_hashes_match': True,
            'exact_crop_sample_equality': True, 'digital_silence_confirmed': True,
            'repeated_burst_sample_equality': True, 'retry_payloads_unchanged': True,
            'asr_vs_description_same_audio_and_parameters_only_text_changed': True},
        'interpretation': ['Shorter context did not establish dog recognition.',
            'Repeated samples yielded repetition-related acoustic text, not a strict dog hit.',
            'Silence outcomes differ across durations/requests; neither a unique duration mechanism nor out-of-distribution input is proven.',
            'Speech transcript versus sound-description discrepancy establishes an observed task-dependent outcome; opaque serving/replica variability remains a possible confound.',
            'Broad water descriptions are partial evidence, not accepted strict rain captions.'],
        'timing_and_video_tests': 'Not run: prerequisite recognition and absence controls did not pass.',
        'automatic_installation': False, 'model_gate_cleared': False}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'attempts': len(rows), 'unique_cells': len(requests), 'http_outcomes': dict(counts), 'integrity': 'passed'}, indent=2))


if __name__ == '__main__':
    main()
