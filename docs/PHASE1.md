# Phase 1 handoff

Two deliverables: a running application and the experimental plan.

**Current demo:** 87 licensed, timed sound-caption cues are installed, with source-anchored wording variants. Automatic sound recognition was replaced with a deterministic import of the [Demuxed caption track](https://github.com/demuxed/big-buck-captions). See [provenance and checks](CAPTION_GENERATION_STATUS.md). No key is needed.

## Start the app

Requires Node.js 22.13+ (Node 25.2.1 checked), npm and unzip. Run from this repository:

```sh
npm ci
npm run setup:demo
npm run dev
```

Open http://localhost:3000 . The movie is downloaded once from Blender's official archive. No API key is needed. To test a production build: `npm run build`, then `npm start`.

Demo in approximately three minutes:

1. Play the sample film. Click the 1:23 apple cue in the timeline to see a caption matched to that moment.
2. Change detail or expressiveness. The candidate changes in the preview; click Apply preferences to change the player.
3. Toggle Follow cue density, Show original, and Original baseline. Baseline content is fixed; readability is available in both conditions.
4. Reload to check preference persistence. Open Why this caption? to inspect the selection rationale.
5. Open your team's own MP4 in Bring your own story. Add matching caption JSON. Files stay on your device. Sample captions are cleared when you change the video.
6. Opt into a study rehearsal, interact with the player, answer optional ratings, stop and export JSON. No data is uploaded or persisted across reloads.
7. Open Experimental plan for the second deliverable; download the full Markdown plan if needed.

## Your video and caption preparation

Your team is making the study video. The temporary Big Buck Bunny sample is about 10 minutes and is not a long-form study stimulus. Its 87 source captions come from a licensed Demuxed SRT, with unchanged timing. Personalized wording is prepared locally from those source labels. Visual sync anchors were spot-checked; full listening and participant review are still required.

See [CAPTION_IMPORT.md](CAPTION_IMPORT.md) for the schema and workflow. The app opens compatible local video files without uploads. The actual study needs reviewed captions tied to the exact edit. With no reviewed caption JSON, your video still plays but sound captions stay off. Caption content is hidden if file and declared duration differ by more than two seconds.

## Setup and keys

- Phase 1 demo: **none**. Node, npm, unzip and a browser are sufficient. ffmpeg is already installed locally; ffprobe is needed only to rebuild captions with npm run setup:captions.
- NVIDIA NIM: needed only if you later choose AI-assisted offline caption generation. The earlier offline NIM probe failed its audio capability gate; that model remains blocked. The working sample uses source captions and does not depend on NIM. No NIM key belongs in the player or NEXT_PUBLIC_*.
- Hosted deployment, external video storage and a controlled participant-data store: not configured and not needed for this local submission. For a hosted study, video must stream from an external host and approved research logs need persistent, restricted storage.
- Formal participant experiments: finalize consent/ethics with your instructor before recruitment; the rehearsal checkbox does not replace it.

## Boundaries

This Phase 1 build is a functional interface prototype. It does not establish an accessibility outcome, validate caption accuracy, demonstrate the full long-form hypothesis or reuse CapTune's engine. It follows the precompute-and-select architecture with imported licensed source captions. Dialogue subtitle import is not implemented; choose a dialogue-free study video or add fixed verified dialogue subtitles equally to both conditions before studying a dialogue-containing video.
