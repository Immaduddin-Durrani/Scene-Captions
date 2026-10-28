import { videoSchema } from "./captions.ts";
import type { CaptionVideo } from "./captions.ts";

/** Preserve the exact licensed event list; richer wording cannot create coverage. */
export function sourceAssistedTrackFor(base: CaptionVideo, candidate: unknown): CaptionVideo {
  const track = videoSchema.parse(candidate);
  if (track.generated_with.wording_style !== "simple-source-richness" || track.video_id !== base.video_id || track.duration_seconds !== base.duration_seconds || !track.generated_with.source_sha256 || track.generated_with.source_sha256 !== base.generated_with.source_sha256 || JSON.stringify(track.generated_with.caption_source) !== JSON.stringify(base.generated_with.caption_source) || track.cues.length !== base.cues.length || JSON.stringify(track.dialogue || []) !== JSON.stringify(base.dialogue || [])) {
    throw new Error("Source-guided captions must match this film, source credit and event coverage.");
  }
  for (let i = 0; i < base.cues.length; i++) {
    const old = base.cues[i], cue = track.cues[i];
    if (cue.cue_id !== old.cue_id || cue.start_s !== old.start_s || cue.end_s !== old.end_s || cue.reference_text !== (old.reference_text || old.original_text) || Object.values(cue.grid).some(text => text.split("\n").length !== cue.reference_text!.split("\n").length)) {
      throw new Error("Source-guided captions must preserve each reference interval and simultaneous sound line.");
    }
  }
  return track;
}
