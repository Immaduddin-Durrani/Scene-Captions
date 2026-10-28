# Media-first DHH sound captions on NVIDIA NIM: what the evidence says before the next experiment

The most useful new finding is architectural. The hosted Nemotron 3 Nano Omni hears through an encoder initialised from an ASR model, Parakeet-TDT-0.6B-v2.\[1\]\[2\] That encoder turns audio into about 12.5 tokens per second, so your 0.357-second dog bark reached the model as roughly four or five tokens out of about 125.\[2\]\[3\] Exact digital silence is also probably unlike anything the model saw in training. Together, these give a specific, testable explanation for good speech transcription alongside weak non-speech recognition and false sounds on zero-valued audio. That explanation does not require a broken transport, and it does not prove the model can never do the job. No paper, NVIDIA release note or issue I found offers a fix you can switch on through chat completions. The published remedies (TAC, SpotSound, ACPO, AVSCap) all require training, and the decoding remedy (RED) needs access to the model's logits.

Research date: Monday 26 October 2026, the same day as your evidence snapshot. Nothing below postdates the snapshot. I have not executed any request; every experiment here is a proposal.

## TL;DR

- **What's new:** The hosted model's ear is an ASR encoder, extended with sound and music data. It samples audio at 80 ms per token, splits audio into 30-second clips, and was trained on inputs from 0.5 seconds to 20 minutes. NVIDIA's own audio-stage mix gives speech, sound and music separate shares (details below). Your pattern (correct novel speech, weak sparse non-speech, invented sound on digital silence) fits independent benchmarks in which models hallucinate least on speech. It also fits visual-dominance studies on other audiovisual models.
- **What remains uncertain:** We still can't tell model-weight limitations apart from hosted preprocessing or binding effects. The hosted runtime version, normalisation and caching behaviour are undisclosed. Your dog/rain controls also differ in density, duration and loudness all at once. I found no documented hosted-endpoint audio bug, and no NVIDIA known-issue entry mentions audio for this model.
- **What to do next:** Run one small audio-only ladder of about 8 calls. It should separate exact digital silence from a low-level noise floor, test a single bark against a repeated bark, and time a fresh spoken phrase at a late offset using the model's documented word-timestamp ability. Pause full-film generation if zero-signal and noise-floor clips still produce invented sounds and a dense, unambiguous event is still missed. Either way, decide digital silence locally from the PCM samples and never ask the model about it.

## Key Findings (ranked)

### 1. The audio path is an ASR encoder that was later given sound and music training

- **Established fact:** The Nemotron 3 Nano Omni technical report (arXiv 2604.24954v1, 27 April 2026) says:
  - The audio encoder "is initialized with Parakeet-TDT-0.6B-v2".\[1\]
  - Audio "inputs are resampled to 16 kHz mono".\[1\]
  - Log-mel features use a 10 ms hop with about 8× subsampling, giving "approximately 12.5 tokens per second of audio (i.e., ∼80 ms per token)".\[1\]\[2\]\[3\]
  - Streams are "segmented into 30-second clips", with "Streams shorter than 30 seconds … not padded".\[1\]\[3\]
  - Training covered "inputs ranging from 0.5 second to 20 minutes".\[1\]\[2\]
- **Established fact:** In audio Stage 3 (encoder and projector training), ASR was 113.8M samples (22.7% of tokens), sound understanding 61.0M (24.4%) and music understanding 19.8M (43.3%).\[2\] Stage 2 projector warm-up used only Granary ASR data. Sound captions were produced synthetically using Qwen3-Omni-30B-A3B.\[1\] The build.nvidia.com model card (release 28 April 2026) calls the component a "Parakeet speech encoder".\[4\]\[5\]
- **Reported result, not your endpoint:** NVIDIA reports MMAU 76.9 on the audio subset with reasoning off.\[1\] That is multiple-choice question answering, not open-ended detection of sparse events with timestamps.
- **Relevance (inference):** At 12.5 tokens per second, the c01/c02 bark is about 4–5 encoder positions in a 125-position sequence, while rain occupies about 62. That alone can explain "rain recognised broadly, dog missed" without any transport fault. Third-party reimplementations of this preprocessing describe "normalized log-mel features": the smg PR #3323 (12 October 2026) and the tokenspeed PR #2228.\[6\]\[7\] The standalone Parakeet config sets `"normalize": "per_feature"`.\[8\]\[9\] Normalising all-zero input per feature removes the only information present, leaving padding-like or dither-like values. My inference is that this makes digital silence out of distribution and makes an invented "tone" plausible. This mechanism is unverified for the hosted runtime.
- **Limitation:** It is unknown whether the hosted service uses identical normalisation, dither or quantisation. The response headers expose none of this.
- **Status:** Usable now as a diagnostic hypothesis that the proposed tests can check.

