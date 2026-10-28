# Audio recognition gate and late visual association — 27 October 2026

**This produces a safer boundary for the visual stage, but it does not establish more accurate subtitles.** The visual model preserved event identities, kept empty ledgers empty and abstained on unrelated contexts. The audio stage still misclassified known controls and added false events, including with NVIDIA's recommended hosted-compatible thinking settings. No new caption track is accepted.

There were **14 NVIDIA requests: 12 HTTP 200 completions and two HTTP 503 capacity responses**. The two capacity-blocked cells were explicitly retried once with unchanged payloads. All raw attempts remain evidence. No request was sent after the fixed 14-request ceiling. No paid provider, local model weights, agent, new runtime installation, push or deployment was used.

## What was tested

1. **Audio-first recognition:** use one common fixed vocabulary on known speech, dog, rain, silence and mixed controls, plus one unscored BBB excerpt. Correct labels are evaluation metadata, not supplied per case. This is a closed-vocabulary diagnostic, not an open-ended caption-generation benchmark.
2. **Documented preset comparison:** test the same dog/silence inputs and category prompt with instruct mode and the hosted-supported thinking parameters: temperature 0.6, top_p 0.95, max_tokens 20480 and reasoning_budget 16384. These requests were accepted; no budget-compatibility retry was needed. Server-only grace/context settings were not assumed configurable. This compares parameter bundles, not a single isolated reasoning switch. See [NVIDIA's model card](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard) and [hosted budget documentation](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning-infer).
3. **Visual association only:** a separate Super VL model sees screenshots and immutable audio-category candidates. It can suggest a possible visible source or mark it unresolved. It cannot add/delete events, alter acoustic categories, verify sound from pictures or generate final caption text.
4. **Negative and context controls:** same BBB candidates with matching/swapped frames; actual model-produced dog candidates with unrelated rabbit frames; and a known-silent, code-gated empty ledger with visually active frames.

The [initial protocol](protocol.json), [audio manifest](inputs/audio.json) and [preparation code](prepare.py) were saved before inference. The [explicit capacity-retry addendum](retry-protocol.json) and [visual protocol](visual-protocol.json) preceded their respective calls. This was an adaptive diagnostic, not a preregistered participant study.

All audio/media are reused hash-verified local fixtures. No fetched subtitles, existing movie-caption labels, plot, title or source SRT intervals were input to generation. The same vocabulary was offered on every audio case, including absent-sound controls. That makes the task easier and can bias responses; a category hit is not proof of reliable open-ended discovery.

## Audio-stage observations

| Input | Instruct response | Thinking response, where tested | Result |
| --- | --- | --- | --- |
| Digital silence | `tone_or_beep` as an invalid bare label | `["tone_or_beep"]` | False sound presence in both modes; format error recorded separately |
| Eight repeated dog bursts | `["dog_barking", "tone_or_beep"]` after capacity retry | `["impact_or_click"]` | One correct dog tag, but with an unsupported added tone; thinking did not supply the dog tag |
| Clean synthetic speech | `["silence"]` | Not tested | False absence; contradicts the separate successful ASR controls |
| Five-second rain crop | `["running_water_or_waves"]` | Not tested | Broad water relationship, not the required strict rainfall category |
| Known speech plus three dog bursts | `["human_speech", "impact_or_click", "tone_or_beep"]` | Not tested | Detects speech, misses dog, adds unsupported categories |
| BBB 85–90 s window | `["impact_or_click", "tone_or_beep"]` after capacity retry | Not tested | Candidate labels only; no independent listening ground truth |

Reports: [initial eight audio calls](reports/audio.json), [two unchanged capacity retries](reports/audio-capacity-retry.json). A missing/incomplete/HTTP-failed result is inconclusive, not a recognition failure. Empty lists or `uncertain` would be abstentions, not positive accuracy. The malformed bare label on silence is excluded from structurally valid category scoring, while its wrong raw semantics remain visible.

The strict controlled sets did not pass. Do not combine reused cases across presets into a general model-accuracy percentage. The correct dog tag is a limited new observation under a constrained vocabulary, not a complete success: the same answer adds an unsupported sound. A claimed water category is not silently upgraded to a rainfall hit.

## Visual-stage observations

The visual stage received only model-generated audio categories, not raw audio. Both real and negative contexts used the same association instruction and schema. Candidate sound times remain null; merely sharing a clip does not establish coincidence with an image instant.

| Condition | Actual visual response | What it establishes |
| --- | --- | --- |
| BBB candidate + matching frames | Possible `orange ball` for the impact; tone source unresolved | One possible source suggestion; object identity and causal attribution remain unverified |
| Same candidates + swapped burrow frames | Both sources unresolved | Abstained rather than forcing an association in this context |
| Dog/tone candidates + unrelated rabbit frames | Both unresolved; says no dog is visible | Known mismatch did not turn dog audio into a rabbit-source claim |
| Empty ledger + rabbit/apple frames | Empty associations | No new sound event created from the pictures in this test |

[Raw visual responses](reports/visual.json), [exact input ledgers](visual-inputs.json), [candidate ledgers after association](candidate-ledgers.json), [complete assessment](assessment.json).

All four responses passed the event-identity/status contract. Off-screen/unresolved audio events stayed in the candidate ledger. The model made one possible suggestion, so the test was not simply all-abstention; that suggestion is still not verified correct. A round object described as an `orange ball` is insufficient evidence to assert an apple impact in a caption. The ledger deliberately retains the audio stage's false tone candidate as unaccepted rather than letting vision silently rewrite the audio.

This is a safer **component contract** than asking the same model to invent joint audiovisual captions. It is not proof that architecture alone improved accuracy: the visual model, instructions, response schema and task also changed from the prior joint Omni-captioning pilot. Empty-ledger safety is partly enforced by code, and does not establish that the audio stage can discover real events.

## Validation and limits

The [bounded runner](run.py) uses the existing NVIDIA client, private key loader, 180-second single-attempt timeout and shared start pacing. It enforces the 14-request ceiling and stops a stage after three consecutive capacity errors. No credentials or inline media bytes are saved in reports. The optional open-description request was omitted to retain the ceiling after the two explicit capacity retries.

[Assessment code](assess.py) verifies manifests and media hashes, checks identical retry payloads, assesses audio labels separately from visual bookkeeping, and preserves acoustic events unchanged during the visual join. The [audio gate checks](audio-offline-checks.json), [visual guard checks](visual-offline-checks.json) and [35 shared offline tests](reports/shared-offline-checks.txt) cover completion, syntax, unknown categories, added IDs, changed fields, erased off-screen events and uncertainty handling. These checks do not validate acoustic or visual truth.

Source frames are local research derivatives of Big Buck Bunny, © 2008 Blender Foundation / peach.blender.org, CC BY 3.0. The dog/rain samples retain their [ESC-10 attribution](../nim-counterfactuals-2026-10-26/control-attribution.json). Media remains ignored under `artifacts/`. All interpretation was done in the main session; no independent listening panel, human-labelled movie benchmark or DHH study was conducted.

**Practical conclusion:** use a strict association-only visual stage to prevent pictures from freely creating sound events, and preserve uncertainty instead of promoting possible sources to facts. The remaining blocking requirement is accurate audio-event discovery and timing. More caption wording or image context cannot validate the incorrect audio candidates observed here. The existing source-assisted player track and failed audio gate remain unchanged.
