# SceneCaptions skill workflow

This is the project's required method for selecting and using skills. Use the relevant skills effectively, efficiently and selectively to support the HCI research and final web application. Merely invoking a skill is not evidence that a decision, interface or implementation is good.

## Goal and boundaries

SceneCaptions investigates personalized non-speech captions during longer, continuous, story-driven viewing by Deaf and hard-of-hearing (DHH) people. The product must support understandable captions, consistency across recurring sounds, manageable reading effort and meaningful viewer control. Benefits remain hypotheses until evaluated.

The intended web application combines persistent caption preferences, context-sensitive adaptation, preview before applying preferences, and an immediately available original-caption override. Compare the experience with a fixed-caption baseline using a justified, accessible experimental protocol.

First-submission requirements are a running application and an experimental plan. During the 24 October audit, the team also requested automated generation, retained the disclosed density proxy and selected viewer detail as a maximum. The agreed preparation path starts from existing timed sound captions and separately checks the corresponding audio. Tooling does not establish model suitability: current model-output/corroboration quality gates have not passed. Keep proposed capabilities separate from implemented and tested capabilities.

All generation stays outside playback. Only precomputed captions are selected while viewing. Preserve rights-clear media, source provenance, private keys, accessible controls and research-data boundaries. Cue density does not establish visual complexity, off-screen importance or cognitive load. A working short demo does not test the longer-form hypothesis.

## Permission and efficiency rules

1. For each new user task, use only skills explicitly requested by name or subsequently approved for that task. This document records planned responsibilities; it is not standing permission to activate skills. Earlier installation or approval does not carry forward to a new task. Higher-priority requirements still apply.
2. Announce the selected skills, their bounded purpose and any required dependencies. Read their actual instructions before use. For consolidated entries, choose the specific internal workflow rather than running the whole suite. If an additional dependency requires approval, disclose it before activation.
3. Work in the main session. Never launch, resume or delegate to agents, external workers or model-powered tools that execute actions without the user's separate delegation request, usage warning and affirmative confirmation. Skill permission, an API key and a model labelled agentic do not authorize agents.
4. Reuse existing decisions, maps, source checks and saved results when they are still applicable. Check freshness and changed files first. Avoid repeated whole-repository scans, unnecessary document conversion, competing design processes and broad model comparisons without a specific unresolved question.
5. Run checks that match the risk and change. Repeat or broaden them when new changes, failures or uncertainty justify it. Keep stdout/stderr and exit status for important automated checks, and identify historical results as historical.
6. Do not automatically install hooks, persistent watchers, MCP connections, integrations or global configuration. Do not enable telemetry, paid generation, publishing or deployment as a side effect of a skill workflow.
7. Use simple language when asking the team to decide something. Find facts in the files, code or appropriate primary sources first; ask about choices, not facts that can be checked. Separate a recommendation from an approved decision.

## Required specialist responsibilities

Each skill below is required when its responsibility is needed and its use is authorized for the current task. They are not all required for every small edit.

