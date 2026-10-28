import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { videoSchema } from "../src/lib/captions.ts";
import { experimentalTrackFor } from "../src/lib/experimental-captions.ts";
import { parseSrt } from "../src/lib/srt.ts";

const base = videoSchema.parse(JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")));
function draft() {
  return { ...base, dialogue: [], dialogue_source: undefined,
    generated_with: { method: "audio only", prompt_version: "test", model: "test-model", kind: "audio-derived" as const,
      experimental: true as const, acoustic_validation: "failed" as const, input_basis: "media-only" as const,
      quality_gate: "unverified" as const, source_sha256: base.generated_with.source_sha256 },
    cues: base.cues.map(({ reference_text, ...cue }) => cue) };
}
test("experimental opt-in cannot claim review, success or reference-free sourced input", () => {
  const track = draft();
  assert.ok(videoSchema.safeParse(track).success);
  assert.equal(videoSchema.safeParse({ ...track, annotation_status: "reviewed" }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, generated_with: { ...track.generated_with, quality_gate: "passed" } }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, dialogue_source: base.generated_with.caption_source }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, cues: base.cues }).success, false);
  assert.equal(videoSchema.safeParse({ ...track, generated_with: { ...track.generated_with, acoustic_validation: undefined } }).success, false);
});
test("an experimental track cannot attach to a different film or edit", () => {
  const track = draft();
  assert.equal(experimentalTrackFor(base, track).video_id, base.video_id);
  for (const change of [{ video_id: "sintel" }, { duration_seconds: base.duration_seconds + 1 },
    { generated_with: { ...track.generated_with, source_sha256: "a".repeat(64) } }]) {
    assert.throws(() => experimentalTrackFor(base, { ...track, ...change }));
  }
});
test("empty experimental output does not masquerade as a missing or verified source track", () => {
  assert.ok(videoSchema.safeParse({ ...draft(), cues: [] }).success);
  assert.equal(videoSchema.safeParse({ ...base, cues: [] }).success, false);
});

for (const id of ["big-buck-bunny", "sintel", "tears-of-steel"]) {
  test(`${id}: complete media-only export stays separate and all three SRTs match its generated data`, () => {
    const original = videoSchema.parse(JSON.parse(readFileSync(`data/captions/${id}.json`, "utf8")));
    const track = experimentalTrackFor(original, JSON.parse(readFileSync(`data/experimental-captions/${id}.json`, "utf8")));
    const summary = JSON.parse(readFileSync(`docs/verification/media-only-2026-10-28/v2/${id}-summary.json`, "utf8"));
    assert.equal(summary.windows, Math.ceil(track.duration_seconds / 15));
    assert.equal(summary.completed, summary.windows);
    assert.deepEqual(summary.missing_windows, []);
    assert.equal(track.generated_with.caption_source, undefined);
    assert.equal(track.dialogue_source, undefined);
    assert.deepEqual(JSON.parse(readFileSync(`public/research/media-only/${id}.json`, "utf8")), track);
    for (const level of [1, 2, 3]) {
      const expected = [
        ...track.cues.map(c => ({ start_s: c.start_s, end_s: c.end_s, text: c.grid[`${level}-2`] })),
        ...(track.dialogue || []).map(c => ({ start_s: c.start_s, end_s: c.end_s, text: c.text })),
      ].sort((a, b) => a.start_s - b.start_s || a.end_s - b.end_s);
      const exported = parseSrt(readFileSync(`public/research/media-only/${id}-detail-${level}.srt`, "utf8"));
      assert.deepEqual(exported.map(c => c.text), expected.map(c => c.text));
      for (let i = 0; i < expected.length; i++) {
        assert.ok(Math.abs(exported[i].start_s - expected[i].start_s) < .001);
        assert.ok(Math.abs(exported[i].end_s - expected[i].end_s) < .001);
      }
    }
  });
}
