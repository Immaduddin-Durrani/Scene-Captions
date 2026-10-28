## Experimental full-film media-only option — 28 October 2026

All three films now have separate, opt-in NVIDIA-generated experimental tracks:
BBB: 40 sound / 0 dialogue cues; Sintel: 59 / 71; Tears of Steel: 49 / 68.
All 149 audio windows completed, without fetched captions, source intervals,
plot or supplied scene descriptions. Sound text spans coarse 15-second analysis
windows; dialogue uses Parakeet word timestamps. Three sound-detail levels are
rendered from the model's own audio observations, with fixed expressiveness.

**These are not accuracy-approved subtitles.** Acoustic tests remain failed;
descriptions/transcriptions may be missing, wrong or invented. The whole-film
pass does not establish complete event recall or reliable timing. Twelve
zero-duration ASR groups were rejected rather than given fabricated timing.
Existing default caption datasets and the global failed gate remain unchanged.
Use **Use media-only AI subtitles** to opt in and **Use existing captions** to
return. Each film offers three SRT exports and caption JSON. See
[raw generation evidence and implementation checks](verification/media-only-2026-10-28/README.md).

## Latest audio-gate and late-association checks — 27 October 2026

[Fourteen additional NIM requests](verification/nim-late-binding-2026-10-27/README.md) tested fixed-category audio recognition, the recommended hosted-compatible thinking preset, and a visual-only association stage. The visual component respected event identities and negative controls, but audio still adds false tones, misclassifies speech/silence and fails strict sound recognition. A constrained source-association contract does not repair false acoustic events. No reliable subtitle-accuracy gain, new movie track or cleared generation gate is claimed.

## Earlier screenshot-assisted prototype — 27 October 2026

The [event-triggered frame prototype](verification/nim-frame-pipeline-2026-10-27/README.md) extracts matched current/nearby frames from audio-activity candidates, then queries actual audio with zero/one/three screenshots. Eight NIM calls tested two BBB moments; six completed and two hit capacity. Visible context helps name objects, but the completed muted-image control invents a thud on zero-valued audio. No accuracy improvement or new track is accepted. Candidate detection is only a lightweight activity heuristic; dependable sound events/timing and listening validation remain unresolved.

## Earlier split-pipeline pilot — 27 October 2026

The [18-request NVIDIA pilot](verification/nim-pipeline-2026-10-27/README.md) establishes hosted Whisper access and useful dedicated ASR for controlled speech, plus successful three-level text rendering. It does not clear sound-caption quality: silence needs guards, speech timing remains partial, and Omni misidentifies barks as metallic clinks and adds an unsupported tone. Renderer success propagates those mistakes rather than validating them. No independent timed movie track was accepted or installed; the existing source-assisted playback draft and failed capability gate remain unchanged.

## Earlier audio-only recognition controls — 27 October 2026

The [new recognition tests](verification/nim-recognition-2026-10-27/README.md) made twelve NIM requests: nine completed and three returned capacity errors. Crop/repetition controls did not establish dog identification; rain remained broadly water-related. Silence behavior was inconsistent. A fresh speech recording transcribed exactly but was described as silent under the general sound-description instruction, with identical audio and generation parameters. This warrants a focused task/serving-path investigation; it does not establish a unique cause. No timing/video/full-film test or new track installation followed the failed prerequisites. The independent sound-caption gate remains failed.

## Earlier caption-free controls — 26 October 2026

Twelve additional NIM requests tested natural sounds, exact audio shifts, silent pictures and digital silence: six HTTP 200, five capacity errors and one timeout. Novel speech transcribed correctly, but a tone was reported on zero-valued audio. Relative sound timing remains unscorable because no correctly identified timed pair completed. The independent audio gate stays failed; no new NIM track is installed. See [the complete results and audit](verification/nim-counterfactuals-2026-10-26/README.md) and [research handoff prompt](research/RESEARCH_HANDOFF_PROMPT.md). Software tests pass; they do not establish sound-caption accuracy.

## Earlier NIM follow-up — 26 October 2026

42 new NVIDIA requests tested audio, video, plot/reference context and source-assisted transformations. NIM access works, but non-speech controls still fail, including false sounds on decoded digital silence. Some Super VL visual/reference expansions are useful drafts; a full NIM-generated track has not been accepted. The existing Qwen/editorial draft remains Personalized; Reference baseline and Show reference display the actual fetched source. See [proof and research](verification/nim-phase1-2026-10-26/README.md). No independent audio-grounded improvement or DHH usability benefit is established.

# Current local draft — 26 October 2026

