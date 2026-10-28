# Phase 1 handoff

Two deliverables: a running application and the experimental plan.

**Current local draft (26 October):** 87 AI-assisted generated sound captions supply Personalized and the generated SRT; Reference baseline shows the fetched source. Qwen2.5-1.5B generated descriptions locally; 63 of 67 labels then needed recorded source-text edits. Demuxed supplies reference events and timestamps. Expression levels change punctuation only. See [generation/demo notes](GENERATED_CAPTIONS_DEMO.md). This is not independent sound recognition or an audio-verified track. No key is needed to view or rebuild saved outputs.

## Start the app

Requires Node.js 22.13+ and npm (Windows checks used Node 24.21.0). Windows uses its installed PowerShell ZIP reader; macOS/Linux need unzip. Run from this repository:

```sh
npm ci
npm run setup:demo
npm run dev
```

Open http://localhost:3000 . The movie is downloaded once from Blender's official archive. No API key is needed. To test a production build: `npm run build`, then `npm start`.

Demo in approximately three minutes:

1. Play the sample film. Click the 1:23 apple cue in the timeline to see a caption matched to that moment.
2. Change detail or expressiveness: changes apply and save immediately, with no Apply button. Preview this cue in the video pauses at a cue for five seconds; the current preferences remain applied. Text size/position changes preserve the chosen content preferences.
3. Toggle Follow cue density, Show reference, and Reference baseline. Reference baseline displays the fetched source, while Personalized uses generated draft wording; readability is available in both conditions.
4. Reload to check preference persistence. Open Why this caption? to inspect the selection rationale.
5. Open your team's own MP4 in Bring your own story. Add matching caption JSON. Files stay on your device. Sample captions are cleared when you change the video.
6. Opt into a study rehearsal, interact with the player, answer optional ratings, stop and export JSON. No data is uploaded or persisted across reloads.
7. Open Experimental plan for the second deliverable; download the full Markdown plan if needed.

## Your video and caption preparation

Your team is making the study video. The temporary Big Buck Bunny sample is about 10 minutes and is not a long-form study stimulus. Its 87 new generated-and-edited captions use events/timestamps from a licensed Demuxed reference. Visual sync anchors were spot-checked; full listening and participant review are still required.

See [CAPTION_IMPORT.md](CAPTION_IMPORT.md) for the schema and workflow. The app opens compatible local video files without uploads. The actual study needs reviewed captions tied to the exact edit. With no reviewed caption JSON, your video still plays but sound captions stay off. Caption content is hidden if file and declared duration differ by more than two seconds.

## Setup and keys

- Phase 1 demo: **none**. Node, npm, unzip and a browser are sufficient. ffmpeg is already installed locally; Rebuilding saved captions uses npm run setup:captions without a model or ffprobe; fresh local generation needs the isolated MLX-LM runtime.
- NVIDIA NIM: used only by separately run offline preparation tools. Current text/audio trials have not passed quality gates. Audio decode and speech controls work, but non-speech tone recognition still fails in the tested setup. The new sample uses local source-assisted wording and does not depend on NIM. No NIM key belongs in the player or NEXT_PUBLIC_*. See scripts/generation/README.md for candidate preparation, retries and response waits.
- Vercel and video storage are configured for the previous release; this new generated draft has not been published. A controlled participant-data store is not configured. For a hosted study, video must stream from an external host and approved research logs need persistent, restricted storage.
- Formal participant experiments: finalize consent/ethics with your instructor before recruitment; the rehearsal checkbox does not replace it.

## Boundaries

This Phase 1 build is a functional interface prototype. It does not establish an accessibility outcome, validate caption accuracy, demonstrate the full long-form hypothesis or reuse CapTune's engine. It follows the precompute-and-select architecture with source-assisted generated draft captions. The app supports fixed dialogue separately; verify dialogue equally in both conditions before a study.
