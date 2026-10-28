"""Assess audio recognition separately from late-association bookkeeping. No inference."""
import hashlib
import importlib.util
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('late_binding_checks', HERE / 'binding.py')
binding = importlib.util.module_from_spec(spec); spec.loader.exec_module(binding)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / 'assessment.json'; assert not out.exists()
    protocol = json.loads((HERE / 'protocol.json').read_text())
    all_calls, audio = [], []
    for name, manifest in [('audio', 'audio'), ('audio-capacity-retry', 'audio-capacity-retry'), ('visual', 'visual')]:
        report = json.loads((HERE / 'reports' / (name + '.json')).read_text())
        assert report['manifest_sha256'] == digest(HERE / 'inputs' / (manifest + '.json'))
        for call in report['calls']:
            for fixture in call.get('fixtures', []):
                assert digest(ROOT / fixture['file']) == fixture['sha256']
            all_calls.append(call)
            if name != 'visual':
                audio.append(call)
    assert len(all_calls) <= protocol['budget']['maximum_total_requests']
    initial = {c['case']: c for c in json.loads((HERE / 'reports/audio.json').read_text())['calls']}
    for call in json.loads((HERE / 'reports/audio-capacity-retry.json').read_text())['calls']:
        assert call['wire_sha256'] == initial[call['case']]['wire_sha256']
    audio_rows, last = [], {}
    for call in audio:
        case = call['case']; fixture = protocol['fixtures'][case.split('-')[0]]
        expected = fixture['evaluation_only_expected_labels']
        choice = (call.get('response', {}).get('choices') or [{}])[0]
        row = {'case': case, 'http_status': call.get('http_status'), 'finish_reason': choice.get('finish_reason'),
            'raw_answer': choice.get('message', {}).get('content'), 'expected_labels': expected}
        if call.get('http_status') != 200:
            row.update(status='inconclusive-provider-or-transport', error=call.get('error'))
        else:
            try:
                predicted = binding.labels(call)
                row.update(status='complete-category-observation', labels=predicted)
                if expected is not None:
                    row.update(exact_set_match=set(predicted) == set(expected),
                        missing=sorted(set(expected) - set(predicted)), unsupported=sorted(set(predicted) - set(expected)))
                last[case] = row
            except (ValueError, TypeError, KeyError) as exc:
                row.update(status='invalid-or-incomplete-output', error=str(exc))
                if case == 'k04-instruct':
                    row['manual_semantic_note'] = 'Bare tone_or_beep label is also wrong on digital silence; format failure is recorded separately.'
        audio_rows.append(row)
    visual_inputs = json.loads((HERE / 'visual-inputs.json').read_text())
    visual_rows, ledgers = [], {}
    for call in json.loads((HERE / 'reports/visual.json').read_text())['calls']:
        case = call['case']; source = visual_inputs[case]['events']; before = deepcopy(source)
        row = {'case': case, 'http_status': call.get('http_status')}
        try:
            if call.get('http_status') != 200:
                raise ValueError('Visual stage inconclusive: provider failure')
            result = binding.validate(binding.parse_json(call['response']), source)
            assert source == before, 'Visual validation mutated acoustic data'
            row.update(contract_pass=True, associations=result['associations'])
            if case in ['v02-swapped', 'v03-known-mismatch']:
                row['all_associations_unresolved'] = all(r['status'] == 'unresolved' for r in result['associations'])
            if case == 'v04-empty':
                row['empty_stays_empty'] = result['associations'] == []
            mapping = {r['event_id']: r for r in result['associations']}
            ledgers[case] = {'acceptance_status': 'UNACCEPTED_AUDIO_CANDIDATES',
                'events': [{**event, 'visual_association': mapping[event['event_id']]} for event in before]}
        except (ValueError, KeyError, TypeError) as exc:
            row.update(contract_pass=False, error=str(exc))
        visual_rows.append(row)
    result = {'inference_attempts': len(all_calls), 'http_counts': dict(Counter(str(c.get('http_status')) for c in all_calls)),
        'audio_rows': audio_rows, 'latest_valid_audio_observations': last, 'visual_rows': visual_rows,
        'findings': ['Closed categories elicited a dog tag on one control but also an unsupported tone; exact controlled recognition remained unaccepted.',
            'The hosted-compatible recommended thinking parameters were accepted but did not solve the tested silence or dog controls.',
            'Late association preserved supplied IDs and empty ledgers, and abstained on swapped/known-mismatched contexts in this small test.',
            'The positive visible-source suggestion was orange ball; identity/cause were not verified and it remains a hypothesis.',
            'New vision component differs in model, instruction and task from prior joint-caption requests. This is not a causal architecture-only comparison.',
            'Closed-vocabulary tagging and schema success are not open-ended caption accuracy or DHH usefulness.'],
        'audio_gate_pass': False, 'caption_accuracy_gain_established': False, 'accepted_for_playback': False,
        'limits': 'Tiny reused controls, preset bundle rather than isolated parameter changes; no independent listening panel; optional open-description call omitted to retain the fixed budget.'}
    (HERE / 'candidate-ledgers.json').write_text(json.dumps(ledgers, indent=2) + '\n')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'requests': len(all_calls), 'http': result['http_counts'],
        'visual_contract_passes': sum(r['contract_pass'] for r in visual_rows),
        'audio_gate_pass': False, 'caption_accuracy_gain_established': False}, indent=2))


if __name__ == '__main__':
    main()
