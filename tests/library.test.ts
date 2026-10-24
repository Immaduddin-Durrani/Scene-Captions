import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { videoSchema } from "../src/lib/captions.ts";
import { parseSrt } from "../src/lib/srt.ts";

for (const [id, count] of [["sintel", 26], ["tears-of-steel", 76]] as const) {
  test(`${id} preserves official dialogue, timing and provenance without inventing sounds`, () => {
    const data = videoSchema.parse(JSON.parse(readFileSync(`data/captions/${id}.json`, "utf8")));
    const bytes = readFileSync(`data/sources/library/${id}-en.srt`);
    const source = parseSrt(bytes.toString("utf8"));
    assert.equal(source.length, count);
    assert.deepEqual(data.dialogue?.map(cue => [cue.start_s, cue.end_s, cue.text]), source.map(cue => [cue.start_s, cue.end_s, cue.text]));
    assert.equal(data.dialogue_source?.sha256, createHash("sha256").update(bytes).digest("hex"));
    assert.equal(data.generated_with.non_speech_status, "not-prepared");
    assert.equal(data.generated_with.quality_gate, "unverified");
    assert.equal(data.cues.length, 0);
  });
}

test("dialogue validation rejects duplicate IDs and intervals outside the selected film", () => {
  const data = JSON.parse(readFileSync("data/captions/sintel.json", "utf8"));
  const duplicate = structuredClone(data); duplicate.dialogue.push(duplicate.dialogue[0]);
  assert.equal(videoSchema.safeParse(duplicate).success, false);
  const outside = structuredClone(data); outside.dialogue[0].end_s = data.duration_seconds + 1;
  assert.equal(videoSchema.safeParse(outside).success, false);
  const backwards = structuredClone(data); backwards.dialogue.reverse();
  assert.equal(videoSchema.safeParse(backwards).success, false);
  const fakeReady = structuredClone(data); delete fakeReady.generated_with.non_speech_status;
  assert.equal(videoSchema.safeParse(fakeReady).success, false);
  const failed = structuredClone(data); failed.generated_with.quality_gate = "failed";
  failed.cues = JSON.parse(readFileSync("data/captions/big-buck-bunny.json", "utf8")).cues;
  assert.equal(videoSchema.safeParse(failed).success, false);
});
