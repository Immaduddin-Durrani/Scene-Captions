# Viewer caption options simplified — 28 October 2026

Removed **Use existing captions** and **Use media-only AI subtitles** from the
viewer, as requested. Big Buck Bunny now opens with the simple source-guided
track selected, including after restoring the sample. Its reference comparison
and three detail levels remain available. Sintel and Tears of Steel retain their
source dialogue captions without an empty source picker. Experimental datasets
and downloads are retained for research, but are no longer loaded into the
viewer. Earlier verification records below describe their historical UI.

29 Node tests, type checking, caption validation and the production build pass.
The updated source-richness browser check passes: both buttons absent across all
three films, source-guided default selected, three detail levels, reference
comparison, keyboard selection, playback position, mobile layout, downloads and
rehearsal locking. No caption generation was run; maps remain stale.

# Simple source-guided richness and prompt improvements — 28 October 2026

The user requested richer wording from existing captions in simple English, then
explicitly limited enhancement to verified/source-caption sounds and requested
more context/better prompting. A separate BBB source-guided option now uses
NVIDIA Ultra with the full licensed 87-cue timeline, precise occurrences,
simultaneous lines, a plain-word glossary, explicit unknown facts and targeted
correction feedback. No media-only sound guesses or plot are supplied. All 67
unique labels were generated and source-text reviewed; 88 fields across 48
labels were edited. 66 labels have distinct wording at all three levels; all
atomic text is at most eight words. This is AI-assisted editorial work, not
untouched model output or acoustic verification. Reading-time flags remain.

Use **Use source-guided captions** for BBB; original reference comparison stays
available. The other titles' fetched tracks have dialogue only and remain
unchanged under the source-only instruction. Existing default/media-only data
and the failed acoustic gate are unchanged. 29 Node / 46 offline Python tests,
types/schema/build and focused browser checks passed. Existing media-only mode
also passed on all three films. No listening/DHH study, named skills, agents,
installation, paid provider, push or deployment occurred. Maps remain stale.
See [complete prompt, reviews and evidence](verification/source-richness-2026-10-28/README.md).

# Experimental media-only full-film tracks — 28 October 2026

The user explicitly requested full generated subtitles for all three films and
an option to select them without existing captions or plot context. All 149
15-second audio windows were processed. Separate experimental outputs contain
40/59/49 sound-caption windows for BBB/Sintel/Tears of Steel and 0/71/68 generated
dialogue cues. These counts do not measure correctness or recall. Sound display
times are analysis windows, not detected event boundaries; 12 zero-duration
ASR groups were rejected and logged. No source-caption text/timestamps or plot
were supplied to generation. Text rendering uses our own unverified acoustic
observations and can propagate their errors. Three detail levels share fixed
expression; no expressive/visual-adaptation capability is claimed.

The viewer now offers **Use media-only AI subtitles**, keeps existing captions
as default, preserves playback position on switching and locks source after a
rehearsal starts. Track identity, source hash and duration are checked. Separate
three-level SRT and JSON downloads are served. Known failed acoustic controls
remain disclosed, and default caption files/global gate are byte-unchanged.
25 Node tests, 42 offline Python tests, all dataset validations, the production
build and Chrome checks of all three films passed. Mobile checks use a 390 CSS
pixel viewport, not a physical device. Source maps/health snapshots are stale
for these edits; no named skills, agents, package installation, paid provider,
push or deployment were used. See [complete evidence](verification/media-only-2026-10-28/README.md).

# Latest audio gate and late visual association tests — 27 October 2026

Fourteen NVIDIA requests tested fixed-category audio recognition, hosted-supported recommended reasoning parameters, and visual association as a separate constrained task. Twelve requests completed; two capacity errors were explicitly retried once without payload changes. The documented reasoning-budget field was accepted. Audio controls remain unaccepted: silence becomes a tone; a dog tag appears alongside a false tone; clean speech becomes silence; rain is only generic water. Visual association preserved IDs in all four cases, kept the empty ledger empty, and abstained on swapped/known-mismatched contexts. The one positive source suggestion remains only a hypothesis. This is improved separation of responsibilities, not a demonstrated caption-accuracy gain or an architecture-only causal comparison. See [full evidence](verification/nim-late-binding-2026-10-27/README.md). The 35 shared offline tests and focused guard checks passed. No source captions, plot, new model installation, named workflow, agents, track replacement, push or deployment were used for this batch. Acoustic grounding and timing remain the blocking requirement.