### 2. Official hosted guidance differs from parts of your configuration; one widely shared claim contradicts it

- **Established fact:** The build.nvidia.com model card recommends two modes:
  - Instruct mode: temperature 0.2, top_k 1, max_tokens 1024.\[4\]\[5\]
  - Thinking mode: temperature 0.6, top_p 0.95, max_tokens 20480, reasoning_budget 16384, grace period 1024.\[4\]\[5\]
  - It says: "For video, audio, and omni use cases, try both enabling and disabling thinking for best results."\[4\]\[5\]
- **Established fact:** The NIM for VLMs 1.7.0 Omni API guide (updated 10 August 2026) says:
  - Thinking is "enabled by default".\[10\]
  - `media_io_kwargs` is a top-level request field. Default video sampling is 2.0 FPS, and at 2 FPS "timestamp precision … will be at best within +/- 0.25 seconds".\[10\]
  - Embedded-audio video needs `"mm_processor_kwargs": {"use_audio_in_video": true}` at the top level.\[10\]
  - Supported audio formats are WAV, MP3 and FLAC; the model card lists only wav and mp3.\[4\]\[5\]\[10\]
  - The guide documents only `audio_url` for audio, so your failed `input_audio` shape is undocumented for this model rather than a disproven alternative.\[10\]
- **Unconfirmed:** A search snippet resembling the hosted infer page lists `reasoning_budget` (−1 to 32768, default 16384) and `max_tokens` 1–65536.\[11\] I could not open the page itself, so its full field list is unverified. Your Ultra `thinking_token_budget` HTTP 400 came from a different model and is not evidence about Omni.
- **Contradiction to flag:** A widely read Substack post by Cobus Greyling states that audio "requires `enable_thinking: false` and temperature: 0".\[12\]\[13\] The official model card does not say this. Treat it as anecdote.
- **Relevance:** Your thinking-off runs at temperature 0.2 and top_k 1 match NVIDIA's instruct preset. Your thinking-on runs did not set NVIDIA's thinking-mode sampling (0.6/0.95) or a budget, so they were not an on-spec comparison of thinking. The only scorable thinking result (rain, "turbulent water") had no matched thinking-off partner.
- **Status:** Usable now.

### 3. No documented audio known issue, but three implementation hazards are documented in neighbouring stacks

- **Established fact:** The NIM for VLMs 1.7.0 release notes (updated 20 July 2026) list two Omni limitations: the variant container, and very large videos (>1 GB) failing with a `NanoNemotronVLProcessor` error.\[14\]
- **Established fact:** The NIM for VLMs 2.0.4-variant notes, the initial certified Omni release (updated 10 August 2026), list a crash on an empty `structured_outputs.json` schema, empty text from blank `/v1/completions` prompts, and HTTP 500 on large videos.\[15\] None mentions audio, `audio_url`, `use_audio_in_video` or short or silent audio.
- **Established fact:** The NIM LLM 2.0.10 notes say the vLLM container "restores audio-input support for omni-class models through vllm[audio]" using av 18.0.0 built against an "audio-decoders-only" FFmpeg 8.1.2.\[16\] The model card likewise says self-hosted vLLM 0.20.0 needs `pip install "vllm[audio]"` if any audio is used.\[4\]\[5\]\[17\] These are container facts, not hosted-endpoint facts. Your correct novel ASR rules out a blanket "audio never arrives".
- **Reproducible issues in other stacks (analogues, not Nemotron-hosted evidence):**
  - **vllm-omni #7295** (vLLM 0.28.0, Qwen3-Omni): with multimodal caching across replicas, repeating identical audio bytes can return HTTP 200 with `finish_reason="error"` and empty content.\[18\]
  - **vllm-mlx PR #807:** audio extracted from video "never got a chat-template placeholder", so frames reached the model and audio silently did not.\[19\]
  - **smg PR #3323:** audio beyond "vLLM's 600 s decode limit is refused".\[6\] Your 596.461678-second edit is just under that, so whole-film single requests leave no margin on any similar runtime.
- **Relevance (inference):** You reused identical WAV bytes across audio-only and audiovisual conditions. If the hosted service caches multimodal encodings, a cache fault is a low-prior but untested confound. Your `finish_reason: "stop"` gate already guards against the #7295 failure mode.
- **Status:** Usable now as harness checks.

### 4. Visual dominance is established on other audiovisual models, and your silent-video results look like it

