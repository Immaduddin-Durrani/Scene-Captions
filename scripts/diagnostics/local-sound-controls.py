"""Bounded local audio observations; never generates or installs a film caption track."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import wave

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ('Describe only the audible contents of this recording in one concise sentence. '
          'Mention overlapping sounds if audible. Do not infer visual events, objects, a story or inaudible causes. '
          'If there is no audible sound, say no audible sound.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-directory', type=Path, required=True)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--plain-observation', action='store_true', help='Single-factor follow-up using a plain audio-observation prompt')
    args = parser.parse_args()
    report = args.report.resolve()
    if not report.is_relative_to((ROOT/'docs/verification').resolve()) or report.exists():
        parser.error('Choose a NEW report under docs/verification/.')
    directory = args.model_directory.resolve()
    info = json.loads((directory/'source-info.json').read_text())
    if info['sha'] != '66e7276cfc589073b4f92ebed58c05301f990222':
        parser.error('This bounded run requires the recorded pinned model revision.')
    weights = directory/'model.safetensors'
    expected = next(item for item in info['siblings'] if item['rfilename'] == weights.name)
    with weights.open('rb') as handle:
        actual = hashlib.file_digest(handle, 'sha256').hexdigest()
    if weights.stat().st_size != expected['size'] or actual != expected['lfs']['sha256']:
        parser.error('Local model weights do not match the pinned Hub LFS object.')
    cases = json.loads(args.cases.read_text())
    if not 1 <= len(cases) <= 6:
        parser.error('This diagnostic is limited to six short controls/anchors.')
    for case in cases:
        path = (ROOT/case['file']).resolve()
        if not path.is_relative_to((ROOT/'artifacts/sound-captions').resolve()) or case['duration_s'] > 8:
            parser.error('Only short local diagnostic fixtures are permitted.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != case['sha256']:
            parser.error('Audio fixture hash changed.')
        with wave.open(str(path), 'rb') as wav:
            duration = wav.getnframes() / wav.getframerate()
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 16000:
                parser.error('Controls require mono 16-bit PCM at 16 kHz.')
        if not 0 < duration <= 8 or abs(duration - case['duration_s']) > 1/16000:
            parser.error('Measured audio duration exceeds the short-control bound or disagrees with metadata.')
    # No network access, credentials, telemetry, persistent service or player code.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HOME'] = str(Path.home()/'runtimes/cache/huggingface')
    import mlx.core as mx
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    mx.random.seed(0)
    mx.set_memory_limit(7 * 1024**3)
    mx.set_cache_limit(256 * 1024**2)
    observation = 'Describe what you hear.' if args.plain_observation else PROMPT
    record = {'model': info['id'], 'revision': info['sha'], 'weights_sha256': actual,
              'engine': 'local MLX-VLM 0.7.10', 'prompt': observation, 'temperature': 0,
              'max_tokens': 96, 'call_ceiling': len(cases), 'tests': [],
              'scope': 'Small synthetic controls and licensed source-caption anchors. Ground-truth metadata is never sent in the prompt. No film track generation, installation or review approval.'}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, indent=2)+'\n')
    model, processor = load(str(directory), trust_remote_code=False)
    prompt = apply_chat_template(processor, model.config, observation, num_audios=1)
    for case in cases:
        started = time.monotonic()
        output = generate(model, processor, prompt, audio=[str((ROOT/case['file']).resolve())], max_tokens=96, temperature=0.0, verbose=False)
        text = output.text if hasattr(output, 'text') else str(output)
        tokens = getattr(output, 'generation_tokens', None)
        record['tests'].append({**case, 'response': text, 'finish_reason': getattr(output, 'finish_reason', None),
                                'generation_tokens': int(tokens) if tokens is not None else None,
                                'seconds': round(time.monotonic()-started, 3)})
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(record, indent=2)+'\n')
        print(case['name'], repr(text), flush=True)
        mx.clear_cache()


if __name__ == '__main__': main()
