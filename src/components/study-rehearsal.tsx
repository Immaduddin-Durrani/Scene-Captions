"use client";
import { useState } from "react";
import { RehearsalRatings } from "./rehearsal-ratings";
import { rehearsalSnapshot } from "@/lib/session";
import type { RecordedEvent } from "@/lib/session";
import type { CaptionProfile, CaptionVideo, Condition } from "@/lib/captions";
import { Icon } from "./icon";
type RehearsalProps = { active: boolean; events: RecordedEvent[]; onStart: () => void; onStop: () => void; data: CaptionVideo | null; condition: Condition; profile: CaptionProfile; startedAt: number | null; sessionId: string; showOriginal: boolean; stoppedElapsed: number | null };

export function StudyRehearsal(props: RehearsalProps) {
  const { active, data, onStart, startedAt } = props;
  const [consent, setConsent] = useState(false);
  return <section className="rehearsal card" aria-labelledby="rehearsal-title"><div className="section-title"><div><span className="eyebrow">PREPARE FOR THE STUDY</span><h2 id="rehearsal-title">Try a study session</h2><p>Check the flow before inviting participants.</p></div><span className={`status-pill ${active ? "recording" : ""}`}>{active ? "Recording locally" : "Recording off"}</span></div>
    <p className="rehearsal-warning">Rehearsal only. This is not formal research consent or an approved participant study. Events stay in this page’s memory; leaving this page or reloading clears them.</p>
    {startedAt === null && <><label className="consent"><input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />I agree to record this demo’s player interactions locally.</label><button className="primary-button" disabled={!consent || !data} onClick={onStart}>Start rehearsal <Icon name="arrow" size={17} /></button>{!data && <p>Add caption data before starting a rehearsal.</p>}</>}
    {startedAt !== null && <RehearsalSession {...props} />}
  </section>;
}

function RehearsalSession({ active, events, onStart, onStop, data, condition, profile, startedAt, sessionId, showOriginal, stoppedElapsed }: RehearsalProps) {
  const [ratings, setRatings] = useState<Record<string, number>>({}); const [note, setNote] = useState(""); const [message, setMessage] = useState("");
  function download() {
    const payload = rehearsalSnapshot({ data, condition, profile, showOriginal, startedAt, stoppedElapsed, sessionId, events, ratings, note }, performance.now());
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })); const a = document.createElement("a"); a.href = url; a.download = `scenecaptions-rehearsal-${sessionId}.json`; a.click(); URL.revokeObjectURL(url); setMessage("Rehearsal exported to your downloads. It has not been uploaded.");
  }
  return <>
    <><div className="session-line"><span>Session <strong>{sessionId}</strong></span><span>{events.length} events recorded{events.length >= 3000 ? " · limit reached; export this session" : ""}</span></div><RehearsalRatings ratings={ratings} onRate={(key, value) => setRatings({ ...ratings, [key]: value })} /><label htmlFor="study-note" className="field-label">What felt clear or confusing? <span>(optional)</span></label><textarea id="study-note" value={note} maxLength={2000} onChange={(e) => setNote(e.target.value)} placeholder="Do not enter names or contact information…" rows={3} /><div className="session-actions">{active && <button className="secondary-button" onClick={onStop}>Stop recording</button>}<button className="primary-button" onClick={download}><Icon name="download" size={17} />Export rehearsal JSON</button></div><p className="helper-text">Unanswered ratings remain missing. These are custom, exploratory questions, not a validated workload scale.</p></>
    {message && <p role="status" className="success-message">{message}</p>}
  </>;
}
