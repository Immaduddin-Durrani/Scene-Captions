# SceneCaptions — Experimental plan

Phase 1 proposal · 23 October 2026

## Research question

Do personalized, scene-aware non-speech captions improve comprehension, perceived consistency and viewer control, while reducing reading effort during a continuous 20–30 minute story-driven video, compared with fixed original non-speech captions?

Hypotheses: personalized captions may reduce reported effort and improve control or consistency without reducing comprehension. These are predictions to test, not demonstrated benefits.

## Phase 1 demonstration

Deliver a running local player with fixed and personalized conditions, precomputed caption variants, persistent preferences, a preview, Show Original, readable text settings, a cue timeline, and opt-in rehearsal export. The team will create the study video. A short licensed sample and illustrative draft captions are included only to demonstrate the interface.

Phase 1 is a technical demonstration and a proposed experimental protocol. No study has been conducted. Rehearsal exports are not research evidence; sample cues are not verified soundtrack annotations.

## Participants and approval

Proposed recruitment target: 12–16 adult DHH participants (6–8 per condition), subject to recruitment feasibility and instructor/ethics approval. This is an exploratory feasibility sample, not a power-based confirmatory sample. Do not generalize to all DHH viewers or claim statistical power from this target.

Collect only relevant self-described hearing/caption-use background and preferred communication accommodations with consent. Offer written instructions, breaks, withdrawal without penalty, and accessible recruitment and consent materials. Final eligibility criteria, compensation, retention period and ethics route must be agreed before recruitment.

## Materials and annotation preparation

The team will make one rights-clear, story-driven 20–30 minute video, with a backup if feasible. Obtain permission for all people, music, sounds and visuals. Keep the exact edit unchanged across conditions. Include quiet, busy and off-screen-sound scenes, plus repeated sound types distributed across the runtime; do not distort the story just to favor the interface.

Create a cue list tied to that exact edit. For every cue, precompute an original caption and all nine detail-by-expression variants, sound key, scene-load tag, representation options and scene context. Human reviewers check sound correctness, timing, clarity, respectful language and same-sound consistency. Reviewers resolve disagreements before the study; record prompt/model versions if AI is used.

Have DHH collaborators review caption readability and study materials before the main study. If the video has dialogue, supply the same verified dialogue subtitles in both conditions, separately from the experimental non-speech captions. The current app imports non-speech JSON only; dialogue-subtitle support must be added before using a dialogue-containing study video. The bundled demonstration has no dialogue.

## Design and allocation

Primary proposal: a randomized, between-participants comparison. Every participant sees the same full video once. Randomly allocate participants approximately equally to fixed original captions or personalized, scene-aware captions. Balance recruitment/assignment by caption-use background where feasible and document the allocation method before collecting data. A between-participants design avoids replay and story-memory effects.

Fixed condition: original non-speech captions throughout. Personalized condition: a saved global detail/expressiveness profile, optional scene adaptation, preview and Show Original. Keep the video, dialogue subtitles if any, device, room, volume policy, caption readability controls and questionnaires the same across groups. Record actual preferences and opt-outs without treating them as protocol failures.

This compares the complete personalized experience with the baseline; it cannot isolate the effects of scene adaptation, preview or individual controls. A future within-person study of matched, distinct 20–30 minute videos with counterbalanced conditions could investigate these mechanisms. Do not replay the same story in two conditions and interpret the resulting comprehension scores as unbiased.

## Session procedure · approximately 45–65 minutes

1. Explain the study in the participant’s preferred accessible format, obtain approved consent, assign a pseudonymous ID, and record relevant caption background (5–10 minutes). Do not use the app’s rehearsal checkbox as formal research consent.

2. Run a practice clip excluded from the main analysis; teach common controls. In the personalized condition, let participants preview and choose preferences (3–5 minutes). Do not coach them toward a preferred setting.

3. Show the continuous 20–30 minute video once in the assigned condition. Keep pauses and breaks participant-controlled; log them. Avoid researcher prompts during viewing. If brief reading-effort probes are added at narrative boundaries, use the same planned points in both groups and acknowledge that they interrupt viewing.

4. Immediately administer the comprehension questions and post-viewing ratings (8–10 minutes). Ask open questions about confusing captions, consistency, fatigue, agency and settings changes (5–10 minutes). Offer a break or end the session at any time.

## Measures and instruments

