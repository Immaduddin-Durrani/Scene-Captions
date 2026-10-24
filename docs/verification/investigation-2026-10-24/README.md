# Model investigation and component cleanup — 24 October 2026

Working tree based on `02f309cbb8cc48801f07036fa27439e32c3d9d40`, macOS/Apple silicon. No commit, push, video download, agents, new dependencies or full-film inference. See the [investigation](../../audits/2026-10-24-investigation.md) for causes, hypothesis table, primary research and remaining limits.

## Model evidence

- [Eight initial controls](reports/factor-controls.json) and [two noun-preservation follow-ups](reports/head-noun-controls.json): **ten actual HTTP attempts**, single attempt per case, shared 2.05-second pacing, 180-second response timeout. All new audio is synthetic. One 48 kHz case returned capacity-related HTTP 503 and is inconclusive. Successful HTTP responses did not satisfy the quality bar; no automatic gate was cleared.
- Historical speech, silence, decoder and failed-variant evidence was reused from the [previous fixes index](../fixes-2026-10-24/README.md). These are small probes, not a benchmark or population error rate.
- Run `python3 scripts/diagnostics/factor-controls.py --help` for the bounded driver. Re-running it makes external requests; use saved reports first. Request data/response text in the reports contain no credential. Cached synthetic WAVs and raw responses remain under ignored `artifacts/diagnostics/factor-controls-v1/`.

## Checks and reproducibility

Each routine result has an adjacent `.command.json` recording argv and exit code, plus stderr where applicable. Browser command records include the exact executed Playwright code. A development server and existing local demo media are required to reproduce browser checks; nothing here downloads media.

| Check | Evidence / scope |
| --- | --- |
| Baseline | `reports/baseline-node.*`, `baseline-python.*`, `baseline-fallow.*`: 13 Node / 14 Python tests; 62.6/C, 13 findings |
| Unit tests | [Node](reports/final-node.txt): 14 passing; [Python](reports/final-python.stderr.txt): 22 passing, including termination, atomic-label, retry and human-receipt guards |
| Types, dataset, build | `final-typecheck.*`, `final-captions.*`, `build.*`: typecheck, unchanged 87-cue schema validation, production build |
| Browser coverage | [Broad smoke](reports/browser-smoke.txt): all 87 source-cue seeks, settings/persistence/imports/rehearsal/plan; [focused regression](reports/player-regression.txt): draft/readability, preview timeout/return, original priority, export flags and frozen stopped time |
| Extra seek regression | [Native keyboard and mouse](reports/native-preview-seek-fixed.txt); [Escape/play/slider cancellation](reports/preview-cancellation-fixed.txt). Initial failures and narrowed observations remain in `preview-cancellation.*`, `stable-preview-seek-reproduction.txt`, `range-input-observation.txt`, `native-preview-seek.*` and `native-seek-diagnosis*` |
| Fallow | [Final health](reports/final-fallow.json): 63.2/C, 17 findings, exit 1. Main component complexity improved; aggregate gate remains failed. Intermediate 65.1/C report is historical. Architecture/dead-code scans retain their actual exit codes and scope; no boundary rules are configured |
| Map | [Refresh](reports/map-refresh.txt), [raw diagnostics](reports/map-diagnostics.json), [input manifest](../../codebase-map-inputs.json): 63 files, 334 nodes, 740 edges; zero semantic/model tokens. 169 unresolved raw endpoints and 28 same-endpoint directed pairs limit completeness; `dedup=False` does not prevent DiGraph parallel-edge collapse |
| Integrity | [Preserved data, map hashes and bounded credential check](reports/integrity-and-secret-check.json). This is not an exhaustive secret/history audit |

The initial broad smoke persistence failure is retained as `intermediate-browser-smoke.*`: native metadata readiness was earlier than React preference restoration. The test now waits for the restored value. The intermediate seek fix also exposed stale parent preview selection; `intermediate-player-regression-seek.txt` and `player-regression-diagnosis.txt` retain that failure. Intermediate browser failures are diagnostic evidence, not passing results.

Screenshots in `screenshots/` were visually inspected at desktop and 390 px width; this is not a complete accessibility or physical-device audit. `exports/` contains synthetic rehearsal sessions only, never participant data. Cue seeks do not establish continuous-play sound alignment or human listening approval.

## Human-review fallback

A three-cue packet exists locally at `artifacts/caption-review/investigation-2026-10-24/index.html`, with contextual WAVs, exact offsets, source/variant comparison and `review.json`. The packet is ignored derived material, not a committed media distribution. The [packet browser check](reports/review-packet.txt) loaded all three audio files with labels initially hidden. Every review decision remains **pending**. [Preparation instructions](../../../scripts/generation/README.md) explain regeneration and receipt checking. A partial packet cannot approve the whole track, and a completed receipt is only documented self-reported review; the tool never installs captions or establishes DHH benefit.

Use this workflow to prepare real reviewed annotations before a study. Automated rewriting, non-speech recognition, temporal grounding and semantic matching remain unaccepted. Playback continues using the unchanged licensed source track and local variants.
