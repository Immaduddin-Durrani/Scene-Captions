# Caption-free NIM counterfactual tests — 26 October 2026

**The new tests do not clear the sound-caption gate. No independent NIM track was installed.** Novel speech transcribed correctly again, but the service also described a sustained tone on digital silence. Water-related responses offer partial recognition, not reliable rain identification or temporal grounding. Provider capacity errors prevented several matched comparisons.

This batch tested research-motivated audio swaps, known silence and shifted natural sounds. It comprises **12 explicit single-attempt requests: six HTTP 200, five HTTP 503 and one timeout**. No paid service, other provider, agent, new model installation, push or deployment was used. The existing source-assisted draft remains separate from this experiment.

## Inputs and method

- [Frozen protocol](protocol.json), [initial input manifest](inputs/manifest.json), [sources](inputs/sources.json), [PCM measurements](pcm-health.json).
- [Source attribution and license](control-attribution.json). ESC-10 is the CC BY subset of ESC-50; the two original recordings are credited as CC0 in the pinned dataset LICENSE. Local derivatives remain ignored under `artifacts/`; they were not bundled into the application.
- Ten-second mono 16-kHz PCM16 WAVs; 160,000 samples each. Same WAV bytes in audio-only and split audiovisual requests. Case names were blinded. Expected categories, movie title, plot and source captions were absent from all requests. A simple label-leak check supplements inspection of the saved prompts; it is not a universal leakage detector.
- c01/c02 contain the same five-second dog source at offsets 1/4 s. Its nonzero support is actually **3.2291875–3.586625 / 6.2291875–6.586625 s**, because the source itself has silence. The shift is exactly 48,000 samples. c03 rain has nonzero support approximately 1–6 s; c00 has no nonzero samples. These are signal support measurements, not human event-boundary annotations.
- The same BBB opening picture accompanies every audiovisual case: H.264, 512 pixels wide, 2 fps, ten seconds, video-only stream, no original soundtrack, subtitle/data streams, chapters or metadata. The separate WAV is explicitly designated as sound evidence.
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, `audio_url` and optional `video_url`, one user message, audio first, then picture, then instructions. Temperature 0.2, top_k 1, max_tokens 4096, thinking off initially, no reasoning_budget, nonstreaming. 180-second timeout, one attempt, shared 2.05-second start pacing. These are tested client settings, not verified account quotas.

## Results and interpretation

| Case | Actual result | Interpretation |
| --- | --- | --- |
| Dog c01, audio | Timeout ~181 s | Inconclusive. |
| Shifted dog c02, audio | 503, worker limit 16/16 | Inconclusive. |
| Rain c03, audio | Water splashing 0–6 s; silence 6–10 s | Broad water relationship, not strict rain; activity starts in known zero padding. Wrong root JSON shape. |
| Dog c01, split AV | Electronic tone 8.5–10.5 s; beep/click 0–0.1 s | Incorrect category, activity in digital silence and impossible end beyond clip. Wrong JSON shape. |
| Shifted dog c02, split AV | Rustling leaves and wind, both 0–10 s | Misses target; activity in known digital silence. Wrong JSON shape. |
| Rain c03, split AV | 503 capacity | Inconclusive. |
| Digital silence c00, split AV | Sustained electronic tone 0–10 s | Definite false positive on all-zero audio; malformed structure as well. |
| New speech control | “17 blue lanterns are beside the window.” | Positive transport/ASR result, explicit `stop`; not proof of non-speech accuracy. |
| Simple-prompt dog/rain, audio | Both 503 | Removing timing/JSON demands remains untested semantically. |
| Thinking + simple dog, audio | 503 | Inconclusive. |
| Thinking + simple rain, audio | Continuous roar of turbulent water | Broad water relationship; fails to acknowledge silent sections. No matched successful thinking-off result, so reasoning benefit is unknown. |

Raw reports: [initial eight](reports/run-01.json), [simple-prompt follow-up](reports/simple-followup.json), [thinking follow-up](reports/thinking-followup.json). Each input manifest was saved before its own requests; the initial protocol was not rewritten to accommodate later outcomes. Reports redact inline media into hashes/lengths and do not include credentials.

The [initial assessment](assessment.json) is preserved. The [audited assessment](reports/assessment-audited.json) additionally enforces manifest binding and explicit speech completion. All four HTTP-200 structured sound responses have invalid root shape. Their absence from strict category scoring is **not a 0% semantic-accuracy estimate**. This report's raw-response interpretation is manual review in the main session, not independent review. Water responses receive partial semantic credit in the narrative even though they fail the requested structure/category.

No correctly identified timed dog pair exists, so the +3-second temporal test is **unscorable**. Audio-only dog requests did not yield answers; we cannot measure how much adding video changed recognition on a successful matched pair. A combined-path false positive is established, but a causal estimate of visual bias in this batch is not. Public ESC-10 exposure, a brief dog burst, two natural source clips, one picture and absent human listening annotations limit generalization.