Primary outcome: accuracy on a prewritten set of approximately 10–12 non-speech-event comprehension questions, sampled from the beginning, middle and end. Prepare answer keys from the actual soundtrack and story before recruitment; avoid questions answerable from dialogue or visuals alone. Prefer plausible multiple-choice options plus an ‘unsure’ choice. Pilot difficulty and ambiguity with the actual material.

Secondary exploratory outcomes: 1–7 ratings for reading effort, perceived same-sound consistency, perceived control and comfort; optional beginning/end fatigue ratings collected identically across conditions. These custom items are not a validated cognitive-load scale. Exact wording and anchors are supplied in the research plan and must be piloted.

Behavioral measures: preference changes, Show Original use, previews, seeks, pauses and session-relative timestamps. Counts describe use; frequent toggling alone does not prove confusion or preference. Qualitative interviews explore why. Keep all measures and scoring rules fixed before the main study.

## Analysis and reporting

Report recruitment, completion, exclusions and missing data transparently. For comprehension, report participant-level scores and descriptive group differences with uncertainty intervals where feasible. For ordinal ratings, show individual responses and medians/ranges; treat any inferential comparison as exploratory and choose the method before inspecting outcomes. Avoid causal claims about individual features.

Compare early/middle/late comprehension items cautiously; unequal question difficulty can mimic fatigue. Analyze fatigue changes only if measured comparably. Report effect sizes and uncertainty rather than declaring a design superior from a small sample or a single p-value. Account for multiple secondary outcomes and report null and negative findings.

Code interview responses using an explicit thematic coding procedure; have a second team member review codes if feasible and document disagreements. No automated or manual single-person pass should be called independent review. Relate themes to logs without deanonymizing participants.

## Data handling and stopping rules

Use pseudonymous IDs and minimal consented events. Keep the identity/contact list separate from study files. Agree an access-controlled research storage location, access permissions and deletion/retention date before the study. Do not send participant data, voices or faces to NIM or other model endpoints.

The app currently records a single rehearsal in browser memory only after opt-in and exports a JSON file on request. It has no shared database, authentication, approved consent capture or central upload. Reloading clears rehearsal data. Treat exports as sensitive and move any future approved research data into the agreed controlled storage; do not commit it to Git.

Stop or reschedule a session for distress, unreadable captions, major timing drift, a playback failure or a participant’s request. Predefine technical-exclusion criteria and record reasons; never exclude someone merely because they disliked personalization or performed poorly.

## Before the actual experiment

Confirm instructor/ethics approval and the participant target; complete and license the team’s video; review captions and questions with DHH collaborators; run a small technical/usability pilot; resolve caption errors; finalize allocation, instruments and analysis; confirm accessible recruitment and data storage. Freeze the study app and annotation version before recruitment.

NVIDIA NIM and ffmpeg are optional for future offline generation; no model is called while viewing. The Phase 1 demonstration needs no API key, cloud account, database or deployment. If hosted later, video must stream from an external host and research logs need a controlled persistent store.

## Draft rating instrument

- How much effort did reading the captions take?
  1 = Very little; 7 = Very much. Intermediate values are unlabeled; allow a skipped answer.
- How consistent did captions for recurring sounds feel?
  1 = Very inconsistent; 7 = Very consistent. Intermediate values are unlabeled; allow a skipped answer.
- How much control did you feel over the captions?
  1 = Very little; 7 = Very much. Intermediate values are unlabeled; allow a skipped answer.
- How comfortable were the captions to read?
  1 = Very uncomfortable; 7 = Very comfortable. Intermediate values are unlabeled; allow a skipped answer.

## Proposed interview prompts

- Which sounds were easy or difficult to understand?
- Did recurring sounds feel consistently described? Give an example.
- Did reading become more tiring as the video progressed? When?
- Did you feel able to control or ignore personalization?
- What would you change before using this for a full film?

## Primary research source

Huang, Jeremy Zhengqi; de Lacerda Pataca, Caluã; Wu, Liang-Yuan; Jain, Dhruv (2025). *CapTune: Adapting Non-Speech Captions With Anchored Generative Models*. ASSETS ’25. https://arxiv.org/abs/2508.19971 . Local PDF: docs/research/huang-2025-captune.pdf.

CapTune motivates personalization and identifies longer-form content as untested. It does not validate this proposed protocol, sample size, scene-load heuristic or custom effort measures. CuCap and Interpretive Caption are adjacent speech-focused work; their quantitative findings are not evidence for our non-speech mechanism.