| Skill | When to use | How to use it in this project | Required result or evidence |
| --- | --- | --- | --- |
| `grill-with-docs` | At a major research/product decision, before a substantial implementation whose behavior is unclear, or when proposal, code and experiment disagree. | Read the proposal, architecture, glossary and relevant code. Work through decisions in dependency order using short questions and clear recommendations. Its interview/domain-modeling dependencies are part of its declared workflow; adapt any delegation instructions to the main-session rule. Confirm shared understanding before implementing decisions. | Agreed answers, unresolved choices and their implications. Update resolved terminology immediately. Record only consequential trade-offs as decisions; do not invent agreement. |
| `domain-modeling` | When defining or changing cues, sound keys, profiles, variants, source captions, adaptations, conditions or study events. | Stress-test terms with concrete examples: overlapping sounds, the same sound in different scenes, an Essential profile in a sparse passage, original override during adaptation, and source text that was not authored by the filmmaker. Compare definitions against actual schemas and consumers. | A concise `GLOSSARY.md` containing domain meanings, not implementation notes. List contradictions and resolve them explicitly. Add a small ADR only when the decision warrants one; maintain crucial architecture decisions in the append-only log. |
| `agent-skills` | When selecting engineering methods for a feature, audit, schema change, integration, security review, performance concern or release preparation. | Select a bounded workflow such as code review/quality, incremental implementation, API/interface design, security/hardening or launch readiness. Review correctness, readability, architecture, security and performance. Use the existing stack and make focused changes. The name does not mean spawning agents. | Clear acceptance criteria, reviewed boundaries, justified changes and relevant verification. Record selected internal workflows and limitations. Do not use a generic checklist as proof that a feature works. |
| `inferya-design` | For the initial design foundation, an authorized interface audit, or a meaningful change to captions, settings, previews, overrides or viewer feedback. | Choose one appropriate workflow for the viewing/settings experience. Begin from `DESIGN.md`, real caption content and existing tokens. Inspect the rendered interface, long/multiline captions, error/empty/loading states, keyboard focus, responsive layouts, contrast, readability and draft/applied state. Review appearance in the context of the actual task; avoid decorative defaults and competing full redesigns. | A coherent, understandable interface with a documented reason for significant choices. Save representative screenshots and verified findings. Treat automated style warnings as candidates, not objective UX judgments. Do not claim a complete accessibility audit from screenshots or a detector score. |
| `context7` | When a current Next.js, React or library behavior affects a decision or implementation and needs documentation verification. | Resolve the official library, choose the installed version when indexed, and query one focused question. Verify version gaps against installed code or current primary documentation. Send generic technical questions, not private source, keys or participant data. | Source links, queried version and the verified implication for this code. Report failed requests or missing version coverage honestly. Do not query simply to tick a skill box. |
| `playwright-cli` | Before accepting changes to playback, captions, controls, profile persistence, imports, rehearsal/export, or responsive behavior; also for a submission rehearsal. | Test the running application, not only isolated functions. Exercise play/pause, seeking both ways, cue start/end and overlaps, baseline/original override, draft/apply separation, reload persistence, malformed imports, duration mismatch, media failures and keyboard operation. Test desktop and narrow layouts; distinguish viewport checks, synthesized touch and real-device checks. Keep evidence for the current version. | Repeatable checks, actual results, console/network findings and representative screenshots. Validate exported contents, not only that a download exists. A successful seek test does not prove continuous-play timing, sound correctness or reading-time suitability. |
| `systematic-debugging` | Whenever playback, synchronization, ingestion, setup, persistence, build or tests fail or behave unexpectedly. | Reproduce the failure, inspect messages and recent changes, trace the value/state across boundaries, compare a working case, and test one root-cause hypothesis at a time. Write a meaningful failing reproduction before fixing. If repeated fixes fail, reconsider the underlying design. | The reproduction, established cause, focused fix and regression evidence. No speculative patch bundles, silent fallbacks or claims that a failure is fixed because unrelated tests pass. |
| `graphify` | From the first working app onward, during an authorized architecture/impact investigation, and after substantial structural changes when a refresh is requested. | Prefer local deterministic code extraction. Trace player, caption selection, profile/preview state, schemas, offline ingestion and rehearsal boundaries. Check the map's freshness and confirm important relationships in source. Preserve extracted vs inferred evidence and coverage limits. Do not rebuild an unchanged map or enable semantic providers/watchers automatically. | A usable code relationship map/report with scope, inputs and gaps. A graph does not prove complete React data flow, runtime behavior, security or research validity. |
| `fallow` | Occasionally after substantial audits, major milestones, structural changes or before release, when explicitly requested for the task. | Use targeted local dead-code, dependency, duplication, cycle, complexity or security-candidate checks. Verify framework entry points, manually invoked scripts and external consumers. Explain what was actually measured; absent boundary rules mean boundaries were not checked. | Reviewed findings, false positives, actionable cleanup and retained limitations. No blind deletion, automatic fixes, extra setup or constant rescanning. Fallow complements Graphify; it is not a substitute for mapping or behavior tests. |

## Presentation and identity skills

Branding, banners and slides are separate deliverables used when requested. Establish reusable assets once, then update them only for a concrete need. They must not delay a functioning player, accurate captions or a defensible experimental plan.

| Requested work | Skill to select explicitly | Purpose and limits |
| --- | --- | --- |
| Product identity, logo direction, voice and consistent messaging | `brand` and, when needed, a specific `design` workflow | Establish an identity appropriate to an accessible research product. Reuse the approved identity. Do not manufacture accessibility benefits, endorsements or participant outcomes. |
| A banner, poster or other promotional image | `banner-design` | Use correct dimensions, honest copy and approved identity. Disclose image-generation dependencies before using them. One banner task does not authorize a website redesign or publication. |
| Submission/research presentation | `presentations` for PowerPoint/Google Slides, or `slides` for an HTML presentation, according to the requested format | Explain the HCI problem, verified related work, research gap, product, method and limitations. Keep proposal, implemented behavior and actual results distinct. Do not invent experiment results. |

