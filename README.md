# SceneCaptions

Adaptive non-speech captions for Deaf and hard-of-hearing (DHH) viewers of long-form video.

## Starting or continuing work

Read this README, [architecture.txt](architecture.txt) and the required
[skill workflow](docs/SKILL_WORKFLOW.md) first. Then read the
[current project state](docs/PROJECT_STATE.md) and
[latest fixes and diagnosis](docs/audits/2026-10-24-fixes.md) for current decisions,
verified findings and unfinished work. Use [the glossary](GLOSSARY.md)
for domain meanings and the experimental plan for study details.
The [documentation index](docs/README.md) explains where each kind of file belongs.

Inspect fresh Graphify maps and relevant Fallow reports before broad source
exploration; use them to identify affected files, then inspect those files
and tests before editing. Maps and scans are bounded snapshots, not proof
of runtime behavior or caption quality. Refresh them when justified and
authorized for the current task, or clearly mark them stale. See the
current-state page for snapshot locations and known coverage gaps.

No automatic skill activation, agents, paid services, publishing or hooks
are authorized by these documents. Keep all model generation outside playback.

## Phase 1: run the prototype

Requires Node.js 22.13+, npm and a modern browser. Windows uses its installed
PowerShell ZIP reader; macOS/Linux require unzip. No API key is needed for playback.

```sh
npm ci
npm run setup:demo
npm run dev
```

Open http://localhost:3000 for the working player and
http://localhost:3000/experiment for the experimental plan.
The licensed sample video downloads once; your team's own video can be
opened locally with matching precomputed caption JSON. Nothing is uploaded.

