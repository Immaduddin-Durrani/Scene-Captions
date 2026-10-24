"use client";
import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import type { CaptionProfile } from "@/lib/captions";
import type { StudyEvent } from "@/lib/session";

export function useVideoPlayback({ source, seekTo, previewProfile, onPreviewEnd, onTime, onEvent }: {
  source: string; seekTo: { seconds: number; nonce: number } | null;
  previewProfile: CaptionProfile | null; onPreviewEnd: () => void;
  onTime: (seconds: number) => void; onEvent: (event: StudyEvent) => void;
}) {
  const video = useRef<HTMLVideoElement>(null); const frame = useRef<HTMLDivElement>(null);
  const [time, setTime] = useState(0); const [duration, setDuration] = useState(0);
  const [playing, setPlaying] = useState(false); const [muted, setMuted] = useState(false);
  const [error, setError] = useState(""); const [ready, setReady] = useState(false); const [waiting, setWaiting] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  useEffect(() => {
    // Metadata may arrive before hydration effects run for a cached local file.
    const el = video.current;
    const loaded = !!el && el.readyState >= 1 && Number.isFinite(el.duration);
    setTime(el?.currentTime || 0); setDuration(loaded ? el.duration : 0);
    setReady(loaded); setPlaying(el ? !el.paused : false); setWaiting(false);
    setError(""); setPlaybackRate(1); setMuted(el?.muted || false);
  }, [source]);
  useEffect(() => {
    if (seekTo && video.current && ready) {
      const target = Math.min(duration, Math.max(0, seekTo.seconds));
      video.current.currentTime = target;
      setTime(target);
      onTime(target);
    }
  }, [seekTo, ready, duration, onTime]);
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
  function seek(seconds: number) {
    if (previewProfile) onPreviewEnd();
    if (video.current) {
      const target = Math.min(duration, Math.max(0, seconds));
      video.current.currentTime = target;
      // Keep the controlled slider current during the render that ends a preview.
      // Waiting for seeked can restore its old value before the next input event.
      setTime(target);
      onTime(target);
    }
  }

  const events = {
    onLoadedMetadata() { if (video.current) { setDuration(video.current.duration); setReady(true); setError(""); } },
    onTimeUpdate() { if (video.current) { setTime(video.current.currentTime); onTime(video.current.currentTime); } },
    onPlay() { setPlaying(true); onEvent({ type: "play", video_s: video.current?.currentTime || 0 }); },
    onPause() { setPlaying(false); onEvent({ type: "pause", video_s: video.current?.currentTime || 0 }); },
    onSeeked() { const seconds = video.current?.currentTime || 0; setTime(seconds); onTime(seconds); onEvent({ type: "seek", video_s: seconds }); },
    onWaiting() { setWaiting(true); },
    onCanPlay() { setWaiting(false); },
    onError() { setError("The video could not load. Run npm run setup:demo for the sample, or open your own MP4 below."); },
    onKeyDown(event: KeyboardEvent<HTMLVideoElement>) {
      if (event.key === "Escape" && previewProfile) { event.preventDefault(); onPreviewEnd(); }
      if (event.key === " " || event.key === "k") { event.preventDefault(); void toggle(); }
      if (event.key === "ArrowRight") { event.preventDefault(); seek((video.current?.currentTime || 0) + 5); }
      if (event.key === "ArrowLeft") { event.preventDefault(); seek((video.current?.currentTime || 0) - 5); }
    },
  };
  function toggleMute() { if (video.current) { video.current.muted = !muted; setMuted(!muted); } }
  function changeRate(value: number) { setPlaybackRate(value); if (video.current) video.current.playbackRate = value; }
  async function fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await frame.current?.requestFullscreen();
    } catch { setError("Fullscreen is unavailable in this browser."); }
  }
  return { video, frame, time, duration, playing, muted, error, ready, waiting, playbackRate, events, toggle, seek, toggleMute, changeRate, fullscreen };
}
