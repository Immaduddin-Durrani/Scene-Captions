// Rebuild the player track from saved local generation and its explicit source-text edits.
// No inference or network request occurs here or during playback.
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { videoSchema } from "../src/lib/captions.ts";
import { parseSrt } from "../src/lib/srt.ts";
const hash = (data: Buffer | string) => createHash("sha256").update(data).digest("hex");
const path = "data/authoring/big-buck-bunny-generated.json";
const bytes = readFileSync(path);
const record = JSON.parse(bytes.toString("utf8"));
const provenance = JSON.parse(readFileSync("data/sources/big-buck-captions/source.json", "utf8"));
const sourceBytes = readFileSync("data/sources/big-buck-captions/big-buck-bunny.srt");
if (hash(sourceBytes) !== provenance.file_sha256) throw new Error("Reference SRT changed.");
const source = parseSrt(sourceBytes.toString("utf8"));
const previous = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
type Label = { reference: string; short: string; balanced: string; detailed: string; report: string; index: number };
const labels = new Map<string, Label>();
for (const item of record.labels as Label[]) {
  if (labels.has(item.reference)) throw new Error("Duplicate generated label");
  const raw = JSON.parse(readFileSync(item.report, "utf8")).items[item.index];
  if (raw.reference !== item.reference || raw.finish_reason !== "stop") throw new Error("Incomplete or mismatched model evidence");
  for (const text of [item.short, item.balanced, item.detailed]) if (!/^\[[^\[\]\r\n]+\]$/.test(text) || text.length > 90) throw new Error("Invalid generated/edited sound wording");
  labels.set(item.reference, item);
}
if (labels.size !== new Set(source.flatMap(cue => cue.text.split("\n"))).size || source.length !== previous.cues.length) throw new Error("Reference coverage differs.");
const style = (text: string, expression: number) => expression === 1 ? text : `[${text.slice(1, -1).replace(/[.!]+$/, "")}${expression === 2 ? "." : "!"}]`;
const baseline = (item: Label) => item.balanced.toLowerCase() !== item.reference.toLowerCase() ? item.balanced : item.detailed;
const cues = source.map((cue, index) => {
  const old = previous.cues[index];
  if (old.start_s !== cue.start_s || old.end_s !== cue.end_s || (old.reference_text || old.original_text) !== cue.text) throw new Error("Existing timeline/reference differs.");
  const items = cue.text.split("\n").map(label => { const item = labels.get(label); if (!item) throw new Error("Missing generated label"); return item; });
  const text = items.map(baseline).join("\n");
  if (text.toLowerCase() === cue.text.toLowerCase()) throw new Error("Fixed caption still copies reference text");
  const grid = Object.fromEntries([1, 2, 3].flatMap(d => [1, 2, 3].map(e => [`${d}-${e}`, items.map(item => style([item.short, item.balanced, item.detailed][d - 1], e)).join("\n")])));
  return { ...old, original_text: text, reference_text: cue.text, grid, representations: { plain: items.map(item => item.short).join("\n") }, scene_context: `Locally generated wording, edited against reference cue ${cue.id}. Sound events and timestamps come from the credited reference, not automatic audio recognition. Expression styles change punctuation only; density adaptation counts nearby cues. Full listening review is pending.` };
});
const track = videoSchema.parse({ ...previous, attribution: "SceneCaptions: locally generated and editorially corrected wording, based on Demuxed / big-buck-captions contributors (CC BY 3.0).", annotation_status: "draft", generated_with: { ...previous.generated_with, kind: "source-assisted", model: record.model, model_revision: record.revision, generation_record_sha256: hash(bytes), prompt_version: record.prompt_version, expression_method: "punctuation-only", expressiveness: "source-anchored", quality_gate: "unverified", method: record.method }, cues });
const json = JSON.stringify(track, null, 2) + "\n";
writeFileSync("data/captions/big-buck-bunny.json", json);
writeFileSync("public/research/demo-captions.json", json);
const stamp = (seconds: number) => { const ms = Math.round(seconds * 1000); return `${String(Math.floor(ms / 3600000)).padStart(2, "0")}:${String(Math.floor(ms / 60000) % 60).padStart(2, "0")}:${String(Math.floor(ms / 1000) % 60).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`; };
const srt = cues.map((cue, index) => `${index + 1}\n${stamp(cue.start_s)} --> ${stamp(cue.end_s)}\n${cue.original_text}\n`).join("\n");
writeFileSync("public/research/big-buck-bunny.srt", srt);
writeFileSync("public/research/big-buck-bunny.vtt", "WEBVTT\n\n" + srt.replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, "$1.$2"));
const rates = cues.flatMap(cue => Object.entries({ baseline: cue.original_text, ...cue.grid }).filter(([,text]) => text.length / (cue.end_s - cue.start_s) > 20).map(([variant,text]) => ({cue_id: cue.cue_id,variant,characters_per_second:text.length/(cue.end_s-cue.start_s)})));
writeFileSync("docs/verification/generated-captions-2026-10-26/installation.json", JSON.stringify({ method: record.method, model: record.model, revision: record.revision, generation_record_sha256: hash(bytes), track_sha256: hash(json), srt_sha256: hash(srt), cue_count: cues.length, unique_labels: labels.size, baseline_differs_from_reference_count: cues.filter(cue => cue.original_text.toLowerCase() !== cue.reference_text.toLowerCase()).length, original_timestamps_preserved: true, simultaneous_sound_lines_preserved: true, expression_styles: "Deterministic punctuation only; not nine independently generated semantic variants.", human_listening_review: false, audio_recognition: false, reading_rate_heuristic: "20 characters/second; flags, not a validated DHH threshold or proof of improvement.", reading_flags: rates }, null, 2) + "\n");
console.log(`Installed ${cues.length} AI-assisted draft captions from ${labels.size} locally generated/edited labels. Reference text is separate; timing unchanged.`);
