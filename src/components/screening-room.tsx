"use client";
import { useState } from "react";
import type { CaptionVideo } from "@/lib/captions";
import { Workspace } from "./workspace";

export type ScreeningFilm = { data: CaptionVideo; experimentalData?: CaptionVideo; sourceAssistedData?: CaptionVideo; source: string; poster: string; credit: string };
export function ScreeningRoom({ films }: { films: ScreeningFilm[] }) {
  const [selected, setSelected] = useState(films[0].data.video_id);
  const [locked, setLocked] = useState(false);
  const film = films.find(item => item.data.video_id === selected) || films[0];
  return <>
    <section className="film-library" aria-label="Film library">
      <div><label htmlFor="film-choice">Choose a film</label><p>Each film opens with its own captions and credits.</p></div>
      <select id="film-choice" value={selected} disabled={locked} onChange={event => setSelected(event.target.value)}>
        {films.map(item => <option key={item.data.video_id} value={item.data.video_id}>{item.data.title}</option>)}
      </select>
      {locked && <p role="status">Film selection stays fixed after a rehearsal starts. Export, then reload to choose another.</p>}
    </section>
    <Workspace key={film.data.video_id} initialVideo={film.data} experimentalVideo={film.experimentalData} sourceAssistedVideo={film.sourceAssistedData} demoSource={film.source} demoPoster={film.poster} demoCredit={film.credit} onMediaLockChange={setLocked} />
  </>;
}
