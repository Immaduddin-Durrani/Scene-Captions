# Current local source-assisted generation

The 26 October Big Buck Bunny draft uses local MLX-LM/Qwen generation, with extensive recorded main-assistant source-text corrections. See [demo notes and reproducibility](../../docs/GENERATED_CAPTIONS_DEMO.md). `npm run setup:captions` installs only saved generation/editorial records; it makes no inference/network calls. Fresh `scripts/generate-local-source-captions.py` output stays under ignored artifacts and cannot install a track. The user's local-only constraint remains active; the historical NVIDIA commands below are not authorization to use a cloud model. No model pipeline is called while viewing.

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

## Human-reviewed preparation when automation fails

Use the new standard-library tool with existing local, rights-clear nonparticipant media. It needs the installed ffmpeg, Node/project schema validator and Python; no key, new package, model request or video download is needed.

```sh
python scripts/prepare-caption-review.py --input data/captions/big-buck-bunny.json --video public/media/big-buck-bunny.mp4 --output-directory artifacts/caption-review/my-new-packet --rights-clear --limit 3
```

Open index.html in the new directory. Listen first, then reveal the source and all variants. Clips include one second of context on each side, clamped to the movie bounds; clips.json records the source interval in local clip coordinates. Source timing and playback data are unchanged.

Edit review.json with a human reviewer ID and decisions (`pending`, `approved`, `needs-changes`) for every check and all nine grid cells. Nothing is pre-approved. A three-cue packet is a rehearsal of review and cannot approve an 87-cue track. Use `--limit 0` to prepare a complete packet locally, without model calls. Fix captions before review approval and rebuild the packet when their bytes change.

```sh
python scripts/prepare-caption-review.py --input data/captions/big-buck-bunny.json --video public/media/big-buck-bunny.mp4 --rights-clear --check artifacts/caption-review/my-new-packet/review.json
```

Checking rejects wrong hashes, changed/unknown/duplicate/missing cues, absent reviewer identity, unapproved checks and missing grid decisions. It reports documented self-reported review completion only; it never installs output, marks a track reviewed, certifies sound truth or claims independent/DHH review. Follow up with listening/readability and DHH review before study use. The current three-cue packet has **no completed human approvals**.

Explicit non-stop model completions are now rejected even if JSON parses. Atomic wording rejects hidden additional bracket groups and empty labels; semantic errors still need review. See the [current investigation](../../docs/audits/2026-10-24-investigation.md) for all controls and uncertainty.


26 October NIM follow-up: the latest request authorizes bounded NVIDIA preparation
for BBB. [42-request evidence](../../docs/verification/nim-phase1-2026-10-26/README.md)
records continued non-speech grounding failures and limited reference/visual-context
success. `prepare-nim-context.py` only prepares silent clips/manifests for that
separate source-assisted experiment; it does not listen to audio, clear a gate or
install a track. A full NIM track is still unaccepted. Earlier local-only decisions
remain historical; paid generation and publication still require fresh requests.