# Earlier event-triggered screenshot prototype — 27 October 2026

An offline prototype now finds audio-activity candidates, extracts exact-PTS current/nearby movie frames, and compares audio-only, single-frame and triplet-frame caption drafts. Eight NIM requests produced six HTTP-200 completions and two capacity errors. Frames add visible object/location claims, but a completed all-zero-audio control still claims a rabbit/apple thud, so caption accuracy is not accepted. RMS candidates are not semantic sound detection or validated event boundaries. The first 120 seconds selected candidates at 54.6 and 87.0 seconds without subtitle/plot input. Reference overlap was examined only after generation; it does not establish full accuracy. See [prototype and complete evidence](verification/nim-frame-pipeline-2026-10-27/README.md). Source-map code inputs, playback data and the failed gate remain unchanged; no push/deployment occurred.

# Earlier NVIDIA speech/sound/rendering pipeline test — 27 October 2026

An 18-request NVIDIA-only pilot used hosted Whisper, dedicated Parakeet ASR, Omni non-speech observations and Super VL three-level text rendering. Eleven gRPC requests and five chat requests completed; two chat requests hit capacity and were explicitly retried. Both ASR models recover the clean/mixed test phrase. Whisper returns no word offsets on those controls and hallucinates on raw silence; Parakeet supplies offset candidates with zero-duration words and endpoint drift, and produces unknown tokens on silence in both WAV/raw PCM. Local zero/markup guards protect tested cases. Sound grounding still fails: barks become metallic clinks and an unsupported tone appears. Rendering preserves words/IDs and three detail levels but propagates that wrong source label. No track or failed gate was replaced. See [the full pilot evidence](verification/nim-pipeline-2026-10-27/README.md). A small pinned Riva client runtime was installed under /Users/hamza/runtimes/scenecaptions-nim-asr; no local recognition model weights or new key were required. Thirty-five shared offline tests and focused guard checks passed. No agents, named workflow activation, push or deployment occurred.

# Earlier audio-only recognition tests — 27 October 2026

Twelve NIM requests across nine cells produced nine HTTP 200 completions and three capacity errors. Cropping did not establish dog recognition; repeated bark samples produced repetition-related impact descriptions without a dog identification. Rain descriptions were broadly water-related. Short digital silence hallucinated a drum, while long silence passed. A fresh speech WAV transcribed exactly, but the identical WAV with only the instruction changed to general sound description was called silent. This is an observed task-dependent discrepancy, not proof of a unique model or backend mechanism. Recognition/absence prerequisites failed, so timing/video/full-film tests stayed paused. The failed gate and playback track are unchanged. See [results, exact requests and integrity checks](verification/nim-recognition-2026-10-27/README.md). Thirty-five offline tests passed. No push, deployment, model installation or named workflow activation was performed for this batch.

# Earlier caption-free tests and audit — 26 October 2026

Twelve additional NVIDIA-only requests tested natural-sound recognition, exact shifts and silence: six HTTP 200, five 503 capacity errors and one timeout. Speech works on the positive control; sound grounding remains unreliable, including a tone on digital silence. No independent NIM track passed acceptance. Completion and experiment-matching guards were tightened; 35 offline Python tests, 19 application tests, TypeScript checking and caption validation passed. The source map is refreshed with documented extraction gaps; Fallow reports application complexity concerns and does not cover Python. Read [the latest evidence](verification/nim-counterfactuals-2026-10-26/README.md), [current map](CODEBASE_MAP.md) and [research handoff prompt](research/RESEARCH_HANDOFF_PROMPT.md). Earlier investigation entries below are historical snapshots.

# NVIDIA-only continuation — 26 October 2026

The user explicitly declined the proposed paid pilot and selected “Keep everything on NVIDIA NIM.” The OpenRouter proposal is closed, not pending. Continue the BBB task using only NVIDIA NIM inference; do not read an OpenRouter key or make paid fallback calls. Independent audio grounding remains failed until a new control actually passes. Reference-assisted generation remains a separate capability and must be disclosed as such.

# Latest NIM investigation — 26 October 2026

