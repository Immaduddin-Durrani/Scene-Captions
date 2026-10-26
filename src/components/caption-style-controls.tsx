"use client";
import { useState } from "react";
import type { CaptionProfile, Level } from "@/lib/captions";
import { Icon } from "./icon";

export function CaptionStyleControls({ draft, profile, onDraft, onCancelPreview, conservative, sceneTagsReady, densityBased, punctuationOnly = false }: {
  draft: CaptionProfile; profile: CaptionProfile; onDraft: (candidate: CaptionProfile) => void;
  onCancelPreview: () => void; conservative: boolean; sceneTagsReady: boolean; densityBased: boolean; punctuationOnly?: boolean;
}) {
  const [advanced, setAdvanced] = useState(false);
  function update<K extends keyof CaptionProfile>(key: K, value: CaptionProfile[K]) {
    onCancelPreview(); onDraft({ ...draft, [key]: value });
  }
  return <>
      <div className="preset-row">{[{ label: "Essential", detail: 1, expression: 1 }, { label: "Balanced", detail: 2, expression: 2 }, { label: "Rich", detail: 3, expression: 3 }].map((preset) => <button key={preset.label} className={`preset ${draft.detail === preset.detail && draft.expression === preset.expression ? "selected" : ""}`} onClick={() => { onCancelPreview(); onDraft({ ...draft, detail: preset.detail as Level, expression: conservative ? profile.expression : preset.expression as Level }); }} aria-pressed={draft.detail === preset.detail && draft.expression === preset.expression}>{preset.label}</button>)}</div>
      <div className="preference-section"><label htmlFor="detail">Level of detail <span>{["", "Less", "Balanced", "More"][draft.detail]}</span></label><input id="detail" type="range" min={1} max={3} step={1} value={draft.detail} onChange={(e) => update("detail", Number(e.target.value) as Level)} /><div className="range-labels"><span>Just the sound</span><span>More context</span></div><p className="helper-text">This is your maximum. Adaptation can shorten captions, but never adds more detail.</p></div>
      <div className="preference-section"><label htmlFor="expression">Expressiveness <span>{(punctuationOnly ? ["", "Minimal", "Sentence", "Emphatic"] : ["", "Neutral", "Balanced", "Evocative"])[draft.expression]}</span></label><input id="expression" disabled={conservative} type="range" min={1} max={3} step={1} value={draft.expression} onChange={(e) => update("expression", Number(e.target.value) as Level)} /><div className="range-labels"><span>Factual</span><span>{punctuationOnly ? "Emphatic" : "Evocative"}</span></div>{punctuationOnly && <p className="helper-text">This generated draft changes punctuation only: minimal, sentence, or emphatic. It does not infer emotion or louder sounds.</p>}{conservative && <p className="helper-text">Expressive variants await review. This track uses factual wording at every expression level.</p>}</div>
      <div className="adapt-setting"><div><label htmlFor="adaptive">{densityBased ? "Follow cue density" : "Follow the scene"}</label><p>{densityBased ? "Shorter captions when sound cues cluster. Your detail limit stays in place." : "Shorter captions in busy moments, within your detail limit."}</p>{!sceneTagsReady && <p>Scene tags await review for this track.</p>}</div><input id="adaptive" className="switch" disabled={!sceneTagsReady} type="checkbox" role="switch" checked={sceneTagsReady && draft.adaptive} onChange={(e) => update("adaptive", e.target.checked)} /></div>
      <button className="advanced-toggle" onClick={() => setAdvanced(!advanced)} aria-expanded={advanced} aria-controls="advanced-settings">More preferences <Icon name="chevron" size={15} style={{ transform: advanced ? "rotate(90deg)" : undefined }} /></button>
      {advanced && <div id="advanced-settings" className="advanced-settings"><label htmlFor="representation">Sound representation</label><select id="representation" value={draft.representation} onChange={(e) => update("representation", e.target.value as CaptionProfile["representation"])}><option value="descriptive">Descriptive</option><option value="plain">Plain sound labels</option><option value="onomatopoeic">Onomatopoeia when available</option></select><p className="helper-text">Unavailable sound spellings fall back to descriptive captions.</p></div>}
  </>;
}
