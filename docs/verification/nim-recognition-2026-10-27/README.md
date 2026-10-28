# Audio-only recognition follow-up — 27 October 2026

**Result: no accepted independent sound-caption capability.** Cropping the bark did not establish dog recognition. Repeating the exact burst produced repetition-related acoustic text but still no dog identification. A fresh speech recording transcribed correctly, yet the **same WAV with the general sound-description instruction was called silent**. That task-dependent discrepancy is a stronger new diagnostic lead than a claim that only event sparsity explains the failures.

There were **12 NVIDIA NIM requests across nine unique cells: nine HTTP 200 with explicit `stop`, three HTTP 503 capacity errors**. Each capacity-blocked cell received at most one unchanged-payload retry; all attempts are retained. No timing, audiovisual or full-film requests were made because the recognition/absence prerequisites failed. Playback data and the existing failed capability gate were unchanged.

## Inputs and decisions

The [27 October research proposal](../../research/SceneCaptions_NIM_Research_2026-10-27.md) motivated the cropped-sound comparison. The [other research response](<../../research/Media-First DHH Sound Captions on NVIDIA NIM_ Diagnosing Nemotron Omni Audio Failures Before the Next Experiment.md>) motivated the repeated-burst control and separating speech from general descriptions. These documents are proposals, not validation of the hosted endpoint.

The initial [protocol](protocol.json) and [manifest](inputs/recognition.json) were saved before inference. Later protocols record the conditional follow-ups before their respective requests: [rain](rain-protocol.json), [speech](speech-protocol.json), [capacity retries](rain-retry-protocol.json) and [final controls](final-protocol.json). This was an adaptive diagnostic, not a preregistered benchmark or independent review.

All recognition requests used:

- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` on the existing NVIDIA hosted chat-completions endpoint.
- One user message, mono 16-kHz PCM16 WAV through `audio_url`, then a text instruction. No video, plot, existing captions or expected category labels were supplied.
- `temperature=0.2`, `top_k=1`, `max_tokens=256`, `stream=false`, `enable_thinking=false`, no reasoning budget. Same parameters across comparisons.
- Single attempts through the existing bounded driver, 180-second timeout and shared 2.05-second minimum spacing. Capacity retries were explicit and followed cooldown, not a hidden retry loop. The run stayed below its 24-call ceiling and stopped at 12.

The common instruction was:

> Describe the audible sounds in this recording. If no sound is audible, say so. Do not infer sounds from context.

Only q07 used a different instruction: “Transcribe the speech in this recording exactly.” Its expected words were evaluation metadata only.

## Actual observations

| Cell | Input | Answer from completed request | Assessment |
| --- | --- | --- | --- |
| q01 | Original ten-second dog fixture | “Silence.” | Missed target and audible activity. |
| q02 | 1.5-second crop containing the exact same bark | “The sound of opening a door” | Wrong source/category; cropping did not yield a dog hit. |
| q03 | 1.5-second digital silence | “The sound of hitting a drum” | Definite false positive on all-zero PCM. |
| q04 | Original ten-second rain fixture | “Waves, surf, Ocean” | Broad water relationship; unsupported source specificity. Not a strict rain hit. |
| q05 | Exact five-second rain crop | “The sound of water flowing” | Partial water relationship; not a strict rain hit. Initial request was 503. |
| q06 | Ten-second digital silence | “Silence.” | This absence control passed. Initial request was 503. |
| q07 | Fresh 2.5924375-second synthesized speech; transcription task | “Nine silver spoons rest beside the red kettle.” | Exact expected words, normal completion. |
| q08 | The identical speech WAV; common sound-description task | “No sound is audible.” | False absence despite the successful ASR control. Initial request was 503. |
| q09 | Same dog burst repeated eight times in ten seconds | A series of sharp percussive impacts, roughly every 0.8 seconds; no speech/music/ambience | Recognizes repetition-related structure but not the dog category. Actual source onsets are one second apart; other acoustic attributes were not independently reviewed. |

Raw reports, in execution order: [recognition](reports/recognition.json), [rain](reports/rain.json), [speech](reports/speech.json), [speech description](reports/speech-description.json), [rain retries](reports/rain-retry.json), [final checks](reports/final-checks.json). The [assessment](assessment.json) retains every attempt, completion status, latency, literal response and limited manual interpretation. HTTP 503 responses are inconclusive, not recognition errors. Neither invalid schema nor JSON repair is relevant to these plain-text answers.

## Media and request integrity

The preparations preserved samples rather than re-encoding or normalizing sound levels:

- q01's PCM equals the prior hash-verified c01 source. The source dog recording and [attribution](../nim-counterfactuals-2026-10-26/control-attribution.json) come from the pinned ESC-10 subset.
- q02 is exactly source samples `[44000:68000]` (2.75–4.25 seconds), containing every original nonzero sample. It has silence on both sides of the ~0.357-second burst. Cropping changes total duration/context and whole-clip RMS; it does not isolate a unique encoder mechanism.
- q03 and q06 contain only zero-valued PCM samples.
- q04 equals the prior rain PCM. q05 is exactly its samples `[16000:96000]`, preserving all nonzero source samples.
- q07 was created locally using installed macOS speech synthesis at rate 170, then FFmpeg to PCM16/16k mono. This is synthetic test-media creation; all recognition calls used NVIDIA. The fresh phrase was not reused from the previous day's positive control. Default voice/platform may affect reproduction; the exact WAV hash is recorded and its bytes remain in the local ignored cache.
- q09 repeats the exact nonzero dog-source burst at 1, 2, …, 8 seconds, with no gain changes or overlapping copies. Repetition changes event count/exposure and whole-clip RMS, so a response difference would not prove a single sparsity mechanism.

[Integrity assessment code](assess-results.py) checked every report against its frozen manifest, every media hash against the current file, all crop/repetition sample equalities, digital-zero controls and unchanged retry payload hashes. It also compared q07/q08 payloads: **after removing only the instruction text, they are identical**, including the media hash and generation parameters. This proves the local request comparison; it cannot reveal internal hosted tensors, caching, checkpoint or replica configuration.

Prompt-token accounting varied with duration: the same description instruction used 169 reported input tokens for ten seconds and 63 for 1.5 seconds. That is compatible with duration-dependent audio tokenization, but is not proof of which acoustic information survived encoding or whether the backend heard a specific sound.

## What this supports

1. **Cropping alone did not solve the tested dog case.** A short event remains a relevant difficulty, but the crop result does not establish successful underlying dog recognition.
2. **More exposure was insufficient for strict source recognition in this trial.** The repeated-burst answer contains some relevant repetition-related acoustics; calling it wholly unrelated would overstate the failure.
3. **Silence behavior is inconsistent.** One short silence elicited a drum hit; one longer silence correctly elicited silence. There were no successful repeated matched-duration trials, so duration, preprocessing, sampling and backend variability are not separated. This does not prove digital silence is out of distribution.
4. **The speech/general-description discrepancy deserves the next focused investigation.** A fresh ASR pass contradicts complete failure of the audio input path. The same-media false absence shows that successful transcription does not guarantee faithful audio descriptions. The instruction was the only changed request field, but opaque serving/replica variability remains a confound; this was one completed pair, not a causal proof about model weights.
5. **Broad water descriptions remain partial evidence.** They do not satisfy the frozen strict rain criterion or establish correct source identity, attributes or timing.

The next diagnostic priority is a small repeated comparison of transcription versus audio-description/question formulations on identical speech and clearly recognizable environmental sound, using exact documented request contracts. Keep semantic recognition, sound presence/absence and output format separate. No such extra requests were made after the final controls; full-film generation remains paused.

## Verification and limits

Dataset categories are evaluation metadata, not fresh human listening annotations. There was no independent listening panel or DHH study. Sample bounds establish signal support, not exact perceptual event boundaries. Caption detail levels, long-form coverage, simultaneous effects and usefulness for DHH viewers were not validated. No new model/runtime installation, agent, paid provider, playback-track installation, commit or push was performed for this batch.

Preparation and assessment scripts here make no network calls. Reproducing inference requires the separate existing driver and NVIDIA access; do not run frozen preparation commands over existing evidence. Exact media is ignored under `artifacts/nim-recognition-2026-10-27/`, so another checkout must reconstruct or obtain the matching files before it can reproduce request hashes.

This batch changes only dated experiment evidence. Existing code-map source inputs remain unchanged; no named skill or mapping workflow was activated for this task.
