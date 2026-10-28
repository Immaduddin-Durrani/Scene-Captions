"use client";
import type { CaptionCue, CaptionProfile } from "@/lib/captions";
import { Icon } from "./icon";
import { CaptionPreview } from "./caption-preview";
import { CaptionReadability } from "./caption-readability";
import { CaptionStyleControls } from "./caption-style-controls";
export function Preferences({ profile, onApply, sample, disabled, onPreview, previewing, originalActive, conservative = false, sceneTagsReady = true, unavailable = false, densityBased = false, punctuationOnly = false }: { profile: CaptionProfile; onApply: (profile: CaptionProfile) => void; sample: CaptionCue | undefined; disabled: boolean; onPreview: (candidate: CaptionProfile) => void; previewing: boolean; originalActive: boolean; conservative?: boolean; sceneTagsReady?: boolean; unavailable?: boolean; densityBased?: boolean; punctuationOnly?: boolean }) {
  const candidate = { ...profile, adaptive: sceneTagsReady && profile.adaptive };
  function update(next: CaptionProfile) {
    onApply({ ...next, adaptive: sceneTagsReady && next.adaptive });
  }
  return <aside className="preferences card" aria-labelledby="preferences-title">
    <div className="panel-heading"><div className="small-symbol"><Icon name="settings" size={20} /></div><div><h2 id="preferences-title">Make it yours</h2><p>A little detail. Or the whole picture.</p></div></div>
    {unavailable ? <p className="baseline-note">Add a matching caption track to enable these preferences.</p> : disabled && <p className="baseline-note">Baseline mode uses fixed captions. Switch to personalized to change preferences.</p>}
    <fieldset disabled={disabled || unavailable} className="preferences-fields"><legend className="sr-only">Caption preferences</legend>
      <CaptionStyleControls draft={profile} profile={profile} onDraft={update} conservative={conservative} sceneTagsReady={sceneTagsReady} densityBased={densityBased} punctuationOnly={punctuationOnly} />
      <CaptionPreview sample={sample} candidate={candidate} onPreview={onPreview} originalActive={originalActive} previewing={previewing} />
      <p className="saved-note">{unavailable ? "Sound preferences are unavailable for this track. Caption readability still works below." : "Changes apply immediately."}</p>
    </fieldset>
    <CaptionReadability profile={profile} onApply={onApply} />
  </aside>;
}
