# Working Big Buck Bunny captions

## Current approach

The demo uses an existing licensed non-speech caption track instead of automatic sound recognition. All 87 source intervals are imported with their original timestamps and text, including simultaneous sound effects. A local editorial lexicon supplies nine cached wording variants per interval. No model, API key or cloud service is used to build or view this track.

- Captions: [Demuxed / big-buck-captions contributors](https://github.com/demuxed/big-buck-captions), created for Demuxed 2022.
- Pinned commit: `e490383ca58f53507cfa18a64e1324f28d77c65a`.
- License: **CC BY 3.0**, explicitly stated in the source README. The README, exact SRT and source manifest are preserved in `data/sources/big-buck-captions/`.
- Film: © 2008 Blender Foundation / peach.blender.org, CC BY 3.0.
- Changes: locally authored source-anchored caption wording, and caption-density metadata. Original captions and source timing are preserved. Plain labels and optional sound spellings are also precomputed.
- Original baseline and Show original return the Demuxed source caption, not an asserted Blender-authored caption.

Detail removes or retains source specificity; expressiveness changes phrasing and punctuation. Variants add no new sounds, instruments or volume claims. Some levels deliberately convey similar information when the source contains little detail. Repeated labels use the same lexicon entry across the film. Source mood words remain source interpretations; this is not proof of listener emotion.

## Timing and adaptation

The final source cue ends at 596.457 seconds, within our exact film's 596.461678-second duration. Visual alignment was spot-checked at the bird sequence (20.7 s), apple impact (83.9 s), butterfly impact (195.9 s), bow string (321.7 s), twig (410.99 s) and final gag (595.9 s). This is not a complete listening review. Full source and video hashes are recorded in `docs/verification/sourced-caption-import.json`.

The former arbitrary thud at 1:18 is absent. At 1:23.624 the track supplies the actual source cue `[APPLE THUDS]`. Gaps are intentional: captions appear for selected sound events, not continuously throughout the film.

**Follow cue density** counts cue intervals intersecting the ±5-second neighborhood: at least four means dense; at most one means sparse; otherwise moderate. It selects less or more detail from the cached grid. The UI names this proxy explicitly. It is not visual scene recognition or a validated measure of cognitive load.

## Rebuild and run

The app already includes the imported track. Playback needs Node/npm and the downloaded film, with no API key:

```sh
npm run setup:demo
npm run dev
```

To rebuild captions from the pinned local SRT and lexicon, ffmpeg/ffprobe must be available (already installed on this machine):

```sh
npm run setup:captions
npm run validate:captions
npm run test
```

The importer rejects modified source bytes, a different video hash, unknown labels, invalid intervals and invalid JSON output. It makes no network requests. Original SRT and WebVTT downloads are available in `public/research/`.

## Earlier approaches retained as evidence

NVIDIA authentication works with the replacement key, but the tested Omni audio path hallucinated sounds on all-zero audio and produced speculative film descriptions. Its ten-clip candidates were never installed. That model's failed gate remains in `docs/verification/nim-capability-status.json`; broad generation with it stays blocked. This failure does not block importing a separate licensed caption source.

Local AST classification of the actual soundtrack also did not supply adequate effect labels. A dedicated Whisper captioning model download was interrupted once this reusable caption source was found; no inference from it was installed. The previous cyclic illustrative track was withdrawn and has not been restored.

## Phase 1 and study limits

A working captioned application and the experimental plan are available locally. This demonstrates source-caption ingestion, timeline playback, persistent preferences, preview/apply, a fixed baseline and cue-density adaptation. It does not establish an accessibility benefit or implement reliable automatic sound recognition for arbitrary videos.

The team will create its study video. Keep a timed sound-event log while editing, prepare a matching source-caption track, check the exported edit by listening, review wording with DHH collaborators, and import the completed JSON. Full caption review, study approval and recruitment remain future work. No participant results are claimed.

No additional key or paid software is required for this approach. No skills, agents, hooks or external workers were activated for this follow-up.
