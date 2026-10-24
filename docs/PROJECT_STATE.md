# Current project state

Last updated: 24 October 2026, after player fixes and controlled model diagnostics. This is the current handoff summary; historical audit findings remain preserved. See [the fixes report](audits/2026-10-24-fixes.md) for current outcomes.

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

See [the original audit](audits/2026-10-24.md), [fixes report](audits/2026-10-24-fixes.md), and [fresh evidence index](verification/fixes-2026-10-24/README.md).

- Fresh verification: 13 Node tests and 14 offline Python tests passed; type checking, 87-cue validation and the production build passed on Windows with Node 24.21.0. Retry/timeout tests are simulated; a separate two-process pacing check passed without API calls.
- Chrome regression checks passed for all 87 source intervals after actual seeks, play/pause, original/baseline, preference persistence, imports, rehearsal/export and the plan route. This does not establish continuous-play timing accuracy or sound truth.
- Production dependency advisory check reported zero known vulnerabilities. This is not proof of supply-chain security.
- Fixed and browser-checked: draft preference loss/readability collapse, detail exceeding the maximum, missing starting original-override state, preview not actually trying the candidate, and elapsed export time increasing after recording stopped.
- Windows ZIP extraction now uses the installed PowerShell/.NET ZIP reader; the cached official archive extracted successfully and matched the expected video hash. Existing video files are also hash-checked before reuse.
- Seven verbose effect entries were shortened locally without adding facts or changing timing. The worst highlighted simultaneous-cue rich text fell from 68 to 28 characters in the same 0.541 seconds; it still needs reading review. The authoring heuristic flags 206 original/variant cases above 20 characters/second; this is not a validated DHH threshold.

The working track remains licensed/source-anchored with locally edited wording. Failed model candidates were quarantined under ignored artifacts. The experimental-plan source and both exported copies now describe current behavior and the outstanding model limits. Existing decision history and original proposal documents are preserved.

## Maps and audit freshness

- `docs/codebase-map.json`, `docs/codebase-map.html` and `docs/codebase-map-inputs.json`: refreshed deterministic source map, with per-file hashes and scope. See [the map guide](CODEBASE_MAP.md) for unmodeled boundaries. Hashes, not just Git HEAD, establish freshness because changes are uncommitted.
- `graphify-out/graph.json`, `graphify-out/graph.html` and `graphify-out/GRAPH_REPORT.md`: separately refreshed broad local code-only scan, including structured JSON/evidence. No semantic document/media indexing or agents. These ignored outputs may be absent in another checkout.
- Fresh Fallow results: `docs/verification/fixes-2026-10-24/reports/fallow-*.json`. Six unused-file candidates are manually invoked/historical utilities, not deletion proof. Seven clone groups include overlapping historical browser scripts; review the report's scope before refactoring. No unused dependencies/exports or cycles were reported.
- There are currently no configured architecture boundary rules. A zero architecture finding count does not mean those boundaries were measured.
- Fallow health also flagged 13 heuristic findings, concentrated in dense UI components; its health gate is not clean. See the fixes report for recommended focused refactoring. Python rate/retry helpers were verified separately; Fallow's JS/TS health is not a Python audit.

After structural changes, refresh an authorized local map or mark it stale and state what changed. After a substantial audit/milestone, run an authorized targeted Fallow check when useful. Save source revision/input coverage, command, results and limitations; never install automatic hooks or watchers to satisfy freshness.

Historical audit scripts remain under `scripts/verification/audit-2026-10-24/`; current acceptance checks are under `scripts/verification/fixes-2026-10-24/` and `scripts/browser-smoke.mjs`. Earlier reports retain their execution-time paths. Temporary full-paper extracts and model/audio caches remain in ignored artifacts. Use the documentation index rather than moving established files for cosmetic consistency.

## Next work

User media preparation is now complete (24 October): both titles have H.264/AAC video, posters and English VTT files. Local hashes match the generated records. Sintel: 1280x544, 888.032 seconds; Tears of Steel: 1280x534, 734.167 seconds. See [verification](verification/fixes-2026-10-24/reports/local-media.json). Listening and subtitle-timing review are still pending. The two requested pending limits remain: model caption/audio quality gates have not passed, and the saved Fallow report's component-complexity findings remain unresolved. No new model/Fallow run was performed for this push.

720p follow-up: the user rejected the initial 480p preparation setting. The helper now preserves the official 720p-release picture dimensions, reuses completed source downloads, and rebuilds lower-resolution/incomplete browser copies. Replacements are checked before publication; posters regenerate when the video is rebuilt. PowerShell syntax and four simulated checks passed (matching dimensions accepted; 480p, missing audio and truncated duration rejected). The user completed film preparation; no film download or conversion was run by the agent.

Local-media preparation: the user explicitly requires agents to provide PowerShell commands instead of downloading films themselves. `scripts/media/prepare-library.ps1` prepares optional Sintel/Tears of Steel browser MP4s with audio, posters, available English subtitles and provenance records when the user runs it. See [the local media guide](LOCAL_MEDIA.md). The user completed the downloads/conversions; local output checks passed as recorded above. The app still has one built-in caption-ready sample; additional-title selection, dialogue playback and reviewed per-title sound captions remain pending.

Map freshness: the saved maps predate the new `scripts/media/prepare-library.ps1` helper and do not cover it. Existing Fallow reports also predate this addition. No new Graphify/Fallow invocation is authorized by this prompt; treat the saved results as the earlier snapshot, not verification of the new helper.

For the prepared local catalogue, obtain and review corresponding sound-caption material, then implement selection without mixing tracks across titles. Keep downloads outside Git, show actual durations and label missing/unreviewed caption features honestly. Do not expand into Phase 2 streaming/services during this demo work.

Use the working source-caption demo for the submission. Further model work must be a bounded diagnostic or a justified replacement-method evaluation; do not resume full-film generation on the failed setup. Before research, complete listening/readability review, DHH feedback, final study video/questions, and instructor/ethics approval. A script/scene log can support annotation but must not be fed as the expected answer to an allegedly independent sound check. No benefit or participant result has been established.
