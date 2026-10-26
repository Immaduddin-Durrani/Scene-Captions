# Research prompt: independent DHH sound captions using NVIDIA NIM

Copy everything below into another AI. It is self-contained; repository access is optional.

---

Act as a careful researcher in audio understanding, audiovisual models, temporal grounding, accessible captioning, and inference debugging. Research only. Find evidence that could change our next experiment, including mistakes in our approach. Do not merely suggest more prompt wording.

Our evidence snapshot is **26 October 2026**. State your research date. Check current official documentation, papers, supplementary material, author repositories, model cards, issues and release notes. Distinguish publication, revision and software-release dates. If your research is later, identify developments that were unavailable at our snapshot. Do not invent sources, endpoints, model availability, measurements or successful experiments.

## 1. Product and actual goal

SceneCaptions is an HCI web application for Deaf and hard-of-hearing (DHH) viewers. Our Phase 1 deliverables are a running application and an experimental plan. The immediate demonstration concerns **Big Buck Bunny only**, using a local edit lasting **596.461678 seconds**. The film has little/no spoken dialogue; recognizing sound effects, nonverbal vocalizations, ambience and music is the main challenge.

We need our own captions generated **from the actual media**. Existing subtitles, descriptive captions, event labels and their timestamps must not be generation inputs. A solution should also work for a video that has no prior captions. Existing tracks may be kept isolated as evaluation/comparison baselines after generation. Do not solve this by paraphrasing or expanding fetched captions, or by asking a model to recall this well-known film.

Audio alone, video alone, or separately processed audio and video may be used. A plot or scene summary can be optional context, but must not establish that a sound happened. Visible actions do not prove audibility. Research when context should enter the pipeline and how to prevent story knowledge from contaminating acoustic evidence.

Desired output:

- An event ledger: event ID, clip identity, local/global start and end, sound description, evidence modality, uncertainty and supported attributes. Accommodate overlapping events, background music and off-screen sounds.
- Essential, Balanced and Detailed DHH captions derived from that same grounded ledger. Detail should add supported information, not just adjectives, punctuation or verbosity. Do not invent source identity, instrument, emotion, pitch, loudness or spatial location.
- Consistent dialogue across levels where dialogue exists; distinguish intelligible speech, unintelligible speech and nonverbal vocalizations.
- Honest abstention and unresolved timing rather than fabricated precision. Captions should be readable while watching the film. Do not assume one universal reading-speed limit for every DHH viewer.

An existing Next.js/React player already supports switching detail levels and a reference comparison. Its **87 current sound cues are source-assisted local Qwen/editorial drafts**, with reference timings. They are not independently generated acoustic observations and do not meet the media-first goal. Nine displayed grid cells do not mean nine independent semantic generations: expression styles are largely deterministic punctuation. No new independent NIM caption track has passed acceptance or been installed. The complete proposed media-first pipeline is unfinished.

Only one licensed detailed BBB sound-caption reference is verified in this project. There is no separately verified ordinary dialogue-subtitle baseline for this largely nonverbal film. Do not invent two independent fetched baselines.

## 2. Hard constraints

- **All model inference must remain on NVIDIA NIM hosted free/trial endpoints.** The user explicitly declined OpenRouter and paid-provider fallbacks. Do not make switching providers your recommendation.
- A working NVIDIA key is already stored privately. Never request, print or include keys. Account balance, expiry, exact quota and unlimited continued availability are unverified.
- Development machine: Apple Silicon Mac, **16 GB RAM**, no available NVIDIA training/inference GPU. Lightweight local FFmpeg, PCM checks and application code are available. Do not assume large local model weights, CUDA, a self-hosted NIM container, fine-tuning infrastructure or newly installed audio models.
- Open-source weights or a paper's demonstration do not imply a usable free hosted NIM endpoint. Verify the exact model ID, input modality, route, current availability and account entitlement separately.
- Research only: do not execute API requests, install software, download model weights, start services, register MCP servers, activate unnamed skills, delegate to agents, spend money, publish, deploy or contact anyone. Propose bounded tests for us to review later.
- Prompt engineering/configuration experiments are allowed in the proposed plan; do not call them weight fine-tuning.