- **Reported result:** "Do Audio-Visual LLMs Really See and Hear?" (arXiv 2604.02605; CVPR Findings 2026; University of Maryland) studies other models, not Nemotron. It reports relative drops of up to 56% on counterfactual audio–visual conflicts. It also finds 61.4% "latent audio understanding" inside the model against only 23% audio fidelity in generated captions on counterfactual samples. Deep fusion layers privilege vision, and the model's audio behaviour "strongly matches its vision-language base model".\[20\]\[21\]
- **Reported result:** ACPO, "Don't Let the Video Speak" (arXiv 2604.14129; ECCV 2026, LNCS 17076), reports that "feeding more video frames into AVLMs actively triggers more audio hallucinations, while adding audio causes no such degradation to visual QA". Its fix is preference optimisation with swapped audio tracks, which is a training method.\[22\]\[23\]
- **Relevance:** In your split audiovisual cases you got rustling leaves and wind for 0–10 s over a dog-plus-silence track, and a sustained tone over zero audio. These look like video-driven or prior-driven sound claims. Whether Nemotron's fusion behaves like these checkpoints is unmeasured. Nemotron did receive dedicated "omni" training, and its Omni-RL included "~4K" unanswerable or mismatched samples to train abstention,\[1\] which may or may not have covered audio.
- **Status:** The findings are research-only. The audio-swap control method is usable now.

### 5. Sparse, short events and absent-event queries are a recognised, separately measured weakness of audio language models

- **Reported result:** SpotSound (arXiv 2604.13023; ACM MM 2026; code, model and benchmark released) builds a "needle-in-a-haystack" benchmark in which targets occupy "less than ~10%" of each clip. On negative queries, where the event is absent, Qwen2-Audio scored 78.0% accuracy and Kimi-Audio 60.5%, and TimeAudio could not answer.\[24\] SpotSound's fix is a training objective that "suppress[es] hallucinated timestamps for events absent from the input".\[25\]\[26\]\[27\]
- **Reported result:** MISHAP-Bench (arXiv 2609.33893, preprint) finds "no model is reliably grounded", with Gemini 3.7 Flash at a 36.5% hallucination rate and all models hallucinating "most on music and least on speech".\[28\] HalluAudio (ACL 2026, DOI 10.18653/v1/2026.acl-long.1797) is a human-verified benchmark covering speech, environmental sound and music.\[29\]\[30\]
- **Relevance:** Your dog fixture occupies about 3.6% of its clip, squarely in SpotSound's hard regime. Rain occupies about 50%. Speech, the easiest category in MISHAP, is exactly where you got a clean result.
- **Inference:** The c01/c02 onset-shift test was posed in the hardest condition first. Test dense-event recognition before sparse-event timing.
- **Status:** The benchmarks are research-only. SpotSound-Bench's design is usable as a fixture pattern, but its audio is public and could be memorised.\[31\]

### 6. TAC is the closest design to your goal, and its evaluation protocol is more reusable than its model

- **Reported result:** TAC v2 (arXiv 2602.15766v2; Kumar, Seetharaman, … Salamon; submitted 17 February 2026, v2 dated 6 October 2026):
  - **Model:** a LoRA fine-tune of Qwen2-Audio on synthetic mixtures of about 150K clips (about 1.2K hours), with timestamps derived from per-source RMS activity.\[32\]
  - **Controls:** style (keywords, brief, detailed), merge threshold, activity threshold and time resolution.\[32\]
  - **Results:** Event F1 0.50 and a 4.9% hallucination rate, against Gemini 3 Pro at 0.42 and 6.1% and Audio Flamingo 3 at 0.27 and 11.6%.\[32\]
  - **Hallucination metric:** a predicted event counts as hallucinated when FLAM confidence falls below τ = 0.25.\[32\]
  - **Matching protocol:** Event F1 uses a ±1.0-second onset collar, Segment F1 a 100 ms resolution, and an LLM judge compares descriptions (Spearman 0.81 with human ratings on 100 TACOS samples).\[32\]
  - **TAC-V:** uses 20-second non-overlapping audio chunks, Whisper on cropped speech intervals, FLAM scores, and Qwen3-VL-32B for visual grounding and "Hallucination Correction".\[32\]
  - **Ablation:** a 0.1-second merge threshold raised hallucination to 13.8%, and "keyword captions have low hallucination because they are conservative".\[32\]
- **Relevance:** This supports your plan: audio first, vision second, detail levels from one event list, and conservative wording when uncertain. The detail-versus-hallucination trade-off (8.0% for detailed against 4.9% for brief)\[32\] is direct evidence that Detailed captions need stricter evidence rules.
- **Limitation:** There is no NIM endpoint, and the reproducibility section makes no release commitment for code or weights. Copying the prompts would not reproduce the trained timestamp tokens or the weighted timestamp loss.
- **Status:** The model is outside constraints. The metrics and matching protocol are usable now.

### 7. "Training-free" decoding fixes and frame-level checkers do not fit a chat-completions, NIM-only budget

