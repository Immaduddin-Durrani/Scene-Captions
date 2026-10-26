# BBB NIM experiments — 26 October 2026

**Outcome: NIM authentication and some media conditioning work. Reliable deep sound-caption generation has not passed. No new NIM track is installed.** The pre-existing local Qwen/editorial draft remains the personalized track. The comparison control now selects the actual fetched reference, rather than another generated caption.

This note consolidates experiments after the initial probes; it is not a preregistration. Each saved input manifest was fixed before its respective run. The latest user request expressly authorizes NVIDIA inference for BBB, superseding the earlier local-only instruction for this task. No paid inference, other-film generation, agents, installation, push or deployment was performed.

## Actual calls and reproduction

[Summary with every response](summary.json): **42 inference requests**, 27 HTTP 200, nine HTTP 503, four HTTP 500, one timeout and one HTTP 404. These are observations, not 27 accepted captions. Account discovery separately returned 85 model IDs; listing did not guarantee access (Kimi returned 404). The models list cache is local under `artifacts/nim-phase1-2026-10-26/models.json`.

The [input manifests](inputs/) and [reports](reports/) preserve exact prompts, model parameters, media hashes, request-body hashes, durations, response status, finish reason, latency, available request IDs and results. Inline media is replaced by hashes/lengths in reports; the account identifier in the Kimi error is redacted (raw original retained locally). No key is included. Local derived media stays ignored under `artifacts/nim-phase1-2026-10-26/`.

| Run | Purpose and observed result |
| --- | --- |
| documented-baseline (6) | Official-shape `audio_url` with a new synthetic phrase: exact transcription, confirming working input on that case. Four non-speech controls: three capacity errors and a narrow piano description for a mixed film excerpt. Super VL text-only grounded-facts control produced three useful levels. |
| capacity-retry (3) | Explicit, single unchanged-payload retries of capacity failures: silence/music still 503; a continuous 440-Hz tone described as picking a pen off a table. |
| video-audio-controls (4) | New spoken phrase inside video transcribed with and without `use_audio_in_video`. Apple clip described as a pop; identical-picture muted clip described as buzzing. The flag is accepted, but this experiment does not show it was necessary on the hosted endpoint. |
| strict-controls (6) | Same audio with a silence/uncertainty-aware prompt: silence → tone, tone → silence, apple → tone. Enabling reasoning on those three returned capacity errors, so reasoning quality is unresolved. |
| grounded-pilot (3) | Super VL, silent video + licensed reference, reasoning none: three complete responses, but essentially repeated reference labels. |
| grounded-context-v2 (3) | Clarified permission for relevant visible context: two repeated-reference responses, one 500. |
| input-audio-controls (3) | Alternate hosted-schema content shape, same WAV bytes: new spoken phrase → “Um”; tone → a person speaking; silence 503. Reject this route. |
| av-reference-plot (3) | Omni with actual sound, ±5-second video context, reference and plot: empty caption arrays. Its identical-picture muted counterpart nevertheless claimed an audible apple thud. Plot text was also misplaced among visible observations. |
| alternative-context (2) | Super VL low reasoning produced useful apple detail; Kimi was listed but unavailable to this account (404). No agent/tool features were used. |
| context-pilot-v3 (5) | Broader, source-assisted Super VL pilot: brook/snoring usable draft context; nuts timed out; overlap/wind 500. No acoustic enrichment was established. |
| context-v3-no-reasoning (4) | Same v3 media/prompts, reasoning none: snoring detail reproduced; nuts/overlap responded but had questionable scene/species claims or little extra information; wind 500. |

Do not count 503/500/timeouts as recognition failures, or exclude successful but wrong controls. Reports are separate from historical 24 October trials. There was no automatic retry loop: 42 counts every explicit observed attempt, including follow-ups.

## Strong evidence and limits

