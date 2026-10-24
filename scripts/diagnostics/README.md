# Bounded NVIDIA controls

`nim-controls.py` runs six synthetic/text cases: arithmetic, one caption-type task with reasoning off/on, silence, tone, and silence with reasoning. It sends no film or participant data and cannot install captions.

Run only for an authorized diagnostic task, using a new report path:

```sh
python scripts/diagnostics/nim-controls.py --report docs/verification/my-run/reports/nim-controls.json
```

The driver uses the project's shared local rate limiter. Response waits default to 180 seconds without reasoning and 300 seconds with reasoning; `--timeout SECONDS` explicitly overrides them. Each diagnostic case is a single observed request, preserving errors rather than silently changing the experimental conditions with retries. Production generation uses the common client's bounded retry policy. The key is read locally and is not recorded.

Earlier control reports used shorter diagnostic waits. A timeout in those reports is inconclusive, not evidence of missing capability. Invalid-WAV and synthetic-speech follow-ups are separately recorded under [the fixes evidence](../../docs/verification/fixes-2026-10-24/README.md). See [the diagnosis](../../docs/audits/2026-10-24-fixes.md) before interpreting the results or repeating a full model run.

## Single-factor follow-up

`factor-controls.py` is a bounded cached diagnostic driver using the shared client, 180-second waits and one attempt per case. The default phase has eight cases (temperature pair, 16/48 kHz tone pair, silence, plain observations and a held-out two-tone mix). `--phase head-noun` has two prompt-specificity/held-out source-text controls. Use a new report path under docs/verification/; identical saved requests reuse ignored caches. The driver never installs data, clears a gate or starts a full-film run.

```sh
python scripts/diagnostics/factor-controls.py --report docs/verification/my-new-run/reports/factors.json
python scripts/diagnostics/factor-controls.py --phase head-noun --report docs/verification/my-new-run/reports/nouns.json
```

The 24 October follow-up made ten actual requests in total, with one inconclusive 503 capacity failure. Inspect [saved results](../../docs/verification/investigation-2026-10-24/README.md) before any authorized rerun. Silence and audible negatives must both be distinguished; correct silence alone is not calibration. Expected audio content stays in local ground-truth metadata, outside the prompts. Repeated small controls are not a representative movie benchmark.
