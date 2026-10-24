"use client";
import { useRef } from "react";
import { Icon } from "./icon";

export function MediaImport({ locked, localName, importError, onVideo, onAnnotations, onRestore }: {
  locked: boolean; localName: string; importError: string;
  onVideo: (file: File) => void; onAnnotations: (file: File) => void; onRestore: () => void;
}) {
  const localVideoInput = useRef<HTMLInputElement>(null);
  const annotationInput = useRef<HTMLInputElement>(null);
  return (
    <section id="your-video" className="own-video card" aria-labelledby="own-title"><div className="section-title"><div><span className="eyebrow">MADE FOR YOUR PROJECT</span><h2 id="own-title">Bring your own story.</h2><p>Open the video your team creates, then add its precomputed captions.</p></div><Icon name="film" size={32} /></div><div className="import-steps"><div><span className="step-number">01</span><div><h3>Open your video</h3><p>{localName || "Choose a browser-compatible MP4. It stays on your device."}</p><input ref={localVideoInput} className="sr-only" type="file" accept="video/mp4,video/webm,video/quicktime" aria-label="Choose local video" disabled={locked} onChange={(e) => { const file = e.target.files?.[0]; if (!file) return; onVideo(file); e.target.value = ""; }} /><button className="secondary-button" disabled={locked} onClick={() => localVideoInput.current?.click()}><Icon name="folder" size={16} />Choose video</button></div></div><div><span className="step-number">02</span><div><h3>Add matching captions</h3><p>Import the nine caption variants per sound cue as JSON.</p><input ref={annotationInput} className="sr-only" type="file" accept=".json,application/json" aria-label="Choose caption JSON" disabled={locked || !localName} onChange={(e) => { const file = e.target.files?.[0]; if (file) onAnnotations(file); e.target.value = ""; }} /><button className="secondary-button" disabled={locked || !localName} onClick={() => annotationInput.current?.click()}><Icon name="download" size={16} />Choose caption JSON</button></div></div></div>{locked && <p className="helper-text">Video and caption files stay fixed after a rehearsal starts. Reload the page to begin a different rehearsal; export first to keep its data.</p>}{importError && <p className="inline-error" role="alert">{importError}</p>}<div className="import-footer"><a href="/research/caption-template.json" download>Download caption JSON template <Icon name="download" size={14} /></a><button className="text-button" disabled={locked} onClick={onRestore}>Restore sample film</button></div></section>
  );
}
