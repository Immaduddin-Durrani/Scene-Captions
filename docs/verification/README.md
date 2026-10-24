# Phase 1 verification

Latest follow-up: [local film integration and caption coverage](library-2026-10-24/README.md).

Latest checks: [24 October model investigation and component cleanup](investigation-2026-10-24/README.md). Earlier results below retain their original scope.

Checked locally on macOS / Apple silicon with Node 25.2.1 and Google Chrome on 23 October 2026.

## Current sourced-caption result

The sample now uses 87 intervals from the licensed Demuxed sound-caption SRT, with unchanged timing and original text. See [caption provenance](../CAPTION_GENERATION_STATUS.md), sourced-caption-import.json and sourced-caption-checks.md. Twelve unit tests, schema validation, type checking and the production build passed. The browser checked every source interval plus preference controls, original captions, import, rehearsal and layout. Original 32-cue results and unavailable-track screenshots below are historical. The failed NVIDIA model remains blocked; its failure does not apply to this separate source-caption import.

## Earlier interface results

- Seven unit tests passed: cue interval boundaries/overlaps, fixed original behavior, scene adaptation without profile mutation, malformed annotation/profile rejection, representation fallback, validated event capture and bounded session buffer.
- Caption dataset validation passed (32 cues, nine variants per cue, explicitly draft).
- Type checking and optimized Next.js production build passed. Build output is saved in production-build.txt; tests in unit-tests.txt.
- Playwright CLI checked actual playback/pause, cue seeking and captions, fixed baseline, original override, draft/apply isolation, browser preference persistence, rapid consecutive keyboard seeks, opt-in rehearsal/export, fixed session media, local file import, cleared sample cues, invalid JSON, duration-mismatch suppression, valid JSON, the experimental-plan route, and a 390 px viewport without horizontal overflow. See browser-smoke.txt and scripts/browser-smoke.mjs.
- Visual screenshots inspected: desktop.png, mobile.png and experimental-plan.png. Final browser console had no errors or warnings. This is not a complete WCAG audit or real-device certification.
- GET /api/ping and HEAD /api/ping returned 200. The local video endpoint supports HTTP 206 byte ranges for seeking.
- Fallow 3.34.1 targeted src unused exports/dependencies. Five internal exports were reviewed and made private; the follow-up report has zero findings. No automated code deletion, hooks, cloud or telemetry setup.
- Graphifyy 0.9.92 used deterministic local extraction only: 21 files, 93 nodes, 187 edges. The two anonymous test/automation files without extracted symbols are documented in CODEBASE_MAP.md. No agents/providers ran.

## Issues found and fixed

- A cached video could deliver metadata before hydration effects completed. Resetting readiness in that effect left working media with disabled controls. Initialization now reads actual metadata readiness; browser regression checks cached reload and enabled playback.
- Consecutive keyboard seeks could read a stale React display time before seek events updated state. Keyboard seeking now uses the actual video currentTime; the browser regression checks immediate Right/Left returns to the same cue.
- Next.js dev automatically generated project agent rules on its first launch. The generated file was removed and agentRules: false configured; no startup rule injection remains.

## Skills used for this task

- agent-skills: incremental-implementation as the primary engineering workflow.
- inferya-design: initial interface foundation, frontend implementation guidance and interface accessibility guidance.
- domain-modeling: canonical cue/profile/baseline/rehearsal terminology in GLOSSARY.md.
- playwright-cli: representative browser checks and screenshots.
- systematic-debugging: metadata readiness and keyboard-seek races.
- markitdown: file-output text extraction of CapTune for a bounded check of its abstract/long-form limitation; full converted text kept in a runtime cache rather than dumped into context.
- graphify: local static codebase mapping, no semantic workers.
- fallow: targeted unused-export/dependency check, no automatic fixes or integrations.
- Sites: required local-only web-app workflow; no registration or publication.

No agents/subagents, background hooks, external model calls, deployment, paid generation, sign-ins or active MCP integrations were used. The local development process is a temporary preview, not an installed system service.

## Remaining study preparation

The team must create its own video and review all caption cues and variants against that exact edit. The bundled short-film cues are intentionally illustrative. No actual participant study, NIM pipeline, centralized storage or deployment was implemented or tested. Formal recruitment, consent, instruments and analysis require instructor approval. The prototype currently imports non-speech JSON only; a dialogue-containing study video additionally needs fixed verified dialogue subtitles in both conditions.
