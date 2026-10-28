"""Prepare blinded PCM controls without inference or reading caption tracks."""
import array
import hashlib
import json
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / 'artifacts/nim-recognition-2026-10-27'
OUT = Path(__file__).resolve().parent
MODEL = 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
PROMPT = ('Describe the audible sounds in this recording. If no sound is audible, '
          'say so. Do not infer sounds from context.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_pcm(path):
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000)
        samples = array.array('h', w.readframes(w.getnframes()))
    if sys.byteorder != 'little':
        samples.byteswap()
    return samples


def write_pcm(path, samples):
    data = array.array('h', samples)
    if sys.byteorder != 'little':
        data.byteswap()
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(data.tobytes())
    assert read_pcm(path) == samples


def job(case, path):
    return {'case': case, 'hypothesis': 'Audio-only recognition with no timing or schema burden; raw media only.',
            'payload': {'model': MODEL, 'messages': [{'role': 'user', 'content': [
                {'type': 'local_wav', 'path': str(path.relative_to(ROOT))},
                {'type': 'text', 'text': PROMPT}]}],
                'temperature': .2, 'top_k': 1, 'max_tokens': 256,
                'stream': False, 'chat_template_kwargs': {'enable_thinking': False}}}


def main():
    assert not (OUT / 'protocol.json').exists(), 'Preserve frozen inputs'
    ART.mkdir(parents=True, exist_ok=True)
    (OUT / 'inputs').mkdir(exist_ok=True)
    old = ROOT / 'docs/verification/nim-counterfactuals-2026-10-26/protocol.json'
    old_protocol = json.loads(old.read_text())
    source = ROOT / old_protocol['cases']['c01']['file']
    assert sha(source) == old_protocol['cases']['c01']['sha256']
    original = read_pcm(source)
    assert len(original) == 160000
    # 1.5 s crop containing the exact burst, with silence on both sides.
    start, end = 44000, 68000
    cropped = original[start:end]
    assert not any(original[:start]) and not any(original[end:])
    assert any(cropped) and len(cropped) == 24000
    fixtures = {'q01': original, 'q02': cropped, 'q03': array.array('h', [0]) * len(cropped)}
    jobs, details = [], {}
    for case, samples in fixtures.items():
        path = ART / (case + '.wav')
        write_pcm(path, samples)
        nonzero = [i for i, value in enumerate(samples) if value]
        details[case] = {'file': str(path.relative_to(ROOT)), 'sha256': sha(path),
            'samples': len(samples), 'duration_s': len(samples) / 16000,
            'nonzero_support_s': [nonzero[0] / 16000, (nonzero[-1] + 1) / 16000] if nonzero else None,
            'evaluation_only_label': 'dog' if case != 'q03' else 'digital-silence'}
        jobs.append(job(case, path))
    manifest = OUT / 'inputs/recognition.json'
    manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    protocol = {'created_before_inference': True, 'date': '2026-10-27',
        'model': MODEL, 'fixtures': details, 'source_protocol_sha256': sha(old),
        'source_wav_sha256': sha(source), 'crop_source_sample_range': [start, end],
        'crop_amplitude_changed': False, 'crop_contains_all_original_nonzero_samples': True,
        'manifest_sha256': sha(manifest), 'caption_or_plot_input': False,
        'criteria': {'completed': 'HTTP 200, finish_reason stop and nonempty text',
            'recognition': 'dog/bark/canine vocalization; generic sound alone is partial, not a strict hit',
            'silence': 'no audible sound, with no asserted sound event',
            'capacity_timeout': 'inconclusive, not semantic failure'},
        'budget': {'initial_recognition_calls': 3, 'max_total_calls': 24,
            'max_retries_per_inconclusive_cell': 1, 'timeout_s': 180,
            'min_start_interval_s': 2.05,
            'stop': 'Stop at authentication failure or three consecutive capacity errors. No full-film run.'},
        'conditional_next_steps': [
            'If sound recognition fails: up to three rain/silence recognition controls; keep original crop samples.',
            'If dog recognized in both recordings: test c01/c02 temporal shift, two requests.',
            'If a natural sound and absence controls succeed: at most four audio/silent-video comparison requests.',
            'A fresh speech positive control may diagnose transport if completed natural-sound requests fail.'],
        'limits': ['Dataset category labels are evaluation-only, not listening-panel annotations.',
            'Cropping changes duration/context and whole-clip RMS, while preserving sample amplitudes; it does not isolate every preprocessing mechanism.',
            'This is a tiny endpoint diagnostic, not movie accuracy or DHH usability evidence.',
            'No output installation or capability-gate changes are authorized by a passing isolated fixture.']}
    (OUT / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    print('Prepared three blinded controls; exact crop equality and silence checks passed. No API calls.')


if __name__ == '__main__':
    main()