## 3. Serving contract we actually tested

Primary audio-capable candidate:

```text
POST https://integrate.api.nvidia.com/v1/chat/completions
model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
```

Recent controlled requests used a single user message without history. Audio was a base64 data URI in `audio_url`, using **mono 16-kHz PCM16 WAV**. A split audiovisual case added a base64 `video_url` MP4 containing **only silent video**, with the same zero-second origin. Content order: audio, optional video, text. Video was H.264, 512 pixels wide, 2 fps, ten seconds, below 4 MB. The WAV bytes were identical between audio-only and split audiovisual cases. Neither supplied expected labels, plot, title, reference captions nor reference timestamps.

Typical parameters:

```json
{
  "max_tokens": 4096,
  "temperature": 0.2,
  "top_k": 1,
  "stream": false,
  "chat_template_kwargs": {"enable_thinking": false}
}
```

The latest thinking ablation changed only `enable_thinking` to `true` on the corresponding simple-prompt requests. It did not set `reasoning_budget`. Diagnostic requests used a single attempt and 180-second timeout; client starts were paced at least 2.05 seconds apart. Request/media hashes, exact text/parameters, status, completion reason, timings, available request IDs and raw responses were recorded. No retry failures were hidden.

Earlier controls also tested:

- Embedded soundtrack in MP4, with and without `mm_processor_kwargs.use_audio_in_video: true`. Novel speech transcribed correctly in both cases on the hosted route. The flag's necessity on that route is therefore unproven.
- `input_audio` as an alternative content shape. The same novel phrase became “Um”; a tone was described as speech. This shape did not improve our result.
- A text-only Ultra request initially returned HTTP 400 for the advertised reasoning-budget control: `thinking_token_budget is not yet supported by the V2 model runner`. Removing that budget produced HTTP 200. This is one confirmed request/serving incompatibility, not evidence that Ultra can hear audio.

The hosted service did not expose a checkpoint, quantization, audio encoder, NIM version or vLLM version in the captured response headers. Do not assume the hosted runtime matches a particular self-hosted documentation release.

## 4. Actual evidence, including the newest tests

Earlier investigation recorded 42 requests, followed by nine additional checks. Do not aggregate their heterogeneous tasks into a film-accuracy score. Useful observations:

- A newly synthesized phrase, absent from the prompt and picture — “Seventeen blue lanterns are beside the window.” — transcribed correctly as “17 blue lanterns are beside the window.” This worked with audio and with embedded video. Authentication, transport and some audio conditioning work.
- Digital silence was described as a tone or buzzing. A continuous 440-Hz tone was described as silence or a person picking up a pen. A muted film clip elicited a thud even though decoded PCM samples were all zero and picture packets matched the audible counterpart.
- Source-caption/plot-assisted requests could repeat supplied facts without establishing acoustic recognition. Some visual descriptions were useful, others contained wrong species or neighboring actions. These do not validate independent sound captioning.
- HTTP 503 `ResourceExhausted: Worker local total request limit reached (16/16)`, HTTP 500 and timeouts also occurred. These are availability/inconclusive outcomes, distinct from wrong HTTP-200 answers.

### Latest frozen counterfactual experiment: 12 requests

Two natural sound controls came from the **ESC-10 subset of ESC-50**, revision `33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6`: dataset-labeled dog (`1-100032-A-0.wav`) and rain (`1-17367-A-10.wav`). Labels were evaluation metadata only; requests used blinded case IDs. Public training contamination is possible, so this is not a held-out generalization claim. Dataset clip labels are not human event-onset annotations.

Each final WAV contained 160,000 PCM16 samples, ten seconds at 16 kHz:

