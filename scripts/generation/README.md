# Offline source-caption preparation

These tools run locally before viewing. They are not web routes and are never imported by the player. Python standard-library code needs no additional package installation. Node and the existing project dependencies validate tracks; audio checks also need ffmpeg.

## Generate wording candidates

From the repository root, using rights-clear, nonparticipant source captions:

```sh
python scripts/generate-caption-variants.py --input data/captions/big-buck-bunny.json --output data/candidates/my-probe.json --rights-clear --limit 3
```

The input must pass the application's caption schema. The output must be a new file under `data/candidates/`; the tool cannot install or overwrite the playback track. A local `NVIDIA_API_KEY` or `NVIDIA_KEY` is required for remote generation. Process environment takes precedence over `.env`. Never supply a key on the command line.

The tool generates each source sound separately, combines simultaneous sounds deterministically, and reuses wording for recurring labels. It rejects wrong IDs, missing/extra grid cells, changed sound-line counts, overlong values and batches that only echo the source. It preserves original text and timing. Responses are cached under ignored `artifacts/generation-cache/`. A successful run writes a separate review report with source/output hashes and reading-time warnings. No automatic semantic validation or participant approval is claimed.

The `--limit` probe should be reviewed before attempting a full track (omit `--limit`). Do not run a larger model comparison merely because a provider is available. Current trials failed the useful-output checks; cached source-copy responses will be rejected before any further request for the same batch. If a provider returns invalid/empty text, the run stops; it never substitutes invented captions or clears the existing audio failure gate.

## Rate limits, retries and response waits

The team specifies a 40-RPM free-tier ceiling. Project tools share a local process/thread limiter spacing starts by 2.05 seconds (about 29 RPM) for headroom. Other projects/apps using the same key are outside this local limiter and share the account allowance.

The common client makes at most seven attempts for temporary 429/502/503/504 responses or transport/timeouts. Delays are 2, 4, 8, 16, 32 and 60 seconds. A valid Retry-After is honored up to 60 seconds; if the provider asks for longer, the tool stops rather than retrying early. Bad requests/authentication/invalid-media errors are not blindly retried. Logs never include the key.

Response waiting is separate: defaults are 180 seconds for ordinary requests and 300 seconds for reasoning requests. Generation accepts `--thinking` and an optional `--timeout SECONDS` override. A timeout is inconclusive, not proof of a model capability failure. Retries are bounded but can make an offline job last longer than one response timeout; no part of this waiting happens during viewing.

## Check corresponding audio

```sh
python scripts/check-caption-audio.py --captions data/captions/big-buck-bunny.json --video public/media/big-buck-bunny.mp4 --report docs/verification/my-run/reports/audio-check.json --rights-clear --limit 3
```

This checks the exact video hash, extracts 1–10 corresponding cue clips, and calibrates the audio model on digital silence and a known tone. The source caption is withheld from the audio-observation prompt to reduce confirmation bias. Failure stops model-based matching. Extracted clips remain available locally for listening review; no source times are shifted and no output is installed. If calibration passes, descriptions/intervals still require human comparison with the source, not automatic acceptance.

Current result: silence calibration failed again. Thus automatic audio corroboration is unavailable. See the [recorded result](../../docs/verification/fixes-2026-10-24/reports/audio-alignment.json). No tone or film inference proceeded after the failed silence check.

## Reading-time budget

Here, budget means caption characters relative to display time, not money or API tokens. The editing heuristic is 20 characters/second, capped at 280 characters and allowing an existing longer source label to remain intact. This is not a validated DHH threshold. Reports flag difficult cases; the tool never silently extends cue timing to make longer text fit. Shorter text still needs an accuracy review.

Run local tests without API calls using `python -m unittest discover -s tests/offline -v`. See [model candidates/results](../../docs/integrations/NVIDIA_MODELS.md) for capability limits and the [current state](../../docs/PROJECT_STATE.md) for the handoff.
