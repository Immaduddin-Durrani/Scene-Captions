# SceneCaptions: Independent DHH Sound Captioning Using NVIDIA NIM

**Research date:** 27 October 2026  
**Evidence cutoff:** 26 October 2026  
**Scope:** Research and proposed experiments only. No inference requests, installations, downloads or deployments were performed.

## Executive summary

**The most useful finding is that SceneCaptions should investigate short-event recognition separately from timestamp generation and audiovisual reasoning.**

Your experiments establish that the hosted Nemotron model can recognize at least some speech and broadly identify some water sounds. They do not establish reliable environmental sound recognition, silence detection or temporal grounding.

Three findings matter particularly:

1. **Your dog fixture is unusually sparse.** The actual nonzero signal lasts approximately 0.357 seconds inside a ten-second recording. Research on temporal grounding identifies precisely this kind of short event as challenging.
2. **Visual contamination is a credible explanation for some errors.** Published audiovisual research demonstrates that models sometimes generate sounds suggested by images rather than sounds supported by audio.
3. **Your next experiment should simplify the task before changing the model.** First establish whether Nemotron recognizes a short sound when the sound is isolated. Only then investigate timing, silence and video effects.

However, the literature does not establish that the hosted Nemotron endpoint can produce reliable independent DHH captions.

**Current recommendation:** Keep full-film generation disabled. Run a small, audio-only recognition experiment using the existing dog fixture, followed by a controlled temporal-shift test if recognition succeeds.

The research below distinguishes documented capabilities, published experimental results and hypotheses about your particular endpoint.

---

# 1. Ranked research findings

## Finding 1 — Sparse sound events may explain part of the dog failure

**Priority: Critical**

