# NVIDIA model candidates

Recorded 24 October 2026 from the model catalogue supplied by the team, with selected official model cards checked below. This is a shortlist for evaluation, not a claim that the models have passed our caption-quality checks or that this account can call every endpoint.

**Latest follow-up (26 October):** [42 new bounded requests](../verification/nim-phase1-2026-10-26/README.md) tested current documented audio/video shapes, embedded audio, reference/plot context and Super VL reasoning controls. Some source-assisted expansions worked; independent sound grounding remains failed. No full NIM track is accepted. The following 24 October shortlist/results are historical.

**Historical outcome:** bounded live tests have now run. No model-generated track has passed acceptance or replaced the source-caption demo. See [the fixes/diagnosis report](../audits/2026-10-24-fixes.md) and the results below. The initial shortlist is not an approved production selection.

## Best fits for SceneCaptions

| Priority | Model | Proposed use | Evidence and limits |
| --- | --- | --- | --- |
| First text-generation candidate | `nvidia/nemotron-3.5-lightning-30b-a3b` | Prepare detail/expressiveness variants offline from trusted sound captions and a recurring-sound glossary. | Official model card and Build example checked. Caption fidelity, structured output, latency and this account's endpoint access still need testing. Text generation does not identify sounds in audio. |
| Text-generation fallback | `openai/gpt-oss-20b` | Compare source-faithful wording and schema compliance against Lightning. | NVIDIA model card confirms text-only input/output. It cannot listen to a film or establish whether a sound occurred. No agents or tool execution are needed to generate text. |
| Visual-context candidate | `nvidia/cosmos3-nano-reasoner` | Examine sampled frames or short video segments for visual activity and visible sound sources. | Official model card lists text, image and video inputs. No audio input is listed. Visible activity cannot prove an audible event or establish that a sound is off-screen without a separate sound annotation. |
| Audio/video research candidate, currently blocked | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Potentially propose sound-event candidates and combine sound with visual context. | Official model card confirms multimodal understanding. Existing project probes reported hallucinated sounds on digital silence. Preserve `docs/verification/nim-capability-status.json`; do not install output or resume full-film generation until a documented new test passes. Advertised audio understanding is not proof of non-speech recognition accuracy. |

Recommended evaluation order: test text variants against trusted source captions first; evaluate visual context separately; retain the audio-model failure as a separate unresolved capability. This ordering is a proposal pending the team's generation-scope decision.

## Other relevant options from the supplied catalogue

These entries have not been independently checked against their current model cards or account endpoint access. Names are catalogue labels, not promised API identifiers. They are alternatives to assess only if the primary candidates fail a measured requirement.

| Catalogue label | Possible role | Why it is secondary |
| --- | --- | --- |
| Nemotron 3.5 Bolt E4B | Compact text-variant experiment. | Source fidelity and output format need comparison; compactness alone does not establish suitability. |
| nemotron-3.5-super-vl-120b-a12b | Alternative image/context interpretation or bounded text-quality comparison. | Early-access status, exact modalities and hosted limits need verification. |
| Step 5 Preview | Alternative text/image context model. | Supplied description lists text and image, not audio; preview behavior and endpoint format need verification. |
| deepseek-v4.1-flash; glm-5-3-flash; muse-glimmer-30b | Alternative multimodal/context candidates. | Do not infer video or audio support from the word multimodal. Check accepted inputs first. |
| gemma-4-31b-it; nemotron-3-ultra-550b-a55b | Optional text-quality comparison. | No demonstrated need to add a larger model to this prototype. |
| nemotron-3.5-parse | Extract text/tables from scanned research pages if ordinary local extraction fails. | Research-support tool, not part of caption generation. Remote document processing requires a separate, appropriate task. |
| nemotron-3.5-embed-1b / 8b; nemotron-3-embed-1b; nemotron-3.5-rerank-8b | Future search across a larger research or caption collection. | No retrieval system is currently required for the player. Embeddings/reranking are not caption accuracy checks. |
| riva-translate-4b-instruct-v2 | Later multilingual caption study. | Translation would add a separate research variable and needs fluent/DHH review. |
| nemotron-3.5-content-safety; llama-3.1-nemotron-safety-guard-8b-v3; llama-guard-4-12b | Optional inappropriate-content screening. | A safety classification does not verify sound correctness, respectful DHH wording or accessibility. |

The catalogue marks `glm-5-3` as approaching deprecation; do not select it for a new dependency without checking its current status. Coding-oriented models such as MiniMax M3.1 Flash or laguna-xs-2.1 are not needed for the caption runtime and are not authorization to start workers.

## Excluded from the caption pipeline

Protein design, quantum calibration, tabular/relational prediction, body pose, autonomous-driving perception, synthetic-video detection and active-speaker identification do not meet a current requirement. Speech enhancement and Background Noise Removal can remove the very effects/ambience we need to preserve. TTS and voice chat do not solve this project's non-speech captioning problem. Generating a video with Cosmos generation/transfer models would not establish what sounds occurred in the source film.

## Keys, usage and acceptance checks

