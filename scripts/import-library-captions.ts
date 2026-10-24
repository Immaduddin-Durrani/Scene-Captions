import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { parseSrt } from "../src/lib/srt.ts";
import { videoSchema } from "../src/lib/captions.ts";

// Deliberately imports only the official English subtitles. No guessed sound events.
for (const id of ["sintel", "tears-of-steel"]) {
  const root = "data/sources/library/";
  const resource = JSON.parse(readFileSync(root + id + ".resources.json", "utf8"));
  const video = readFileSync("public" + resource.video);
  if (createHash("sha256").update(video).digest("hex") !== resource.sha256) throw new Error(`Different ${id} edit; inspect alignment before importing.`);
  const raw = readFileSync(root + id + "-en.srt");
  const source = parseSrt(raw.toString("utf8"));
  const track = videoSchema.parse({
    schema_version: 1, video_id: id, title: resource.title,
    source_url: resource.licenseSource, license: resource.license, attribution: resource.credit,
    duration_seconds: resource.durationSeconds, annotation_status: "draft",
    generated_with: { method: "Official English dialogue subtitles imported without changing wording or timing. No verified non-speech track is available for this film.", prompt_version: "official-dialogue-v1", kind: "sourced", source_sha256: resource.sha256, expressiveness: "conservative", scene_load_method: "unreviewed", quality_gate: "unverified", non_speech_status: "not-prepared" },
    dialogue_source: { url: id === "sintel" ? resource.source : resource.subtitleSource, author: "Blender Foundation", license: "CC BY 3.0", sha256: createHash("sha256").update(raw).digest("hex") },
    dialogue: source.map(cue => ({ cue_id: `${id}-dialogue-${cue.id}`, start_s: cue.start_s, end_s: cue.end_s, text: cue.text })),
    cues: [],
  });
  const json = JSON.stringify(track, null, 2) + "\n";
  writeFileSync(`data/captions/${id}.json`, json);
  writeFileSync(`public/research/${id}-captions.json`, json);
  console.log(`${id}: ${source.length} dialogue cues; non-speech captions explicitly not prepared.`);
}
