"""Prepare a repeated-event control and one exact-payload capacity retry; no inference."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('controls', HERE / 'prepare-controls.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def main():
    manifest = HERE / 'inputs/final-checks.json'
    assert not manifest.exists(), 'Preserve frozen inputs'
    original = c.read_pcm(c.ART / 'q01.wav')
    nonzero = [i for i, value in enumerate(original) if value]
    burst = original[nonzero[0]:nonzero[-1] + 1]
    repeated = c.array.array('h', [0]) * 160000
    for onset in range(1, 9):
        start = onset * 16000
        assert not any(repeated[start:start + len(burst)])
        repeated[start:start + len(burst)] = burst
    assert len(repeated) == 160000
    assert sum(bool(x) for x in repeated) == 8 * sum(bool(x) for x in burst)
    assert max(map(abs, repeated)) == max(map(abs, original))
    path = c.ART / 'q09.wav'
    c.write_pcm(path, repeated)
    retry = json.loads((HERE / 'inputs/speech-description.json').read_text())[0]
    dense = c.job('q09', path)
    dense['hypothesis'] = 'Same source burst repeated without gain changes at eight onsets; test recognition under increased event exposure.'
    manifest.write_text(json.dumps([retry, dense], indent=2) + '\n')
    (HERE / 'final-protocol.json').write_text(json.dumps({
        'created_before_final_inference': True,
        'manifest_sha256': c.sha(manifest),
        'q08': {'purpose': 'One unchanged-payload retry after capacity failure; same speech WAV as successful ASR control.',
                'max_total_attempts_for_this_cell': 2},
        'q09': {'wav_sha256': c.sha(path), 'duration_s': 10, 'evaluation_only_label': 'dog',
                'onsets_s': list(range(1, 9)), 'burst_samples': len(burst),
                'amplitude_changed': False, 'source_burst_samples_identical': True,
                'criteria': 'Dog/bark/canine vocalization is strict recognition. Generic taps or another source is not.',
                'limits': 'Changes repetition, temporal exposure and whole-clip RMS; not proof of a unique encoder or sparsity mechanism.'},
        'stop': 'Final two requests for this session, no retry of q09. No timing/video/full-film calls because prerequisite recognition/absence tests failed.'
    }, indent=2) + '\n')
    print('Prepared exact-sample repeated-event fixture and one unchanged capacity retry. No inference.')


if __name__ == '__main__':
    main()