- c01: the five-second dog source inserted at 1–6 s. The source itself was mostly zero padding: its actual nonzero samples occurred only at **3.2291875–3.586625 s** in the final clip.
- c02: the exact same source samples shifted by **48,000 samples / three seconds**. Nonzero support **6.2291875–6.586625 s**. This was verified sample-for-sample.
- c03: rain source inserted at 1–6 s, nonzero support approximately **1.0–5.9999375 s**.
- c00: digital silence, all 160,000 samples zero.

Thus the dog is a brief ~0.357-second burst, not five seconds of continuous barking. Its whole-clip RMS was −30.65 dBFS and peak 32347/32768; rain RMS was −24.19 dBFS and peak 21288/32768. Research event-duration/sparsity and preprocessing as hypotheses rather than assuming these controls are equally difficult. Nonzero support proves silence outside those samples, not exact human semantic event boundaries.

Every split audiovisual case used the same first ten seconds of BBB, with the original audio, text/data streams, metadata and chapters removed. Identical PCM inputs avoid an AAC-versus-WAV confound. However, a hosted model might process simultaneous separate audio/video differently; successful speech transport does not prove this path preserves every non-speech cue.

The initial prompt requested only audible events with approximate local times, speech separately, no visual/story guesses, null/null times when uncertain, empty arrays for silence, maximum 20 events, and this object:

```json
{"events":[{"sound":"description","start_s":null,"end_s":null}],"speech":[],"limitations":[]}
```

Actual initial eight responses:

| Case | Result |
| --- | --- |
| c01 audio only | Timeout after about 181 s; inconclusive. |
| c02 audio only | HTTP 503 capacity error; inconclusive. |
| c03 audio only | HTTP 200: “Water splashing” 0–6 s and “Silence” 6–10 s. Broadly water-related, not strict rain recognition; claims activity in known silent 0–1 s. Returned an array rather than the requested object. |
| c01 audio + silent video | HTTP 200: electronic tone 8.5–10.5 s, beep/click 0–0.1 s. Wrong category, sound in known zero padding and an end beyond ten-second duration. Wrong JSON root shape too. |
| c02 audio + same video | HTTP 200: rustling leaves and wind, each 0–10 s. Missed dog; events extend through digital silence. Wrong root shape. |
| c03 audio + same video | HTTP 503 capacity error; inconclusive. |
| c00 silence + same video | HTTP 200: sustained electronic tone 0–10 s. Definite false positive on zero-valued PCM; malformed result structure. |
| fresh speech positive control | HTTP 200 and explicit normal completion: the exact expected phrase. |

Two follow-ups removed **only** JSON/timing requirements from dog/rain audio requests, asking for one concise description of what is heard. Both returned 503, so they do not tell us whether output-format burden was the cause.

Two more used the same simple requests with thinking enabled. Dog returned 503. Rain returned HTTP 200: “The audio consists solely of a continuous, immersive roar of turbulent water with no other audible elements.” This is broad water-related recognition, not an accepted rain/timing result; it did not acknowledge the silent sections. Because its matched thinking-off request had 503, we cannot claim thinking improved accuracy.

Total for this new batch: **six HTTP 200, five HTTP 503, one timeout**. Four structured sound responses had the wrong JSON root shape. Inspect raw semantics separately: schema invalidity alone is not proof of wrong sound recognition. Conversely, a schema repair would not cure sounds invented on digital silence. No correctly identified timed dog pair was available, so the three-second onset-shift test is **unscorable**, not a measured timing pass/fail. Missing/failed requests must not be scored as wrong recognition or quietly dropped.

### Harness audit and limits

The local audit found and fixed acceptance gaps: require explicit `finish_reason: "stop"` for structured output and the speech control; reject missing/invalid/nonfinite/reversed/out-of-range timestamps; bind assessment to the frozen manifest. Two targeted guard mutations were detected by regression tests. All 35 offline Python tests, 19 application tests, TypeScript checks and caption-data validation passed. These validate software contracts, not sound accuracy or DHH usability. No human listening panel or independent reviewer has approved the generated tracks.

