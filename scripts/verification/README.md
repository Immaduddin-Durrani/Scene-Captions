# Manual browser verification

This directory contains browser-check functions invoked with Playwright CLI. They are verification tooling, not web application modules and not standalone Node programs. Read the [evidence index](../../docs/verification/audit-2026-10-24/README.md) and [audit report](../../docs/audits/2026-10-24.md) before interpreting results.

## Dated audit reproductions

`audit-2026-10-24/` contains:

- `browser-smoke.mjs`: snapshot of the existing source-caption regression flow, configured for audit port 3001.
- `edge-cases.mjs`: draft-loss, detail-limit and initial original-override export reproductions.
- `readability-check.mjs`: source-original caption bounds, a keyboard sample and root-font scaling checks.

The maintained browser regression remains at `scripts/browser-smoke.mjs`; open the desired local origin first. It now writes disposable output under ignored `artifacts/browser-smoke/`. The dated `audit-2026-10-24/` reproductions document pre-fix behavior; they are not a green post-fix acceptance suite. Current acceptance is in `fixes-2026-10-24/player-regression.mjs`, with [evidence](../../docs/verification/fixes-2026-10-24/README.md). A reproduced defect is recorded as an observation, not automatically a test failure.

## Running an authorized check

Start the prototype on `127.0.0.1:3001`, download the licensed sample film, open an isolated named Playwright session at that URL, and run the desired function from the repository root. For example, with an existing authorized session named `scene-audit`:

```sh
playwright-cli -s=scene-audit run-code --filename=scripts/verification/audit-2026-10-24/edge-cases.mjs
```

These scripts reset this local origin's caption preferences, interact with the sample, and write synthetic exports/screenshots into the dated evidence directory. Use a fresh evidence location for a new audit so old outputs are preserved. They require a matching sample video/caption track and the expected prototype controls.

Do not install tools, launch agents, publish the app or activate a skill merely because this guide exists. Follow the current task's authorization and skill workflow. Syntax checking is possible with `node --check`; executing these function files directly with Node does not run browser verification.
