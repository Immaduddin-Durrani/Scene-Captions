"use client";
import { resolveCaption } from "@/lib/captions";
import type { CaptionCue, CaptionProfile } from "@/lib/captions";
import { Icon } from "./icon";

export function CaptionPreview({ sample, candidate, onPreview, originalActive, previewing }: {
  sample: CaptionCue | undefined; candidate: CaptionProfile; onPreview: (candidate: CaptionProfile) => void;
  originalActive: boolean; previewing: boolean;
}) {
  const preview = sample ? resolveCaption(sample, candidate, "personalized").text : "Add your caption file to preview a sound.";
  return (
      <div className="preview-card"><div><span>CAPTION PREVIEW</span><Icon name="sound" size={16} /></div><p>{preview}</p><button className="text-button" disabled={!sample || originalActive} onClick={() => onPreview(candidate)}><Icon name="play" size={13} />Preview this cue in the video</button><small>{originalActive ? "Turn Show original off to try different wording." : previewing ? "Cue preview ends in five seconds, or choose Return to saved settings." : "Pauses the video at this cue for five seconds. Your preferences stay applied."}</small></div>
  );
}
