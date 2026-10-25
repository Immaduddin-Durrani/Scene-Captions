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