Graphify mapped the code locally, but extraction has missing-reference/edge-collapse limitations. Fallow reports application complexity issues and does not analyze Python. Neither a code map nor a static health score proves a correct inference pipeline. The old failed audio-capability gate remains failed; full-film generation/install was not enabled.

Other candidates checked earlier: Super VL supports visual/text context but has no documented audio input; Kimi K2.6 was listed but returned account-specific 404; Phi-4's documented model-specific route returned 404; Gemma 3n E4B returned 410 with a retirement date. These observations are snapshot-specific, not proof of permanent global unavailability. Audio Flamingo has official research code/weights, but we have not verified a usable free NIM hosted endpoint for it.

## 5. Prior research to verify and extend

These are leads, not fixes already reproduced. Prefer new evidence over restating their abstracts. For each, verify method, applicable model/version, release status and whether it can actually be used through our hosted API.

1. [TAC: Timestamped Audio Captioning, v2, 6 October 2026](https://arxiv.org/html/2602.15766v2), [author demo](https://sonalkum.github.io/tacmodel/). Particularly close to our goal: variable detail and overlapping timed audio events. TAC-V uses an audio-first cascade, 20-second audio chunks, speech transcription, FLAM scoring and later visual grounding. It relies on specialized training. Its reproducibility section makes no code/weights release commitment. Do not present copying its prompts as reproducing its trained capability or assume a free NIM endpoint exists.
2. [Don't Let the Video Speak / ACPO](https://vision.cs.utexas.edu/projects/acpo/). Audio-swapping controls expose visual dominance. Its preference optimization is a training method, not a client prompt switch; verify which tested models support transfer of its findings to our case.
3. [Do Audio-Visual LLMs Really See and Hear?](https://ramaneswaran.github.io/avllm_interpretability/). Modality-intervention evidence; distinguish its model checkpoints from our hosted Nemotron.
4. [NVIDIA NIM LLM 2.0.10 release notes](https://docs.nvidia.com/nim/large-language-models/2.0.10/about-nim-llm/release-notes.html). Mentions restored audio support via `vllm[audio]` and PyAV/FFmpeg. This concerns containers, not proven hosted-endpoint state. Our successful novel ASR contradicts a blanket “no audio is reaching the model” diagnosis.
5. [Official Omni media guide](https://docs.nvidia.com/nim/vision-language-models/1.7.0/examples/nemotron-3-nano-omni-30b-a3b-reasoning/api.html), [hosted model reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer). Check exact hosted payload examples, accepted parameters, modality limits and preprocessing assumptions. Do not confuse server environment flags with hosted request parameters.
6. [OpenFLAM, official Adobe repository](https://github.com/adobe-research/openflam/). Framewise text/audio similarity and localization may help check candidate events, but similarity is not calibrated truth. Its local implementation is not automatically available under our NIM-only inference constraint.
7. [AVSCap](https://nju-link.github.io/AVSCap/), [OmniCapBench](https://github.com/Tencent-Hunyuan/OmniCapBench), [Relevant Evidence Decoding](https://arxiv.org/abs/2610.02976), [TimeAudio](https://ojs.aaai.org/index.php/AAAI/article/view/39827). Verify evidence separation, temporal grounding, hallucination measurements and whether methods need training, logits/decoding access or unavailable weights. “Training-free” does not automatically mean usable through chat completions.
8. [HalluAudio](https://arxiv.org/abs/2604.19300), [SpotSound](https://arxiv.org/abs/2604.13023), [CapTune](https://arxiv.org/abs/2508.19971). Separate sound recognition, temporal localization and source-caption personalization. CapTune's source-conditioned objective is different from our required caption-free discovery.

Search beyond these leads for relevant recent work, including dense audio captioning, non-speech encoder limitations, event sparsity, modality conflict, conditional hallucination, calibrated abstention and DHH caption preferences. Include reproducible issue reports with exact versions if available. Separate user anecdotes from validated measurements.

## 6. Questions your research must resolve

**Model vs serving vs client:** Which plausible failures remain in decoding, resampling, channel conversion, duration truncation, audio tokenization, separate audiovisual binding, input ordering or instruction format? Which are ruled out only partially? Could a speech-oriented path retain ASR while losing non-speech detail? What official evidence or control would distinguish this from model-weight limitations? Identify any documented request error we missed. Do not conclude “harness ideal” or “definitely model incapable” from the current tiny sample.

**Discriminating controls:** What is the smallest useful next test? Consider dense versus sparse natural events, cropping the existing brief burst versus repeating it, a fresh spoken phrase at a late known offset, identical visuals with swapped audio, and no-video/zero-audio controls. Identify confounds: changing duration, loudness or codec together; missing matched responses; public benchmark memorization; expected labels in prompts; forced event counts; schema demands hiding recognition. Do not repeat a large prompt grid.

**Pipeline:** Research an audio-first event-discovery stage, separate visual source binding and late optional plot context. Assess whole-film versus chunked processing, overlap, event persistence across boundaries, local/global time conversion, deduplication and compact scene memory. Cite why any window/overlap is proposed; no arbitrary “optimal chunk size.” Distinguish semantic event detection from timing refinement. ASR forced alignment cannot locate every non-speech effect; voice activity detection is not general sound detection; waveform energy is not source identity.

**Trustworthy detail:** How can a text reasoner produce three useful detail levels without adding unsupported events or attributes? Can event IDs, evidence fields, conservative descriptions and cross-level checks help? What can a verifier using the same model miss? A second prompt is not independent evidence. Identify DHH research supporting which details matter, evaluation with DHH participants, reading burden and ethical presentation of unreviewed generated captions.

**Practical availability:** For every proposed model/tool, give its actual access path, supported modalities, release/license status, resource requirements and whether it satisfies NIM-hosted free/trial-only inference today. Mark unknown account access explicitly. If no verified NIM-only method fits, say so and identify the precise missing capability rather than recommending an unauthorized paid service.

## 7. Required response

1. Start with a simple, concise explanation of what is newly useful and what remains uncertain.
2. Give **6–8 ranked findings**. For each: discovery, primary source/version/date, relevance to our observations, exact limitation, and whether usable now, research-only, or outside constraints. Separate established fact, reported result and your inference.
3. Provide a diagnosis table: hypothesis, current supporting evidence, contradicting evidence, missing evidence and best distinguishing test. Do not invent numerical confidence probabilities.
4. Propose **2–4 bounded experiments**, with controls and fixture ground truth, one changed factor per comparison, complete request sketch for the exact model, call/token limits, pass/fail criteria, treatment of 503/timeout, and a stopping rule. Explain how each possible outcome changes our diagnosis. These are proposals only; do not execute them.
5. Sketch the smallest credible NIM-only pipeline, marking components that remain unvalidated or unavailable. Separate a Phase 1 demonstration from a scientifically validated captioning system.
6. List verification criteria separately for transport/media integrity, schema/completion, sound presence and absence, semantic attributes, temporal alignment, cross-level consistency and DHH usefulness. Use precision/recall and false-positive controls where suitable, not only fluent-text similarity. Avoid WER as the main metric for this nonverbal film.
7. End with a short recommendation: the next experiment most likely to reduce uncertainty, and what evidence would justify pausing full-film generation. Include direct source links next to claims and note contradictory or unavailable evidence.

Use plain language first, technical detail only where useful. Be candid if the literature offers no available fix. Do not claim you tested anything you only researched. Do not treat a published benchmark score as our endpoint's measured performance.
