"""Caption-free audio-onset candidates and timestamp-matched movie frames. No inference."""
import array
import hashlib
import json
import math
import re
import statistics
import subprocess
import wave
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / 'artifacts/nim-frame-pipeline-2026-10-27'
MODEL = 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'
PROMPT = ('Listen to the attached five-second recording. Describe the audible non-speech '
    'event near local time 2 seconds, plus essential background sound if audible. '
    'Some requests include images near that moment. Images may help identify a source '
    'only when supported by the sound; visible actions alone never establish audibility. '
    'Do not infer sound from story knowledge or unrelated scenery. If no sound is '
    'audible, reply NO_AUDIBLE_EVENT. If source identity is unclear, use a broad '
    'description. Give one short sound-caption draft, followed by one sentence '
    'explaining the audio/image evidence. Do not invent acoustic attributes or timestamps.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000)
        return array.array('h', w.readframes(w.getnframes()))


def save(path, data):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(data.tobytes())
    assert read(path) == data


def candidates(pcm):
    hop = 1280  # 80-ms analysis, not a semantic sound detector.
    values = []
    for start in range(0, len(pcm) - hop + 1, hop):
        rms = math.sqrt(sum(x*x for x in pcm[start:start+hop]) / hop)
        values.append(max(-100, 20 * math.log10(max(rms, 1e-9) / 32768)))
    ranked = []
    for i in range(6, len(values)):
        time = (i + .5) * hop / 16000
        rise = values[i] - statistics.median(values[i-5:i])
        if 8 <= time <= 112 and values[i] >= -38 and rise >= 6:
            ranked.append({'time_s': round(time, 4), 'rise_db': rise, 'rms_dbfs': values[i]})
    chosen = []
    for item in sorted(ranked, key=lambda x: (-x['rise_db'], x['time_s'])):
        if all(abs(item['time_s'] - prev['time_s']) >= 15 for prev in chosen):
            chosen.append(item)
            if len(chosen) == 2:
                break
    return sorted(chosen, key=lambda x: x['time_s'])


def job(case, audio, frames):
    content = [{'type': 'local_wav', 'path': str(audio.relative_to(ROOT))},
               {'type': 'text', 'text': PROMPT}]
    for frame in frames:
        content.extend([{'type': 'text', 'text': f"Image at LOCAL {frame['local_time_s']:.4f} seconds."},
                        {'type': 'local_jpeg', 'path': frame['file']}])
    return {'case': case, 'hypothesis': 'Same audio/prompt/settings with zero, one or three aligned images; source captions withheld.',
        'payload': {'model': MODEL, 'messages': [{'role': 'user', 'content': content}],
            'temperature': .2, 'top_k': 1, 'max_tokens': 512, 'stream': False,
            'chat_template_kwargs': {'enable_thinking': False}}}


def main():
    assert not (HERE / 'protocol.json').exists(), 'Preserve frozen inputs'
    ART.mkdir(parents=True, exist_ok=True)
    film = ROOT / 'public/media/big-buck-bunny.mp4'
    old = json.loads((ROOT / 'docs/verification/nim-counterfactuals-2026-10-26/protocol.json').read_text())
    assert sha(film) == old['original_film_sha256']
    scan = ART / 'scan.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(film), '-t', '120', '-map', '0:a:0',
        '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', '-map_metadata', '-1', str(scan)], check=True)
    pcm = read(scan); assert len(pcm) == 1920000
    found = candidates(pcm)
    assert len(found) == 2, 'Pilot needs two candidates; do not alter thresholds after inference'
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=avg_frame_rate,r_frame_rate', '-of', 'json', str(film)]))['streams'][0]
    fps = float(Fraction(info['avg_frame_rate']))
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-read_intervals', '0%+121', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(film)]))
    source_times = [float(frame['best_effort_timestamp_time']) for frame in probe['frames']]
    assert source_times[0] == 0 and all(b > a for a, b in zip(source_times, source_times[1:]))
    frame_index = lambda time: min(range(len(source_times)), key=lambda n: abs(source_times[n] - time))
    indices = sorted({frame_index(event['time_s'] + offset) for event in found for offset in [-.5, 0, .5]})
    expression = '+'.join(f'eq(n,{i})' for i in indices)
    process = subprocess.run(['ffmpeg', '-y', '-hide_banner', '-i', str(film), '-map', '0:v:0',
        '-vf', f"select='{expression}',scale=512:-2,showinfo", '-frames:v', str(len(indices)),
        '-fps_mode', 'passthrough', '-q:v', '4', str(ART / 'frame-%02d.jpg')],
        capture_output=True, text=True, check=True)
    (ART / 'frame-extraction.txt').write_text(process.stderr)
    times = [float(value) for value in re.findall(r'\bn:\s*\d+\s+pts:.*?pts_time:([0-9.e+-]+)', process.stderr)]
    assert len(times) == len(indices), (times, indices)
    frame_map = {}
    for number, (index, pts) in enumerate(zip(indices, times), 1):
        assert abs(pts - source_times[index]) < .002, 'Decoded frame PTS disagrees with probed source timestamp'
        image = ART / f'frame-{number:02d}.jpg'
        assert image.read_bytes().startswith(b'\xff\xd8\xff')
        frame_map[index] = {'file': str(image.relative_to(ROOT)), 'sha256': sha(image),
            'source_frame_index': index, 'actual_pts_s': pts}
    jobs, fixtures = [], {}
    for number, event in enumerate(found, 1):
        case = f'f{number:02d}'; start = round((event['time_s'] - 2) * 16000)
        data = pcm[start:start + 80000]; assert len(data) == 80000 and any(data)
        audio = ART / (case + '.wav'); save(audio, data)
        clip_start = start / 16000
        frames = []
        for offset in [-.5, 0, .5]:
            frame = dict(frame_map[frame_index(event['time_s'] + offset)])
            frame['requested_time_s'] = event['time_s'] + offset
            frame['local_time_s'] = frame['actual_pts_s'] - clip_start
            assert abs(frame['actual_pts_s'] - frame['requested_time_s']) <= .05
            frames.append(frame)
        fixtures[case] = {**event, 'clip_start_s': clip_start, 'clip_duration_s': 5,
            'audio_file': str(audio.relative_to(ROOT)), 'audio_sha256': sha(audio), 'frames': frames}
        jobs.extend([job(case+'-audio', audio, []), job(case+'-single', audio, [frames[1]]),
                     job(case+'-triplet', audio, frames)])
    silent = ART / 'zero.wav'; save(silent, array.array('h', [0]) * 80000)
    for case, fixture in fixtures.items():
        jobs.append(job(case+'-mute', silent, fixture['frames']))
    manifest = HERE / 'inputs/manifest.json'; manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    (HERE / 'protocol.json').write_text(json.dumps({'created_before_inference': True,
        'film_sha256': sha(film), 'scan_audio_sha256': sha(scan), 'scan_interval_s': [0, 120],
        'candidate_method': '80ms RMS rise over median prior five windows; >=6dB rise, >=-38dBFS; ignore first8/last8 scan seconds; top2 separated>=15s',
        'candidate_semantics': 'Activity candidates only, not recognized events or reliable boundaries.',
        'source_average_fps': fps, 'source_reported_rates': info,
        'frame_selection': 'Nearest actual decoded source PTS; never assume frame index / average FPS.',
        'fixtures': fixtures, 'manifest_sha256': sha(manifest),
        'zero_wav_sha256': sha(silent), 'zero_sample_count': 80000,
        'caption_reference_or_plot_input': False, 'asr_calls': 0,
        'asr_role': 'Existing separate speech branch; this pilot targets sound-effect candidates, not ASR event detection.',
        'criteria': {'mute': 'NO_AUDIBLE_EVENT; any asserted sound is a false positive.',
            'alignment': 'Actual decoded image PTS within one source frame of requested time.',
            'pairing': 'Same exact WAV, generation settings and main instruction across context conditions.',
            'quality': 'Manual visual/reference comparison after generation only; no independent listening ground truth.'},
        'budget': {'initial_requests': 8, 'maximum_requests': 8, 'automatic_retries': 0,
            'stop_after_consecutive_capacity_errors': 3, 'timeout_each_s': 180},
        'limits': ['Music/ambience can trigger RMS candidates; low-energy and overlapping events may be missed.',
            'A frame can suggest source identity but cannot establish an audible event.',
            'Frame conditions include timestamp annotations in addition to images.',
            'No full-film generation, human listening approval or automatic playback installation.']}, indent=2) + '\n')
    print(json.dumps({'candidates': found, 'source_fps': fps, 'frame_pts': times, 'prepared_requests': len(jobs)}, indent=2))


if __name__ == '__main__':
    main()
