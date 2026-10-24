"""Check source cue clips against independent audio descriptions, with calibration first."""
import argparse
import base64
import hashlib
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

from nim_client import MODEL, ROOT, parse_json, request

VERSION = "blind-audio-check-v1"
PROMPT = """Listen only to this audio. Do not guess visual events. Return only JSON {"sounds":[{"description":"short factual sound label","start_s":0,"end_s":1}]}. Include only identifiable audible NON-SPEECH sounds. If silent, return an empty sounds array. Do not infer music, people, objects, emotions or causes without audible evidence. No more than eight sounds; timestamps are relative to this clip and must stay inside its duration."""


def observe(path, duration, cache):
    data = path.read_bytes()
    digest = hashlib.sha256((MODEL + VERSION + str(duration)).encode() + data).hexdigest()
    record = cache / (digest + ".json")
    if record.exists():
        response = json.loads(record.read_text(encoding="utf-8"))
    else:
        response = request([{"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64," + base64.b64encode(data).decode()}}, {"type": "text", "text": PROMPT + f"\nClip duration: {duration:.3f} seconds."}], max_tokens=1024, thinking=False)
    result = parse_json(response)
    sounds = result.get("sounds") if isinstance(result, dict) else None
    if not isinstance(sounds, list) or len(sounds) > 8:
        raise ValueError("Audio response must contain a bounded sounds array")
    for sound in sounds:
        start, end = sound.get("start_s"), sound.get("end_s")
        if not isinstance(start, (int, float)) or isinstance(start, bool) or not isinstance(end, (int, float)) or isinstance(end, bool) or not math.isfinite(start) or not math.isfinite(end) or not 0 <= start < end <= duration + .01:
            raise ValueError("Invalid audio observation interval")
        if not isinstance(sound.get("description"), str) or not 0 < len(sound["description"]) <= 280:
            raise ValueError("Invalid audio observation label")
    record.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    return sounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--rights-clear", action="store_true")
    parser.add_argument("--limit", type=int, default=3, help="Maximum source cues in this bounded audio check")
    args = parser.parse_args()
    if not args.rights_clear or not 1 <= args.limit <= 10:
        parser.error("Confirm rights-clear nonparticipant media and choose 1–10 cues")
    report_path = args.report.resolve()
    if not report_path.is_relative_to((ROOT / "docs/verification").resolve()) or report_path.exists():
        parser.error("Choose a new report path under docs/verification/")
    source_bytes = args.captions.read_bytes()
    source = json.loads(source_bytes)
    video_hash = hashlib.sha256(args.video.read_bytes()).hexdigest()
    if source.get("generated_with", {}).get("source_sha256") != video_hash:
        parser.error("Video hash must match this source track's exact edit")
    cache = ROOT / "artifacts/audio-checks" / video_hash[:16]
    cache.mkdir(parents=True, exist_ok=True)
    clips = []
    for cue in source["cues"][:args.limit]:
        # Filename derives from trusted hashes, not cue text or arbitrary ZIP paths.
        identity = hashlib.sha256(f"{cue['cue_id']}:{cue['start_s']}:{cue['end_s']}".encode()).hexdigest()[:16]
        clip = cache / (identity + ".wav")
        duration = cue["end_s"] - cue["start_s"]
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(cue["start_s"]), "-i", str(args.video.resolve()), "-t", str(duration), "-vn", "-ac", "1", "-ar", "16000", "-y", str(clip)], check=True)
        clips.append({"cue_id": cue["cue_id"], "start_s": cue["start_s"], "end_s": cue["end_s"], "source_text": cue["original_text"], "local_review_clip": str(clip.relative_to(ROOT)), "duration_s": duration})
    silence = cache / "calibration-silence.wav"
    tone = cache / "calibration-tone.wav"
    for path, audible in [(silence, False), (tone, True)]:
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000)
            wav.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 16000)) if audible else 0) for i in range(48000)))
    report = {"version": VERSION, "model": MODEL, "source_sha256": hashlib.sha256(source_bytes).hexdigest(), "video_sha256": video_hash, "status": "inconclusive", "human_reviewed": False, "notice": "Audio observations are independent of source caption text, but model agreement is not ground truth. No candidate is installed and no existing failed gate is cleared.", "clips": clips}
    try:
        silent_result = observe(silence, 3, cache)
        report["silence_observation"] = silent_result
        if silent_result:
            report["status"] = "failed-calibration"
            report["reason"] = "Model described sounds on digital silence. Semantic matching is blocked; use the extracted clips for human review."
        else:
            tone_result = observe(tone, 3, cache)
            report["tone_observation"] = tone_result
            if not tone_result or not any(any(word in item["description"].lower() for word in ["tone", "beep", "hum", "sine"]) for item in tone_result):
                report["status"] = "failed-calibration"
                report["reason"] = "Known tone was not identified; semantic matching is blocked."
            else:
                for clip in clips:
                    clip["blind_model_observation"] = observe(ROOT / clip["local_review_clip"], clip["duration_s"], cache)
                    clip["review_status"] = "needs-human-comparison"
                report["status"] = "observations-ready-for-review"
                report["reason"] = "Calibration passed this bounded probe only. Compare each independent sound description and interval with its source caption by listening."
    except (ValueError, KeyError, RuntimeError, OSError) as error:
        report["reason"] = "Audio check could not produce usable evidence: " + str(error)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audio check: {report['status']}; {len(clips)} local review clips; report: {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
