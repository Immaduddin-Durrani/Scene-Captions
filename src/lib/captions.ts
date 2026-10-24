import { z } from "zod";

const LEVELS = [1, 2, 3] as const;
export type Level = (typeof LEVELS)[number];
export type Condition = "personalized" | "baseline";
const gridKeys = LEVELS.flatMap((detail) => LEVELS.map((expression) => `${detail}-${expression}`));
const gridSchema = z.record(z.string(), z.string().trim().min(1).max(280)).refine(
  (grid) => gridKeys.every((key) => key in grid) && Object.keys(grid).length === 9,
  "Provide exactly the nine detail-expression variants (1-1 through 3-3).",
);
const cueSchema = z.object({
  cue_id: z.string().min(1).max(80), start_s: z.number().finite().nonnegative(),
  end_s: z.number().finite().positive(), original_text: z.string().trim().min(1).max(280),
  scene_context: z.string().max(500), sound_key: z.string().min(1).max(80),
  scene_load: z.enum(["quiet", "balanced", "dense"]), grid: gridSchema,
  scene_load_basis: z.enum(["manual", "cue-density"]).optional(),
  representations: z.object({ plain: z.string().min(1).max(280), onomatopoeic: z.string().min(1).max(280).optional() }),
}).refine((cue) => cue.end_s > cue.start_s, "Cue end must follow its start.");
export const videoSchema = z.object({
  schema_version: z.literal(1), video_id: z.string().regex(/^[a-z0-9-]+$/).max(80),
  title: z.string().min(1).max(160), source_url: z.string().url(),
  license: z.string().min(1).max(240), attribution: z.string().min(1).max(500),
  duration_seconds: z.number().finite().positive().max(14400),
  annotation_status: z.enum(["draft", "reviewed"]),
  generated_with: z.object({
    method: z.string().min(1), prompt_version: z.string().min(1),
    kind: z.enum(["illustrative", "audio-derived", "audio-video-derived", "human", "sourced"]).optional(),
    model: z.string().optional(), source_sha256: z.string().regex(/^[a-f0-9]{64}$/).optional(),
    expressiveness: z.enum(["conservative", "reviewed", "source-anchored"]).optional(),
    scene_load_method: z.enum(["unreviewed", "reviewed", "cue-density"]).optional(),
    caption_source: z.object({ url: z.string().url().regex(/^https?:\/\//), revision: z.string(), license: z.string(), author: z.string(), sha256: z.string().regex(/^[a-f0-9]{64}$/) }).optional(),
    quality_gate: z.enum(["failed", "unverified", "passed"]).optional(),
  }),
  cues: z.array(cueSchema).max(5000),
}).superRefine((video, ctx) => {
  if (!video.cues.length && video.generated_with.quality_gate !== "failed") ctx.addIssue({ code: "custom", path: ["cues"], message: "Provide caption cues, or explicitly mark the failed generation gate." });
  if (video.generated_with.quality_gate === "failed" && video.cues.length) ctx.addIssue({ code: "custom", path: ["cues"], message: "Failed generation candidates cannot be used for playback. Review and correct the captions first." });
  const ids = new Set<string>();
  video.cues.forEach((cue, index) => {
    if (ids.has(cue.cue_id)) ctx.addIssue({ code: "custom", path: ["cues", index, "cue_id"], message: "Cue IDs must be unique." });
    ids.add(cue.cue_id);
    if (cue.end_s > video.duration_seconds) ctx.addIssue({ code: "custom", path: ["cues", index], message: "Cue exceeds the video duration." });
    if (index && cue.start_s < video.cues[index - 1].start_s) ctx.addIssue({ code: "custom", path: ["cues", index], message: "Cues must be ordered by start time." });
  });
});
export type CaptionCue = z.infer<typeof cueSchema>;
export type CaptionVideo = z.infer<typeof videoSchema>;
export const profileSchema = z.object({
  detail: z.union([z.literal(1), z.literal(2), z.literal(3)]),
  expression: z.union([z.literal(1), z.literal(2), z.literal(3)]),
  adaptive: z.boolean(), representation: z.enum(["descriptive", "plain", "onomatopoeic"]),
  size: z.enum(["standard", "large", "extra-large"]), position: z.enum(["bottom", "top"]),
});
export type CaptionProfile = z.infer<typeof profileSchema>;
export const DEFAULT_PROFILE: CaptionProfile = { detail: 2, expression: 2, adaptive: true, representation: "descriptive", size: "large", position: "bottom" };

export function activeCues(cues: CaptionCue[], seconds: number): CaptionCue[] {
  return cues.filter((cue) => cue.start_s <= seconds && seconds < cue.end_s);
}

export function resolveCaption(cue: CaptionCue, profile: CaptionProfile, condition: Condition, showOriginal = false) {
  if (condition === "baseline" || showOriginal) return { text: cue.original_text, reason: "Original caption", adapted: false, detail: profile.detail };
  const detail: Level = profile.adaptive && cue.scene_load === "dense" ? 1 : profile.detail;
  const adapted = profile.adaptive && detail !== profile.detail;
  const text = profile.representation === "plain" ? cue.representations.plain
    : profile.representation === "onomatopoeic" && cue.representations.onomatopoeic ? cue.representations.onomatopoeic
      : cue.grid[`${detail}-${profile.expression}`];
  const reason = adapted ? cue.scene_load_basis === "cue-density" ? cue.scene_load === "dense" ? "Less detail among frequent sound cues" : "More detail among sparse sound cues" : cue.scene_load === "dense" ? "Less detail in a busy scene" : "More detail in a quiet scene" : "Your saved preferences";
  return { text, reason: profile.representation !== "descriptive" ? "Your selected sound representation" : reason, adapted: adapted && profile.representation === "descriptive", detail };
}

export function formatTime(seconds: number): string {
  const safe = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
  return `${Math.floor(safe / 60)}:${String(safe % 60).padStart(2, "0")}`;
}