- **RED (Relevant Evidence Decoding),** arXiv 2610.02976, submitted 2 October 2026:
  - **Method:** pointwise mutual information over audio-only, video-only and joint passes, plus a question-only pass, applied to output logits.\[33\]
  - **Results:** up to +7% on CMM, +6.3% on AVHBench and +3.8% on SVHalluc across three audiovisual models, at about 1.5× time to first token.\[34\]
  - **Fit:** it is training-free but needs logit-level access, so it is not a chat-completions switch.
  - **What you can borrow:** the evidence-relevance logic. Compare audio-only, video-only and joint outputs at the text level.
- **OpenFLAM** (Adobe; `pip install openflam`; 48 kHz input; repo updated 4 June 2026) gives frame-wise text–audio similarity.\[35\]\[36\] It is local inference, so it breaks your NIM-only rule. Its scores are similarity, not calibrated truth.
- **AVSCap** (arXiv 2607.12820; EMNLP 2026) supports a "decoupled-then-fused" design that "anchors visual and acoustic evidence independently before composing" captions.\[37\] Its model is a trained Qwen2.5-Omni 7B with no NIM endpoint.\[38\]
- **Audio Flamingo 3 and Audio-Visual Flamingo** have Hugging Face weights. AF3 checkpoints carry non-commercial terms. Neither has a verified hosted NIM endpoint.
- **Status:** All outside constraints except the design ideas.

### 8. DHH research supports selective, important-sound captioning and argues against one fixed reading rate

- **Reported results:**
  - "Beyond Subtitles" (Alonzo, Shin and Li, ACM ASSETS 2022; interviews with 11 DHH participants and a prototype evaluation with 10 hearing creators) found DHH participants want *important* non-speech sounds included in captions and advises being "selective".
  - "Unspoken Sound" (May et al., CHI 2024) documents inconsistent non-speech captioning practice on YouTube.
  - OnomaCap (CHI 2025) found a strong preference for onomatopoeic captions across levels of hearing loss.\[39\]
  - µCap (CHI 2026) addresses instrumental music captions for DHH viewers.\[40\]
  - An EEG study (PMC7040021) documents limits of standard sound and music captioning.\[41\]
- **Reading speed:** Jensema (1998, American Annals of the Deaf 143(4); 578 deaf, hard-of-hearing and hearing viewers) found the "OK" speed was about 145 wpm, with most viewers having little trouble until at least 170 wpm, while a recent eye-tracking study (ACM DOI 10.1145/3806039) found deaf viewers reading comfortably at 180 wpm when segmentation was good. Szarkowska et al. (2011, American Annals of the Deaf 156(4); eye tracking with 9 deaf, 21 hard-of-hearing and 10 hearing viewers) found deaf viewers differed from the other two groups only with verbatim captions.
- **Relevance:** Essential/Balanced/Detailed should be a selection of events by importance, not only more adjectives, which matches your goal. Reading burden should be tested with participants rather than fixed by a constant.
- **Status:** Usable now for design and evaluation.

## Diagnosis table

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Best distinguishing test |
|---|---|---|---|---|
| Transport/decoding fault (audio not reaching the model) | None specific | Novel phrase transcribed via `audio_url` and embedded MP4; identical PCM verified | Hosted decoder version | Already largely ruled out for speech; keep the speech control in every batch |
| Digital silence is out of distribution after log-mel normalisation | Tone/buzz on all-zero PCM, repeatedly; per-feature normalisation in the Parakeet config and normalised log-mel in reimplementations | Model card claims RL included abstention samples | Hosted normalisation and dither details | Exact zero vs −60 dBFS noise floor, same duration, audio-only (E1a/E1b) |
| Sparse events are under-represented (about 4–5 tokens for the bark) | Dog missed in both scorable cases; rain broadly recognised; SpotSound's needle regime | Only two scorable responses; dog audio-only runs failed (timeout/503) | Any HTTP-200 audio-only dog result | Single bark vs the same bark tiled across the clip, audio-only (E1c/E1d) |
| Visual dominance in split audiovisual requests | Leaves/wind and tone with silent BBB video; consistent with ACPO and the interpretability study | Embedded-video speech transcribed correctly | Video-only baseline; audio-swap with fixed video | Same silent video with zero, rain and dense-dog audio, plus a video-only call (E2) |
| Separate `audio_url` + `video_url` parts are not temporally interleaved | The report describes temporal interleaving for "videos with audio"; separate parts are undocumented | Speech was fine with separate parts | Server-side placeholder construction | Late-offset phrase timing: separate parts vs embedded MP4 (E3) |
| Speech-oriented encoder keeps ASR and loses non-speech detail | Encoder origin; Stage 2 trained on ASR only; MISHAP finds least hallucination on speech | Stage 3 includes sound and music data; MMAU audio 76.9 | Open-ended sound captioning numbers for this model | Dense, unambiguous non-speech fixtures (E1d); cannot be separated from weights without encoder access |
| Output-format burden masks recognition | Four wrong JSON roots | Rain recognised partly in both formats | Matched simple-prompt dog result (both were 503) | Simple description first, ledger extraction as a separate text-only step |
| Multimodal cache fault on reused bytes | Analogous vllm-omni #7295 | No empty or error completions observed | Hosted caching policy | Append a tiny non-semantic difference (e.g., 1 ms of extra zero tail) to one repeat; compare |
| Model weights cannot do calibrated non-speech detection | Pattern consistent across controls | Tiny sample; many inconclusive calls | Everything above | Only a clean failure of E1 with matched successes would support this, and still only for this endpoint |