Big Buck Bunny now uses 87 AI-assisted generated fixed captions and exports, supplying Personalized and exports. Reference baseline displays the fetched source. A local Qwen2.5-1.5B 4-bit model generated drafts from licensed reference labels. The main assistant then made extensive source-text corrections: 63 of 67 labels, 120 of 201 generated fields. All raw prompts/outputs and edits are saved. This is generated-and-edited source-assisted wording, not untouched model output or independent audio recognition.

The reference supplies event coverage and timestamps, with CC BY attribution retained. Each cue has separate reference_text. Three detail descriptions and three punctuation styles form nine cached combinations; they are not nine independent semantic generations. All 87 fixed captions differ from fetched wording. Full human listening review is pending; existing failed audio-model gates remain unchanged. A 20-character/second heuristic flags 7 baseline intervals versus 10 before; this is not a validated DHH measure or evidence of better accessibility.

See [demo/presentation notes](GENERATED_CAPTIONS_DEMO.md), [saved generation evidence](verification/generated-captions-2026-10-26/README.md) and [generated SRT](../public/research/big-buck-bunny.srt). Playback and rebuilding saved outputs need no model, cloud request or API key. The new draft is local until a fresh push/publish request.

# Historical source-track status (superseded for current local Big Buck Bunny wording)

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

**Follow cue density** counts cue intervals intersecting the ±5-second neighborhood: at least four means dense; at most one means sparse; otherwise moderate. Dense passages select shorter wording; other passages retain the viewer's chosen maximum. Sparse cues never raise detail above that limit. This is not visual scene recognition or a validated measure of cognitive load.

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

The working source-caption track requires no API key or paid software. Subsequent 24 October work used authorized skills and bounded free-model diagnostics in the main session; no agents or hooks were launched. See [the fixes report](audits/2026-10-24-fixes.md) for current evidence rather than treating earlier verification as current.

## 24 October preparation and controls

The user selected existing timed sound captions plus corresponding-audio checks. Offline generation/audio tools now exist, but no model track has passed acceptance. An example-like structured silence response failed calibration. Simpler controls correctly recognized silence and transcribed synthetic speech, but classified the audible tone as silence with reasoning off/on. Invalid WAV input caused a decoder error. The input reaches an audio-capable path; non-speech task suitability remains unproven in the tested setup.

Text probes copied source wording, omitted a simultaneous sound, returned incomplete grids, invented unrelated content or timed out. Missing output/timeouts are inconclusive where applicable, not global model-capability judgments. The strict generation path rejects source-copy-only batches and missing/added sound lines, and only writes separate candidates. Rejected probes are quarantined; the default demo never loads them.

Seven verbose rich-effect entries were shortened locally while preserving the licensed original text and all intervals. One problematic simultaneous cue is now 28 rather than 68 characters in 0.541 seconds. This is still a reading-review concern. A 20-character/second editing heuristic flags 206 original/variant cases; it is not a validated DHH threshold, and timing is not extended automatically.

See [tool usage and request limits](../scripts/generation/README.md), [model results](integrations/NVIDIA_MODELS.md), and [fresh evidence](verification/fixes-2026-10-24/README.md). Review the exact soundtrack and captions with DHH collaborators before study use. Model agreement, concise wording and schema validity do not independently establish sound accuracy.

## Current bounded investigation

See [the 24 October follow-up](audits/2026-10-24-investigation.md). Ten single-attempt synthetic/text requests tested temperature, audio sample rate and prompt specificity. One capacity error is inconclusive; neither non-speech calibration nor English source-fidelity requirements passed. Partial speech/noun successes do not justify clearing the failed gate, and these results do not condemn all audio models.

Structural completion/bracket guards were fixed and regression-tested. The source track is unchanged. A practical human-review alternative now prepares contextual clips, source/variant comparisons and hash-bound pending decisions with `scripts/prepare-caption-review.py`. A three-cue packet was generated; all decisions remain pending. Whole-track review, not just a small sample or valid JSON, is required. See [the guide](../scripts/generation/README.md).

## Added local films — 24 October 2026

The user subsequently authorized downloads/integration. Sintel and Tears of Steel are selectable, with their official 26 / 76 English dialogue cues. Their non-speech status is explicitly `not-prepared`; no generation-failure result or human approval is invented. Source wording/timing and exact-media hashes are retained. A fuller Sintel caption candidate was found online but its separate reuse terms and timing were not verified, so it stays outside playback. See [per-title coverage](LIBRARY_CAPTIONS.md) and the current library evidence. The original failed automated model gate is unchanged.
