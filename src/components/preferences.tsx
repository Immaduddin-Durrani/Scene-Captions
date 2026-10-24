"use client";
import { useEffect, useState } from "react";
import type { CaptionCue, CaptionProfile } from "@/lib/captions";
import { Icon } from "./icon";
import { CaptionPreview } from "./caption-preview";
import { CaptionReadability } from "./caption-readability";
import { CaptionStyleControls } from "./caption-style-controls";
export function Preferences({ profile, onApply, sample, disabled, onPreview, onCancelPreview, previewing, originalActive, conservative = false, sceneTagsReady = true, unavailable = false, densityBased = false }: { profile: CaptionProfile; onApply: (profile: CaptionProfile) => void; sample: CaptionCue | undefined; disabled: boolean; onPreview: (candidate: CaptionProfile) => void; onCancelPreview: () => void; previewing: boolean; originalActive: boolean; conservative?: boolean; sceneTagsReady?: boolean; unavailable?: boolean; densityBased?: boolean }) {
  const [draft, setDraft] = useState(profile);
  // Content updates (including hydration) replace the draft; readability updates do not.
  useEffect(() => { setDraft((current) => ({ ...current, detail: profile.detail, expression: profile.expression, adaptive: profile.adaptive, representation: profile.representation })); }, [profile.detail, profile.expression, profile.adaptive, profile.representation]);
  const candidate = { ...draft, size: profile.size, position: profile.position, adaptive: sceneTagsReady && draft.adaptive };
  const changed = JSON.stringify(candidate) !== JSON.stringify(profile);
  return <aside className="preferences card" aria-labelledby="preferences-title">
    <div className="panel-heading"><div className="small-symbol"><Icon name="settings" size={20} /></div><div><h2 id="preferences-title">Make it yours</h2><p>A little detail. Or the whole picture.</p></div></div>
    {unavailable ? <p className="baseline-note">Add a matching caption track to enable these preferences.</p> : disabled && <p className="baseline-note">Original mode uses fixed captions. Switch to personalized to change preferences.</p>}
    <fieldset disabled={disabled || unavailable} className="preferences-fields"><legend className="sr-only">Caption preferences</legend>
      <CaptionStyleControls draft={draft} profile={profile} onDraft={setDraft} onCancelPreview={onCancelPreview} conservative={conservative} sceneTagsReady={sceneTagsReady} densityBased={densityBased} />
      <CaptionPreview sample={sample} candidate={candidate} onPreview={onPreview} originalActive={originalActive} previewing={previewing} />
      <button className="primary-button apply-button" disabled={!changed} onClick={() => onApply(candidate)}><Icon name={changed ? "check" : "shield"} size={17} />{changed ? "Apply preferences" : "Preferences applied"}</button>
      <p className="saved-note">{unavailable ? "Sound preferences are unavailable for this track. Caption readability still works below." : changed ? "Previewing changes. Your video settings stay the same until you apply." : "Saved in this browser. You’re always in control."}</p>
    </fieldset>
    <CaptionReadability profile={profile} onApply={onApply} />
  </aside>;
}
