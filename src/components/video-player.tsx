"use client";
import { useEffect, useRef, useState } from "react";
import { activeCues, formatTime, resolveCaption } from "@/lib/captions";
import type { CaptionProfile, CaptionVideo, Condition } from "@/lib/captions";
import type { StudyEvent } from "@/lib/session";
import { Icon } from "./icon";

export function VideoPlayer({ source, data, profile, condition, showOriginal, onOriginal, onTime, onEvent, seekTo, previewProfile, onPreviewEnd }: {
  source: string; data: CaptionVideo | null; profile: CaptionProfile; condition: Condition;
  showOriginal: boolean; onOriginal: () => void; onTime: (time: number) => void;
  onEvent: (event: StudyEvent) => void; seekTo: { seconds: number; nonce: number } | null;
  previewProfile: CaptionProfile | null; onPreviewEnd: () => void;
}) {
  const video = useRef<HTMLVideoElement>(null); const frame = useRef<HTMLDivElement>(null);
  const [time, setTime] = useState(0); const [duration, setDuration] = useState(0);
  const [playing, setPlaying] = useState(false); const [muted, setMuted] = useState(false);
  const [error, setError] = useState(""); const [ready, setReady] = useState(false); const [waiting, setWaiting] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1); const [why, setWhy] = useState(false);
  const mismatch = !!data && duration > 0 && Math.abs(duration - data.duration_seconds) > 2;
  const cues = data && !mismatch ? activeCues(data.cues, time) : [];
  const nextCue = data && !mismatch ? data.cues.find((cue) => cue.start_s > time) : undefined;
  const active = cues.map((cue) => resolveCaption(cue, previewProfile || profile, condition, showOriginal));
  useEffect(() => {
    // Metadata may arrive before hydration effects run for a cached local file.
    const el = video.current;
    const loaded = !!el && el.readyState >= 1 && Number.isFinite(el.duration);
    setTime(el?.currentTime || 0); setDuration(loaded ? el.duration : 0);
    setReady(loaded); setPlaying(el ? !el.paused : false); setWaiting(false);
    setError(""); setPlaybackRate(1); setMuted(el?.muted || false);
  }, [source]);
  useEffect(() => { if (seekTo && video.current && ready) video.current.currentTime = Math.min(seekTo.seconds, duration); }, [seekTo, ready, duration]);
  useEffect(() => {
    if (!previewProfile || !ready) return;
    video.current?.pause();
    const timer = window.setTimeout(onPreviewEnd, 5000);
    return () => window.clearTimeout(timer);
  }, [previewProfile, ready, onPreviewEnd]);
  async function toggle() {
    const el = video.current; if (!el) return;
    if (previewProfile) onPreviewEnd();
    if (!el.paused) { el.pause(); return; }
    try { await el.play(); setError(""); } catch { setError("Playback could not start. Choose a compatible MP4 video or try again."); }
  }
  function seek(seconds: number) { if (previewProfile) onPreviewEnd(); if (video.current) video.current.currentTime = Math.min(duration, Math.max(0, seconds)); }
  return <>
    <div className="video-frame" ref={frame}>
      <video ref={video} src={source} poster={source.startsWith("blob:") ? undefined : "/media/bunny-poster.jpg"} preload="metadata" playsInline
        aria-label={`${data?.title || "Your video"} video player`} aria-describedby="video-description" tabIndex={0}
        onLoadedMetadata={() => { if (video.current) { setDuration(video.current.duration); setReady(true); setError(""); } }}
        onTimeUpdate={() => { if (video.current) { setTime(video.current.currentTime); onTime(video.current.currentTime); } }}
        onPlay={() => { setPlaying(true); onEvent({ type: "play", video_s: video.current?.currentTime || 0 }); }}
        onPause={() => { setPlaying(false); onEvent({ type: "pause", video_s: video.current?.currentTime || 0 }); }}
        onSeeked={() => { setTime(video.current?.currentTime || 0); onTime(video.current?.currentTime || 0); onEvent({ type: "seek", video_s: video.current?.currentTime || 0 }); }}
        onWaiting={() => setWaiting(true)} onCanPlay={() => setWaiting(false)}
        onError={() => setError("The video could not load. Run npm run setup:demo for the sample, or open your own MP4 below.")}
        onKeyDown={(event) => {
          if (event.key === "Escape" && previewProfile) { event.preventDefault(); onPreviewEnd(); }
          if (event.key === " " || event.key === "k") { event.preventDefault(); void toggle(); }
          if (event.key === "ArrowRight") { event.preventDefault(); seek((video.current?.currentTime || 0) + 5); }
          if (event.key === "ArrowLeft") { event.preventDefault(); seek((video.current?.currentTime || 0) - 5); }
        }} />
      <div className="video-topline"><span className="screen-label"><span className="live-dot" />{condition === "baseline" ? "Original captions" : "Your caption experience"}</span><span className="video-quality">{data?.annotation_status === "draft" ? "DEMO" : "LOCAL VIDEO"}</span></div>
      {!playing && !error && <button className="big-play" onClick={() => void toggle()} disabled={!ready} aria-label={ready ? "Play video" : "Loading video"}><Icon name="play" size={30} /></button>}
      {waiting && playing && <span className="buffering" role="status">Buffering video…</span>}
      {active.length > 0 && <div className={`caption-overlay ${profile.position} ${profile.size}`} aria-label="Non-speech captions"><div className="caption-lines">{active.map((caption, index) => <p key={cues[index].cue_id}>{caption.text}</p>)}</div></div>}
      <div className="video-controls">
        <label className="sr-only" htmlFor="timeline">Seek video</label><input id="timeline" className="timeline" type="range" min={0} max={duration || 1} step={0.1} value={Math.min(time, duration || 1)} disabled={!ready} onChange={(e) => seek(Number(e.target.value))} aria-valuetext={`${formatTime(time)} of ${formatTime(duration)}`} />
        <div className="transport"><button className="icon-button" onClick={() => void toggle()} disabled={!ready} aria-label={playing ? "Pause video" : "Play video"}><Icon name={playing ? "pause" : "play"} /></button><button className="icon-button" onClick={() => { if (video.current) { video.current.muted = !muted; setMuted(!muted); } }} aria-label={muted ? "Unmute video" : "Mute video"}><Icon name={muted ? "mute" : "volume"} /></button><span className="time-code">{formatTime(time)} <span>/ {formatTime(duration)}</span></span><div className="transport-right"><label className="sr-only" htmlFor="speed">Playback speed</label><select id="speed" aria-label="Playback speed" value={playbackRate} onChange={(e) => { const value = Number(e.target.value); setPlaybackRate(value); if (video.current) video.current.playbackRate = value; }}><option value={0.75}>0.75×</option><option value={1}>1×</option><option value={1.25}>1.25×</option></select><button className="original-video" onClick={onOriginal} disabled={condition === "baseline" || !data?.cues.length} aria-pressed={showOriginal || condition === "baseline"}>{showOriginal || condition === "baseline" ? "Original on" : "Show original"}</button><button className="icon-button" aria-label="Fullscreen player" onClick={() => { if (document.fullscreenElement) void document.exitFullscreen().catch(() => setError("Fullscreen is unavailable in this browser.")); else void frame.current?.requestFullscreen().catch(() => setError("Fullscreen is unavailable in this browser.")); }}><Icon name="expand" /></button></div></div>
      </div>
    </div>
    {previewProfile && <div className="caption-preview-notice" role="status"><span>Preview only · your saved settings have not changed.</span><button className="text-button" onClick={onPreviewEnd}>Return to saved settings</button></div>}
    {error && <p role="alert" className="inline-error">{error}</p>}
    {mismatch && <p role="alert" className="inline-error">Caption timing does not match this video’s duration. Captions are hidden. Import JSON for this exact video edit.</p>}
    {!data && <p className="inline-notice">Your video is open. Add its caption JSON below to enable non-speech captions.</p>}
    <div className="caption-status"><span><Icon name="sound" size={17} />{active.length ? active.some((c) => c.adapted) ? cues.some((cue) => cue.scene_load_basis === "cue-density") ? "Adapted to sound-cue density" : "Adapted to this scene" : showOriginal || condition === "baseline" ? "Showing original captions" : "Using your preferences" : data?.cues.length ? nextCue ? `Next sound caption at ${formatTime(nextCue.start_s)}` : "No more sound captions in this track" : "No sound-caption track available"}</span><button className="text-button" onClick={() => setWhy(!why)} aria-expanded={why}><Icon name="info" size={16} />Why this caption?</button></div>
    {why && <div className="explanation"><strong>{active[0]?.reason || "Sound captions follow the video timeline."}</strong><p>{cues[0]?.scene_context || "When a cue is active, this panel explains the caption selection. You can turn scene adaptation off or show the original at any time."}</p></div>}
    <p id="video-description" className="sr-only">Non-speech captions are displayed on the video. Focus the video and press Space to play or pause; use Left and Right arrows to seek five seconds. Full text and jump controls are available in the sound timeline below.</p>
  </>;
}
