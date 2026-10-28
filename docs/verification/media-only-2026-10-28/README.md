# Experimental media-only tracks — 28 October 2026

The user explicitly requested full subtitles for all three films and a viewer
option to select them, without reference captions, plot or supplied scene text.
These are **unverified experiments**, not accepted sound recognition or verified
accessibility captions. The existing failed acoustic gate is preserved.

## Preparation and inference

`scripts/generate-media-only.py --experimental` uses only local CC BY 3.0 film
audio for inference. Film names/credits appear in export metadata, not model
prompts. Existing caption JSON/SRT, reference timestamps and dialogue are never
read by this generation script. No visual or plot context is supplied.

The interrupted initial run used a structured three-detail sound prompt on
30-second audio. Some responses copied the illustrative labels and 0–1-second
times; others were invalid JSON or HTTP 503. Its protocol and raw per-window
responses are retained in this directory. Two subsequent [prompt diagnostics](prompt-diagnostic.json)
showed that plain prose completed, while the no-example structured prompt still
failed the requested schema. A text response is not evidence of acoustic truth.
The [hosted API schema](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer)
does not document a response-format field; no undocumented forced-JSON support
was assumed.

The revised [v2 protocol](v2/protocol.json) processes the entire duration in
15-second audio windows, with a shorter final window. Omni produces bounded
plain-text non-speech observations. Super VL rewords those observations at three
detail levels in batches of eight, with strict ID/structure guards. This is
generation from our own media-derived observations, not paraphrasing fetched
captions. It can still propagate wrong acoustic claims; rendering does not verify
them. Same-description variants are allowed when evidence contains little detail.
Expressiveness stays conservative and visual scene adaptation stays disabled.

Separate dedicated Parakeet gRPC ASR processes speech in 30-second windows.
Reported word offsets are grouped into subtitles; source transcripts are not
used. Unknown tokens, missing timestamps and out-of-window offsets are rejected
and recorded. Exact-audio ASR responses from the interrupted attempt are reused
only after raw PCM hash equality. Word timestamps and lexical-looking speech can
still be wrong. Model omission is not proof that there was no speech or sound.

**Sound display intervals are the 15-second analysis windows, not independently
detected event boundaries.** The text can describe a sound that occurs in only
part of its displayed interval. No precision, complete event recall, whole-film
accuracy score or suitability for DHH reliance is claimed.

## Runtime and separation

Reuses `/Users/hamza/runtimes/scenecaptions-nim-asr/bin/python`, the existing
pinned NVIDIA Riva client and shared request-start limiter. At most two fixed
inference requests run concurrently; these are ordinary API calls, not agents.
No new packages, local model weights, hooks, integrations or persistent services
are installed. Raw request summaries omit credentials and inline media data.

The original caption datasets and generation gate are not overwritten. Exports
go to `data/experimental-captions/` and `public/research/media-only/` only after
every window has both modality outcomes and rendering. A failed request is an
incomplete window, never silently replaced by a reference caption or assumed
silence. Full processing does not imply all model outputs are factual.

The initial bounded pass allows two attempts per unfinished stage; the optional
`--retry-incomplete` addendum allows at most six total, with unchanged payloads
and cached complete outcomes reused. No repeated resume expands that ceiling.
See per-film summaries and raw reports under `v2/` for actual outcomes.

## App selection and checks

The webapp offers **Use media-only AI subtitles** separately from **Use existing
captions**. Existing captions remain the default. Source switching preserves
playback position, ends previews/overrides, and locks after a rehearsal starts.
The selected experimental track supplies both sound and dialogue; fetched
dialogue is never mixed in. Film changes reset selection to that film's default.
Three SRT downloads and a JSON export are available per generated film.

Final exports: **BBB 40 sound / 0 dialogue; Sintel 59 / 71; Tears of Steel 49 /
68**. All 149 windows completed with no failed-request gaps. One Sintel sound
observation was rendered as no identifiable non-speech sound; that model omission
is not verified silence. Twelve zero-duration speech groups were rejected and
logged. [Per-film summaries](v2/summary.json), [saved request counts and usage](request-summary.json).

The saved reports contain 389 requests (193 chat completions, 121 HTTP 503s and
75 successful ASR calls). Up to two additional in-flight requests may be absent
when the initial process was stopped. Raw ASR results were reused by audio hash,
not counted as new calls. No paid provider was used; remaining free-tier quota
and hosted checkpoint internals were not independently verified.

Some text-rendering responses contain the same JSON object twice, compact then
pretty-printed. A renderer-only parser accepts them only when every complete
object is identical; it rejects differing objects, trailing prose and truncated
content. This does not change the shared completion/acoustic gate. Cached
responses were recovered with observation-ID/text binding before new rendering
requests. Raw original reports remain unchanged. Tests include adversarial
duplicates, incomplete completions and private-header filtering.

[Implementation checks](checks.json): 25 Node tests, 42 offline Python tests,
default/experimental schema validation and production build passed. Chrome
verified all three films' default selection, keyboard activation, playback-time
preservation, three detail choices, fixed draft, returning to existing captions,
nine SRT downloads, and rehearsal source locking/export provenance. There were
no page errors in that run. [Browser results](reports/browser-checks.json),
[synthetic rehearsal export](exports/rehearsal.json),
[desktop screenshot](screenshots/big-buck-bunny-desktop.png),
[390px viewport screenshot](screenshots/big-buck-bunny-mobile.png).
No independent listening panel, DHH review, complete accessibility audit,
physical-device testing, accuracy score, push or deployment is claimed.

[Media integrity](reports/media-integrity.json) verifies all 149 exact WAV hashes
and durations against the actual audio stream. Tears of Steel's audio ends at
734.092993 s, while picture ends at 734.166667 s (about 74 ms later). Its last
decoded/resampled window includes a small AAC packet tail; this is not a skipped
generation window or justification to extend a caption into absent audio.
The duration check uses one source AAC packet plus two resampling samples as its
explicit tolerance. No audio, timestamps or captions were changed to make this
check pass.

Film audio derivatives: © 2008/2010/2012 Blender Foundation, CC BY 3.0. No source
subtitle text is used by this experiment. No participant media/data is sent.