**Primary source:** [SpotSound: Enhancing Large Audio-Language Models with Fine-Grained Temporal Grounding](https://arxiv.org/abs/2604.13023)

**Publication history:**
- Initial submission: 14 April 2026.
- Revised version: 10 August 2026.
- Code, models and benchmark are reported as released.

### Established research

SpotSound investigates temporal grounding for audio events that occupy a small fraction of a recording.

Its benchmark deliberately includes short events occupying less than approximately 10% of a clip.

The authors identify two important problems:

- Audio-language models are often trained using clip-level descriptions rather than precise event boundaries.
- Short events embedded within longer recordings are difficult to locate, particularly when background sounds are present.

SpotSound introduces training designed to reduce hallucinated timestamps for events that are absent.

These are reported findings for SpotSound, not measurements of Nemotron.

### Relevance to SceneCaptions

Your dog fixture contains approximately:

\[
6.586625-6.2291875=0.3574375\text{ seconds}
\]

of nonzero samples in the shifted case.

The fraction of the ten-second recording containing nonzero samples is:

\[
\frac{0.3574375}{10}\times100\approx3.57\%
\]

This is considerably below the 10% sparsity threshold discussed in SpotSound.

That makes the fixture useful for testing sparse-event recognition, but potentially unsuitable as the first positive control for general environmental sound recognition.

A failure to recognize this dog event does not establish that Nemotron cannot recognize a longer or isolated bark.

### Recommended change

Compare the exact same dog signal in two conditions:

**Condition A:** Original ten-second recording.

**Condition B:** A shorter recording containing the same nonzero signal, with limited surrounding silence.

Preserve the sample values and avoid loudness normalization.

This isolates the effect of temporal context and event sparsity more cleanly than replacing the sound with a different recording.

A third condition could repeat the burst, but repetition changes event frequency and acoustic structure. It should be treated as a separate experiment.

### Limitation

SpotSound's improvements depend on its own model and training method.

There is no verified hosted NVIDIA NIM free/trial endpoint for SpotSound in the evidence reviewed.

**Status: Research-only method; directly useful experimental design.**

---

## Finding 2 — Audiovisual inference can make audio recognition worse

**Priority: Critical**

**Primary source:** [Don't Let the Video Speak: Audio-Contrastive Preference Optimization](https://vision.cs.utexas.edu/projects/acpo/)

**Publication:** ECCV 2026.

### Established research

The ACPO authors investigate audiovisual language models that rely excessively on visual information when answering questions about sound.

They describe a phenomenon called *video-driven audio hallucination*.

A model may infer that an event is audible because the corresponding action is visible.

For example, seeing an object fall does not establish that an impact sound exists in the soundtrack.

The researchers construct counterfactual inputs by changing the audio while retaining the video.

Their proposed training method, Audio-Contrastive Preference Optimization, attempts to penalize responses that remain unchanged despite relevant audio changes.

### Relevance to your observations

Your silent audiovisual fixture produced a sustained electronic-tone description despite having zero-valued PCM.

Other audiovisual requests produced wind, leaves and electronic sounds when the dog fixture was present.

These observations are compatible with several explanations:

1. Visual information influenced the audio description.
2. The model hallucinated a plausible sound without relying on the video.
3. The separate audio/video serving path mishandled or underweighted the audio.
4. The model failed to recognize the brief acoustic event.

The current evidence cannot distinguish these explanations.

### Recommended change

Use a controlled audiovisual matrix:

| Audio | Video | Expected behavior |
|---|---|---|
| Digital silence | None | No audible events |
| Digital silence | BBB silent video | No audible events |
| Recognizable dog sound | None | Dog sound recognized |
| Same dog sound | Same BBB video | Dog sound still recognized |

Keep the acoustic waveform identical within the relevant comparison.

If the model correctly recognizes the dog without video but changes its answer when silent video is added, that would support an audiovisual interference hypothesis.

It would not, by itself, prove the specific mechanism identified by ACPO.

### Limitation

ACPO is a preference-training method.

It is not a parameter that can be enabled in NVIDIA's hosted chat API.

Its published improvements cannot be transferred directly to the hosted Nemotron model without evidence.

**Status: Research-only mitigation; usable-now counterfactual testing.**

---

## Finding 3 — NVIDIA's documentation reveals an additional serving-response condition

**Priority: High**

**Primary sources:**

- [NVIDIA hosted Nemotron API reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer)
- [NVIDIA Nemotron Omni media guide](https://docs.nvidia.com/nim/vision-language-models/1.7.0/examples/nemotron-3-nano-omni-30b-a3b-reasoning/api.html)

### Established documentation

The hosted API reference explicitly documents:

- `audio_url` and `input_audio` media types, subject to model-schema support.
- `video_url` inputs.
- `reasoning_budget`.
- HTTP 200 for fulfilled requests.
- HTTP 202 for pending requests.
- HTTP 422 for validation failures.
- HTTP 500 for execution failures.

The documented `reasoning_budget` range is −1 through 32768.

However, your earlier Ultra request produced a specific runner error when using a reasoning-budget control.

That demonstrates an important distinction:

**A parameter appearing in API documentation does not guarantee that every hosted model runner accepts it.**

The documentation also identifies HTTP 202 as a pending invocation requiring polling through a request identifier.

Your harness should therefore distinguish:

| Response | Interpretation |
|---|---|
| HTTP 200, completed | Candidate for semantic evaluation |
| HTTP 200, incomplete | Not an accepted structured result |
| HTTP 202 | Pending; follow documented polling behavior |
| HTTP 422 | Request validation failure |
| HTTP 503 | Capacity or availability failure |
| Timeout | Inconclusive |
| HTTP 500 | Serving failure |

HTTP 202 handling is an additional contract case worth auditing if the current harness assumes every successful invocation returns a final HTTP 200 response.

### Important distinction: container versus hosted service

[NVIDIA NIM LLM 2.0.10 release notes](https://docs.nvidia.com/nim/large-language-models/2.0.10/about-nim-llm/release-notes.html) document restoration of audio support for omni-class models using `vllm[audio]` and a PyAV/FFmpeg configuration.

That is evidence about the container software release.

It does not establish which version NVIDIA's hosted endpoint currently uses.

The separate Omni media guide also includes container-launch instructions requiring NVIDIA GPU infrastructure.

Those instructions are not appropriate for your 16 GB Apple Silicon development machine.

### What remains uncertain

The reviewed hosted API reference does not establish:

- Which audio encoder checkpoint serves your account.
- The precise resampling pipeline.
- Whether separate audio/video content is synchronized internally as expected.
- Whether all documented parameters work with the current runner.
- The hosted model's effective temporal resolution for non-speech events.
- Account-specific quota or future availability.

The successful speech test rules out complete audio transport failure for that request.

It does **not** rule out selective degradation of environmental sounds.

**Status: Hosted API usable for controlled testing; sound-captioning capability unvalidated.**

---

## Finding 4 — Timestamped captioning requires capabilities beyond ordinary audio description

**Priority: High**

**Primary source:** [TAC: Timestamped Audio Captioning, version 2](https://arxiv.org/html/2602.15766v2)

**Revision date:** 6 October 2026.

### Reported research

TAC is particularly relevant because its task closely resembles SceneCaptions.

It targets:

- Multiple overlapping sound events.
- Event-specific timestamps.
- Different description detail levels.
- Sound-event separation.
- Audiovisual descriptions.

The researchers train a specialized model using dynamic acoustic mixtures and temporally structured supervision.

They also propose a cascade in which an audio captioning model produces evidence for a subsequent language model.

This separation matters.

A general-purpose reasoner can describe, organize and summarize events, but those capabilities do not establish that it can discover acoustically grounded events.

### Relevance to SceneCaptions

The strongest architectural lesson is:

**Separate acoustic event discovery from caption writing.**

A model should first establish what happened.

Only afterward should another stage decide how to express the information.

For example:

```text
Audio
  ↓
Acoustic event discovery
  ↓
Event identities and evidence
  ↓
Temporal refinement
  ↓
Optional visual source association
  ↓
DHH caption generation
```

Your existing approach combines event discovery, timing and structured output in one request.

That makes failures difficult to interpret.

### Chunking implications

TAC-V's use of 20-second audio segments is a useful architectural precedent.

It does not prove that 20 seconds is optimal for Nemotron or Big Buck Bunny.

Chunk duration should be selected after evaluating:

- Recognition of short events.
- Recognition of sustained ambience.
- Event continuation across boundaries.
- Latency.
- Capacity failures.
- Timestamp reliability.

For your 596.461678-second film, 20-second non-overlapping segments would require approximately 30 segments.

Adding overlap increases requests and requires event reconciliation.

There is no reason to incur that expense until the audio-capability gate passes.

### Limitation

TAC relies on specialized training.

Its research demonstration does not establish a usable hosted NVIDIA endpoint.

Copying TAC's prompt format would not reproduce its learned temporal-grounding capability.

**Status: Research-only model; strong architectural reference.**

---

## Finding 5 — A training-free decoding improvement is not necessarily available through chat completions

**Priority: High**

**Primary source:** [Relevant Evidence Decoding for Audio-Visual Hallucination Mitigation](https://arxiv.org/abs/2610.02976)

**Submission:** 2 October 2026.

### Reported research

Relevant Evidence Decoding, or RED, addresses cases in which combining audio and video weakens a correct prediction.

The paper describes an example where a model correctly identifies an instrument from audio but becomes less confident after conflicting visual information is added.

RED estimates how much predictive evidence comes from:

- Audio.
- Video.
- Their interaction.

The authors report improvements on several audiovisual hallucination benchmarks.

### Relevance

This supports the possibility that your audio-only and audiovisual conditions can behave differently even when the waveform is unchanged.

It also supports evaluating audio independently before adding visual context.

### Critical limitation

RED operates at the decoding level.

Its method depends on information beyond an ordinary final text response, including model prediction distributions.

Your hosted chat-completions access has not been shown to expose the required decoding controls.

Sending separate prompts and comparing their final answers is not equivalent to implementing RED.

Therefore, RED should not be presented as a working NVIDIA-hosted solution.

**Status: Research-only; not established as implementable through the current hosted route.**

---

## Finding 6 — Hallucination evaluation must test absent sounds, not just correct descriptions

**Priority: High**

**Primary source:** [HalluAudio: A Comprehensive Benchmark for Hallucination Detection in Large Audio-Language Models](https://arxiv.org/abs/2604.19300)

**Submission:** 21 April 2026.  
**Publication status:** Reported as accepted to ACL 2026.

### Reported research

HalluAudio evaluates hallucinations involving speech, environmental sounds and music.

Its evaluation includes:

- Binary judgments.
- Multiple-choice questions.
- Attribute verification.
- Open-ended responses.
- Hallucination rates.
- Refusal rates.
- Yes/no response bias.

The benchmark contains more than 5,000 human-verified question-answer pairs.

### Relevance

Your silent fixture is especially important.

A model that recognizes some real sounds but invents sounds during silence is unsuitable for unreviewed accessibility captions.

A fluent caption is not necessarily an accurate caption.

Consider two hypothetical outputs:

**Output A:** Correctly identifies three events but invents two additional sounds.

**Output B:** Correctly identifies two events, misses one and invents nothing.

For an accessibility application, deciding which is preferable requires explicit evaluation of omission and false-positive costs.

That decision should not be hidden inside a text-similarity score.

### Recommended metrics

Use:

\[
Precision=\frac{TP}{TP+FP}
\]

\[
Recall=\frac{TP}{TP+FN}
\]

Also record:

- False event detections during digital silence.
- Unsupported sound-source claims.
- Unsupported acoustic attributes.
- Missed events.
- Incorrectly timed events.
- Abstentions.
- Incomplete or invalid responses.

Report these separately.

Do not combine transport failures and semantic errors into one accuracy number.

### Limitation

HalluAudio is an evaluation resource, not a demonstrated correction for Nemotron.

Its published benchmark scores are not SceneCaptions measurements.

**Status: Evaluation methodology usable now; benchmark-specific model results not transferable.**

---

## Finding 7 — DHH caption detail is a user preference, not simply a word-count setting

**Priority: High**

**Primary source:** [CapTune: Adapting Non-Speech Captions With Anchored Generative Models](https://arxiv.org/abs/2508.19971)

**Publication:** ASSETS 2025.

### Reported research

CapTune studies personalization of non-speech captions.

The system supports customization along four dimensions:

1. Detail.
2. Expressiveness.
3. Sound representation.
4. Genre alignment.

Its evaluation included seven caption creators and twelve DHH participants.

The authors report trade-offs between information richness, cognitive load and different ways of representing sound.

### Relevance

Your three caption levels should not simply be:

**Essential:** `[BARKING]`

**Balanced:** `[LOUD BARKING]`

**Detailed:** `[VERY LOUD, SUDDEN BARKING]`

These variants mainly add unsupported or redundant modifiers.

Instead, detail should expose additional verified information.

For example, suppose the ledger independently establishes:

- A dog bark.
- Two separate bark events.
- Background rain.
- Overlap between the second bark and rain.

Then the levels could be:

| Level | Caption |
|---|---|
| Essential | [Dog barks] |
| Balanced | [Dog barks twice] |
| Detailed | [Dog barks twice as rain continues] |

This example is hypothetical. It is not a claim about your dog fixture.

The important rule is that each additional fact must already exist in the grounded event ledger.

### Recommended design

Treat detail levels as controlled projections of the same verified information.

Do not allow each level to independently discover events.

Also preserve consistent speech content across levels.

For dialogue, distinguish:

- Intelligible speech.
- Unintelligible speech.
- Nonverbal vocalizations.

Do not convert an animal sound, grunt or gasp into invented dialogue.

### Limitation

CapTune primarily addresses transformation and personalization of caption content.

It does not solve independent acoustic event discovery.

Its participant results also do not establish a universal reading-speed limit or a universally preferred caption style.

**Status: Usable design guidance; acoustic discovery remains unresolved.**

---

# 2. Diagnosis: What is probably failing?

The available evidence does not support a single definitive explanation.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Best distinguishing test |
|---|---|---|---|---|
| Audio never reaches the model | Some outputs unrelated to sound | Novel speech transcribed correctly | Non-speech processing verification | Isolated natural sound versus silence |
| Speech processing works but environmental sound understanding is weak | Correct speech; poor dog recognition | Broad water recognition | Reliable non-speech positive controls | Dense environmental sound with simple prompt |
| Sparse events are missed | Dog occupies only 3.57% of clip | No completed matched cropped-dog test | Isolated-burst result | Same burst, shorter duration |
| Audio preprocessing corrupts certain sounds | Unexpected descriptions | WAV integrity checked locally; speech works | Server-side decoded waveform | Compare identical samples under controlled duration changes |
| Separate audiovisual binding is faulty | Audiovisual hallucinations | Embedded-video speech worked | Matched successful audio-only and audiovisual non-speech tests | Same sound with/without silent video |
| Visual context overrides acoustic evidence | Silence-plus-video hallucination | Audio-only hallucinations also occurred | Matched audiovisual counterfactuals | Silence/no-video versus silence/video |
| Output-format requirements interfere with recognition | Malformed JSON and invented times | No successful matched simple-prompt comparison | Completed format ablation | Same audio, simple versus structured request |
| Temporal grounding is weak | Events placed in silence or beyond duration | No scored dog-shift pair | Recognized event with known onset | Three-second shifted event pair |
| Model has a general silence hallucination problem | Repeated false positives on digital silence | Too few independent completed controls | Repeated zero-input results | Audio-only silence controls |
| Hosted capacity limits distort comparisons | Five 503s and one timeout in latest batch | Some requests completed | Matched successful responses | Bounded reruns of only inconclusive cells |

### Most important diagnostic distinction

The experiment currently mixes three questions:

1. **Recognition:** Does the model identify the sound?
2. **Localization:** Does it identify when the sound occurs?
3. **Instruction following:** Does it return the requested structure?

These should be tested separately.

A model might recognize barking but fail to locate it.

It might locate a sound approximately but describe the source incorrectly.

It might identify and locate an event but return malformed JSON.

Each outcome suggests a different engineering response.

---

# 3. Proposed bounded experiments

All experiments below are proposals.

They use the existing hosted model and local fixtures. They require no new model downloads or provider changes.

## Common request contract

Endpoint:

```text
POST https://integrate.api.nvidia.com/v1/chat/completions
```

Model:

```text
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
```

For recognition tests, use a single user message containing the WAV and the question.

Illustrative request:

```json
{
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "audio_url",
          "audio_url": {
            "url": "data:audio/wav;base64,<WAV_BASE64>"
          }
        },
        {
          "type": "text",
          "text": "Describe the audible sounds in this recording. If no sound is audible, say so. Do not infer sounds from context."
        }
      ]
    }
  ],
  "max_tokens": 256,
  "temperature": 0.2,
  "top_k": 1,
  "stream": false,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
```

This is a proposed request shape, not a newly validated request.

The media representation follows the previously tested `audio_url` pattern.

Keep the same request structure for all recognition comparisons.

Do not add a reasoning-budget parameter until its runner compatibility is independently established.

For these tests, define:

- Maximum 180 seconds per attempt.
- No more than one retry per capacity failure.
- At least the previously used 2.05-second separation between starts.
- Maximum 256 output tokens for simple descriptions.
- Maximum 512 output tokens for timing tests.
- No hidden retries.
- No automatic substitution of another model.

A 503 or timeout is inconclusive, not a recognition failure.

Record all attempts.

---

## Experiment 1 — Can Nemotron recognize the isolated dog event?

**Priority: First**

### Purpose

Separate weak environmental sound recognition from the effects of event sparsity.

### Fixtures

| Fixture | Description | Ground truth |
|---|---|---|
| A | Original c01, ten seconds | Dog source, nonzero support 3.229–3.587 s |
| B | Cropped c01 containing the exact burst and short surrounding silence | Same dog source |
| C | Digital silence matching B's duration | No sound |

The crop should preserve the original PCM sample values.

Do not normalize loudness.

Do not tell the model that the source is a dog.

### Request budget

Three initial calls, with at most one retry per inconclusive call.

**Maximum: six calls.**

### Acceptance

**Recognition pass:** The model identifies a dog bark or clearly equivalent canine vocalization in both A and B, while correctly reporting silence for C.

**Partial result:** It recognizes B but not A.

**Failure:** It completes both sound requests but cannot identify the dog, or invents a sound for C.

### Interpretation

| Outcome | Implication |
|---|---|
| A and B correct | Basic dog recognition demonstrated; investigate timing |
| B correct, A wrong | Temporal sparsity/context is implicated |
| Both wrong | Basic recognition remains unsupported |
| Silence hallucinated | Sound-presence gate remains unreliable |
| Capacity failures | Experiment inconclusive |

### Stopping rule

If the cropped dog is not recognized in completed responses, do not proceed directly to timestamp testing.

Instead, test a longer, independently verified natural sound.

---

## Experiment 2 — Can Nemotron distinguish sound presence from silence?

**Priority: Second**

### Purpose

Determine whether the model can distinguish a sustained environmental sound from digital silence.

### Fixtures

Use:

- Existing rain fixture c03.
- Ten seconds of digital silence.
- A shorter rain-only segment preserving original PCM values.

The full rain fixture and silence should have equal duration.

The cropped rain condition is a separate duration comparison.

### Request

Use the same simple recognition request from Experiment 1.

Do not request timestamps.

### Budget

Three initial calls, with at most one retry per inconclusive call.

**Maximum: six calls.**

### Acceptance

The model should:

- Identify the rain fixture as rain or precipitation-like sound.
- Avoid asserting unsupported water-source details.
- Identify digital silence as silence.
- Avoid inventing events in silent intervals.

The exact dataset label remains hidden from the request.

### Interpretation

Correct recognition of sustained rain but failure on the sparse dog would suggest that event density or acoustic category matters.

Failure on both would raise concern about environmental sound understanding or the hosted audio path.

A correct rain description does not establish temporal accuracy.

### Stopping rule

If completed silence controls continue producing invented sounds, keep automatic caption publication disabled.

---

## Experiment 3 — Can the model follow a known three-second onset shift?

**Priority: Third, conditional**

Run only if Experiment 1 establishes reliable recognition of the dog sound.

### Fixtures

Use the existing c01 and c02 recordings.

Their source samples are identical.

Their nonzero regions differ by exactly three seconds.

### Request

```json
{
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "audio_url",
          "audio_url": {
            "url": "data:audio/wav;base64,<WAV_BASE64>"
          }
        },
        {
          "type": "text",
          "text": "Identify the audible sound and estimate when it begins and ends in seconds relative to this recording. If you cannot determine the timing, state that explicitly."
        }
      ]
    }
  ],
  "max_tokens": 512,
  "temperature": 0.2,
  "top_k": 1,
  "stream": false,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
```

### Budget

Two initial calls, with one retry per inconclusive result.

**Maximum: four calls.**

### Evaluation

Measure the difference between predicted onset times:

\[
\Delta t=t_{\text{onset,c02}}-t_{\text{onset,c01}}
\]

Expected shift:

\[
\Delta t=3.0\text{ seconds}
\]

For this screening experiment, propose a tolerance of ±0.5 seconds.

That is an experimental acceptance threshold, not a published Nemotron accuracy guarantee.

Also compare the predicted intervals with independently established acoustic event boundaries.

The nonzero sample boundaries are useful objective controls, but they are not automatically equivalent to perceptual barking boundaries.

### Interpretation

If the model identifies the dog correctly but fails the onset-shift comparison, recognition and temporal grounding must remain separate pipeline stages.

If it passes, the result demonstrates only one controlled timing capability.

It does not establish reliable timing for music, ambience, overlaps or real film sound effects.

### Stopping rule

Do not expand to full-film timestamp generation based on one passing pair.

---

## Experiment 4 — Does silent video interfere with acoustic evidence?

**Priority: Fourth, conditional**

Run only after a recognizable environmental sound has been established.

### Fixtures

Use:

1. Recognized sound, audio only.
2. Identical sound plus silent BBB video.
3. Digital silence, audio only.
4. Identical digital silence plus the same silent BBB video.

### Request

Use the same recognition prompt as Experiment 1.

For audiovisual conditions, insert the silent MP4 as a separate `video_url` content part between audio and text, preserving the previously tested content order.

### Budget

Four initial calls, with one retry per inconclusive result.

**Maximum: eight calls.**

### Acceptance

The recognized sound should remain consistent when video is introduced.

Silence should remain silence.

No visible action should be converted into an audible event without acoustic support.

### Interpretation

If audio-only recognition succeeds but audiovisual recognition fails, retain an audio-first architecture and avoid joint inference for initial sound discovery.

If both fail, audiovisual interference is not the primary demonstrated problem.

If both succeed, audiovisual inference becomes worth investigating for source association.

### Stopping rule

Any repeated completed response inventing sounds during digital silence prevents automatic acceptance of audiovisual captions.

---

# 4. Smallest credible NIM-only pipeline

The following architecture respects the constraint that model inference must use NVIDIA's hosted free/trial endpoints.

It does not assume another provider, a local GPU or additional installed audio models.

## Stage 1 — Media preparation

**Available locally.**

Use FFmpeg to:

- Extract the original soundtrack.
- Produce mono 16-kHz PCM16 WAV segments.
- Record sample counts and durations.
- Check decoded silence.
- Generate silent video segments when needed.
- Record hashes and clip offsets.

Preserve the original media separately.

Do not introduce reference captions or subtitle timestamps into this stage.

### Important limitation

PCM energy can help identify potentially active regions.

It cannot establish whether an event is barking, music, footsteps or speech.

Silence thresholds also require care because low-energy sounds can remain perceptually important.

---

## Stage 2 — Audio-first event discovery

**Hosted NIM available; accuracy unvalidated.**

Send audio-only segments to the tested Nemotron model.

Initially request simple sound descriptions without timestamps or strict JSON.

Only use a segment for ledger construction when the model has passed the relevant sound-recognition controls.

For a production candidate, use an event representation such as:

```json
{
  "event_id": "evt_001",
  "clip_id": "clip_012",
  "local_start_s": null,
  "local_end_s": null,
  "global_start_s": null,
  "global_end_s": null,
  "sound": "brief animal vocalization",
  "evidence_modality": "audio",
  "source_identity": null,
  "attributes": [],
  "uncertainty": "source identity unresolved",
  "status": "unreviewed"
}
```

The example is illustrative, not an observed BBB event.

### Essential rule

The model must not be required to invent timestamps merely to satisfy the schema.

Null values should remain valid.

---

## Stage 3 — Temporal refinement

**Unvalidated.**

Once a sound has been recognized, estimate its location.

This should be treated as a different task from event discovery.

Use:

\[
t_{\text{global}}=t_{\text{clip origin}}+t_{\text{local}}
\]

Validate that:

\[
0\leq t_{\text{start}}<t_{\text{end}}\leq t_{\text{clip duration}}
\]

When the model cannot establish a boundary, retain unresolved timing.

Do not substitute waveform-energy boundaries for semantic event boundaries without justification.

### Chunking

Start with short, controlled segments because your immediate problem is event recognition.

If the capability gate passes, evaluate a small number of candidate window sizes.

Use overlapping windows only where needed to protect boundary events.

Maintain event identity across adjacent chunks.

For deduplication, compare:

- Temporal overlap.
- Acoustic description.
- Event continuity.
- Whether two events are genuinely simultaneous.

Do not merge overlapping music and sound effects merely because their timestamps overlap.

---

## Stage 4 — Optional visual association

**Unvalidated.**

Only after acoustic event discovery should the pipeline inspect video.

The purpose is to associate an already detected sound with a plausible visible source.

For example:

```text
Audio evidence:
A short impact sound occurred.

Visual evidence:
An object visibly contacted the floor.

Possible association:
The impact may correspond to the visible contact.
```

The visual association must not create the acoustic event.

If the source cannot be established, leave it unspecified.

Off-screen sounds should remain valid events.

Plot summaries, if used, should enter only after acoustic discovery and should never override sound-presence evidence.

---

## Stage 5 — Three caption detail levels

**Application logic available; grounded generation unvalidated.**

Generate all three levels from the same event ledger.

### Essential

Communicate the most important verified sound information.

### Balanced

Include useful supported distinctions, such as repetition, continuity or overlapping sounds.

### Detailed

Include additional verified acoustic properties or relationships.

Do not add unsupported source identities, emotions, instruments or spatial descriptions.

A deterministic consistency checker should ensure:

- Every caption maps to ledger event IDs.
- No caption introduces a new event.
- Detailed captions do not contradict Essential captions.
- Speech transcripts remain identical across levels.
- Captions respect event timing.
- Unresolved events are not presented as certain.

A second request to the same model may help identify inconsistencies, but it is not independent acoustic verification.

---

## Stage 6 — Human review and player integration

**Player available; independent caption track not accepted.**

The existing 87 cues should remain identified as source-assisted drafts.

They should not be relabeled as independent model-generated observations.

For Phase 1, the application can demonstrate:

- Detail-level switching.
- Reference comparison.
- Event provenance.
- Uncertainty handling.
- A small independently generated experimental segment, if it passes acceptance.

A scientifically validated full-film captioning system requires substantially more evidence.

---

# 5. Practical model and tool availability

| Model or tool | Access path | Relevant modality | Resource/release status | NIM-only suitability |
|---|---|---|---|---|
| Nemotron 3 Nano Omni | NVIDIA hosted chat completions | Audio, video, text | Hosted model documented; account-specific availability unverified | **Yes, for testing; accuracy unvalidated** |
| TAC / TAC-V | Research paper and demonstration | Audio and audiovisual | Specialized training; hosted access not established | Research-only |
| SpotSound | Released research code/models/benchmark | Audio | Local model requirements not established here | No verified hosted NIM route |
| ACPO | Research paper and repository link | Audiovisual | Training method | Not a hosted inference switch |
| RED | Research paper | Audiovisual | Requires decoding-level functionality | Not established through hosted chat API |
| OpenFLAM | [Official Adobe repository](https://github.com/adobe-research/openflam) | Audio/text similarity | Research implementation | No verified hosted NIM route |
| HalluAudio | Research benchmark | Audio evaluation | Human-verified evaluation data | Useful methodology; not a hosted inference model |
| CapTune | Research system | Caption personalization | Published DHH evaluation | Useful design guidance; does not solve discovery |

For other previously considered models, the recorded account-specific failures remain relevant.

However, a past 404 or 410 is not proof of permanent global unavailability.

I did not verify a new free hosted NIM model that demonstrably solves dense, timestamped environmental sound captioning.

**The precise missing capability is reliable, independently grounded non-speech event discovery and localization through an accessible hosted NIM endpoint.**

---

# 6. Verification criteria

SceneCaptions should maintain separate acceptance gates.

| Category | Verification criteria | Failure example |
|---|---|---|
| Transport/media integrity | Correct sample rate, channels, sample count, hashes and clip identity | Wrong audio segment submitted |
| Schema/completion | Explicit successful completion, valid structure, finite timestamps | HTTP 200 with malformed event array |
| Sound presence | Correctly detects audible events | Misses a verified bark |
| Sound absence | Does not invent events during verified silence | Reports an electronic tone on zero PCM |
| Semantic attributes | Supported source, event category and acoustic properties | Invents an instrument |
| Temporal alignment | Correct event location, duration and shifted onset | Event extends beyond clip |
| Cross-level consistency | Same grounded events and dialogue across levels | Detailed level invents another sound |
| DHH usefulness | Readability, relevance, comprehension and preference | Captions obscure important visuals |

### Semantic evaluation

Use independently reviewed acoustic annotations for selected test segments.

Report event-level precision, recall and F1.

Where multiple events overlap, evaluate each event separately.

### Timing evaluation

For events with human-reviewed boundaries, report:

- Onset error.
- Offset error.
- Temporal overlap.
- Missed events.
- Unsupported event intervals.

A useful overlap metric is temporal intersection-over-union:

\[
IoU=\frac{|I_{\text{pred}}\cap I_{\text{reference}}|}
{|I_{\text{pred}}\cup I_{\text{reference}}|}
\]

Report timing quality only for appropriately matched events.

### Sound absence

Maintain dedicated silence controls.

Report false-positive event counts and false-positive rates separately from recognition accuracy.

### DHH evaluation

Recruit DHH participants for later usability testing.

Evaluate:

- Whether captions convey useful sound information.
- Whether users can follow events while watching.
- Whether additional detail improves comprehension.
- Whether caption density becomes distracting.
- Whether uncertainty indicators are understandable.
- Whether users prefer different levels in different scenes.

Do not assume that more words always improve accessibility.

For Big Buck Bunny, word error rate should not be the primary evaluation metric because most important events are nonverbal.

---

# 7. What the current evidence does not establish

Several conclusions would be premature.

**First, successful speech recognition does not prove that the model can caption environmental sounds.** The hosted system may handle speech and non-speech differently, or the model may simply be stronger at speech.

**Second, the dog experiment does not establish a timing failure.** Both matched audio-only requests were inconclusive, and no correctly identified timed dog pair was available.

**Third, malformed JSON does not necessarily mean acoustic recognition failed.** Format compliance and semantic correctness are separate properties.

**Fourth, an audio-only architecture does not automatically eliminate hallucinations.** Your earlier tone and silence controls already produced unsupported descriptions without video.

**Fifth, published improvements from TAC, SpotSound, ACPO and RED cannot be assumed to transfer to Nemotron.** They involve different models, training procedures or decoding capabilities.

Finally, there is no verified evidence that your account can continue making unlimited free NIM requests.

The proposed request budgets are experimental ceilings, not promises of available quota.

---

# 8. Final recommendation

## Run the isolated-dog experiment first

Of the proposed tests, **Experiment 1 has the highest immediate diagnostic value**.

It changes the temporal context while preserving the acoustic samples.

It directly addresses a weakness in the existing evidence: the dog sound occupies only 0.357 seconds of a ten-second recording.

The result determines the next step:

| Result | Next action |
|---|---|
| Dog recognized in both recordings | Test temporal grounding |
| Dog recognized only when cropped | Investigate event sparsity and chunking |
| Dog not recognized in either | Test a longer environmental sound |
| Silence hallucinated | Prioritize sound-presence reliability |
| Requests fail operationally | Investigate hosted availability before judging recognition |

### When to pause full-film generation

Keep full-film generation paused if completed controlled tests continue to show:

- False events during digital silence.
- Failure to recognize clearly audible environmental sounds.
- Unsupported source or attribute claims.
- Unreliable event timing.
- Inconsistent responses when identical audio is paired with silent video.
- Insufficient hosted availability to obtain matched results.

A few successful descriptions would justify further controlled experiments, not automatic acceptance of 596 seconds of captions.

### Research conclusion

The literature supports an audio-first, evidence-preserving pipeline with separate recognition, temporal grounding, visual association and caption personalization.

It does **not** currently provide a verified drop-in fix for the hosted Nemotron endpoint.

For SceneCaptions Phase 1, the defensible approach is to demonstrate the functioning player, document the failed capability gate, and present a small reproducible experimental plan.

An independently generated caption segment should be included only if it passes the relevant acoustic and timing checks.

**The immediate research priority is not better caption wording. It is determining whether the available hosted model can reliably recognize a real environmental sound before asking it to produce timestamps and accessibility-ready descriptions.**

---

### Research limitations and date qualification

This review used official NVIDIA documentation and primary research pages accessible on **27 October 2026**. It did not execute inference or independently reproduce published experiments.

The reviewed TAC revision, SpotSound revision, RED submission, ACPO publication and NVIDIA documentation were already relevant to the 26 October evidence snapshot. I did not establish a newly released model or capability that became available specifically on 27 October.

NVIDIA's documentation can change independently of its hosted deployment. The reviewed pages do not reveal the exact software revision serving your requests.

The review also did not independently establish current hosted entitlement for every candidate, inspect every linked supplementary repository or verify all proposed methods against Nemotron. Those remain open verification items rather than negative findings.

**Bottom line:** No verified NIM-hosted, free/trial-only solution was found that can already be claimed to satisfy SceneCaptions' full independent sound-captioning requirements.
