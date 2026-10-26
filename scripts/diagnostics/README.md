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

## Local offline replacement controls

`local-sound-controls.py` uses the isolated `~/runtimes/scenecaptions-mlx` installation and a pinned, checksum-verified local Gemma 3n artifact. It permits at most six mono 16 kHz PCM WAV fixtures under eight seconds each, checks actual duration/hash, and requires a new report path. It sets offline/telemetry-disabled Hub mode, runs no server and cannot produce/install a film track. `--plain-observation` is a bounded prompt-specificity follow-up; it is not approval for a full-film run. The 24 October run failed non-speech controls. See [scope, setup and actual results](../../docs/verification/sound-captions-2026-10-24/README.md) before repeating anything. Runtime requirements/setup records live under `~/skill-library/setup-records`; no application dependency was added.

`whisper-sound-controls.py` is the second bounded offline diagnostic, using the existing isolated audio runtime and pinned/checksummed Whisper sound-caption weights. It validates the same six short mono WAV inputs, requires a new verification report, passes an explicit audio attention mask, and rejects weight-loading mismatches. Both the initial and corrected six-case runs failed recognition; do not use `scripts/caption-audio.py` to process full films on the assumption that these controls passed. See the linked local-trial evidence.

## 26 October exact-payload BBB experiments

`phase1_nim.py` is a separate single-attempt, NVIDIA-only driver. It permits at most
12 explicit jobs per report, bounds WAV/video fixtures, records exact parameter and
media hashes, and redacts inline media. It cannot accept or install playback data.
Both audio_url and input_audio were tested; schema acceptance did not establish
non-speech quality. `scripts/generation/prepare-nim-context.py` prepares exact-hash
BBB reference/silent-visual context jobs without inference. Use new manifest/report
paths and inspect [saved results](../../docs/verification/nim-phase1-2026-10-26/README.md)
before any authorized repeat. Raw failures remain evidence. Offline shape/redaction
tests are in tests/offline/test_phase1_nim.py.

# Caption-free counterfactual follow-up

`nim-counterfactuals.py` prepares blinded natural-sound/shift/silence controls and assesses saved reports. Preparation and scoring make no API calls and cannot install captions. `phase1_nim.py` is the separate bounded NVIDIA request driver; invoking it does make API calls. Preserve frozen manifests/reports rather than overwriting them. See [the dated results and audit](../../docs/verification/nim-counterfactuals-2026-10-26/README.md) and [the research handoff prompt](../../docs/research/RESEARCH_HANDOFF_PROMPT.md).