- [Muted short clip proof](muted-control-proof.json): 48,128 decoded PCM16 samples, all zero; sound-on/muted video packets have identical hashes. Buzzing was a controlled false positive.
- [Muted contextual clip proof](muted-context-proof.json): 182,272 decoded samples, all zero; picture packets identical. Adding a plausible reference and plot did not prevent the false claim of an audible thud.
- The new spoken phrase was not in the prompt or visible on screen. Correct transcription supports authentication, decoding and some audio conditioning; it does **not** establish non-speech reliability.
- Super VL can transform supplied facts. It has no documented audio input. Its detailed apple caption adds visible location, not newly recognized acoustic qualities.
- Manual inspection of exact-time frames confirmed a sleeping rabbit in a burrow and a grassy brook. The nuts response also called the film's rodents a fox/mouse and drew on surrounding actions. A single screenshot cannot certify a whole moving event; no full listening review or independent review occurred.
- Three detail levels must add supported information. Copying a label, adding punctuation or describing scenery is insufficient evidence of improved deaf-centered captions. Equal levels are preferable to invented detail, but do not meet the request for deep acoustic detail.

The tested request contract is supported and partially validated. We cannot prove an “ideal harness,” identify the hosted checkpoint/quantization/audio-tower configuration, or attribute all failures exclusively to model weights. The remaining bottleneck is the **tested model/serving path's non-speech grounding**, with additional availability failures. New prompt wording cannot be assumed to cure it. No model weights were fine-tuned; these were prompt/configuration experiments.

## Research and model selection

Official sources checked on 26 October:

