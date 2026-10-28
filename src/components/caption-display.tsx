"use client";
import { useState } from "react";
import { activeCues, formatTime, resolveCaption } from "@/lib/captions";
import type { CaptionCue, CaptionProfile, CaptionVideo, Condition } from "@/lib/captions";
import { Icon } from "./icon";

type Selected = ReturnType<typeof resolveCaption>;
function captionStatus(cues: CaptionCue[], active: Selected[], hasTrack: boolean, nextCue: CaptionCue | undefined, condition: Condition, original: boolean) {
  if (!hasTrack) return "No sound-caption track available";
  if (!active.length) return nextCue ? `Next sound caption at ${formatTime(nextCue.start_s)}` : "No more sound captions in this track";
  if (active.some(caption => caption.adapted)) return cues.some(cue => cue.scene_load_basis === "cue-density") ? "Adapted to sound-cue density" : "Adapted to this scene";
  if (original || condition === "baseline") return cues.some(cue => cue.reference_text) ? "Showing fetched reference captions" : "Showing original captions";
  return "Using your preferences";
}

export function useCaptionDisplay(data: CaptionVideo | null, duration: number, time: number, profile: CaptionProfile, condition: Condition, showOriginal: boolean) {
  const mismatch = !!data && duration > 0 && Math.abs(duration - data.duration_seconds) > 2;
  const cues = data && !mismatch ? activeCues(data.cues, time) : [];
  const nextCue = data && !mismatch ? data.cues.find(cue => cue.start_s > time) : undefined;
  const active = cues.map(cue => resolveCaption(cue, profile, condition, showOriginal));
  return { mismatch, cues, nextCue, active };
}

export function CaptionOverlay({ active, cues, profile, dialogue = [] }: { active: Selected[]; cues: CaptionCue[]; profile: CaptionProfile; dialogue?: { cue_id: string; text: string }[] }) {
  if (!active.length && !dialogue.length) return null;
  return <div className={`caption-overlay ${profile.position} ${profile.size}`} aria-label="Captions">
    {!!dialogue.length && <div className="dialogue-lines" aria-label="Dialogue subtitles">{dialogue.map(cue => <p key={cue.cue_id}>{cue.text}</p>)}</div>}
    {!!active.length && <div className="caption-lines" aria-label="Non-speech captions">{active.map((caption, index) => <p key={cues[index].cue_id}>{caption.text}</p>)}</div>}
  </div>;
}

export function CaptionFeedback({ data, display, condition, showOriginal }: {
  data: CaptionVideo | null; display: ReturnType<typeof useCaptionDisplay>; condition: Condition; showOriginal: boolean;
}) {
  const [why, setWhy] = useState(false);
  const { cues, active, nextCue } = display;
  return <>
    <div className="caption-status"><span><Icon name="sound" size={17} />{data?.generated_with.experimental && showOriginal ? "Showing fixed generated draft" : captionStatus(cues, active, !!data?.cues.length, nextCue, condition, showOriginal)}</span><button className="text-button" onClick={() => setWhy(!why)} aria-expanded={why}><Icon name="info" size={16} />Why this caption?</button></div>
    {why && <div className="explanation"><strong>{active[0]?.reason || "Sound captions follow the video timeline."}</strong><p>{cues[0]?.reference_text && (showOriginal || condition === "baseline") ? "The credited source caption is shown unchanged at its original interval. Leave reference mode to return to your saved preferences." : cues[0]?.scene_context || "When a cue is active, this panel explains the caption selection. You can turn scene adaptation off or show the original at any time."}</p></div>}
  </>;
}
