import { videoSchema } from "./captions.ts";
import type { CaptionVideo } from "./captions.ts";

/** A separate opt-in track may never attach to another film or masquerade as reviewed. */
export function experimentalTrackFor(base: CaptionVideo, candidate: unknown): CaptionVideo {
  const track = videoSchema.parse(candidate);
  if (!track.generated_with.experimental || track.video_id !== base.video_id || Math.abs(track.duration_seconds - base.duration_seconds) > .05 || !track.generated_with.source_sha256 || track.generated_with.source_sha256 !== base.generated_with.source_sha256) {
    throw new Error("Experimental captions must match this exact film's identity, duration and source hash.");
  }
  return track;
}