- [Omni API card](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning), [hosted schema](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer), [NIM 1.7 media guide](https://docs.nvidia.com/nim/vision-language-models/1.7.0/examples/nemotron-3-nano-omni-30b-a3b-reasoning/api.html). Audio/video support makes Omni the relevant hosted audio candidate. We used bounded WAV and MP4 data URIs, 16-kHz mono PCM audio, adequate token budgets, reasoning off/on and the documented embedded-audio flag. Self-hosted examples are not a guarantee of hosted implementation parity.
- [Super VL hosted schema](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3_5-super-vl-120b-a12b-infer): use its own `reasoning_effort` controls. [Build listing](https://build.nvidia.com/nvidia/nemotron-3.5-super-vl-120b-a12b) advertises text/image/video and Free Endpoint. It is a reference/context transformation candidate, not an audio detector. The Build listing and other docs disagree on some headline parameter/context figures; this experiment does not need those maxima and does not resolve the discrepancy.
- [Kimi card](https://docs.api.nvidia.com/nim/reference/moonshotai-kimi-k2-6) lists text/image/video, not audio. Its account-specific access check failed. [Gemma 4 31B](https://docs.api.nvidia.com/nim/reference/google-gemma-4-31b-it) reserves family audio support for smaller E2B/E4B variants; [Step 5's hosted schema](https://docs.api.nvidia.com/nim/reference/stepfun-ai-step-5-preview-infer) explicitly excludes audio. Swapping among these cannot solve independent sound recognition.
- [Audio Flamingo's official repository](https://github.com/NVIDIA/audio-flamingo) is promising research, but no applicable free hosted NIM endpoint was verified in this account's catalogue or targeted search. Open weights are not a free hosted service. No new large local weights/container/GPU service was installed on the 16-GB Apple Silicon machine.

The Build catalogue advertises free endpoints, but exact account balance/quota/expiry and unlimited continued availability were not verified. Client pacing is 2.05 seconds between starts, approximately 29/minute; that is our bound, not a newly established NVIDIA entitlement. Existing key loading stayed private. No inference SDK, GPU, new account or persistent service was needed for these calls.

Research applied, with transfer limits:

- [CapTune](https://arxiv.org/abs/2508.19971), section 4: reference anchors and local audiovisual context motivated our bounded context pipeline. Its actual implementation uses VideoLLaMA2.1-7B-AV plus GPT-4o. It does not establish equivalent NIM performance. We did not reproduce its study or claim its results.
- [HalluAudio](https://arxiv.org/abs/2604.19300): negative/presence and mixed-content checks motivated separating speech success from false sound assertions. Our tiny custom controls are not the published benchmark.
- [SpotSound](https://arxiv.org/abs/2604.13023): timing is a separate problem; transcription timestamps do not establish effect onsets. We retained reference timings and did not invent model-derived timestamps.
- [NVIDIA's Omni report](https://arxiv.org/abs/2604.24954v2), [local PDF](../../research/nvidia-2026-nemotron-omni.pdf): supports the advertised multimodal architecture, not this hosted endpoint's film-caption accuracy. PDF version/license/hash is in the research manifest.

Requested user reports were checked separately: [this firsthand Reddit report](https://www.reddit.com/r/LocalLLaMA/comments/1wpu6wf/best_omni_model_under_40b_parameters_currently/) praises transcription correction, not sound-effect captioning. [NVIDIA-repository issue 7415](https://github.com/NVIDIA/NemoClaw/issues/7415) documents a capacity error hidden by another client stack; it motivates preserving raw status, not blaming capacity for incorrect HTTP-200 answers. Neither anecdote overrides our controls or justifies installing its software.

## Preparation harness and acceptance

The [bounded diagnostic driver](../../../scripts/diagnostics/phase1_nim.py) sends only explicit NIM requests, records results and cannot install a track. [Context preparation](../../../scripts/generation/prepare-nim-context.py) checks the exact film and licensed SRT hashes, extracts silent 2-FPS/512px clips around source cues and creates explicit manifests. Context is normally ±5 seconds, clipped at film boundaries and bounded to 15 seconds. It is intentionally separate from audio grounding. All generation is outside playback.

Before full-film acceptance: pass silence/audible controls; inspect representative music, ambience, impacts, simultaneous events and recurring sounds; distinguish reference-only from audible observations and visual context; preserve every reference event; reject added unsupported attributes; validate output type/completeness; check reading time at each detail; review timing against this exact edit; resolve listening/wording issues and obtain DHH usability review before a participant study. JSON validity or agreement with supplied captions is insufficient. A reference-assisted pilot can be useful without clearing the failed audio gate.

Only one licensed BBB sound-caption reference is verified here. The nonverbal film does not supply a second ordinary dialogue-subtitle baseline. Do not label two versions of the same source as independently fetched baselines. A/B demo comparisons are for presentation; repeated viewing would confound a comprehension experiment.

## Skills and verification

Work stayed in the main session. `systematic-debugging` supplied boundary/one-factor controls and separation of transport, capacity and semantic failures. `inferya-design` used Impeccable's existing-context and clarify guidance for a narrow reference-comparison correction; existing visual tokens were preserved. No competing component workflows, redesign, hook or automatic skill chain was needed. Existing code maps remain stale for the pending changes.

[Implementation checks](implementation-checks.json), [Playwright regression](browser_smoke.json), [focused comparison checks](comparison.json) and [production build](build.log) passed. The browser rendered all 87 fetched cues after actual seeks, exercised three detail presets on three cues, verified same-time reference toggling, keyboard activation, imports, preference persistence, rehearsal/export and mobile layout. A stale feedback label found during visual review was corrected and checked in the final build. Desktop/mobile and 720px reflow screenshots are local under the task artifacts. CSS zoom produced an unsuitable simulation with clipping; it was retained as a limitation and replaced with a narrower-viewport reflow check. Native 200% browser zoom is unverified. None of these implementation checks validate sound correctness or DHH usability. Test messages about retries are mocked/offline, not additional inference calls.

## Paid proposal declined — historical only

If independently grounded acoustic depth is required, a separately authorized OpenRouter pilot can test an alternative serving/model path on the same controls before any film-wide generation. [OpenRouter audio documentation](https://openrouter.ai/docs/guides/overview/multimodal/audio) supports base64 `input_audio`; [video documentation](https://openrouter.ai/docs/guides/overview/multimodal/videos) supports compatible video models. A paid model is not presumed accurate.

Concrete proposed pilot: Gemini 3.8 Flash, at most eight short requests (new speech, silence, tone, music, overlap, impact and matched-muted controls), at most US$1 estimated usage, account/key spending cap, no full-film run unless the pilot passes and that scope is approved. [Proposed inputs](inputs/openrouter-pilot-proposed.json) are prepared but not executed. Recheck model/provider/audio pricing before invocation; the [current listing](https://openrouter.ai/google/gemini-3.8-flash) is not an exact audiovisual invoice. No OpenRouter key was read and no paid call was made. Fresh permission is required by the user's personal workflow rule, not by an inferred skill restriction.

User decision after this report: **Keep everything on NVIDIA NIM.** The paid proposal above is closed, not pending. No paid provider is authorized. Continuing results will be recorded separately.
