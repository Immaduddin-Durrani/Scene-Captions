# Full sound-caption preparation follow-up — 24 October 2026

The user requested full sound-effect captions for Sintel and Tears of Steel. The existing automatic method failed sound checks, so it is not being used for full-film generation. The working playback datasets and dialogue remain unchanged during a bounded replacement trial. This page records preparation; it does not claim completion or sound accuracy.

## Local candidate and scope

The available Mac has 16 GB unified memory. The existing isolated audio runtime contains coarse AST classification and a partial Whisper-caption-model download; it is not an accepted captioning solution. The official Audio Flamingo 3 model describes an 8B model tested on NVIDIA A100 hardware; no suitable small local AF3 runtime was already installed. The small MLX Qwen Thinker search result was an encoder without an LM head, not a caption-generation replacement.

The selected single local trial uses [MLX-VLM](https://github.com/Blaizzy/mlx-vlm) 0.7.10 and [Gemma 3n E2B 4-bit](https://huggingface.co/mlx-community/gemma-3n-E2B-it-4bit), pinned to `66e7276cfc589073b4f92ebed58c05301f990222`, with 4,462,976,625 weight bytes. [Google documents audio input/analysis](https://ai.google.dev/gemma/docs/gemma-3n); that does not establish our non-speech caption quality. The converted model's metadata has an inconsistent base-model field (E4B versus its E2B title); the exact artifact/revision is recorded rather than silently treating the conversion as an independently reproduced original model.

The isolated runtime is under `~/runtimes/scenecaptions-mlx`; package setup/pins are under `~/skill-library/setup-records`. No system Python/PATH, model defaults, skills, persistent service, agents, account login, telemetry exporter or cloud inference is enabled. Local model inference runs offline. Gemma license applies; there is no API inference charge. Downloads are preparation artifacts, never part of the player or Git.

## Predeclared checks

Six inputs only, each under eight seconds: synthetic silence, continuous 440 Hz tone, a 440/980 Hz overlap with the second tone at 1–2 seconds, and three short licensed Big Buck Bunny source-caption anchors (music, brook/fly overlap, apple thud). File hashes and reference metadata are in [cases](reports/cases.json). The expected names/content are kept out of the common audio-observation prompt. Filenames are hash-based.

Silence must produce no invented events; known audible tone/overlap must not be called silence or speech/music. Film anchors must identify the referenced broad sounds without inventing visual scenes or dropping important overlapping events. A source caption is a reference, not new human listening ground truth. Small controls do not establish an error rate or long-form completeness.

Only if basic recognition is adequate should the next stage test known onset/offset/absent-event controls and a short per-film draft. Timing, rewriting and reading time require separate checks. No full-film generation or playback installation occurs merely because weights loaded, text looks plausible or JSON validates. Actual human listening/wording review remains necessary for a verified track.

Driver: `scripts/diagnostics/local-sound-controls.py`. It enforces the pinned model weight hash, six short local inputs, new report path, deterministic sampling and offline execution. It cannot generate or install a playback dataset. Actual results and limitations will be recorded after the bounded run.

## Actual results and decision

Twelve local text generations were performed: six careful observations, four plain observations, one direct speech transcription and one text-only control. There were zero cloud inference calls and zero full-film caption-generation calls. No playback dataset or quality gate was changed.

- [Careful prompt](reports/local-controls.json): all six inputs, including audible tones, music and source events, returned “No audible sound.” Each stopped normally, so truncation does not explain these answers.
- [Plain prompt](reports/plain-controls.json): changing only the observation wording did not yield the needed sound recognition. Music/silence produced requests to rephrase, the tone was not identified, and the speech clip received a request to rephrase.
- [Direct speech/text controls](reports/positive-controls.json): a specific transcription instruction produced recognisable but imperfect film dialogue. The text-only arithmetic answer included 5, added an unrelated puzzle explanation and hit the 96-token limit. Neither output was accepted as caption rewriting.
- [Input tensors](reports/input-inspection.json) and [merged embeddings](reports/embedding-inspection.json): all clips had 188 audio placeholder tokens. Non-silent inputs produced different, nonzero spectrograms and distinct merged embedding hashes. Partial transcription further demonstrates some audio conditioning. This narrows a simple missing-audio hypothesis; it does not establish original-model parity or isolate quantisation, conversion, implementation and task training.

**The tested local checkpoint/runtime is not accepted for non-speech caption preparation.** No speculative runtime/model patch was made to manufacture a pass, and no claim is made about every Gemma or audio model. Model weights passed the pinned Hub LFS SHA-256 check. The downloaded model/runtime remain reusable locally; no API cost was incurred.

The existing short-control gate therefore remains closed. Timing tests and full-film inference were not launched. A small Gemini 3.8 Flash trial was proposed at this point, then declined by the user (see local-only decision below). [Google documents non-speech audio understanding and 32 audio tokens/second](https://ai.google.dev/gemini-api/docs/audio); [current pricing](https://ai.google.dev/gemini-api/docs/pricing) lists Standard input $0.75 and output including thinking $3.75 per million tokens through 31 December 2026. These are provider claims/prices, not a local capability result or a verified account entitlement. Its free tier is account/quota dependent; the requested estimated API budget ceiling is US$1. No request has been sent.

Both exact-hash films now also have local 16 kHz mono input-window manifests under ignored `artifacts/sound-captions/<film>/windows.json`, with 30-second target intervals and one second of neighboring context. This is audio preparation only, not event segmentation, transcription, review or cloud upload. See [prepared-audio scope](reports/prepared-audio.json).

The question about cloud generation is required by the user's pasted workflow rule: “Do not … enable paid/cloud generation without a new explicit request.” The historical permission question covered bounded controls first, then draft tracks only if recognition/timing checks passed; it was declined. Verified full captions still require listening/wording review, including simultaneous sounds and reading time. No agent, cloud connection, sign-in or payment was enabled.

Validation: driver Python compilation passed; a synthetic 9-second WAV falsely labelled as 3 seconds was rejected before model loading/inference ([guard evidence](reports/duration-guard.command.json)). Existing playback datasets and failed gate are checked against the pushed checkpoint. No commit or push was requested for this follow-up. The graph/map remains explicitly stale for new diagnostics.

## User decision: local only

The user declined the cloud proposal and explicitly selected “Keep everything local.” The Gemini proposal is closed, with zero requests. Local-only processing is now the active constraint; the historical proposed budget above is not authorization. The next bounded trial reuses the existing audio-captioning runtime and completes the partial, pinned `cahya/whisper-small-audio-captioning-v1.5` cache. The [author model card](https://huggingface.co/cahya/whisper-small-audio-captioning-v1.5) describes sound-caption fine-tuning on 1M audio samples, under Apache 2.0; that is a training claim, not local accuracy evidence. Six short controls/anchors were run, then repeated after correcting a runtime attention-mask warning. No new runtime, cloud service, login or agent is needed. The approximately 967 MB weight artifact was downloaded and SHA-256 verified; all inference ran offline.


## Completed local Whisper trial

The pinned revision is `b815cffa35c2bc424d8acc07db50c3dd9430b978`; the 966,995,080-byte weights match Hub LFS SHA-256 `99699e342db513e5570a5ee428b953656005a769fdee41be6f084e9740049950`. Existing isolated runtime: `~/runtimes/audio-captioning`, Transformers 4.57.6, Torch 2.14.1, MPS. Setup provenance is recorded under `~/skill-library/setup-records/scenecaptions-whisper-captioning-2026-10-24.json`. Loading into `WhisperForConditionalGeneration` reported no missing, unexpected or mismatched weight keys; no custom remote code was executed. This does not prove parity with the author's training implementation.

Driver: `scripts/diagnostics/whisper-sound-controls.py`, same six hash-verified short fixtures, no expected labels in model input. Uses checkpoint generation defaults, deterministic decoding with three beams and a 96-token cap. It cannot install playback tracks. [Initial results](reports/whisper-controls.json) included an attention-mask warning. The driver was corrected to request and pass the audio mask; the [corrected results](reports/whisper-masked-controls.json) contain identical descriptions without that warning:

- Silence correctly described no audible events, but added unsupported recording-quality commentary.
- Continuous and overlapping synthetic tones both returned `laioning`.
- The source music anchor produced a piano description with an extraneous prefix and subjective claims; this does not rescue the failed controls.
- The brook/fly overlap produced repeated `oh` text rather than its sound events.
- The apple-thud anchor returned `laioning.com`.

**This checkpoint/runtime also fails the recognition gate.** Twelve Whisper generations plus twelve earlier Gemma generations were performed in this follow-up: 24 total local diagnostic generations, zero full-film generations and zero cloud inference calls. No inference charge or API key was needed. Timing tests were not reached; fixed audio-window bounds have not been treated as sound-event times. Neither a complete sound track nor human listening approval exists for the two additional films. Existing source-backed Big Buck Bunny sound captions and official dialogue tracks are unchanged.

The actionable local route remaining is manual listening, event timing and wording annotation, followed by review; the prepared 55 audio windows are listening inputs only. No additional model sweep, cloud request or automated pass is queued. Full sound-effect captions remain **unfinished**, rather than represented by these rejected outputs.
