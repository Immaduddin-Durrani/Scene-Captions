import { test } from "node:test";
import assert from "node:assert/strict";
import { parseSrt } from "../src/lib/srt.ts";

test("SubRip preserves BOM/CRLF multiline sound cues and millisecond timing", () => {
  assert.deepEqual(parseSrt("\uFEFF1\r\n00:01:23,624 --> 00:01:24,999\r\n[THUD]\r\n[SQUEAK]\r\n"), [{ id: "1", start_s: 83.624, end_s: 84.999, text: "[THUD]\n[SQUEAK]" }]);
});
test("SubRip rejects broken blocks, reversed intervals, duplicate IDs and invalid timestamps", () => {
  for (const bad of ["", "1\n00:00:02,000 --> 00:00:01,000\n[THUD]", "1\n00:99:01,000 --> 00:99:02,000\n[THUD]", "1\nnot timing\n[THUD]", "1\n00:00:01,000 --> 00:00:02,000\n[THUD]\n\n1\n00:00:03,000 --> 00:00:04,000\n[THUD]"]) assert.throws(() => parseSrt(bad));
});

test("SubRip accepts multiple blank separators without dropping official dialogue", () => {
  const input = "1\n00:00:01,000 --> 00:00:02,000\nFirst line.\n\n\n \n2\n00:00:03,000 --> 00:00:04,000\nSecond line.";
  assert.deepEqual(parseSrt(input).map(cue => cue.text), ["First line.", "Second line."]);
});