## Proposed experiments (proposals only — not executed)

All experiments use these common settings:

- **Endpoint and model:** `POST https://integrate.api.nvidia.com/v1/chat/completions`, model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`.\[42\]
- **Message:** a single user message, audio part first, then text.
- **Parameters:** NVIDIA's instruct preset, `temperature 0.2`, `top_k 1`, `max_tokens 1024`, `stream false`, `chat_template_kwargs.enable_thinking false`.
- **Prompt hygiene:** no labels, titles, plot or reference times in prompts.
- **Pacing:** client starts at least 2.05 s apart (well under the 40 RPM limit that several 2026 NVIDIA Developer Forums threads report for build.nvidia.com keys; a moderator there says the free-tier limit depends on model, use case and overall traffic, with no official way to raise it on the same tier).

**Handling 503s and timeouts** (applies to all experiments):

- Record every attempt.
- Retry at most twice, with at least 60 seconds' backoff. Halt the session after three consecutive 503s and resume later.
- Score a comparison only when both members are HTTP 200 with `finish_reason: "stop"`. Otherwise mark it *unscorable*, never *wrong*.

Base prompt, P-open: "Listen to the audio only. Describe every sound you can actually hear, in order. If there is no audible sound, say exactly NO AUDIBLE SOUND. Do not guess from context."

### E1 — Audio-only presence/absence and density ladder (about 8 calls, plus up to 8 retries)

All fixtures are 10.000 s, 160,000 samples, mono 16 kHz PCM16 WAV, with sample-level ground truth.

| ID | Fixture | Ground truth | Comparison (one factor) |
|---|---|---|---|
| E1a | All zeros | No signal | vs E1b: exact zero vs noise floor |
| E1b | Gaussian white noise at −60 dBFS RMS, fixed seed | Continuous faint hiss only | vs E1a |
| E1c | Existing c02 (single bark, 6.229–6.587 s) | One brief bark | vs E1d: density |
| E1d | The same 0.357 s nonzero bark samples tiled 8 times at 1.0, 2.0, … 8.0 s onsets, zeros elsewhere | Eight barks | vs E1c |
| E1e | Fresh synthesized phrase, not used before, placed with onset at 7.000 s, zeros elsewhere; prompt asks "Transcribe with word-level start times in seconds" | Text plus a known onset | Speech timing control |
| E1f | Repeat of E1a with an extra 16 zero samples (10.001 s) | No signal | Cache/determinism check vs E1a |

Request sketch (E1a):
```json
{"model":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
 "messages":[{"role":"user","content":[
   {"type":"audio_url","audio_url":{"url":"data:audio/wav;base64,<E1a>"}},
   {"type":"text","text":"<P-open>"}]}],
 "max_tokens":1024,"temperature":0.2,"top_k":1,"stream":false,
 "chat_template_kwargs":{"enable_thinking":false}}
