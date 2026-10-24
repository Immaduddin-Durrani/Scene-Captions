import { z } from "zod";
import { profileSchema } from "./captions.ts";
const eventSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("play"), video_s: z.number() }),
  z.object({ type: z.literal("pause"), video_s: z.number() }),
  z.object({ type: z.literal("seek"), video_s: z.number() }),
  z.object({ type: z.literal("profile"), video_s: z.number(), profile: profileSchema }),
  z.object({ type: z.literal("original"), video_s: z.number(), enabled: z.boolean() }),
  z.object({ type: z.literal("condition"), video_s: z.number(), condition: z.enum(["baseline", "personalized"]) }),
  z.object({ type: z.literal("preview"), video_s: z.number(), profile: profileSchema.optional(), cue_id: z.string().optional() }),
  z.object({ type: z.literal("preview_end"), video_s: z.number() }),
]);
export type StudyEvent = z.infer<typeof eventSchema>;
export type RecordedEvent = StudyEvent & { elapsed_ms: number };
const MAX_EVENTS = 3000;
export function appendEvent(events: RecordedEvent[], event: StudyEvent, elapsed_ms: number): RecordedEvent[] {
  const valid = eventSchema.parse(event);
  if (events.length >= MAX_EVENTS) return events;
  return [...events, { ...valid, elapsed_ms: Math.max(0, Math.round(elapsed_ms)) }];
}
