"""Six bounded synthetic controls. No film or participant data; never installs captions."""
import argparse
import base64
import hashlib
import json
import math
import struct
import sys
import time
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nim_client import ROOT, MODEL, api_key, rate_limit, TEXT_TIMEOUT, REASONING_TIMEOUT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--timeout", type=float, help="Optional response timeout in seconds; otherwise 180 for text or 300 for reasoning")
    args = parser.parse_args()
    report = args.report.resolve()
    if not report.is_relative_to((ROOT / "docs/verification").resolve()) or report.exists():
        parser.error("Choose a new report under docs/verification/")
    directory = ROOT / "artifacts/diagnostics"
    directory.mkdir(parents=True, exist_ok=True)
    audio = {}
    for name, audible in [("silence", False), ("tone", True)]:
        path = directory / (name + ".wav")
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000)
            samples = [int(8000 * math.sin(2 * math.pi * 440 * i / 16000)) if audible else 0 for i in range(48000)]
            wav.writeframes(b"".join(struct.pack("<h", value) for value in samples))
        data = path.read_bytes()
        audio[name] = {"url": "data:audio/wav;base64," + base64.b64encode(data).decode(), "sha256": hashlib.sha256(data).hexdigest(), "pcm_all_zero": not any(samples), "samples": len(samples)}
    caption_prompt = "Return only the broad sound type in [SERENE MUSIC]. Omit the mood word. Use one bracketed label."
    audio_prompt = "Classify this recording with one word: SILENCE, TONE, MUSIC, SPEECH, OTHER, or UNAVAILABLE. Base the answer only on the audio."
    tests = [
        ("text-arithmetic", "nvidia/nemotron-3.5-lightning-30b-a3b", "What is 17 + 8? Return only the number.", False, None),
        ("text-caption-no-reasoning", "nvidia/nemotron-3.5-lightning-30b-a3b", caption_prompt, False, None),
        ("text-caption-reasoning", "nvidia/nemotron-3.5-lightning-30b-a3b", caption_prompt, True, None),
        ("audio-silence-no-reasoning", MODEL, audio_prompt, False, "silence"),
        ("audio-tone-no-reasoning", MODEL, audio_prompt, False, "tone"),
        ("audio-silence-reasoning", MODEL, audio_prompt, True, "silence"),
    ]
    results = []
    key = api_key()
    for name, model, prompt, thinking, audio_name in tests:
        content = [{"type": "audio_url", "audio_url": {"url": audio[audio_name]["url"]}}, {"type": "text", "text": prompt}] if audio_name else prompt
        payload = {"model": model, "messages": [{"role": "user", "content": content}], "max_tokens": 2048, "temperature": 0.2, "stream": False, "chat_template_kwargs": {"enable_thinking": thinking}}
        if thinking:
            payload["reasoning_budget"] = 512
        started = time.monotonic()
        record = {"name": name, "requested_model": model, "reasoning": thinking, "max_tokens": 2048}
        if audio_name:
            record["audio"] = {k: v for k, v in audio[audio_name].items() if k != "url"}
        try:
            req = urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json"})
            rate_limit()
            record['timeout_s'] = args.timeout if args.timeout is not None else REASONING_TIMEOUT if thinking else TEXT_TIMEOUT
            with urllib.request.urlopen(req, timeout=record['timeout_s']) as response:
                data = json.load(response)
                record["http_status"] = response.status
            choices = data.get("choices") or []
            record.update({"response_model": data.get("model"), "choices": choices, "usage": data.get("usage"), "error": data.get("error")})
        except Exception as error:
            record["transport_error"] = (type(error).__name__ + ": " + str(error)).replace(key, "[REDACTED]")
        record["seconds"] = round(time.monotonic() - started, 2)
        results.append(record)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps({"scope": "Synthetic controls only; audio_url with WAV data URI. Documentation establishes audio_url in self-hosted examples, not conclusive hosted transport support.", "tests": results}, indent=2) + "\n", encoding="utf-8")
        content = ((record.get("choices") or [{}])[0].get("message") or {}).get("content")
        print(f"{name}: {content!r}; finish={((record.get('choices') or [{}])[0]).get('finish_reason')}; error={record.get('transport_error') or record.get('error')}", flush=True)
        time.sleep(max(0, 2.05 - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