The current user request authorizes NVIDIA inference for Big Buck Bunny only. This supersedes the historical local-only rule below for this task; paid generation and publication still need fresh requests. We made 42 bounded inference requests: 27 HTTP 200, nine 503, four 500, one timeout and one account-specific 404. Correct novel-speech transcription establishes some audio conditioning. Wrong tone/silence answers and sound claims on two verified muted clips leave the independent audio gate failed. Super VL generated some useful reference-plus-visible-context detail, but no full NIM track was accepted. Do not call the harness ideal or attribute everything solely to model weights.

The player still uses the earlier local Qwen/editorial draft for Personalized. Reference baseline and Show reference now select the actual fetched reference_text at identical timestamps. Both are drafts/references, not validated DHH study stimuli. [Current evidence and next-step proposal](verification/nim-phase1-2026-10-26/README.md) include exact inputs/results, paper links, documented API settings and an unexecuted capped paid pilot. No paid call, new model installation, push or deployment occurred. Existing maps remain stale. Browser/build verification is recorded with this investigation.

# Current local draft — 26 October 2026

Big Buck Bunny now uses 87 AI-assisted generated fixed captions and exports, replacing fetched text in playback. A local Qwen2.5-1.5B 4-bit model generated drafts from licensed reference labels. The main assistant then made extensive source-text corrections: 63 of 67 labels, 120 of 201 generated fields. All raw prompts/outputs and edits are saved. This is generated-and-edited source-assisted wording, not untouched model output or independent audio recognition.

The reference supplies event coverage and timestamps, with CC BY attribution retained. Each cue has separate reference_text. Three detail descriptions and three punctuation styles form nine cached combinations; they are not nine independent semantic generations. All 87 fixed captions differ from fetched wording. Full human listening review is pending; existing failed audio-model gates remain unchanged. A 20-character/second heuristic flags 7 baseline intervals versus 10 before; this is not a validated DHH measure or evidence of better accessibility.

See [demo/presentation notes](GENERATED_CAPTIONS_DEMO.md), [saved generation evidence](verification/generated-captions-2026-10-26/README.md) and [generated SRT](../public/research/big-buck-bunny.srt). Playback and rebuilding saved outputs need no model, cloud request or API key. The new draft is local until a fresh push/publish request.

# Vercel production deployment — 25 October 2026

The user selected Vercel and supplied a private account token. The demo is live at https://scene-captions.vercel.app with the experimental plan at /experiment. Three videos stream directly from public Vercel Blob storage (630,993,877 bytes total). Sintel picture was recompressed without changing its audio, frame count or full duration; frame timestamps differ by at most 0.334 ms. The Next.js cloud build, local 18-test suite and hosted Chrome playback/seek/caption checks passed. No model inference, paid plan upgrade, telemetry activation or agents were enabled. The user subsequently connected the transferred `hamzahisam/Scene-Captions` GitHub repository in Vercel; local `origin` matches it. See [deployment evidence](verification/deployment-2026-10-25/README.md) and [hosting guide](VERCEL_DEPLOYMENT.md). Full sound-caption limitations below remain unchanged. The codebase map is stale for the new media URL configuration. The deployment source edits and evidence are included in this Git follow-up.

# Local-only constraint confirmed — 24 October 2026

The user declined cloud generation and selected “Keep everything local.” No Gemini/cloud calls are authorized for this work; the earlier pending cloud proposal is closed. Continue only with local preparation and bounded local model controls. The pinned small Whisper sound-caption fine-tune has now also failed six controls, repeated with an explicit audio attention mask (12 local generations; identical descriptions). Both tested local candidates are rejected for full-film preparation. Full sound tracks remain unfinished until a local method passes recognition/timing checks and actual annotations are prepared.

# Sound-caption preparation follow-up — 24 October 2026

The user requested full sound-effect captions. A new isolated local Gemma 3n/MLX trial made 12 bounded generations and did not pass non-speech controls. Audio feature/embedding checks and partial speech transcription show some audio conditioning, but no reliable sound descriptions or event timings were obtained. No full-film caption inference, cloud call or playback change occurred. Audio input windows for both exact-hash films are prepared locally (55 target intervals total). The proposed Gemini trial was declined; no cloud work is pending or authorized. See [results and limits](verification/sound-captions-2026-10-24/README.md). Full reviewed sound tracks remain unfinished.

# Current library integration — 24 October 2026

