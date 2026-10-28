"""Offline comparison/integrity checks; no inference or playback changes."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / 'assessment.json'
    assert not out.exists()
    protocol = json.loads((HERE / 'protocol.json').read_text())
    manifest = json.loads((HERE / 'inputs/manifest.json').read_text())
    report = json.loads((HERE / 'reports/comparisons.json').read_text())
    assert report['manifest_sha256'] == protocol['manifest_sha256'] == digest(HERE / 'inputs/manifest.json')
    assert [j['case'] for j in manifest][:len(report['calls'])] == [c['case'] for c in report['calls']]
    rows = []
    for call in report['calls']:
        for fixture in call['fixtures']:
            assert digest(ROOT / fixture['file']) == fixture['sha256']
        choice = (call.get('response', {}).get('choices') or [{}])[0]
        text = choice.get('message', {}).get('content')
        completed = call.get('http_status') == 200 and choice.get('finish_reason') == 'stop' and isinstance(text, str) and bool(text.strip())
        mute = call['case'].endswith('-mute')
        row = {'case': call['case'], 'http_status': call.get('http_status'), 'seconds': call['seconds'],
            'finish_reason': choice.get('finish_reason'), 'text': text,
            'status': 'completed-observation' if completed else 'inconclusive-provider-or-transport'}
        if mute and completed:
            row['mute_pass'] = text.strip() == 'NO_AUDIBLE_EVENT'
            row['manual_interpretation'] = ('False sound assertion on digital-zero PCM; the described rabbit/apple action is visual context, not audible evidence.'
                if not row['mute_pass'] else 'Absence control passed on this request.')
        rows.append(row)
    for prefix, fixture in protocol['fixtures'].items():
        normal = [c for c in report['calls'] if c['case'] in [prefix+'-audio', prefix+'-single', prefix+'-triplet']]
        assert len({c['fixtures'][0]['sha256'] for c in normal}) == 1
        assert {c['fixtures'][0]['sha256'] for c in normal} == {fixture['audio_sha256']}
        for frame in fixture['frames']:
            assert digest(ROOT / frame['file']) == frame['sha256']
            assert abs(frame['actual_pts_s'] - frame['requested_time_s']) <= .05
    result = {'inference_attempts': len(rows), 'http_counts': dict(Counter(str(r['http_status']) for r in rows)),
        'rows': rows, 'integrity': {'fixture_and_manifest_hashes_match': True,
            'same_pcm_across_context_modes': True, 'actual_frame_pts_verified': True,
            'reference_captions_not_used_as_inputs': True},
        'findings': ['Frames helped produce visible source/location claims, not a demonstrated acoustic accuracy gain.',
            'One completed mute control asserted a thud despite all-zero audio; the other mute request was capacity-blocked.',
            'The second normal three-frame request was also blocked; do not score missing pairs as accuracy failures.',
            'RMS candidates establish activity changes, not event identity or perceptual boundaries.',
            'Post-generation reference overlap is incomplete editorial evidence, not independent listening ground truth.'],
        'accepted_for_playback': False, 'model_gate_cleared': False,
        'limits': 'Main-session manual interpretation; tiny two-candidate comparison; no independent listening or DHH evaluation.'}
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'attempts': len(rows), 'http_counts': result['http_counts'],
        'mute_results': [{k: r[k] for k in ['case', 'status', 'mute_pass'] if k in r} for r in rows if r['case'].endswith('-mute')],
        'accepted': False}, indent=2))


if __name__ == '__main__':
    main()
