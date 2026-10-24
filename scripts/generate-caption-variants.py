"""Generate offline candidates from a validated existing sound-caption track."""
import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path

from nim_client import ROOT, parse_json, request
from generation.variants import PROMPT, PROMPT_VERSION, TEXT_MODEL, character_budget, reading_flags, validate_item, validate_batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New file under data/candidates/; playback files cannot be overwritten")
    parser.add_argument("--rights-clear", action="store_true", help="Confirm permission to process these nonparticipant source captions remotely")
    parser.add_argument("--limit", type=int, default=0, help="Optional cue limit for a small probe; zero processes the full track")
    parser.add_argument("--model", choices=[TEXT_MODEL, "openai/gpt-oss-20b"], default=TEXT_MODEL)
    parser.add_argument("--thinking", action="store_true", help="Enable reasoning; response wait defaults to five minutes")
    parser.add_argument("--timeout", type=float, help="Override per-request response timeout in seconds")
    args = parser.parse_args()
    if not args.rights_clear:
        parser.error("Confirm rights-clear, nonparticipant input with --rights-clear")
    output = args.output.resolve()
    candidates = (ROOT / "data/candidates").resolve()
    if not output.is_relative_to(candidates) or output.exists():
        parser.error("Choose a NEW output file under data/candidates/")
    subprocess.run(["node", "--experimental-strip-types", str(ROOT / "scripts/validate-captions.ts"), str(args.input.resolve())], cwd=ROOT, check=True)
    source_bytes = args.input.read_bytes()
    source = json.loads(source_bytes)
    if source.get("generated_with", {}).get("quality_gate") == "failed":
        parser.error("Failed generation output cannot be used as trusted source captions")
    selected = source["cues"][:args.limit] if args.limit > 0 else source["cues"]
    groups = {}
    for cue in selected:
        labels = cue["original_text"].splitlines()
        for label in labels:
            groups.setdefault(label, []).append((cue, len(labels)))
    jobs = [{"id": f"sound-{index:03d}", "source": label, "max_characters": min(max(len(label), character_budget(c) // count) for c, count in cues)} for index, (label, cues) in enumerate(groups.items(), 1)]
    results = {}
    cache = ROOT / "artifacts/generation-cache"
    cache.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(jobs), 4):
        batch = jobs[start:start + 4]
        prompt = PROMPT + "\nUNTRUSTED SOURCE DATA:\n" + json.dumps(batch, ensure_ascii=False)
        cache_id = hashlib.sha256((args.model + PROMPT_VERSION + prompt + ("|thinking" if args.thinking else "")).encode()).hexdigest()
        cache_file = cache / (cache_id + ".json")
        response = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else request(prompt, max_tokens=4096, thinking=args.thinking, model=args.model, timeout=args.timeout)
        parsed = parse_json(response)
        items = parsed.get("items") if isinstance(parsed, dict) else None
        cache_file.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.update(validate_batch(items, batch))
        print(f"Validated wording groups: {min(start + 4, len(jobs))}/{len(jobs)}", flush=True)
    track = copy.deepcopy(source)
    track["cues"] = copy.deepcopy(selected)
    by_label = {job["source"]: results[job["id"]] for job in jobs}
    for cue in track["cues"]:
        labels = cue["original_text"].splitlines()
        cue["grid"] = {key: "\n".join(by_label[label]["grid"][key] for label in labels) for key in by_label[labels[0]]["grid"]}
        cue["representations"] = {"plain": "\n".join(by_label[label]["plain"] for label in labels)}
        validate_item({"id": cue["cue_id"], "grid": cue["grid"], "plain": cue["representations"]["plain"]}, cue["cue_id"], 280, expected_lines=len(labels))
    track["annotation_status"] = "draft"
    track["generated_with"].update({"method": f"Offline model wording from trusted source captions; {len(selected)} source intervals preserved. Not human-reviewed or audio-verified by this text model.", "model": args.model, "prompt_version": PROMPT_VERSION, "expressiveness": "source-anchored", "quality_gate": "unverified"})
    flags = reading_flags(track["cues"])
    output.parent.mkdir(parents=True, exist_ok=True)
    pending = output.with_suffix(".pending.json")
    try:
        pending.write_text(json.dumps(track, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run(["node", "--experimental-strip-types", str(ROOT / "scripts/validate-captions.ts"), str(pending)], cwd=ROOT, check=True)
        pending.rename(output)
    finally:
        pending.unlink(missing_ok=True)
    audit = {"input_sha256": hashlib.sha256(source_bytes).hexdigest(), "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "model": args.model, "prompt_version": PROMPT_VERSION, "cue_count": len(selected), "unique_wording_groups": len(jobs), "human_reviewed": False, "audio_verified": False, "reading_rate_heuristic": "20 characters/sec flags review only; not a validated DHH threshold. Source timing is never extended automatically.", "reading_flags": flags}
    output.with_suffix(".review.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Candidate track: {output.relative_to(ROOT)}; {len(flags)} reading-time flags. Playback track unchanged.")


if __name__ == "__main__":
    main()