The latest user request explicitly authorized downloading and integrating Sintel and Tears of Steel. Both official full 720p sources are now local and selectable alongside Big Buck Bunny, with independent posters, credits and precomputed English dialogue (26 / 76 cues). Title switching clears the previous workspace; rehearsal locks title selection. Full non-speech tracks for the two new films remain unprepared, and their sound-personalization controls are disabled. No successful automatic sound-caption generation or human review is claimed. See [coverage](LIBRARY_CAPTIONS.md) and [current evidence](verification/library-2026-10-24/README.md).

Current library checks passed: 18 Node tests, 22 offline Python tests, types, all three dataset validations and production build; Chrome checked every new dialogue cue after seek/decode, the existing 87 sound cues, title isolation, transcript/readability behavior and rehearsal locking. These are implementation checks, not full listening approval.

The previously refreshed Graphify map and Fallow reports describe the earlier investigation snapshot and are now stale for the changed player/schema/catalogue files. Their scores and input hashes remain historical evidence; no skill activation or fresh scan was requested for this follow-up.

# Current project state

Last updated: 24 October 2026, after the bounded model investigation and focused component cleanup. Read [the current investigation](audits/2026-10-24-investigation.md) and [current evidence](verification/investigation-2026-10-24/README.md). Prior fixes/audits remain historical evidence, not fresh checks of the new modules.

## Start here

Read `README.md`, `architecture.txt` and `docs/SKILL_WORKFLOW.md` first. Then read this page and the latest linked audit. Use `GLOSSARY.md` for canonical domain meanings. Read the original proposal/idea when checking research intent. Follow links to the experimental plan, caption provenance and task-specific evidence rather than assuming the three entry documents contain every detail.

For structural work, inspect a fresh Graphify map first and relevant Fallow findings second. Use them to identify affected files. Inspect those source files and their tests before editing; static tools do not establish runtime behavior, caption correctness or research validity. Check snapshot inputs against changed files and report gaps. Do not automatically rerun a skill without current-task authorization.

## Product and research

- Research focus: personalized non-speech captions for DHH viewers during continuous longer storytelling, preserving consistency, understandability and viewer control.
- Intended product: a web player with persistent preferences, preview/apply, adaptation and original-caption override. Benefits are research hypotheses.
- Demo catalogue direction: a few curated local titles of roughly 10–30 minutes, none over 30 minutes, with a video selector. The existing sample is 9:56 and should display its true duration. Additional titles/selector are planned; only the current single title is bundled today.
- Phase 2 roadmap: investigate suitable APIs/free or open services for browser streaming, discovery, title metadata, thumbnails and available captions. No provider/integration is selected or authorized by this roadmap entry. Keep rights, caption provenance and exact-edit alignment separate from discovery.
- First submission: a running application and proposed experimental plan. The team also requested source-caption generation and audio corroboration. The tooling is implemented, but model quality checks have not passed; do not present automated generation/alignment as a finished capability.
- Team proposal sources are preserved unchanged in `docs/research/proposals/`: `SceneCaptions_Project_Proposal.pptx` (seven slides and seven speaker-note sections) and `SceneCaptions-Project-Idea.docx`. Their original root placement was superseded with the user's approval to organize them.

## Current implementation

- Working local Next.js prototype using 87 licensed Demuxed sound-caption intervals for Big Buck Bunny and locally authored variants.
- The sample is about ten minutes, not the planned 20–30 minute study stimulus. Timing/import checks do not replace a full listening/readability review.
- Cue-density adaptation is explicitly labelled as a proxy, not visual scene understanding or measured cognitive load.
- Preferences persist in browser storage. Local video/JSON import and opt-in rehearsal/export are implemented. Rehearsal is not an approved participant study.
- No model is called while watching. Formal participant infrastructure, approved study materials and reliable arbitrary-video sound recognition are not implemented.
- Existing audio-model failure evidence remains valid. Do not remove its gate to obtain apparent success.

## Decisions from the current audit interview

The user selected:

1. Include automated generation in the submission work.
2. Retain and clearly disclose the cue-density proxy.
3. Treat chosen detail as a maximum; adaptation must not increase it above the viewer's choice.

