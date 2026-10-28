import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { videoSchema } from "../src/lib/captions.ts";
import { sourceAssistedTrackFor } from "../src/lib/source-captions.ts";
import { parseSrt } from "../src/lib/srt.ts";

const base = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
const draft = () => {
  const track = structuredClone(base);
  track.generated_with.wording_style = "simple-source-richness";
  return track;
};

test("source-guided richness cannot change event identity, timing or simultaneous sound coverage", () => {
  assert.equal(sourceAssistedTrackFor(base, draft()).cues.length, 87);
  const changed = draft(); changed.cues[0].start_s += .1;
  assert.throws(() => sourceAssistedTrackFor(base, changed));
  const changedLabel = draft(); changedLabel.cues[0].reference_text = "[NEW SOUND]";
  assert.throws(() => sourceAssistedTrackFor(base, changedLabel));
  const missing = draft(); missing.cues.pop();
  assert.throws(() => sourceAssistedTrackFor(base, missing));
  const lostSound = draft(); lostSound.cues[1].grid["3-3"] = "[Only one of two simultaneous sounds]";
  assert.throws(() => sourceAssistedTrackFor(base, lostSound));
});
test("source-guided richness cannot attach to another film or remove source credit", () => {
  assert.throws(() => sourceAssistedTrackFor(base, { ...draft(), video_id: "sintel" }));
  const wrongEdit = draft(); wrongEdit.generated_with.source_sha256 = "a".repeat(64);
  assert.throws(() => sourceAssistedTrackFor(base, wrongEdit));
  const wrongCredit = draft(); wrongCredit.generated_with.caption_source!.license = "Unknown";
  assert.throws(() => sourceAssistedTrackFor(base, wrongCredit));
});
test("new source-guided wording cannot claim independent generation or completed review", () => {
  const track = draft();
  assert.equal(videoSchema.safeParse({ ...track, annotation_status: "reviewed" }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, generated_with: { ...track.generated_with, kind: "audio-derived" } }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, generated_with: { ...track.generated_with, quality_gate: "passed" } }).success, false);
});

test("new source-guided exports keep all pinned intervals and preserve every richness level", () => {
  const track = sourceAssistedTrackFor(base, JSON.parse(readFileSync("data/source-assisted-captions/big-buck-bunny.json", "utf8")));
  const source = parseSrt(readFileSync("data/sources/big-buck-captions/big-buck-bunny.srt", "utf8"));
  assert.deepEqual(track.cues.map(c => [c.start_s,c.end_s,c.reference_text]), source.map(c => [c.start_s,c.end_s,c.text]));
  assert.deepEqual(JSON.parse(readFileSync("public/research/source-richness/big-buck-bunny.json", "utf8")), track);
  for (const d of [1,2,3]) {
    const exported = parseSrt(readFileSync(`public/research/source-richness/big-buck-bunny-detail-${d}.srt`, "utf8"));
    assert.deepEqual(exported.map(c=>[c.start_s,c.end_s,c.text]),track.cues.map(c=>[c.start_s,c.end_s,c.grid[`${d}-2`]]));
    assert.ok(track.cues.every(c=>c.grid[`${d}-1`]===c.grid[`${d}-2`] && c.grid[`${d}-2`]===c.grid[`${d}-3`]));
  }
});
