"""Prepare five caption-free pipeline fixtures. No inference."""
import array
import hashlib
import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ART = ROOT / 'artifacts/nim-pipeline-2026-10-27'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def samples(path):
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000)
        return array.array('h', w.readframes(w.getnframes()))


def save(path, data):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(data.tobytes())
    assert samples(path) == data


def main():
    assert not (OUT / 'protocol.json').exists(), 'Preserve frozen protocol'
    ART.mkdir(parents=True, exist_ok=True)
    recent = ROOT / 'artifacts/nim-recognition-2026-10-27'
    speech_info = json.loads((ROOT / 'docs/verification/nim-recognition-2026-10-27/speech-protocol.json').read_text())
    assert sha(recent / 'q07.wav') == speech_info['wav_sha256']
    speech = samples(recent / 'q07.wav')
    zero = array.array('h', [0]) * 160000
    assert not any(samples(recent / 'q06.wav'))
    repeated = samples(recent / 'q09.wav')
    original = samples(recent / 'q01.wav')
    indices = [i for i, value in enumerate(original) if value]
    burst = original[indices[0]:indices[-1] + 1]
    mixed = zero[:]
    mixed[8000:8000 + len(speech)] = speech
    for onset in [4, 6, 8]:
        start = onset * 16000
        assert not any(mixed[start:start + len(burst)])
        mixed[start:start + len(burst)] = burst
    data = {'p01': speech, 'p02': zero, 'p03': repeated, 'p04': mixed}
    for name, pcm in data.items():
        save(ART / (name + '.wav'), pcm)
    film = ROOT / 'public/media/big-buck-bunny.mp4'
    old = json.loads((ROOT / 'docs/verification/nim-counterfactuals-2026-10-26/protocol.json').read_text())
    assert sha(film) == old['original_film_sha256']
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(film), '-t', '10', '-map', '0:a:0',
        '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', '-map_metadata', '-1',
        str(ART / 'p05.wav')], check=True)
    assert len(samples(ART / 'p05.wav')) == 160000
    jobs = [{'case': name, 'file': str((ART / (name + '.wav')).relative_to(ROOT)),
             'sha256': sha(ART / (name + '.wav')), 'duration_s': len(samples(ART / (name + '.wav'))) / 16000}
            for name in ['p01', 'p02', 'p03', 'p04', 'p05']]
    (OUT / 'inputs/asr.json').write_text(json.dumps(jobs, indent=2) + '\n')
    protocol = {'created_before_inference': True, 'date': '2026-10-27',
        'asr': {'model': 'openai/whisper-large-v3', 'endpoint': 'grpc.nvcf.nvidia.com:443',
            'function_id': 'b702f636-f60c-4a3d-a6f4-f3568c13bd7d', 'language_code': 'en',
            'word_timestamps_requested': True, 'single_attempt_timeout_s': 90},
        'manifest_sha256': sha(OUT / 'inputs/asr.json'),
        'evaluation_only': {'p01': {'speech': speech_info['evaluation_only_expected_text'], 'non_speech': []},
            'p02': {'speech': '', 'non_speech': [], 'digital_zero': True},
            'p03': {'speech': '', 'non_speech': 'dog vocalizations, eight repeated exact bursts'},
            'p04': {'speech': speech_info['evaluation_only_expected_text'], 'speech_offset_s': .5,
                    'non_speech': 'same dog source, three bursts', 'onsets_s': [4, 6, 8]},
            'p05': {'source': 'BBB first ten seconds; fixed window independent of caption timing',
                    'film_sha256': sha(film), 'human_audio_ground_truth': 'not annotated'}},
        'criteria': {'asr_words': 'Correct clean/mixed phrase, no invented dialogue on absent-speech controls.',
            'asr_timing': 'Finite ordered word intervals within clip; zero/missing offsets are not timing success.',
            'sound_stage': 'Audio-grounded events separate from dialogue; strict dog recognition on controlled bursts; no effects on digital silence.',
            'rendering': 'One ledger, stable event IDs and speech, three detail levels, no invented events/attributes/times.',
            'no_speech_vs_no_sound': 'Empty ASR transcript never establishes acoustic silence.'},
        'budget': {'max_total_requests': 18, 'initial_asr_cells': 5, 'initial_sound_cells': 5,
            'initial_renderer_requests': 1, 'max_one_explicit_retry_per_inconclusive_cell': True,
            'stop': 'Stop at auth/access failure for the affected stage or three consecutive capacity errors; no full-film run.'},
        'stages': ['Whisper speech and word offsets', 'Omni non-speech observations with own ASR as uncertain context',
                   'Evidence-labelled ledger and three-level draft rendering', 'Validate and retain failed candidates separately'],
        'raw_zero_asr': 'Diagnostic request deliberately tests all-zero input. A production preprocessor can bypass exact zeros; raw and wrapped behavior must be reported separately.',
        'limits': ['Known synthetic/ESC-10 controls, not a generalization benchmark.',
            'BBB window has no independent listening annotation; do not claim movie accuracy.',
            'ASR output is generated from media, not fetched subtitle input; it may itself hallucinate.',
            'Renderer cannot correct ungrounded observations. Unresolved sound timing cannot become invented subtitles.',
            'All artifacts remain drafts outside playback; existing failed sound gate stays failed.']}
    (OUT / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    print('Five fixtures frozen: speech, silence, effects, constructed mixture and fixed BBB window. No inference.')


if __name__ == '__main__':
    main()