The user confirmed the implementation direction: start from existing captions, check corresponding audio, offer a temporary on-video preview and test free NVIDIA models. The detail maximum is now implemented and regression-tested. Preview pauses at a cue for five seconds, then returns to saved settings; manual return and original override remain available. It never persists the candidate profile.

Source-caption generation and corresponding-audio checks are now the agreed path. Bounded free NVIDIA calls have run without agents or participant material. The client supports both key names; values remain private. See [model candidates and results](integrations/NVIDIA_MODELS.md) and [offline tool usage](../scripts/generation/README.md). No generated track was accepted or installed. Known-speech transcription works, but a known tone is classified as silence. The tested setup does not yet provide reliable non-speech corroboration.

## Fresh verification and findings

See [the original audit](audits/2026-10-24.md), [fixes report](audits/2026-10-24-fixes.md), and [latest investigation](audits/2026-10-24-investigation.md) and [fresh evidence index](verification/investigation-2026-10-24/README.md).

- Earlier investigation verification: 14 Node tests and 22 offline Python tests passed, plus types, 87-cue validation, production build and Chrome checks in the macOS checkout. Retry/timeout tests are simulated. The earlier Windows/two-process pacing evidence remains historical; no new cross-process network test is claimed.
- Chrome regression checks passed for all 87 source intervals after actual seeks, play/pause, original/baseline, preference persistence, imports, rehearsal/export and the plan route. This does not establish continuous-play timing accuracy or sound truth.
- The prior checkpoint’s production dependency advisory check reported zero known vulnerabilities; it was not repeated during this investigation. This is not proof of supply-chain security.
- Fixed and browser-checked: draft preference loss/readability collapse, detail exceeding the maximum, missing starting original-override state, preview not actually trying the candidate, and elapsed export time increasing after recording stopped.
- Windows ZIP extraction now uses the installed PowerShell/.NET ZIP reader; the cached official archive extracted successfully and matched the expected video hash. Existing video files are also hash-checked before reuse.
- Seven verbose effect entries were shortened locally without adding facts or changing timing. The worst highlighted simultaneous-cue rich text fell from 68 to 28 characters in the same 0.541 seconds; it still needs reading review. The authoring heuristic flags 206 original/variant cases above 20 characters/second; this is not a validated DHH threshold.

The working track remains licensed/source-anchored with locally edited wording. Failed model candidates were quarantined under ignored artifacts. The experimental-plan source and both exported copies now describe current behavior and the outstanding model limits. Existing decision history and original proposal documents are preserved.

## Maps and audit freshness

- `docs/codebase-map.json`, `docs/codebase-map.html` and `docs/codebase-map-inputs.json`: refreshed deterministic source map, with per-file hashes and scope. See [the map guide](CODEBASE_MAP.md) for unmodeled boundaries. Hashes, not just Git HEAD, establish freshness because changes are uncommitted.
- The current authorized refresh is the committed source map: 63 files, 334 nodes and 740 edges, with zero semantic/model tokens. Eight inventoried files yielded no symbols. Broad ignored graphify-out outputs from earlier tasks are historical and were not refreshed or used as current proof.
- Fresh Fallow results: `docs/verification/investigation-2026-10-24/reports/final-fallow*.json`. Six unused-file candidates are manually invoked/historical utilities, not deletion proof. Seven clone groups include overlapping historical browser scripts; review the report's scope before refactoring. No unused dependencies/exports or cycles were reported.
- There are currently no configured architecture boundary rules. A zero architecture finding count does not mean those boundaries were measured.
- Fallow 3.34.1 comparison: 62.6/C and 13 findings before, 63.2/C and 17 after cleanup. Main component cognitive complexity fell from 66/56/30/19 to 21/27/17/7 (player/workspace/preferences/rehearsal); branching is now distributed among cohesive owners, with residual cognitive/estimated-coverage findings. The health gate remains failed; no suppressions or invented coverage. Python helpers are verified separately. A newly reproduced preview/seek slider race is fixed by updating display time at both external and slider seek requests; native keyboard/pointer and Escape/play/slider cancellation checks pass.

After structural changes, refresh an authorized local map or mark it stale and state what changed. After a substantial audit/milestone, run an authorized targeted Fallow check when useful. Save source revision/input coverage, command, results and limitations; never install automatic hooks or watchers to satisfy freshness.