- The local client supports `NVIDIA_API_KEY` and the supplied `NVIDIA_KEY`. Process environment takes precedence over local `.env`. Credential-resolution tests use fake values; actual values remain private. Do not put a key in source, public files, model outputs, command arguments or logs.
- The supplied catalogue says Free Endpoint. Exact account eligibility, quotas, rate limits, retention terms, available models and request formats remain unverified. Do not assume unlimited or permanent free access, or repeat the historical 40-RPM figure as a newly verified limit.
- Initial shortlist preparation made no model calls. Subsequent bounded tests used the supplied key without agents; no `.env` value was changed. Current outcomes are recorded below.
- All future caption generation stays offline from playback. Use rights-clear nonparticipant material for tests; do not send participant data or personal footage.
- For text variants: preserve cue IDs/timestamps, reject missing/extra variants, prevent added sounds/unsupported attributes, maintain recurring-sound wording, cache by source/model/prompt version, and require review before research use. Valid JSON alone does not establish factual fidelity.
- For sound detection: include silence, simple known sounds and representative film excerpts; measure false positives, missed events and timing errors. A failed test must leave the working caption track untouched.
- For visual context: assess activity and visible-source claims against reviewed examples. Keep visual facts distinct from sound evidence and disclose the current cue-density proxy.

## Bounded live results, 24 October

- Account model discovery returned the Lightning, Bolt, Super VL, Gemma and GPT OSS identifiers used/considered in this task. Discovery is not a quality test or a guarantee of future availability.
- Lightning passed a basic connectivity/JSON prompt and arithmetic control. Source-caption probes copied original wording, dropped a simultaneous sound or produced an incomplete grid. Reasoning off/on did not correct the broad-music-label control. Such responses are rejected, not installed.
- `nvidia/nemotron-3.5-bolt-e4b` invented a breeze when rewriting a music caption. GPT OSS did not yield usable text in its bounded trial; Gemma timed out. These are particular test results, not general benchmark rankings. No further broad catalogue sweep is justified without a specific hypothesis.
- Omni's example-shaped structured output failed digital silence. Simpler classification labelled silence correctly but labelled a known tone as silence with reasoning off/on. Invalid WAV input caused a decoder error; valid synthetic speech transcribed correctly. Audio transport is therefore functioning at least for these controls, but non-speech recognition in the tested hosted setup is not adequate for corroboration. It remains uncertain which model/serving/prompt limitations explain all failures.
- No candidate track is approved. Rejected raw probes remain under ignored `artifacts/rejected-generation/`; review clips and responses are local. [Generation tooling](../../scripts/generation/README.md) enforces structural/source-preservation checks and writes separate candidates only. Human review remains required even if a model passes the small controls.

## Official references checked

- [Lightning model card](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/modelcard) and [API model identifier example](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/build).
- [GPT OSS 20B on NVIDIA](https://build.nvidia.com/openai/gpt-oss-20b/modelcard).
- [Cosmos3 Nano Reasoner model card](https://build.nvidia.com/nvidia/cosmos3-nano-reasoner/modelcard).
- [Nemotron 3 Nano Omni model card](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard).

These references support advertised capabilities, not successful requests from this account or suitability for the participant study. Existing local failure evidence is described in [caption generation status](../CAPTION_GENERATION_STATUS.md).

## Follow-up: isolated factors and honest limits

The [current investigation](../audits/2026-10-24-investigation.md) reuses historical speech/decoder controls and records ten new single-attempt calls in [current evidence](../verification/investigation-2026-10-24/README.md). Same-prompt Lightning temperature .2/1.0 both returned ambient. Explicit noun-copy prompts produced an unexpected Spanish music word and correct held-out footsteps. This supports partial prompt/task sensitivity, not accepted English caption variants.

Omni again called 16 kHz audible tones silent. Its 48 kHz counterpart returned HTTP 503 worker-capacity exhaustion, so sample-rate suitability is still unresolved. Plain silence was correctly called silent, while classification silence was incorrectly TONE; a held-out two-tone mix was called silent. No film inference, automatic sound matching or gate clearance followed. All requests used 2.05-second shared pacing, one attempt and 180-second waits; production retry defaults remain intact. Account limits/backend checkpoints remain unverified.

Primary-source research also considered Audio Flamingo Next/AF3, specialised temporal grounding (SpotSound), framewise event detection and CLAP retrieval. Published benchmark results do not transfer to this hosted setup. No alternative GPU service, weight download or paid integration was started. The implemented fallback is hash-bound human listening/wording review, not another plausible model response. Exact references, dates, evaluation limits and acceptance criteria are in the current investigation.

## Subsequent local replacement trial

A separate local Gemma 3n E2B 4-bit / MLX-VLM 0.7.10 trial made 12 bounded generations on 24 October. It failed non-speech observations despite distinct audio feature/embedding tensors and some speech transcription. This is not a new NVIDIA result or a claim about all models. No existing failed NVIDIA gate was cleared. The user subsequently required local-only work and declined Gemini. A separate pinned Whisper sound-caption fine-tune also failed 12 short local generations, including a repeat with an explicit attention mask; no cloud alternative is pending. See [local trial evidence](../verification/sound-captions-2026-10-24/README.md).
