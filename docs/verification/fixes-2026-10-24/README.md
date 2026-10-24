# Player fixes and model-control evidence

Read [the fixes report](../../audits/2026-10-24-fixes.md) and [current state](../../PROJECT_STATE.md). This folder contains synthetic engineering checks, not participant research results.

- `reports/player-regression.txt`: acceptance checks for draft/readability retention, temporary preview, detail limits and rehearsal state/duration.
- `reports/browser-smoke.txt`: full source-caption/browser flow after the updates.
- `reports/build.txt` and stderr: final production build result.
- `reports/audio-alignment.json`: failed structured silence calibration and local review-clip references.
- `reports/nim-controls.json`: arithmetic, caption and synthetic silence/tone comparisons.
- `reports/nim-invalid-audio.json`: negative decode control (expected rejection; HTTP 500 observed).
- `reports/nim-audio-positive-controls.json`: known synthetic speech and tone-with-reasoning comparison.
- `reports/shared-rate-limit.json`: two local processes paced at least two seconds apart; no external requests.
- `reports/local-media.json`: user-prepared Sintel/Tears of Steel metadata, hash/resource checks and remaining review limits; checked later on 24 October.
- `reports/reading-time-review.json`: authoring flags, not a validated accessibility measure.
- `reports/fallow-*.json`: dead-code, architecture, duplication and health findings, with stderr preserving failed gate exits.
- `reports/committed-map*` and `reports/graphify-*`: mapping commands' outputs and extraction warnings.
- `screenshots/`: inspected preview/player layouts.
- `exports/`: synthetic original-state and stopped-duration samples.

Repeatable player checks live in `scripts/verification/fixes-2026-10-24/player-regression.mjs`; the general browser flow remains `scripts/browser-smoke.mjs` and writes disposable outputs under ignored artifacts. The six-case control driver is `scripts/diagnostics/nim-controls.py`. Additional one-off negative/speech controls are recorded with parameters and actual response metadata in the reports.

Original application revision: `fdf7802`; changes were uncommitted during verification. Use source-map input hashes/current diff to establish freshness rather than comparing HEAD alone. Raw model reports contain synthetic material only; no key/header values were saved. No paid APIs, agents, participant data or publishing were used. Reports must not be relabelled as proof of model correctness or a complete accessibility audit.