Historical audit scripts remain under `scripts/verification/audit-2026-10-24/`; current acceptance checks are under `scripts/verification/fixes-2026-10-24/` and `scripts/browser-smoke.mjs`. Earlier reports retain their execution-time paths. Temporary full-paper extracts and model/audio caches remain in ignored artifacts. Use the documentation index rather than moving established files for cosmetic consistency.

## Next work

User media preparation is now complete (24 October): both titles have H.264/AAC video, posters and English VTT files. Local hashes match the generated records. Sintel: 1280x544, 888.032 seconds; Tears of Steel: 1280x534, 734.167 seconds. See [verification](verification/fixes-2026-10-24/reports/local-media.json). Listening and subtitle-timing review are still pending. The model quality gates still have not passed. This follow-up performed ten single-attempt synthetic/text requests and measured focused component cleanup; the Fallow gate remains non-clean despite lower main-component complexity. A local contextual listening/review packet is now available; no human approval was fabricated.

720p follow-up: the user rejected the initial 480p preparation setting. The helper now preserves the official 720p-release picture dimensions, reuses completed source downloads, and rebuilds lower-resolution/incomplete browser copies. Replacements are checked before publication; posters regenerate when the video is rebuilt. PowerShell syntax and four simulated checks passed (matching dimensions accepted; 480p, missing audio and truncated duration rejected). The user completed film preparation; no film download or conversion was run by the agent.

Local-media preparation: the user explicitly requires agents to provide PowerShell commands instead of downloading films themselves. `scripts/media/prepare-library.ps1` prepares optional Sintel/Tears of Steel browser MP4s with audio, posters, available English subtitles and provenance records when the user runs it. See [the local media guide](LOCAL_MEDIA.md). The user completed the downloads/conversions; local output checks passed as recorded above. That preparation-only checkpoint preceded the new request above: title selection/dialogue playback are now implemented; reviewed per-title sound tracks remain pending.

Map freshness: the newly authorized source refresh includes the media-preparation helper, new component owners, diagnostics and review tools. Verify its per-file hashes before relying on it. PowerShell/media/runtime coverage remains limited. Current Fallow reports are distinct from preserved historical results.

For the prepared local catalogue, obtain and review corresponding sound-caption material, then implement selection without mixing tracks across titles. Keep downloads outside Git, show actual durations and label missing/unreviewed caption features honestly. Do not expand into Phase 2 streaming/services during this demo work.

Use the working source-caption demo for the submission. Further model work must be a bounded diagnostic or a justified replacement-method evaluation; do not resume full-film generation on the failed setup. Before research, complete listening/readability review, DHH feedback, final study video/questions, and instructor/ethics approval. A script/scene log can support annotation but must not be fed as the expected answer to an allegedly independent sound check. No benefit or participant result has been established.

## Current investigation outcomes

- Fixed reproduced guards: explicit non-stop model completions cannot become candidates merely because JSON parses; each atomic caption line must contain one nonempty bracket group. This does not validate its meaning.
- Ten synthetic/text endpoint requests: one HTTP 503 capacity error is inconclusive; sound controls and required English source fidelity did not pass. Correct speech transcription and one held-out noun control show partial capability; the precise hosted failure cause remains uncertain. No broad model sweep or full-film generation.
- `scripts/prepare-caption-review.py` generates contextual listening clips, a local HTML page and an all-pending receipt. Exact video/track/cue hashes and complete per-variant/check decisions are required for documented human-review completion. It never installs a track or substitutes for listening/DHH review. The generated three-cue packet is under ignored artifacts/caption-review/.
- Media lifecycle/transport, local imports/blob ownership, rehearsal capture, draft preview, style/readability, source-track presentation and rating/session export now have cohesive owners. Existing component interfaces and successful behavior are preserved by current browser checks.
- Current skill use: systematic-debugging, conditional Context7 React documentation, playwright-cli, Fallow and deterministic Graphify. No new package installation, agents, film downloads, paid service, persistent integration, commit or push.

Mapping limitation: the raw Graphify diagnostic flags 169 dangling endpoint references and 28 same-endpoint directed pairs under default diagnostic deduplication; the committed DiGraph has bound stored endpoints. The mapper’s dedup=False controls entity merging and does not prevent edge collapse. Treat this as an extraction/resolution warning and inspect source, not evidence of complete call coverage. Eight files yield no symbols. See the current map guide and diagnostic report.
