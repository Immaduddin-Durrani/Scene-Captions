"use client";
import { formatTime } from "@/lib/captions";
import { Icon } from "./icon";
import type { useVideoPlayback } from "./hooks/use-video-playback";

export function PlayerControls({ playback, baseline, hasCaptions, showOriginal, onOriginal, generatedBaseline = false }: {
  playback: ReturnType<typeof useVideoPlayback>; baseline: boolean; hasCaptions: boolean;
  showOriginal: boolean; onOriginal: () => void; generatedBaseline?: boolean;
}) {
  const { time, duration, ready, playing, muted, playbackRate, toggle, seek, toggleMute, changeRate, fullscreen } = playback;
  return (
      <div className="video-controls">
        <label className="sr-only" htmlFor="timeline">Seek video</label><input id="timeline" className="timeline" type="range" min={0} max={duration || 1} step={0.1} value={Math.min(time, duration || 1)} disabled={!ready} onChange={(e) => seek(Number(e.target.value))} aria-valuetext={`${formatTime(time)} of ${formatTime(duration)}`} />
        <div className="transport"><button className="icon-button" onClick={() => void toggle()} disabled={!ready} aria-label={playing ? "Pause video" : "Play video"}><Icon name={playing ? "pause" : "play"} /></button><button className="icon-button" onClick={toggleMute} aria-label={muted ? "Unmute video" : "Mute video"}><Icon name={muted ? "mute" : "volume"} /></button><span className="time-code">{formatTime(time)} <span>/ {formatTime(duration)}</span></span><div className="transport-right"><label className="sr-only" htmlFor="speed">Playback speed</label><select id="speed" aria-label="Playback speed" value={playbackRate} onChange={(e) => changeRate(Number(e.target.value))}><option value={0.75}>0.75×</option><option value={1}>1×</option><option value={1.25}>1.25×</option></select><button className="original-video" onClick={onOriginal} disabled={baseline || !hasCaptions} aria-pressed={showOriginal || baseline}>{showOriginal || baseline ? (generatedBaseline ? "Reference on" : "Original on") : (generatedBaseline ? "Show reference" : "Show original")}</button><button className="icon-button" aria-label="Fullscreen player" onClick={() => void fullscreen()}><Icon name="expand" /></button></div></div>
      </div>
  );
}
