import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { parseSrt } from "../src/lib/srt.ts";
import { activeCues, resolveCaption, DEFAULT_PROFILE, videoSchema, profileSchema, formatTime } from "../src/lib/captions.ts";
const video = () => videoSchema.parse(JSON.parse(readFileSync("public/research/caption-template.json", "utf8")));
test("cue boundaries exclude ended captions and preserve simultaneous sounds", () => {
  const cue = video().cues[0];
  assert.equal(activeCues([cue], cue.start_s).length, 1);
  assert.equal(activeCues([cue], cue.end_s).length, 0);
  assert.equal(activeCues([cue, { ...cue, cue_id: "overlap" }], cue.start_s).length, 2);
});
test("baseline and Show Original always preserve the original", () => {
  const cue = video().cues[0];
  assert.equal(resolveCaption(cue, DEFAULT_PROFILE, "baseline").text, cue.original_text);
  assert.equal(resolveCaption(cue, DEFAULT_PROFILE, "personalized", true).text, cue.original_text);
});
test("adaptation is cached selection and does not mutate saved preferences", () => {
  const cue = { ...video().cues[0], scene_load: "dense" as const };
  const profile = { ...DEFAULT_PROFILE };
  assert.equal(resolveCaption(cue, profile, "personalized").text, cue.grid["1-2"]);
  assert.equal(profile.detail, 2);
  assert.equal(resolveCaption(cue, { ...profile, adaptive: false }, "personalized").text, cue.grid["2-2"]);
});
test("malformed and incomplete annotation files are rejected", () => {
  const bad = video(); bad.cues[0].grid = { "1-1": "Missing variants" };
  assert.equal(videoSchema.safeParse(bad).success, false);
  const duplicates = video(); duplicates.cues.push(duplicates.cues[0]);
  assert.equal(videoSchema.safeParse(duplicates).success, false);
  assert.equal(profileSchema.safeParse({ ...DEFAULT_PROFILE, detail: 99 }).success, false);
});
test("alternate representation falls back to descriptive when unavailable", () => {
  const cue = video().cues[0]; delete cue.representations.onomatopoeic;
  assert.equal(resolveCaption(cue, { ...DEFAULT_PROFILE, adaptive: false, representation: "onomatopoeic" }, "personalized").text, cue.grid["2-2"]);
  assert.equal(formatTime(67.9), "1:07");
});
test("failed audio generation cannot activate unreviewed candidates", () => {
  const unavailable = video(); unavailable.cues = []; unavailable.generated_with.quality_gate = "failed";
  assert.equal(videoSchema.safeParse(unavailable).success, true);
  unavailable.cues = video().cues;
  assert.equal(videoSchema.safeParse(unavailable).success, false);
  const empty = video(); empty.cues = [];
  assert.equal(videoSchema.safeParse(empty).success, false);
});
test("bundled captions preserve every licensed source interval and simultaneous event", () => {
  const bundled = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
  const bytes = readFileSync("data/sources/big-buck-captions/big-buck-bunny.srt");
  const source = parseSrt(bytes.toString("utf8"));
  assert.equal(source.length, 87);
  assert.equal(bundled.generated_with.kind, "source-assisted");
  assert.equal(bundled.generated_with.caption_source?.sha256, createHash("sha256").update(bytes).digest("hex"));
  assert.deepEqual(bundled.cues.map(cue => [cue.start_s, cue.end_s, cue.reference_text]), source.map(cue => [cue.start_s, cue.end_s, cue.text]));
  assert.equal(activeCues(bundled.cues, 78).length, 0);
  assert.equal(activeCues(bundled.cues, 83.9)[0].reference_text, "[APPLE THUDS]");
  assert.equal(activeCues(bundled.cues, 12)[0].reference_text, "[BROOK BABBLES]\n[FLY BUZZES]");
  assert.equal(activeCues(bundled.cues, 595.9)[0].reference_text, "[POOP SPLATS]");
});
test("source-derived adaptation discloses its caption-density proxy", () => {
  const bundled = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
  const cue = bundled.cues.find(cue => cue.scene_load === "dense")!;
  const selected = resolveCaption(cue, DEFAULT_PROFILE, "personalized");
  assert.equal(selected.detail, 1);
  assert.match(selected.reason, /frequent sound cues/);
  assert.equal(resolveCaption(cue, { ...DEFAULT_PROFILE, adaptive: false, detail: 3 }, "personalized").detail, 3);
});

test("adaptation never exceeds the viewer's detail limit", () => {
  const cue = video().cues[0];
  for (const detail of [1, 2, 3] as const) {
    for (const scene_load of ["quiet", "balanced", "dense"] as const) {
      const selected = resolveCaption({ ...cue, scene_load }, { ...DEFAULT_PROFILE, detail }, "personalized");
      assert.ok(selected.detail <= detail, `${scene_load} exceeded detail ${detail}`);
      assert.equal(selected.detail, scene_load === "dense" ? 1 : detail);
    }
  }
});

test("generated captions and fetched comparison remain separate with shared timings", () => {
  const track = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
  const exported = parseSrt(readFileSync("public/research/big-buck-bunny.srt", "utf8"));
  assert.equal(track.generated_with.model, "mlx-community/Qwen2.5-1.5B-Instruct-4bit");
  assert.equal(track.generated_with.generation_record_sha256, createHash("sha256").update(readFileSync("data/authoring/big-buck-bunny-generated.json")).digest("hex"));
  assert.equal(track.annotation_status, "draft");
  assert.equal(track.generated_with.quality_gate, "unverified");
  assert.deepEqual(exported.map(c => [c.start_s, c.end_s, c.text]), track.cues.map(c => [c.start_s, c.end_s, c.original_text]));
  for (const cue of track.cues) {
    assert.notEqual(cue.original_text.toLowerCase(), cue.reference_text!.toLowerCase());
    assert.equal(resolveCaption(cue, DEFAULT_PROFILE, "baseline").text, cue.reference_text);
    assert.equal(resolveCaption(cue, DEFAULT_PROFILE, "personalized", true).text, cue.reference_text);
    assert.equal(resolveCaption(cue, { ...DEFAULT_PROFILE, adaptive: false }, "personalized").text, cue.grid["2-2"]);
    for (const text of Object.values(cue.grid)) assert.equal(text.split("\n").length, cue.reference_text!.split("\n").length);
  }
  const missingCredit = structuredClone(track); delete missingCredit.generated_with.caption_source;
  assert.equal(videoSchema.safeParse(missingCredit).success, false);
  const missingReference = structuredClone(track); delete missingReference.cues[0].reference_text;
  assert.equal(videoSchema.safeParse(missingReference).success, false);
});