These optional assets do not require all presentation/branding skills together. Use the smallest appropriate set. Image generation, external services and publishing require their own applicable authorization; naming a branding task does not authorize agents or paid generation.

## Order of work for a major milestone

1. **Set the question and acceptance criteria:** establish what the research or prototype must demonstrate. Resolve consequential uncertainty with `grill-with-docs`; sharpen affected terms with `domain-modeling`.
2. **Understand the existing implementation:** use current maps and source first. Use `graphify` for the requested structural questions and `agent-skills` to select appropriate engineering review. Consult `context7` only for live library questions.
3. **Check the viewing experience:** use `inferya-design` on the real player and controls, with representative short, long and overlapping captions. Prioritize comprehension, readability and control over visual novelty.
4. **Reproduce and repair:** use `systematic-debugging` for observed failures. Implement agreed changes in small, reviewable steps. Preserve the working demonstration while evaluating any new generation path separately.
5. **Verify:** combine relevant unit/schema/build checks with `playwright-cli` behavior checks. After a major milestone, use an authorized targeted `fallow` pass where useful. Refresh the graph only when structural changes justify it and current-task approval covers it.
6. **Align the research materials:** make the experimental plan describe the intended manipulation accurately. Record what the prototype does, what is only proposed, what needs participant/instructor review and what the tests cannot establish.
7. **Package the submission:** rehearse from a clean checkout, confirm startup steps, present the running app and experimental plan, and prepare optional presentation assets if requested. Hosted launch is a separate task.

## Model use is separate from skill use

Skills guide the work; caption models generate candidate data. A model call is not evidence that a skill was used well, and a model response is not sound ground truth. Use [the NVIDIA shortlist](integrations/NVIDIA_MODELS.md) to select bounded tests, not to activate every available model. Keep caption rewriting, sound detection and visual-context interpretation as separate capabilities with separate acceptance checks.

## File organization and maintainability

Follow [the documentation and ownership index](README.md) and architecture section 0c. Keep domain rules in `src/lib/`, viewing/settings components in `src/components/`, and Next.js entry points in `src/app/`. Offline model/media tools belong in `scripts/`, not the web application's runtime imports. Keep reusable tests in `tests/` and manually invoked browser-check utilities under `scripts/verification/`.

Keep a single authoritative document for each subject. Put dated audit findings in `docs/audits/`, service/model notes in `docs/integrations/`, research/proposals in `docs/research/`, and dated evidence under `docs/verification/`. Separate reports, screenshots and sample exports inside each evidence run. Temporary derived files and caches belong in ignored `artifacts/` or the designated cache folder. Do not create duplicate status documents or scatter code among evidence files.

Create a new folder or abstraction only when it gives related files a clear owner. Use descriptive names, preserve established conventions and update relative links, output paths and handoff pointers when moving files. Preserve raw historical logs; describe relocated paths in an evidence index. Mark affected maps/reports stale rather than silently rewriting their recorded results. Verify links and moved scripts without rerunning unrelated checks.

Never weaken the failed audio-model gate to make a demonstration appear complete. Preserve source timings and provenance, validate generated structure, review unsupported sound/mood claims, check reading time, and require reviewed annotations before participant research. No NIM/LLM call belongs in the viewing path.

## How to record effective use

Maintain `docs/PROJECT_STATE.md` as the current handoff, with a link to the latest audit and the locations/coverage of saved maps and Fallow reports. Read fresh snapshots first to narrow investigation, then inspect affected source and tests. After meaningful changes, refresh authorized snapshots or label them stale, and update the current findings/decisions. Historical committed maps and old green test logs must not be presented as current verification. See architecture sections 0b, 12, 13b and 15a for the same operating requirements.

For each substantial task, record in its audit or verification note:

- The goal, named skills actually used and selected internal workflow where relevant.
- The evidence inspected and decisions made, including who approved unresolved research choices.
- The specific findings and changes; separate defects from preferences and research hypotheses.
- Checks run, results, source/documentation versions and evidence paths.
- Unverified limits, false positives, unavailable capabilities and remaining work.

Do not claim a skill was executed because a file with its name exists, that all tests passed when only some ran, or that review was independent when it happened in one session. Efficient, selective use with traceable evidence is the requirement.