Deliverables and demonstration steps: [Phase 1 handoff](docs/PHASE1.md).
Research protocol: [Experimental plan](docs/EXPERIMENTAL_PLAN.md).
Own-video preparation: [Caption import guide](docs/CAPTION_IMPORT.md).
Optional short-film downloads and local resources: [local media guide](docs/LOCAL_MEDIA.md).
The user runs video downloads; agents prepare commands and code only.
The sample now includes 87 timed non-speech caption cues from the licensed
[Demuxed caption track](https://github.com/demuxed/big-buck-captions), with
source-anchored wording variants and cue-density adaptation. No API key is
needed. See [caption provenance and checks](docs/CAPTION_GENERATION_STATUS.md).
The study still needs a full caption review against your team's own video.
Offline model preparation is separate: see [the tooling guide](scripts/generation/README.md).
Current model trials have not passed caption-generation/audio-corroboration quality gates.

## Team
- Zuhair Amirali Merchant (29021)
- Muhammad Hamza Kashif (29022)
- Immaduddin Durrani (29204)

## Problem
Non-speech captions (e.g. "[soft piano music]") are authored once, in one fixed
style, for every viewer. DHH viewers differ in how much detail and expressiveness
they want, and prior customizable-caption research has only been tested on
short 2–8 minute clips — not on full episodes or films, where consistency,
pacing, and cumulative reading effort matter.

## Research Question
How can personalized non-speech captions adapt across long-form, story-driven
video while staying consistent, understandable, and under the viewer's control?

## What We're Building
A Next.js web video player for one full TV episode or a licensed 20–30 minute
film, with:
- **Persistent caption profile** — set detail/expressiveness once, holds for the runtime
- **Scene-aware adaptation** — captions shorten/simplify in fast action, expand for quiet or off-screen sound
- **"Show Original" toggle** — one tap back to the creator's caption
- **Preview pane** — see how a caption reads before committing to a setting

## Scope
Non-speech sound captioning for story-driven video only — not general subtitling,
not live captioning, not speech/paralinguistic styling. The viewer uses precomputed caption variants supplied as JSON. CapTune engine reuse remains unverified; it is
not integrated into this prototype.

## Tech Stack
- Frontend: Next.js (React)
- API: Next.js GET/HEAD health route; no model calls or participant uploads
- Caption data: licensed sound-caption SRT converted to validated JSON, with local video/JSON import
- Future generation: local-only ingestion; CapTune reuse versus NIM prompts
  remains an open decision. Generation never runs during viewing.

## Status
Working local captioned player and proposed experimental plan.
The team will create the study video. Proposed sample size, recruitment,
instruments and ethics require instructor approval; no participant study has run.

---

## Related Work

The detailed figures below are retained proposal notes. Unless verified
against the collected source, treat them as [UNVERIFIED]. See
[research index](docs/RESEARCH_INDEX.md) for retrieved papers and limitations.

### CapTune — the most directly relevant paper
The closest neighbor to this project: non-speech captioning, customization,
creator-viewer negotiation. Its core gap is exactly our research question —
its own limitations section states its evaluation used clips of 2–8 minutes,
and that longer content "introduces additional challenges related to narrative
consistency, viewer fatigue, and cumulative comprehension" that it did not
address.

**Findings** (12 DHH participants, 7 caption creators — small qualitative
samples; treat counts as indicative, not generalizable):
- 9 of 12 viewers felt customization enhanced engagement.
- 9 participants wanted **persistent user profiles** so settings carry across videos.
- 7 participants wanted **preview/comparison before committing** to a setting.
- 6 participants found the 10×10 detail/expressiveness grid too dense or hard
  to navigate; subtle changes (e.g. 3→4) weren't perceptible.
- 8 participants said dense/fast captions were hard to follow in fast-paced scenes.
- Participants (P2 specifically) wanted richer captions for **off-screen sound**.
- 7 participants were uncomfortable with captions feeling too *interpretive*
  (e.g. "the movie is thinking for me"), wanting to preserve their own meaning-making.
- **Consistency problem:** identical sounds (e.g. [Dolphin whistles]) were
  sometimes captioned differently at different points in the same video — a
  real risk for long-form content.
- Onomatopoeia had mixed reception; 5 of 12 found it ambiguous or (for one
  Deaf participant) inaccessible due to unfamiliarity with how sounds "are
  supposed to sound" phonetically.
- 4 of 7 creators wanted scene-specific (not just global) parameter control.

### CuCap — relevant for design principles, not content
**Important accuracy note:** CuCap is *not* about non-speech captions. It's
about visualizing *speech prosody/emotion* (loudness, pitch, rhythm, valence,
arousal) through typography (font size, color, weight) — a different
captioning problem than sound-effect captions. Its specific percentages
should not be cited as evidence about non-speech sound.

**Findings** (49 participants: 28 North American, 21 South Korean):
- Valence → font-color was the most common mapping in both groups.
- Statistically significant cultural difference: pitch was chosen by 21% of
  NA participants vs. 52% of Korean participants (p=0.04).
- Arousal (61% NA vs. 84% Korean) and loudness (63% NA vs. 76% Korean)
  differences were **not statistically significant** (p=0.21, p=0.36) — not
  confirmed cultural differences.
- Generalizable design recommendations: **progressive disclosure** (a small
  set of toggles first, advanced options later), **sensible defaults with
  room for override**, and **genre-based presets**.
- Some participants disliked customization entirely and preferred
  conventional, unstyled captions.

**What transfers to SceneCaptions:** the *design philosophy* (progressive
disclosure, defaults + override, genre templates) — not the specific
parameters, since we are not doing speech-prosody styling.

### Interpretive Caption — smallest, least directly applicable
Also a different problem space: real-time *speech emotion* tagging for live
STEM lectures (via Whisper + Wav2Vec2), not non-speech sound captioning, and
not long-form pre-recorded story-driven video.

**Findings** (8 DHH participants, qualitative, single ~30-minute session —
explicitly early-stage/exploratory; no formal cognitive-load measurement,
e.g. NASA-TLX was not used):
- Emotion classifier accuracy was ~73%; Whisper WER was ~5.5% on a benchmark
  (not on the authors' own live data).
- **Hover-based, on-demand disclosure** of extra information was well
  received as less visually cluttering than prior always-visible
  color/font-coded systems.
- Segmenting captions into short chunks (Miller's "magic number") helped
  readability for some, felt "choppy" to others.
- Emotion-recognition accuracy dropped for accented speech.

**What transfers to SceneCaptions:** the on-demand disclosure pattern is a
useful UI idea for optional detail — but this paper does not validate
anything about non-speech sound captions or full-length video, so it should
not be cited as evidence for our core mechanism.

---

## Features Backed Directly by Existing Findings
Low-risk to build — each is grounded in a specific finding above:
- Persistent viewer-level detail/expressiveness profile (CapTune: 9/12 wanted this)
- Preview before committing to a setting (CapTune: 7/12 wanted this)
- One-tap "Show Original" fallback (CapTune's opt-out concern + CuCap's
  "some prefer conventional captions")
- Simpler captions during fast/dense scenes, richer captions for off-screen
  or ambient sound (CapTune's cognitive-load and off-screen findings)
- Avoiding redundant captions of clearly visible actions (CapTune: 5/12 flagged this)
- A simplified control scheme (2–3 presets/sliders, not a 10×10 grid) —
  CapTune's grid was explicitly criticized as too dense
- Progressive disclosure of advanced controls (CuCap's design recommendation)

## Open Questions — What We're Actually Testing
None of the three papers tested full-length content, so these are genuinely
unanswered and are this project's real contribution:
- Does a **persistent profile** actually feel consistent across 20–90
  minutes, or do preferences drift by act/scene?
- Does **reading fatigue** compound over a full episode the way it might not
  in an 8-minute clip?
- Does the **consistency problem** CapTune flagged (same sound, different
  caption) get worse at scale, and does "lock"/caching per sound-type fix it?
- Do viewers want scene-level overrides on top of a global profile (creators
  wanted this in CapTune; untested from the viewer side)?
- Does onomatopoeia's mixed reception change over a longer viewing session as
  viewers "learn" a video's caption vocabulary?

## Things We Can Experiment With
No prior evidence either way — open design space:
- Whether a coarser 3–5 point scale (instead of a fine-grained slider)
  reduces the "can't tell the difference" problem CapTune's participants hit
- Whether hover/on-demand disclosure (loosely borrowed from Interpretive
  Caption's pattern) helps viewers understand *why* a caption changed
- Whether genre-based starting presets reduce onboarding friction before
  viewers tune manually

---

## References
- Huang, de Lacerda Pataca, Wu, Jain. *CapTune: Adapting Non-Speech Captions
  With Anchored Generative Models*. ASSETS '25. arXiv:2508.19971
- de Lacerda Pataca et al. *CuCap: Comparative Analysis of Customized Captioning
  between North American and South Korean d/Deaf and Hard-of-Hearing Users*.
  ASSETS '25. doi:10.1145/3663547.3746400
- Ubur, Adewale, Donekel Chandrashekar, Akli, Gracanin. *Interpretive Caption:
  Real-Time Vocal Emotion Cues for DHH Users*. ASSETS '25. doi:10.1145/3663547.3759697
