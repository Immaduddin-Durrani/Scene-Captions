# 24 October 2026 audit evidence

Read the [audit report](../../audits/2026-10-24.md) for conclusions and [current state](../../PROJECT_STATE.md) for remaining work. These are engineering test samples, not participant data or study results.

## Contents

| Folder | Contents |
| --- | --- |
| `reports/` | Fallow dead-code/architecture/duplication/security JSON and stderr; npm production advisory result; design-detector result; targeted browser reproduction output |
| `screenshots/` | [desktop](screenshots/sourced-captions-desktop.png), [mobile](screenshots/sourced-captions-mobile.png) and [root-font scaling experiment](screenshots/text-scaling.png) |
| `exports/` | [synthetic rehearsal sample](exports/sourced-rehearsal-test.json) and [missing initial override reproduction](exports/start-with-original.json) |

Browser-check scripts are in [scripts/verification](../../../scripts/verification/README.md), with the dated reproduction functions under `scripts/verification/audit-2026-10-24/`.

## Scope and provenance

The baseline was checked with Node 24.21.0 on Windows and a local production build in Chrome. Twelve unit tests, types, 87-cue schema validation and the production build passed. Browser checks exercised actual source-caption seeks, playback, preferences, imports, rehearsal/export and responsive layout. See the audit for all limits; no complete listening or accessibility-conformance review is claimed.

The starting application revision was `fdf7802`. Product source files were unchanged during this audit. Subsequent documentation/utility reorganization is not covered by older graph/Fallow file inventories. No model requests, agents, hooks, telemetry setup, deployment or publishing were performed for this run.

## File relocation record

Files originally sat directly inside this evidence folder. Organization subsequently moved raw result/log files into `reports/`, PNGs into `screenshots/`, sample exports into `exports/`, and executable browser functions into the scripts directory. Their raw historical logs were preserved verbatim and can therefore contain the old paths.

Full local PDF text extracts were moved from this folder to ignored `artifacts/research-extracts/2026-10-24/`. They are disposable derived material, not canonical research documents. Original PDFs remain in `docs/research/`.

Updated scripts write to the organized evidence subfolders. A future replay may generate different output and should use its own dated run or clearly identify what was rerun; do not silently overwrite baseline evidence and call it the original result. No replay was needed for this path-only organization change.
