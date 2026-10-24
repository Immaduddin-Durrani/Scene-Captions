"""Bounded single-attempt, cached diagnostic calls. Never generates a film track."""
import argparse, base64, hashlib, json, math, struct, sys, time, wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nim_client import ROOT, MODEL, request
from generation.variants import TEXT_MODEL

CLASSIFY = 'Classify this recording with one word: SILENCE, TONE, MUSIC, SPEECH, OTHER, or UNAVAILABLE. Base the answer only on the audio.'
OBSERVE = 'Describe only the audible contents of this recording in one short sentence. If there are no audible contents, say silence. Do not infer visual events or causes.'
TEXT = 'Return only the broad sound type in [SERENE MUSIC]. Omit the mood word. Use one bracketed label.'


def audio_case(path, rate, kind):
    samples = []
    for i in range(rate * 3):
        t = i / rate
        value = 0 if kind == 'silence' else .24 * math.sin(2 * math.pi * 440 * t)
        if kind == 'mixed':
            value += .13 * math.sin(2 * math.pi * 980 * t) if 1 < t < 2 else 0
        samples.append(int(32767 * value))
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate)
        out.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return {'duration_s': 3, 'sample_rate': rate, 'channels': 1, 'pcm_width': 2, 'rms': (sum(x*x for x in samples)/len(samples))**.5/32767, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'known_contents': kind}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--phase', choices=['initial', 'head-noun'], default='initial')
    args = parser.parse_args()
    report = args.report.resolve()
    if not report.is_relative_to((ROOT/'docs/verification').resolve()) or report.exists():
        parser.error('Choose a new report under docs/verification/')
    cache = ROOT/'artifacts/diagnostics/factor-controls-v1'; cache.mkdir(parents=True, exist_ok=True)
    cases = [
        ('text-temperature-low', TEXT_MODEL, TEXT, .2, None, None),
        ('text-temperature-recommended', TEXT_MODEL, TEXT, 1., None, None),
        ('tone-classify-16k', MODEL, CLASSIFY, .2, 16000, 'tone'),
        ('tone-classify-48k', MODEL, CLASSIFY, .2, 48000, 'tone'),
        ('silence-classify-16k', MODEL, CLASSIFY, .2, 16000, 'silence'),
        ('tone-observe-16k', MODEL, OBSERVE, .2, 16000, 'tone'),
        ('silence-observe-16k', MODEL, OBSERVE, .2, 16000, 'silence'),
        ('holdout-mixed-observe-16k', MODEL, OBSERVE, .2, 16000, 'mixed'),
    ]
    if args.phase == 'head-noun':
        explicit = 'Copy the sound-category noun from the supplied bracketed caption. Delete descriptive modifiers. Do not substitute a genre, mood or synonym. Return one bracketed lowercase noun. Caption: '
        cases = [('explicit-head-music', TEXT_MODEL, explicit+'[SERENE MUSIC]', .2, None, None),
                 ('heldout-head-footsteps', TEXT_MODEL, explicit+'[RAPID FOOTSTEPS]', .2, None, None)]
    results = []; calls = 0
    for name, model, prompt, temperature, rate, kind in cases:
        record = {'name': name, 'requested_model': model, 'prompt': prompt, 'temperature': temperature, 'thinking': False, 'max_tokens': 512, 'timeout_s': 180, 'max_attempts': 1}
        content = prompt
        if rate:
            path = cache/f'{kind}-{rate}.wav'; record['audio'] = audio_case(path, rate, kind)
            content = [{'type':'audio_url','audio_url':{'url':'data:audio/wav;base64,'+base64.b64encode(path.read_bytes()).decode()}},{'type':'text','text':prompt}]
        key = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        saved = cache/(key+'.json'); started = time.monotonic()
        if saved.exists():
            record = json.loads(saved.read_text()); record['cache_hit'] = True
        else:
            calls += 1
            try:
                response = request(content, model=model, thinking=False, max_tokens=512, temperature=temperature, max_attempts=1)
                record.update(response=response, operational_status='response-received')
            except (RuntimeError, ValueError, OSError) as error:
                record.update(operational_status='inconclusive-error', error=str(error))
            record['seconds'] = round(time.monotonic()-started, 3)
            saved.write_text(json.dumps(record, indent=2)+'\n')
        results.append(record)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps({'version':'factor-controls-v1','actual_calls_this_run':calls,'call_ceiling':len(cases), 'phase':args.phase,'scope':'Synthetic, nonparticipant material only. Single-attempt requests through shared 2.05-second pacing. No installation or quality-gate changes. Ground truth metadata never enters the audio prompts. Historical speech/decode controls reused separately.','tests':results},indent=2)+'\n')
        choices = record.get('response',{}).get('choices') or []
        answer = (choices[0].get('message',{}).get('content') or '') if choices else record.get('error','no choices')
        print(name, record['operational_status'], repr(answer[:450]), flush=True)

if __name__ == '__main__':
    main()