## Audit, tests and code health

Applied the four explicitly requested workflows locally: `systematic-debugging`; `agent-skills` using its code-review-and-quality workflow; deterministic Graphify; and Fallow. No automatic chaining or delegated review was used.

Required acceptance fixes, with regression coverage:

1. The shared JSON parser accepted a missing/null finish marker. It now requires explicit `finish_reason: "stop"`; parseable truncated content cannot pass.
2. Counterfactual speech scoring could count the expected text without verifying normal completion. It now rejects incomplete, missing or unusable speech responses.
3. Counterfactual scoring did not bind the report to its protocol's manifest. Mismatched experiments now fail before scoring.
4. New temporal validators reject absent fields, booleans, NaN/infinity, reversed/zero-length/out-of-range intervals. Explicit null/null remains uncertainty, not timing success.

The [check records](reports/checks.json) and logs show **35 Python offline tests, 19 Node application tests, TypeScript checking and caption-data validation passing**. The latter validates structure of the existing drafts, not new acoustic quality. [Two targeted mutations](reports/mutation-checks.json) weakened completion/manifest guards; tests failed on both mutations and original file bytes were restored. This is not a project-wide mutation score. Mocked retry logs are not extra API requests. No new UI/browser/build check was run for this harness-only batch; prior UI evidence belongs to the [earlier investigation](../nim-phase1-2026-10-26/README.md).

[Integrity checks](reports/integrity-and-outcomes.json) bind each report to its saved manifest, verify current fixture hashes against recorded hashes, confirm identical WAVs between audio and AV, and verify the picture contains video only. This proves local consistency, not the opaque backend's internal decoded tensors. Headers did not expose checkpoint/quantization or serving versions.

[Fallow commands and exit statuses](reports/fallow-commands.json): health exits 1 with **23 complexity/risk findings, 53.8/100 (D)**; architecture exits 0 with no detected cycles, but boundary/policy rules are unconfigured and therefore unmeasured; scoped unused-file analysis exits 1 with ten candidates. These are standalone import/preparation/browser/verification scripts, including manually invoked tools. Static unreachability from application entries is not deletion proof; none were deleted or suppressed. Coverage/risk estimates are static, not measured production coverage. This scan is a current whole-project snapshot, not a causal comparison against a clean baseline. **Fallow does not analyze the Python harness.** Its correctness/security/performance boundaries were reviewed manually alongside tests; no comprehensive security audit is claimed.

Graphify refreshed [79 input files, 436 nodes, 1,019 edges](../../codebase-map-inputs.json), using local AST extraction, `parallel=False`, no semantic provider/model calls. All input hashes match. [Raw diagnostics](reports/map-diagnostics.json) report **302 dangling endpoint references, 29 same-endpoint directed edge collapses and 11 inventoried files yielding no symbols**. The stored DiGraph binds endpoints but cannot recover missing semantic/runtime relationships. The map is usable for orientation, with these integrity/coverage warnings. Python API/client/validator edges were checked in the graph; JSON/file writes, media decoding and UI selection were checked against source. See [the boundary guide](../../CODEBASE_MAP.md).

## What this changes

The failed gate stays failed. The new parser and experiment-binding fixes improve acceptance correctness; they do not repair sound recognition. The short dog burst motivates a duration/crop control. The successful speech nonce rules out complete audio transport failure on that request, while silence hallucination rules out a claim of reliable sound grounding. We cannot yet isolate model weights from hosted non-speech preprocessing or request-path behavior. Capacity errors and missing paired answers prevent further conclusions about simple prompts, thinking and audiovisual bias.

Research motivation: [ACPO](https://vision.cs.utexas.edu/projects/acpo/) supports counterfactual modality checks; [TAC](https://arxiv.org/html/2602.15766v2) separates event discovery, timing and later reasoning, but depends on specialized training and does not promise released weights. Neither establishes a working free NIM solution. The [research handoff prompt](../../research/RESEARCH_HANDOFF_PROMPT.md) contains the exact constraints, available evidence and a request for small discriminating experiments. No further model calls should be inferred from that research request.

Reproduction uses the already installed isolated runtime and saved media. Preparation/scoring do not call a model. `phase1_nim.py` does call NIM and is deliberately omitted from automatic test commands:

```sh
/Users/hamza/runtimes/markitdown/.venv/bin/python -m unittest discover -s tests/offline -v
npm test
npm run typecheck
npm run validate:captions
```

Cached artifacts may be absent from another checkout. Inspect source attribution and obtain the exact source files before regenerating controls. Do not overwrite the frozen manifests, raw reports or existing assessments.
