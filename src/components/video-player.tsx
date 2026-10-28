"use client";
import { useVideoPlayback } from "./hooks/use-video-playback";
import { PlayerControls } from "./player-controls";
import { CaptionOverlay, CaptionFeedback, useCaptionDisplay } from "./caption-display";
import type { CaptionProfile, CaptionVideo, Condition } from "@/lib/captions";
import type { StudyEvent } from "@/lib/session";
import { Icon } from "./icon";

export function VideoPlayer({ source, data, profile, condition, showOriginal, onOriginal, onTime, onEvent, seekTo, previewProfile, onPreviewEnd, poster = "/media/bunny-poster.jpg" }: {
  source: string; data: CaptionVideo | null; profile: CaptionProfile; condition: Condition;
  showOriginal: boolean; onOriginal: () => void; onTime: (time: number) => void;
  onEvent: (event: StudyEvent) => void; seekTo: { seconds: number; nonce: number } | null;
  previewProfile: CaptionProfile | null; onPreviewEnd: () => void;
  poster?: string;
}) {
  const playback = useVideoPlayback({ source, seekTo, previewProfile, onPreviewEnd, onTime, onEvent });
  const { video, frame, ready, playing, error, waiting, duration, time, toggle } = playback;
  const display = useCaptionDisplay(data, duration, time, previewProfile || profile, condition, showOriginal);
  return <>
    <div className="video-frame" ref={frame}>
      <video ref={video} src={source} poster={source.startsWith("blob:") ? undefined : poster} preload="metadata" playsInline
        aria-label={`${data?.title || "Your video"} video player`} aria-describedby="video-description" tabIndex={0}
        {...playback.events} />
      <div className="video-topline"><span className="screen-label"><span className="live-dot" />{data?.generated_with.experimental ? (showOriginal ? "Experimental · fixed draft" : "Experimental · media-only AI") : condition === "baseline" || showOriginal ? (data?.generated_with.kind === "source-assisted" ? "Fetched reference captions" : "Original captions") : "Your caption experience"}</span><span className="video-quality">{data?.annotation_status === "draft" ? "DEMO" : "LOCAL VIDEO"}</span></div>
      {!playing && !error && <button className="big-play" onClick={() => void toggle()} disabled={!ready} aria-label={ready ? "Play video" : "Loading video"}><Icon name="play" size={30} /></button>}
      {waiting && playing && <span className="buffering" role="status">Buffering video…</span>}
      <CaptionOverlay active={display.active} cues={display.cues} profile={profile} dialogue={display.mismatch ? [] : data?.dialogue?.filter(cue => cue.start_s <= time && time < cue.end_s)} />
      <PlayerControls playback={playback} baseline={condition === "baseline"} hasCaptions={!!data?.cues.length} showOriginal={showOriginal} onOriginal={onOriginal} generatedBaseline={data?.generated_with.kind === "source-assisted"} experimental={data?.generated_with.experimental} />
    </div>
    {previewProfile && <div className="caption-preview-notice" role="status"><span>Preview only · your saved settings have not changed.</span><button className="text-button" onClick={onPreviewEnd}>Return to saved settings</button></div>}
    {error && <p role="alert" className="inline-error">{error}</p>}
    {display.mismatch && <p role="alert" className="inline-error">Caption timing does not match this video’s duration. Captions are hidden. Import JSON for this exact video edit.</p>}
    {!data && <p className="inline-notice">Your video is open. Add its caption JSON below to enable non-speech captions.</p>}
    <CaptionFeedback data={data} display={display} condition={condition} showOriginal={showOriginal} />
    <p id="video-description" className="sr-only">Available dialogue and non-speech captions are displayed on the video. {data?.generated_with.experimental ? "Experimental dialogue is transcribed from audio; words and timing are unverified." : "Dialogue keeps its source wording regardless of sound preferences."} Focus the video and press Space to play or pause; use Left and Right arrows to seek five seconds. Full sound text and jump controls are available in the timeline below.</p>
  </>;
}
