# Bounded NVIDIA controls

`nim-controls.py` runs six synthetic/text cases: arithmetic, one caption-type task with reasoning off/on, silence, tone, and silence with reasoning. It sends no film or participant data and cannot install captions.

Run only for an authorized diagnostic task, using a new report path:

```sh
python scripts/diagnostics/nim-controls.py --report docs/verification/my-run/reports/nim-controls.json
```

The driver uses the project's shared local rate limiter. Response waits default to 180 seconds without reasoning and 300 seconds with reasoning; `--timeout SECONDS` explicitly overrides them. Each diagnostic case is a single observed request, preserving errors rather than silently changing the experimental conditions with retries. Production generation uses the common client's bounded retry policy. The key is read locally and is not recorded.

Earlier control reports used shorter diagnostic waits. A timeout in those reports is inconclusive, not evidence of missing capability. Invalid-WAV and synthetic-speech follow-ups are separately recorded under [the fixes evidence](../../docs/verification/fixes-2026-10-24/README.md). See [the diagnosis](../../docs/audits/2026-10-24-fixes.md) before interpreting the results or repeating a full model run.
