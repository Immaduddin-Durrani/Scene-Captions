"use client";
import { useEffect, useRef, useState } from "react";
import { videoSchema } from "@/lib/captions";
import type { CaptionVideo } from "@/lib/captions";

export function useLocalMedia(initialVideo: CaptionVideo, demoSource: string, notify: (text: string) => void) {
  const [data, setData] = useState<CaptionVideo | null>(initialVideo);
  const [source, setSource] = useState(demoSource);
  const [localName, setLocalName] = useState("");
  const [importError, setImportError] = useState("");
  const blob = useRef<string | null>(null);
  function release() {
    if (blob.current) URL.revokeObjectURL(blob.current);
    blob.current = null;
  }
  useEffect(() => release, []);
  function openVideo(file: File) {
    release();
    blob.current = URL.createObjectURL(file);
    setSource(blob.current); setLocalName(file.name); setData(null); setImportError("");
    notify("Your video is open. Add the matching caption JSON next.");
  }
  function restore() {
    release(); setSource(demoSource); setLocalName(""); setData(initialVideo); setImportError("");
    notify("Sample film and its saved caption track restored.");
  }
  function selectPreparedTrack(track: CaptionVideo) {
    if (localName || source !== demoSource || track.video_id !== initialVideo.video_id) return;
    setData(track); setImportError("");
    notify(track.generated_with.experimental ? "Experimental media-only subtitles selected. Sound recognition and timing are unverified." : track.generated_with.wording_style ? "Simple source-guided captions selected. Sound events and timing follow the credited reference." : "Existing caption track restored.");
  }
  async function importAnnotations(file: File) {
    setImportError("");
    if (file.size > 5 * 1024 * 1024) { setImportError("Choose a caption JSON file smaller than 5 MB."); return; }
    let content: unknown;
    try { content = JSON.parse(await file.text()); }
    catch { setImportError("This file is not valid JSON. Export the caption data as JSON and try again."); return; }
    const parsed = videoSchema.safeParse(content);
    if (!parsed.success) {
      setImportError(`Caption file needs correction: ${parsed.error.issues[0]?.message || "invalid schema"}. See the import guide in docs.`);
      return;
    }
    setData(parsed.data);
    notify(`Loaded ${parsed.data.cues.length} caption cues for ${parsed.data.title}. Confirm they match this exact video edit.`);
  }
  return { data, source, localName, importError, openVideo, restore, selectPreparedTrack, importAnnotations };
}
