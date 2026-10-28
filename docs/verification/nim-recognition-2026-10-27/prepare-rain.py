"""Prepare the conditional sustained-sound comparison. No inference."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('controls', HERE / 'prepare-controls.py')
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


def main():
    path = HERE / 'inputs/rain.json'
    assert not path.exists(), 'Preserve frozen inputs'
    source_protocol = json.loads((controls.ROOT / 'docs/verification/nim-counterfactuals-2026-10-26/protocol.json').read_text())
    source = controls.ROOT / source_protocol['cases']['c03']['file']
    assert controls.sha(source) == source_protocol['cases']['c03']['sha256']
    original = controls.read_pcm(source)
    cropped = original[16000:96000]
    assert not any(original[:16000]) and not any(original[96000:])
    assert any(cropped) and len(cropped) == 80000
    fixtures = {'q04': original, 'q05': cropped, 'q06': controls.array.array('h', [0]) * 160000}
    jobs, details = [], {}
    for case, samples in fixtures.items():
        fixture = controls.ART / (case + '.wav')
        controls.write_pcm(fixture, samples)
        jobs.append(controls.job(case, fixture))
        details[case] = {'file': str(fixture.relative_to(controls.ROOT)), 'sha256': controls.sha(fixture),
            'samples': len(samples), 'duration_s': len(samples) / 16000,
            'evaluation_only_label': 'rain' if case != 'q06' else 'digital-silence'}
    path.write_text(json.dumps(jobs, indent=2) + '\n')
    (HERE / 'rain-protocol.json').write_text(json.dumps({
        'created_before_rain_inference': True,
        'trigger': 'All three first-stage calls completed; neither bark recognized and short silence hallucinated.',
        'source_wav_sha256': controls.sha(source), 'manifest_sha256': controls.sha(path),
        'fixtures': details, 'source_crop_samples': [16000, 96000],
        'amplitude_changed': False, 'crop_contains_all_source_nonzero_samples': True,
        'same_prompt_and_generation_parameters_as_first_stage': True,
        'criteria': {'strict': 'rain/precipitation-like sound', 'partial': 'generic water noise without correct rain identification',
            'silence': 'no audible sound and no asserted event', 'inconclusive': 'capacity, timeout or incomplete completion'},
        'limits': ['Dataset labels, not fresh human panel annotations.',
            'One sustained source cannot establish all environmental sound capability.',
            'No timing or audiovisual requests unless recognition/absence prerequisites pass.']}, indent=2) + '\n')
    print('Prepared sustained-sound controls with exact crop/padding checks. No inference.')


if __name__ == '__main__':
    main()
