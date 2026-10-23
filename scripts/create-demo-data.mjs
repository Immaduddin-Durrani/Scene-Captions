import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
// Build only from the real audio detections. There is no placeholder fallback.
const evidencePath = "docs/verification/sound-event-detections.json";
const evidence = JSON.parse(readFileSync(evidencePath, "utf8"));
const hash = createHash("sha256").update(readFileSync("public/media/big-buck-bunny.mp4")).digest("hex");
if (hash !== evidence.video_sha256) throw new Error("Sound detections belong to a different video. Re-analyze this exact file.");
// Deliberately broad, non-interpretive labels; no character, motive or visual-event inference.
const labels = new Map([
  ["Music", ["music", "music", "music plays"]],
  ["Bird vocalization, bird call, bird song", ["birdsong", "birds calling", "bird calls are heard"]],
  ["Chirp, tweet", ["chirping", "bird chirps", "short bird chirps are heard"]],
  ["Chirping, tweeting", ["chirping", "bird chirps", "short bird chirps are heard"]],
  ["Crow", ["cawing", "a crow caws", "cawing is heard"]],
  ["Wind", ["wind", "wind blowing", "the sound of wind"]],
  ["Rustling leaves", ["rustling", "leaves rustle", "rustling leaves are heard"]],
  ["Footsteps", ["footsteps", "footsteps", "footsteps are heard"]],
  ["Walk, footsteps", ["footsteps", "footsteps", "footsteps are heard"]],
  ["Running", ["running footsteps", "running footsteps", "rapid footsteps are heard"]],
  ["Laughter", ["laughter", "laughing", "laughter is heard"]],
  ["Chuckle, chortle", ["chuckling", "chuckling", "a chuckle is heard"]],
  ["Sigh", ["a sigh", "sighing", "a sigh is heard"]],
  ["Snoring", ["snoring", "snoring", "snoring is heard"]],
  ["Breathing", ["breathing", "breathing", "breathing is heard"]],
  ["Sniff", ["sniffing", "sniffing", "sniffing is heard"]],
  ["Thump, thud", ["a thud", "a dull thud", "a thudding sound is heard"]],
  ["Whack, thwack", ["a whack", "a whacking sound", "a sharp whacking sound is heard"]],
  ["Slam", ["a slam", "a slamming sound", "a slamming sound is heard"]],
  ["Crash", ["a crash", "a crashing sound", "a crashing sound is heard"]],
  ["Splash, splatter", ["splashing", "water splashes", "splashing water is heard"]],
  ["Water", ["water", "water sounds", "the sound of water"]],
  ["Squeak", ["a squeak", "squeaking", "a squeaking sound is heard"]],
  ["Fart", ["flatulence", "a fart", "a farting sound is heard"]],
]);
const cells = evidence.windows.map((window) => {
  if (window.rms < 0.001) return null;
  const candidates = window.predictions.filter((p) => labels.has(p.label) && p.score >= (p.label === "Music" ? 0.75 : 0.85));
  // Prefer a supported sound effect to a generic soundtrack label.
  const best = candidates.find((p) => p.label !== "Music") || candidates[0];
  return best ? { start_s: window.start_s, end_s: Math.min(window.start_s + evidence.stride_seconds, evidence.audio_duration_seconds), label: best.label, score: best.score, window } : null;
});
const runs = [];
for (const cell of cells) {
  if (!cell) continue;
  const last = runs.at(-1);
  if (last && last.label === cell.label && Math.abs(last.end_s - cell.start_s) < 0.01) { last.end_s = cell.end_s; last.cells.push(cell); }
  else runs.push({ start_s: cell.start_s, end_s: cell.end_s, label: cell.label, cells: [cell] });
}
const cues = []; const audit = [];
for (const run of runs) {
  // Reject an isolated broad classifier hit. Transient events remain a review limitation.
  if (run.label !== "Music" && run.cells.length < 2) continue;
  const variants = labels.get(run.label);
  // Show sustained sounds briefly, with a reminder every 20 seconds, rather than a permanent overlay.
  for (let start = run.start_s; start < run.end_s; start += 20) {
    const end = Math.min(run.end_s, start + 6);
    if (end - start < 1) continue;
    const grid = {};
    for (let detail = 1; detail <= 3; detail++) for (let expression = 1; expression <= 3; expression++) grid[`${detail}-${expression}`] = `[${variants[detail - 1]}]`;
    const id = `audio-${String(cues.length + 1).padStart(3, "0")}`;
    cues.push({ cue_id: id, start_s: start, end_s: end, original_text: `[${variants[0]}]`, sound_key: run.label.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-$/, ""), scene_context: `The audio classifier detected ${run.label.toLowerCase()} in this interval. Timing is estimated from overlapping ${evidence.window_seconds}-second windows, not manually aligned. Scene load is not inferred; adaptation stays neutral.`, scene_load: "balanced", grid, representations: { plain: `[${variants[0]}]` } });
    audit.push({ cue_id: id, classifier_label: run.label, start_s: start, end_s: end, source_windows: run.cells.filter((c) => c.window.end_s > start && c.window.start_s < end).map((c) => ({ start_s: c.window.start_s, end_s: c.window.end_s, score: c.score })) });
  }
}
cues.sort((a,b) => a.start_s - b.start_s);
if (!cues.length) throw new Error("No supported sounds met the threshold. Do not invent fallback captions.");
const metadata = { schema_version: 1, video_id: "big-buck-bunny", title: "Big Buck Bunny", source_url: "https://peach.blender.org/about/", license: "CC BY 3.0", attribution: "© 2008 Blender Foundation / peach.blender.org. Audio-classifier-generated captions added by SceneCaptions; not creator-authored or human-reviewed.", duration_seconds: evidence.audio_duration_seconds, annotation_status: "draft", generated_with: { method: `Local AudioSet AST ${evidence.model}@${evidence.revision}; deterministic conservative wording; ${evidencePath}`, prompt_version: "actual-audio-v1" }, cues };
writeFileSync("docs/verification/ast-caption-candidates.json", JSON.stringify(metadata, null, 2)+"\n");
writeFileSync("docs/verification/caption-generation-audit.json", JSON.stringify({ model: evidence.model, revision: evidence.revision, video_sha256: hash, machine_generated: true, human_reviewed: false, timing_uncertainty_seconds: evidence.window_seconds / 2, confidence_note: "Model scores are not calibrated correctness probabilities.", scene_load: "balanced for every cue: no unsupported scene-density claims", expressiveness: "Intentionally identical across expression levels: no unsupported emotions or acoustic qualities added.", cues: audit }, null, 2)+"\n");
console.log(`Generated ${cues.length} actual-audio-derived draft candidates to docs/verification only. Nothing installed; human review remains required.`);