```

**Pass criteria:**
- E1a/E1f return NO AUDIBLE SOUND or an equivalent.
- E1b mentions hiss or noise or faint static, or says no sound, and names no discrete source event.
- E1d mentions a dog or bark, or at least repeated short animal-like sounds.
- E1e transcribes correctly, with a first-word onset within ±0.5 s of 7.0 s.

**What each outcome means:**
- **E1a fails, E1b passes:** zero-signal input is out of distribution. Treat silence as a local signal fact and stop asking the model about it.
- **Both fail:** absence calibration is broken more generally.
- **E1d passes, E1c fails:** sparsity is the bottleneck. Chunk tightly and expect brief effects to be missed.
- **Both fail:** non-speech recognition on this endpoint is inadequate for these fixtures. ESC-50 contamination makes a pass weaker evidence, not a fail.
- **E1e timing passes:** the model can localise audio in time for speech, so non-speech timing failures are semantic rather than positional.

### E2 — Audio-swap under fixed silent video (4 calls, plus E1 partners)

Use the same BBB 0–10 s silent MP4 already used, with content order audio, video, text. Vary only the audio (E1a zeros, c03 rain, E1d dense dog), and add one video-only call asking "What sounds would you hear?". That last call deliberately measures the visual prior.

**Pass criteria:**
- Each audiovisual output agrees with its audio-only partner from E1 on presence and category.
- No sound named only in the video-only output appears in any audiovisual output.

**What each outcome means:**
- **Outputs vary with the audio and match the audio-only results:** the split path is usable for binding.
- **Outputs stay invariant across audio swaps, or copy video-only claims:** visual dominance. Never let the omni call create events; use video only for source binding of already-detected audio events.

### E3 — Separate parts vs embedded soundtrack timing (2 calls)

Use the E1e phrase. Condition A sends it as a separate `audio_url` plus the silent video. Condition B embeds it in an MP4 with the same picture (AAC at 256 kbps, decoded back locally and checked against the WAV to within a stated tolerance), with `mm_processor_kwargs.use_audio_in_video: true`.\[10\] Prompt: word-level start times.

**Pass criterion:** both onsets within ±0.5 s of 7.0 s.

**What each outcome means:**
- **A drifts and B does not:** separate parts are not temporally aligned. Use audio-only discovery plus embedded-video binding.
- **Both pass:** the binding route is not your bottleneck.

### E4 — Only if E1 passes: 120-second chunked pilot (about 6 calls)

- **Input:** BBB 0–120 s audio-only, in 30-second windows (matching the model's internal 30-second clip segmentation) with 10-second overlap so boundary events are seen whole at least once.\[3\] This is a proposal, not an evidence-backed optimum; TAC used 20-second non-overlapping chunks.\[32\]
- **Prompt:** P-open, with a text-only extraction step afterwards.
- **Scoring:** blinded, after generation, against the licensed reference.

**Pass criterion:** decide in advance, e.g., event precision ≥ 0.7 at a ±1.0-second collar, with zero events inside locally verified digital-silence spans.

**Total budget:** about 20 scored calls plus at most 2 retries each, 1024 output tokens per call, thinking off.

**Stopping rule:** stop the whole programme after E1 if E1a, E1b and E1d all fail with HTTP 200/stop. That outcome is enough to pause full-film generation.

## Smallest credible NIM-only pipeline

```
[Local, deterministic]          [NIM: Omni, audio-only]       [NIM: Omni, video]          [NIM: text-only]           [Local]
FFmpeg decode → PCM stats  →  30 s windows, 10 s overlap  →  bind detected events  →  render Essential/      →  validator:
digital-zero spans marked      P-open description           to visible sources         Balanced/Detailed         IDs, attributes,
(absence = signal fact)        → separate text-only          (may ADD nothing;          from ledger IDs only      timing, reading
                               ledger extraction             may mark on/off-screen)                               load → human review
