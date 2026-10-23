import { test } from "node:test";
import assert from "node:assert/strict";
import { appendEvent } from "../src/lib/session.ts";
import type { RecordedEvent } from "../src/lib/session.ts";
test("event recording validates event types and stores relative elapsed time", () => {
  const events = appendEvent([], { type: "seek", video_s: 12 }, 24.7);
  assert.deepEqual(events, [{ type: "seek", video_s: 12, elapsed_ms: 25 }]);
  assert.throws(() => appendEvent([], { type: "seek", video_s: NaN }, 1));
});
test("rehearsal event buffer stays bounded", () => {
  const events: RecordedEvent[] = Array.from({ length: 3000 }, () => ({ type: "pause", video_s: 0, elapsed_ms: 0 }));
  assert.equal(appendEvent(events, { type: "play", video_s: 1 }, 200).length, 3000);
});
