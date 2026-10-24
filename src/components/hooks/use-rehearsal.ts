"use client";
import { useCallback, useState } from "react";
import { appendEvent } from "@/lib/session";
import type { StudyEvent, RecordedEvent } from "@/lib/session";
import type { CaptionProfile, Condition } from "@/lib/captions";

export function useRehearsal() {
  const [recording, setRecording] = useState(false);
  const [events, setEvents] = useState<RecordedEvent[]>([]);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [stoppedElapsed, setStoppedElapsed] = useState<number | null>(null);
  const record = useCallback((event: StudyEvent) => {
    if (recording && startedAt !== null) setEvents(current => appendEvent(current, event, performance.now() - startedAt));
  }, [recording, startedAt]);
  function start(video_s: number, condition: Condition, profile: CaptionProfile, enabled: boolean) {
    setStartedAt(performance.now()); setStoppedElapsed(null);
    setSessionId(crypto.randomUUID().slice(0, 8)); setRecording(true);
    setEvents([
      { type: "condition", video_s, condition, elapsed_ms: 0 },
      { type: "profile", video_s, profile, elapsed_ms: 0 },
      { type: "original", video_s, enabled, elapsed_ms: 0 },
    ]);
  }
  function stop() {
    setStoppedElapsed(startedAt !== null ? Math.round(performance.now() - startedAt) : 0);
    setRecording(false);
  }
  return { recording, events, startedAt, sessionId, stoppedElapsed, record, start, stop };
}