```

- **Stage 0 (available, validated locally):**
  - Decode and hash the media, compute RMS per 100 ms, and mark exact-zero spans.
  - Only true digital zero counts as proof of absence. Low energy is not, and energy says nothing about source identity.
- **Stage 1 (available, unvalidated): audio-only discovery on Omni.**
  - Global time = window start + local time.
  - Deduplicate across overlaps by label similarity plus temporal IoU (intersection over union) ≥ 0.5.
  - Mark any event touching a window edge as `boundary_uncertain`.
  - Drop or flag any event inside a digital-zero span.
- **Stage 2 (available, partly validated):** Omni ASR for speech, with word timestamps.\[5\] Label speech as intelligible, unintelligible or nonverbal vocalisation.
- **Stage 3 (available, unvalidated): source binding.**
  - Send the silent video chunk with the candidate events.
  - Allowed outputs per event: `source_visible`, `source_not_visible`, `undetermined`.
  - The model may not add events.
  - Optional plot context may enter only here or later, and only to word captions, never to establish occurrence.
- **Stage 4 (available, unvalidated): caption rendering.**
  - A text-only NIM model receives the ledger only: event ID, global start and end, description, `evidence_modality`, `uncertainty`, `supported_attributes`.
  - Every caption must cite event IDs.
  - The same speech text must appear at every level.
  - Detailed may add only attributes in `supported_attributes` or extra ledger events of lower importance. It may not add new adjectives about pitch, loudness, emotion, instrument or location.
- **Stage 5 (local, available):** a deterministic validator plus human review. A second prompt to the same model is not independent verification, because it shares the same blind spots (e.g., visual priors, silence handling).
- **Unavailable under constraints:** calibrated frame-level sound localisation (FLAM-like), a trained timestamped captioner (TAC/SpotSound-like), and logit-level decoding (RED).

**Phase 1 demonstration vs validated system:** Phase 1 can honestly show the pipeline running on BBB. The player should label the output "experimental, unreviewed machine-generated sound captions" and show uncertainty and abstentions. A scientifically validated system additionally needs passing presence/absence controls, scored precision and recall against the licensed reference, independent human annotation, and DHH participant evaluation.

## Verification criteria

| Layer | Criteria |
|---|---|
| Transport/media integrity | Request and media hashes; decoded PCM matches source sample for sample; duration ≤ model limits; speech positive control in every batch; `finish_reason: "stop"` |
| Schema/completion | Raw text kept separately from parsed ledger; schema validity scored separately from semantics; timestamps finite, ordered, within [0, clip duration] |
| Sound presence/absence | False-positive rate on digital-zero and noise-floor fixtures; event precision/recall on fixtures with sample-level truth; no events inside digital-zero spans |
| Semantic attributes | Category match by blinded human judgement (an LLM judge only as secondary); each attribute traceable to `supported_attributes`; unsupported-attribute count per caption |
| Temporal alignment | Event-based F1 at ±1.0 s onset collar and segment F1 at 100 ms, following TAC's protocol; report collars explicitly; abstention rate for `null` times |
| Cross-level consistency | Essential ⊆ Balanced ⊆ Detailed by event ID; identical speech text across levels; zero events or attributes absent from the ledger |
| DHH usefulness | DHH participants rate importance, comprehension and distraction; measure reading load (characters/sec, overlap with dialogue) without one universal threshold; informed consent and disclosure that captions are unreviewed machine output |

WER is relevant only to the speech control, not to this largely nonverbal film.

## Caveats

- Third-party sources here (Substack posts, the free-tier limits on rate-limit blogs, GitHub PRs in non-NVIDIA stacks) are anecdotes or analogues, not validated measurements of your endpoint.
- The 12.5 tokens/s and 30-second segmentation figures describe the released model, not a verified hosted configuration.\[3\]
- ESC-50 audio may be in training data, so a pass on it is weaker evidence than a pass on fresh audio.
- Published benchmark scores (MMAU, SpotSound, TAC) are not your endpoint's measured performance.
- I could not open the hosted "infer" API page directly.

## Recommendation

Run E1 next. It is the cheapest test that separates the leading hypotheses: zero-signal out-of-distribution, sparsity, and general non-speech weakness. It also adds a speech-timing control you haven't had.

Regardless of the outcome, stop sending digitally silent spans to the model. Absence should come from the PCM samples, not from inference.

Pause full-film generation if E1 yields, with HTTP 200 and `finish_reason: "stop"`:
- invented sounds on both the zero and the noise-floor fixtures, and
- a miss on the dense, repeated bark.

That result would mean the precise missing capability is calibrated non-speech event detection with abstention on the hosted endpoint, and no verified NIM-hosted model currently supplies it.

If E1 passes but E2 shows invariance to audio swaps, keep the pipeline audio-first and restrict video strictly to binding sources for events the audio stage already found.

## Sources

1. [Nemotron 3 Nano Omni: Efficient and Open Multimodal Intelligence](https://arxiv.org/html/2604.24954v1)
2. [Nemotron 3 Omni Explained: Architecture, Training, and How to Run It](https://kaitchup.substack.com/p/nemotron-3-omni-explained-architecture)
3. [2026-4-27 Nemotron 3 Nano Omni: Efficient and Open Multimodal Intelligence](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Omni-report.pdf)
4. [nemotron-3-nano-omni-30b-a3b-reasoning Model by NVIDIA | NVIDIA NIM](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard)
5. [nvidia / nemotron-3-nano-omni-30b-a3b-reasoning](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning)
6. [feat(multimodal): Nemotron-H Omni image, audio and video by nperrin-fr · Pull Request #3323 · smg-project/smg · GitHub](https://github.com/smg-project/smg/pull/3323)
7. [feat(models): Nemotron-H Omni with C-RADIO vision and Parakeet audio by nperrin-fr · Pull Request #2228 · lightseekorg/tokenspeed · GitHub](https://github.com/lightseekorg/tokenspeed/pull/2228)
8. [Fine-tuning NVIDIA Nemotron Speech ASR on Amazon EC2 for domain adaptation](https://aws.amazon.com/blogs/machine-learning/fine-tuning-nvidia-nemotron-speech-asr-on-amazon-ec2-for-domain-adaptation/)
9. [update · nvidia/parakeet-tdt-0.6b-v2 at 1e45d87](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2/commit/1e45d87c732f0d77f734cfcb2e3677a71244de53)
10. [Query the NVIDIA Nemotron 3 Nano Omni API — NVIDIA NIM for Vision Language Models (VLMs)](https://docs.nvidia.com/nim/vision-language-models/1.7.0/examples/nemotron-3-nano-omni-30b-a3b-reasoning/api.html)
11. [Request response from the model](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-5-content-safety-infer)
12. [NVIDIA Nemotron 3 Nano Omni](https://cobusgreyling.substack.com/p/nvidia-nemotron-3-nano-omni)
13. [NVIDIA Nemotron 3 Nano Omni. One model to see, hear & reason](https://cobusgreyling.medium.com/nvidia-nemotron-3-nano-omni-fdecc9a4a125)
14. [Release Notes — NVIDIA NIM for Vision Language Models (VLMs)](https://docs.nvidia.com/nim/vision-language-models/_1.7.0/1.7.0/release-notes.html)
15. [Release Notes — NVIDIA NIM for Vision Language Models (VLMs)](https://docs.nvidia.com/nim/vision-language-models/2.0.4-variant/release-notes.html)
16. [Release Notes — NVIDIA NIM for Large Language Models](https://docs.nvidia.com/nim/large-language-models/2.0.10/about-nim-llm/release-notes.html)
17. [nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 · Hugging Face](https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16)
18. [\[Bug\]: Repeated audio requests fail across stage-0 replicas with multimodal caching · Issue #7295 · vllm-project/vllm-omni · GitHub](https://github.com/vllm-project/vllm-omni/issues/7295)
19. [fix(mllm): Omni audio extraction froze the server and never reached the prompt by sbayer2 · Pull Request #807 · waybarrios/vllm-mlx · GitHub](https://github.com/waybarrios/vllm-mlx/pull/807)
20. [Do Audio-Visual Large Language Models Really See and Hear?](https://openaccess.thecvf.com/content/CVPR2026F/papers/Selvakumar_Do_Audio-Visual_Large_Language_Models_Really_See_and_Hear_CVPRF_2026_paper.pdf)
21. [Do Audio-Visual Large Language Models Really See and Hear?](https://ramaneswaran.github.io/avllm_interpretability/)
22. [\[2604.14129\] Don't Let the Video Speak: Audio-Contrastive Preference Optimization for Audio-Visual Language Models](https://arxiv.org/abs/2604.14129)
23. [ACPO](https://vision.cs.utexas.edu/projects/acpo/)
24. [SpotSound: Enhancing Large Audio-Language Models with Fine-Grained Temporal Grounding](https://arxiv.org/pdf/2604.13023)
25. [SpotSound: Enhancing Large Audio-Language Models with Fine-Grained Temporal Grounding](https://arxiv.org/html/2604.13023)
26. [Paper page - SpotSound: Enhancing Large Audio-Language Models with Fine-Grained Temporal Grounding](https://huggingface.co/papers/2604.13023)
27. [SpotSound: Verbesserung großer Audio-Sprachmodelle durch feingranulare zeitliche Verankerung](https://www.alphaxiv.org/de/abs/2604.13023)
28. [MISHAP-Bench: A Hallucination Benchmark for Large Audio-Language Models](https://arxiv.org/html/2609.33893v1)
29. [A Comprehensive Benchmark for Hallucination Detection ...](https://aclanthology.org/2026.acl-long.1797.pdf)
30. [HalluAudio: A Comprehensive Benchmark for Hallucination Detection in Large Audio-Language Models - ACL Anthology](https://aclanthology.org/2026.acl-long.1797/)
31. [Loie/SpotSound-Bench · Datasets at Hugging Face](https://huggingface.co/datasets/Loie/SpotSound-Bench)
32. <https://arxiv.org/html/2602.15766v2>
33. [Relevant Evidence Decoding for Audio-Visual Hallucination Mitigation](https://arxiv.org/html/2610.02976)
34. [\[2610.02976\] Relevant Evidence Decoding for Audio-Visual Hallucination Mitigation](https://arxiv.org/abs/2610.02976)
35. [GitHub - adobe-research/openflam: OpenFLAM: Framewise Language Audio Model · GitHub](https://github.com/adobe-research/openflam)
36. [Adobe Research · GitHub](https://github.com/adobe-research)
37. [AVSCap: Orchestrating Audio-Visual Synergy for Omni-modal Video Captioning - ACL Anthology](https://aclanthology.org/2026.emnlp-main.1433/)
38. [AVSCap: Orchestrating Audio-Visual Synergy for Omni-modal Video Captioning](https://arxiv.org/html/2607.12820v1)
39. [OnomaCap: Making Non-speech Sound Captions Accessible and Enjoyable through Onomatopoeic Sound Representation](https://dl.acm.org/doi/full/10.1145/3706598.3713911)
40. [Beyond Subtitles: Captioning and Visualizing Non-speech Sounds to Improve Accessibility of User-Generated Videos](https://dl.acm.org/doi/10.1145/3517428.3544808)
41. [Limitations of Standard Accessible Captioning of Sounds and Music for Deaf and Hard of Hearing People: An EEG Study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7040021/)
42. [nemotron-3-nano-omni-30b-a3b-reasoning Model by NVIDIA](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning)
