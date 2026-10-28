"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { DEFAULT_PROFILE, activeCues, profileSchema } from "@/lib/captions";
import type { CaptionVideo, CaptionProfile, Condition } from "@/lib/captions";
import { useLocalMedia } from "./hooks/use-local-media";
import { useRehearsal } from "./hooks/use-rehearsal";
import { MediaImport } from "./media-import";
import { CaptionTrackNotice, SoundTimeline } from "./caption-track";
import { VideoPlayer } from "./video-player";
import { Preferences } from "./preferences";
import { StudyRehearsal } from "./study-rehearsal";
import { Icon } from "./icon";

const PROFILE_KEY = "scenecaptions.profile.v1";
export function Workspace({ initialVideo, experimentalVideo, sourceAssistedVideo, demoSource, demoPoster = "/media/bunny-poster.jpg", demoCredit = "Blender Foundation · 2008", onMediaLockChange }: { initialVideo: CaptionVideo; experimentalVideo?: CaptionVideo; sourceAssistedVideo?: CaptionVideo; demoSource: string; demoPoster?: string; demoCredit?: string; onMediaLockChange?: (locked: boolean) => void }) {
  const [profile, setProfile] = useState<CaptionProfile>(DEFAULT_PROFILE);
  const [condition, setCondition] = useState<Condition>("personalized"); const [showOriginal, setShowOriginal] = useState(false);
  const [previewProfile, setPreviewProfile] = useState<CaptionProfile | null>(null);
  const [time, setTime] = useState(0); const [seekTo, setSeekTo] = useState<{ seconds: number; nonce: number } | null>(null);
  const [notice, setNotice] = useState("");
  const media = useLocalMedia(initialVideo, demoSource, setNotice);
  const { data, source, localName, importError } = media;
  const rehearsal = useRehearsal();
  const { recording, events, startedAt, sessionId, stoppedElapsed, record } = rehearsal;
  const currentTime = useRef(0); const seekNonce = useRef(0);
  useEffect(() => { onMediaLockChange?.(startedAt !== null); }, [startedAt, onMediaLockChange]);
  const updateTime = useCallback((seconds: number) => { currentTime.current = seconds; setTime(seconds); }, []);
  useEffect(() => { setPreviewProfile(null); }, [source, data]);
  useEffect(() => {
    try { const value = localStorage.getItem(PROFILE_KEY); if (value) { const parsed = profileSchema.safeParse(JSON.parse(value)); if (parsed.success) setProfile(parsed.data); } }
    catch { setNotice("Browser storage is unavailable. Preferences still work for this visit."); }
  }, []);
  const endPreview = useCallback(() => { setPreviewProfile(null); record({ type: "preview_end", video_s: currentTime.current }); }, [record]);
  function apply(next: CaptionProfile) { if (previewProfile) endPreview(); setProfile(next); record({ type: "profile", video_s: time, profile: next }); try { localStorage.setItem(PROFILE_KEY, JSON.stringify(next)); setNotice("Caption preferences applied and saved in this browser."); } catch { setNotice("Preferences applied for this visit. Browser storage is unavailable."); } }
  function original() { if (previewProfile) endPreview(); const enabled = !showOriginal; setShowOriginal(enabled); record({ type: "original", video_s: time, enabled }); }
  function changeCondition(next: Condition) { if (previewProfile) endPreview(); setCondition(next); setShowOriginal(false); record({ type: "condition", video_s: time, condition: next }); record({ type: "original", video_s: time, enabled: false }); }
  function jump(seconds: number) { if (previewProfile) endPreview(); setSeekTo({ seconds, nonce: ++seekNonce.current }); }
  function sample() {
    if (startedAt !== null) return;
    setPreviewProfile(null); media.restore(); setTime(0);
  }
  const captionSource = data?.generated_with.caption_source;
  const experimental = !!data?.generated_with.experimental;
  const enriched = !!data?.generated_with.wording_style;
  function selectTrack(track: CaptionVideo) {
    if (startedAt !== null) return;
    if (previewProfile) endPreview();
    changeCondition("personalized");
    media.selectPreparedTrack(track);
  }
  const previewCue = data && (activeCues(data.cues, time)[0] || data.cues.find((cue) => cue.start_s >= time) || data.cues[0]);
  const viewerProfile = data?.generated_with.scene_load_method === "unreviewed" ? { ...profile, adaptive: false } : profile;
  return <main id="main" className="workspace">
    <div className="page-intro"><div><div className="eyebrow"><span className="small-line" />YOUR SOUND. YOUR WAY.</div><h1>Stay in the story.</h1><p>Sound captions that make room for the way you watch.</p></div><a className="quiet-link" href="#your-video"><Icon name="folder" size={17} />Use your own video <Icon name="arrow" size={16} /></a></div>
    <div className="watch-layout"><section className="watch-column" aria-label="Video workspace"><div className="watch-heading"><div><span className="film-kicker">{localName ? "YOUR VIDEO" : "THE DEMO SCREENING"}</span><h2>{data?.title || localName || "Your video"}<span>{localName ? "Local file" : demoCredit}</span></h2></div>{!experimental && <div className="condition-switch" role="group" aria-label="Caption condition"><button aria-pressed={condition === "personalized" && !showOriginal} onClick={() => changeCondition("personalized")}>Personalized</button><button aria-pressed={condition === "baseline" || showOriginal} onClick={() => changeCondition("baseline")}>{data?.generated_with.kind === "source-assisted" ? "Reference baseline" : "Original baseline"}</button></div>}</div>
      {(experimentalVideo || sourceAssistedVideo) && !localName && <section className="caption-track-picker" aria-label="Subtitle source"><div><strong>Subtitle source</strong><p id="media-only-description">{sourceAssistedVideo ? "Source-guided captions use existing sound references and simple words. " : ""}Media-only AI uses audio without existing subtitles; its accuracy is unverified.</p></div><div className="caption-track-actions" role="group" aria-label="Choose subtitle source"><button className="secondary-button" aria-pressed={!experimental && !enriched} disabled={startedAt !== null} onClick={() => selectTrack(initialVideo)}>Use existing captions</button>{sourceAssistedVideo && <button className="secondary-button" aria-pressed={enriched} disabled={startedAt !== null} onClick={() => selectTrack(sourceAssistedVideo)}>Use source-guided captions</button>}{experimentalVideo && <button className="secondary-button" aria-pressed={experimental} aria-describedby="media-only-description" disabled={startedAt !== null} onClick={() => selectTrack(experimentalVideo)}>Use media-only AI subtitles</button>}</div>{startedAt !== null && <p>Subtitle source stays fixed after a rehearsal starts. Export, then reload to switch.</p>}</section>}
      <VideoPlayer poster={demoPoster} source={source} data={data} profile={viewerProfile} condition={condition} showOriginal={showOriginal} onOriginal={original} onTime={updateTime} onEvent={record} seekTo={seekTo} previewProfile={previewProfile} onPreviewEnd={endPreview} />
      <div className="film-footnote"><Icon name="leaf" size={16} /><span>{localName ? "Your video stays on this device. Nothing is uploaded." : `${initialVideo.title} · ${initialVideo.license} · ${demoCredit}`}</span><a href="#media-credits">{localName ? "Local playback" : "Credits & demo notes"}</a></div>
      <CaptionTrackNotice data={data} />
      <SoundTimeline data={data} time={time} profile={profile} condition={condition} showOriginal={showOriginal} jump={jump} />
    </section><Preferences key={`${data?.video_id || "empty"}-${condition}-${experimental}-${enriched}`} profile={profile} onApply={apply} conservative={data?.generated_with.expressiveness === "conservative"} sceneTagsReady={data?.generated_with.scene_load_method !== "unreviewed"} sample={previewCue || undefined} disabled={condition === "baseline"} unavailable={!data?.cues.length} densityBased={data?.generated_with.scene_load_method === "cue-density"} punctuationOnly={data?.generated_with.expression_method === "punctuation-only"} previewing={!!previewProfile} originalActive={showOriginal} onCancelPreview={() => { if (previewProfile) endPreview(); }} onPreview={(candidate) => { if (previewCue && !showOriginal) { setPreviewProfile({ ...candidate }); setSeekTo({ seconds: (previewCue.start_s + previewCue.end_s) / 2, nonce: ++seekNonce.current }); record({ type: "preview", video_s: time, profile: candidate, cue_id: previewCue.cue_id }); } }} /></div>
    <MediaImport locked={startedAt !== null} localName={localName} importError={importError} onVideo={(file) => { setPreviewProfile(null); media.openVideo(file); setTime(0); }} onAnnotations={(file) => { setPreviewProfile(null); void media.importAnnotations(file); }} onRestore={sample} />
    <StudyRehearsal active={recording} events={events} onStart={() => { setPreviewProfile(null); rehearsal.start(time, condition, profile, showOriginal); }} onStop={() => { rehearsal.stop(); setNotice("Rehearsal recording stopped. Export your data before reloading."); }} data={data?.cues.length ? data : null} condition={condition} profile={profile} showOriginal={showOriginal} stoppedElapsed={stoppedElapsed} startedAt={startedAt} sessionId={sessionId} />
    <footer id="media-credits" className="page-footer"><div><span className="footer-brand">SceneCaptions</span><p>More of the story. On your terms.</p></div><div><p>Research prototype · No AI calls during viewing</p><p>Demo film: <a href={initialVideo.source_url} target="_blank" rel="noreferrer">{initialVideo.title}, Blender Foundation</a> · <a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noreferrer">CC BY 3.0</a><br />{captionSource ? <>{data?.generated_with.kind === "source-assisted" ? "Generation reference: " : "Sound captions: "}<a href={captionSource.url} target="_blank" rel="noreferrer">{captionSource.author}</a> · {captionSource.license}. {data?.generated_with.kind === "source-assisted" ? "New wording generated and edited by SceneCaptions." : "Wording variants added by SceneCaptions."}</> : <>See the caption coverage above for this title.</>}</p>{data?.dialogue_source && <p>English subtitles: <a href={data.dialogue_source.url} target="_blank" rel="noreferrer">{data.dialogue_source.author}</a> · {data.dialogue_source.license}. Source wording and timing retained.</p>}</div></footer>
    <div className="sr-only" role="status" aria-live="polite">{notice}</div>
  </main>;
}
