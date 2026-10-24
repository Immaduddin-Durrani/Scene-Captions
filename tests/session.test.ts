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

test("rehearsal snapshots keep stopped duration and the complete caption override state", async () => {
  const { rehearsalSnapshot } = await import("../src/lib/session.ts");
  const { DEFAULT_PROFILE } = await import("../src/lib/captions.ts");
  const session = { data: null, condition: "personalized" as const, profile: DEFAULT_PROFILE, showOriginal: true, startedAt: 100, stoppedElapsed: 420, sessionId: "synthetic", events: [], ratings: {}, note: "" };
  const first = rehearsalSnapshot(session, 1000), later = rehearsalSnapshot(session, 5000);
  assert.equal(first.elapsed_ms, 420);
  assert.equal(later.elapsed_ms, first.elapsed_ms);
  assert.equal(first.final_original_override, true);
  assert.equal(first.purpose, "phase1-rehearsal-not-research");
  assert.equal(rehearsalSnapshot({ ...session, stoppedElapsed: null }, 1000).elapsed_ms, 900);
});
