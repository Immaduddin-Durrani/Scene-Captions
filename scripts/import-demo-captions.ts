import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { parseSrt } from "../src/lib/srt.ts";
import { videoSchema } from "../src/lib/captions.ts";

// Offline, deterministic import of a pinned, CC BY 3.0 caption source.
const root = "data/sources/big-buck-captions/";
const provenance = JSON.parse(readFileSync(root + "source.json", "utf8"));
const sourceBytes = readFileSync(root + "big-buck-bunny.srt");
const sha256 = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
if (sha256(sourceBytes) !== provenance.file_sha256) throw new Error("Caption source hash changed; inspect before importing.");
const source = parseSrt(sourceBytes.toString("utf8"));
const videoHash = sha256(readFileSync("public/media/big-buck-bunny.mp4"));
if (videoHash !== "738e2f999860553d056dd79c952f58f63cbb73892a57c72342ce9e5330d9d2d7") throw new Error("Different movie edit. Check caption alignment before importing.");
const duration = Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", "public/media/big-buck-bunny.mp4"], { encoding: "utf8" }));
type Wording = { grid: Record<string, string>; plain: string; onomatopoeic?: string };
const lexicon: Record<string, Wording> = JSON.parse(readFileSync("data/authoring/big-buck-bunny-lexicon.json", "utf8"));
const keys = [1, 2, 3].flatMap(d => [1, 2, 3].map(e => `${d}-${e}`));
const cues = source.map((cue) => {
  const labels = cue.text.split("\n").map(line => {
    const match = line.match(/^\[([^\]]+)\]$/);
    if (!match || !lexicon[match[1]]) throw new Error(`Unrecognized source text in cue ${cue.id}; do not invent a fallback.`);
    return match[1];
  });
  const neighbors = source.filter(other => other.start_s <= cue.start_s + 5 && other.end_s > cue.start_s - 5).length;
  const load = neighbors >= 4 ? "dense" : neighbors <= 1 ? "quiet" : "balanced";
  const spelling = labels.every(label => lexicon[label].onomatopoeic);
  return {
    cue_id: `bbb-sdh-${cue.id.padStart(3, "0")}`, start_s: cue.start_s, end_s: cue.end_s,
    original_text: cue.text, sound_key: labels.map(label => label.toLowerCase().replace(/[^a-z0-9]+/g, "-")).join("--"),
    scene_context: `Demuxed source cue ${cue.id}: ${cue.text.replace(/\n/g, " ")}. Original source timing preserved. Adaptation uses ${neighbors} cue intervals intersecting the ±5-second neighborhood, a caption-density proxy, not measured visual scene complexity.`,
    scene_load: load, scene_load_basis: "cue-density",
    grid: Object.fromEntries(keys.map(key => [key, labels.map(label => lexicon[label].grid[key]).join("\n")])),
    representations: { plain: labels.map(label => lexicon[label].plain).join("\n"), ...(spelling ? { onomatopoeic: labels.map(label => lexicon[label].onomatopoeic).join("\n") } : {}) },
  };
});
const result = videoSchema.parse({
  schema_version: 1, video_id: "big-buck-bunny", title: "Big Buck Bunny",
  source_url: "https://peach.blender.org/about/", license: "CC BY 3.0",
  attribution: "Film © 2008 Blender Foundation / peach.blender.org. Sound captions: Demuxed / big-buck-captions contributors, CC BY 3.0. Wording variants and cue-density adaptation added by SceneCaptions.",
  duration_seconds: duration, annotation_status: "draft",
  generated_with: {
    method: "Imported licensed Demuxed sound captions with unchanged timings; locally authored source-anchored wording variants. Visual sync anchors spot-checked; not a complete listening or participant review.",
    prompt_version: "demuxed-anchored-v2-concise-effects", kind: "sourced", source_sha256: videoHash,
    expressiveness: "source-anchored", scene_load_method: "cue-density", quality_gate: "unverified",
    caption_source: { url: provenance.source_url, revision: provenance.commit, license: provenance.license, author: provenance.author, sha256: provenance.file_sha256 },
  }, cues,
});
const json = JSON.stringify(result, null, 2) + "\n";
writeFileSync("data/captions/big-buck-bunny.json", json);
writeFileSync("public/research/demo-captions.json", json);
writeFileSync("public/research/big-buck-bunny.srt", sourceBytes);
writeFileSync("public/research/big-buck-bunny.vtt", "WEBVTT\n\n" + sourceBytes.toString("utf8").replace(/^\uFEFF/, "").replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, "$1.$2"));
writeFileSync("docs/verification/sourced-caption-import.json", JSON.stringify({
  approach: "licensed-source-captions", source: provenance, video_sha256: videoHash,
  cue_count: cues.length, source_event_count: cues.reduce((count, cue) => count + cue.original_text.split("\n").length, 0),
  timing: "All source intervals preserved exactly; no shifts, retiming or cyclic cues.",
  full_listening_review: false, participant_review: false,
  visual_sync_anchors: [20.7, 83.9, 195.9, 321.7, 410.99, 595.9],
  adaptation: "Cue-interval count in ±5 seconds: >=4 dense, <=1 quiet, otherwise balanced. Not visual scene analysis.",
  variants: "Local editorial paraphrases of 67 source labels. Detail changes source specificity; expression changes phrasing/punctuation. No new instruments, volume claims, sounds or inferred scene events.",
}, null, 2) + "\n");
console.log(`Installed ${cues.length} licensed source cues, original timestamps and nine cached wording variants each. No model calls.`);
