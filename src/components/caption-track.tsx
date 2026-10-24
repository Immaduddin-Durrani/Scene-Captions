"use client";
import { activeCues, formatTime, resolveCaption } from "@/lib/captions";
import type { CaptionVideo, CaptionCue, CaptionProfile, Condition } from "@/lib/captions";
import { Icon } from "./icon";

export function CaptionTrackNotice({ data }: { data: CaptionVideo | null }) {
  const captionSource = data?.generated_with.caption_source;
  if (data?.generated_with.non_speech_status === "not-prepared") return <div className="demo-note" role="status"><Icon name="info" size={17} /><p><strong>English dialogue subtitles available.</strong> These are the film’s source dialogue subtitles. A verified sound-caption track has not been prepared for this title, so personalized sound captions are unavailable. Dialogue wording stays fixed. <a href="/research/library-caption-status.md">Caption coverage</a></p></div>;
  return (data?.generated_with.quality_gate === "failed" ? <div className="demo-note" role="status"><Icon name="info" size={17} /><p><strong>Sound captions are unavailable.</strong> Automatic sound-caption generation failed its audio checks. The mismatched sample track has been removed. The film still plays; add corrected caption JSON for your own video below. <a href="/research/caption-generation-status.md">Generation report</a></p></div> : data?.generated_with.kind === "sourced" && captionSource ? <div className="demo-note"><Icon name="info" size={17} /><p><strong>Sourced sound captions.</strong> Timed captions from <a href={captionSource.url} target="_blank" rel="noreferrer">{captionSource.author}</a> · {captionSource.license}. Personalized wording is based on those captions. Adaptation follows cue density. This demo still needs a full review before a participant study.</p></div> : data?.annotation_status === "draft" && <div className="demo-note"><Icon name="info" size={17} /><p><strong>{data.generated_with.kind?.startsWith("audio") ? "AI-generated draft captions." : "Draft captions."}</strong> {data.generated_with.kind?.startsWith("audio") ? "Generated offline from this film’s actual audio. Sound descriptions and estimated timings still need listening review before research use." : "Sound descriptions and timestamps need review before research use."} Your team’s own video and verified captions will replace this sample.</p></div>);
}

function cueLabel(cue: CaptionCue, data: CaptionVideo | null) {
  if (cue.scene_load_basis === "cue-density") return { dense: "Clustered sound cues", quiet: "Sparse sound cues", balanced: "Moderate cue density" }[cue.scene_load];
  if (data?.generated_with.scene_load_method === "unreviewed") return "Scene tags unreviewed";
  return { dense: "Busy moment", quiet: "Quiet moment", balanced: "Steady moment" }[cue.scene_load];
}

export function SoundTimeline({ data, time, profile, condition, showOriginal, jump }: {
  data: CaptionVideo | null; time: number; profile: CaptionProfile; condition: Condition;
  showOriginal: boolean; jump: (seconds: number) => void;
}) {
  if (!data?.cues.length && data?.dialogue?.length) return <section className="sound-timeline card" aria-labelledby="dialogue-title"><div className="section-title"><div><span className="eyebrow">FOLLOW THE DIALOGUE</span><h2 id="dialogue-title">Dialogue transcript</h2></div><span className="muted-text">{data.dialogue.length} subtitle cues</span></div><p className="section-description">Jump to a line. These source subtitles stay the same at every sound preference.</p><div className="cue-list">{data.dialogue.map(cue => <button key={cue.cue_id} className={`cue-row dialogue-row ${cue.start_s <= time && time < cue.end_s ? "current" : ""}`} onClick={() => jump(cue.start_s)} aria-label={`Jump to ${formatTime(cue.start_s)}: ${cue.text}`} aria-current={cue.start_s <= time && time < cue.end_s ? "true" : undefined}><span className="cue-time">{formatTime(cue.start_s)}</span><span className="cue-copy"><strong>{cue.text}</strong><small>English dialogue</small></span><Icon name="play" size={15} /></button>)}</div></section>;
  const activeIds = new Set(data ? activeCues(data.cues, time).map(cue => cue.cue_id) : []);
  return (
<section className="sound-timeline card" aria-labelledby="sounds-title"><div className="section-title"><div><span className="eyebrow">FOLLOW THE SOUNDS</span><h2 id="sounds-title">A moment in the story</h2></div><span className="muted-text">{data?.cues.length || 0} sound cues</span></div><p className="section-description">Jump to a sound to compare how its caption changes.</p><div className="cue-list">{data?.cues.map((cue) => <button key={cue.cue_id} className={`cue-row ${activeIds.has(cue.cue_id) ? "current" : ""}`} onClick={() => jump(cue.start_s)} aria-label={`Jump to ${formatTime(cue.start_s)}: ${cue.original_text}`} aria-current={activeIds.has(cue.cue_id) ? "true" : undefined}><span className="cue-time">{formatTime(cue.start_s)}</span><span className="cue-icon"><Icon name="sound" size={17} /></span><span className="cue-copy"><strong>{resolveCaption(cue, profile, condition, showOriginal).text}</strong><small>{cueLabel(cue, data)}</small></span><Icon name="play" size={15} /></button>)}{!data?.cues.length && <p className="empty-state">No approved sound cues. Add corrected caption JSON to build your sound timeline.</p>}</div></section>
  );
}
