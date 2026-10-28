# Simple source-guided richness — 28 October 2026

The user asked for existing captions as prompt input, richer descriptions at
several levels, and common, easy English at every level. The user then selected
**only verified/source-caption sounds**, declining the use of our unverified
audio-generated sound labels for Sintel and Tears of Steel. Consequently this
run enriches Big Buck Bunny's licensed sound reference only. The other films'
source dialogue remains unchanged; no sound coverage is invented for them.

The user further requested better prompt engineering and more useful context.
The final [v4 protocol](v4/protocol.json), [generator](../../../scripts/generate-source-richness.py)
and [exact requests/responses](v4/reports/) record the implemented prompt.

## What the revised prompt supplies

- The complete 87-cue licensed reference timeline, with original timestamps.
- Every occurrence of each target sound, including simultaneous source lines.
- A plain-English sound-word glossary: for example, crescendo means music gets
  louder, and conkers means nuts. Definitions explain words, not newly heard facts.
- DHH viewing goals, three clear level descriptions, short fixed reading windows,
  and explicit per-field word/character budgets.
- A boundary between source evidence and unknown facts: no inferred instruments,
  material, location, surface, loudness, pitch, tempo or scene cause.
- Concrete earlier failures: brook does not establish stones; thud does not
  establish a heavy object falling onto ground; laughter is not loud chatter;
  serene music does not establish soft volume or a steady tempo.
- A source-fidelity pass, simple-word pass and coverage/length pass in the prompt.
- One bounded corrective request with the previous **unverified draft** and exact
  validation feedback, such as the offending field, its length and its limit.

Neighboring caption context is explicitly not permission to move another sound
into the current cue. No movie plot, media-only observations or other-film
dialogue is input. No audio/video is input in this source-only rewrite run.
This is source-assisted wording, not independent acoustic recognition.

## Experiments and actual limits

The first Super VL pilots passed formatting but mostly repeated the same wording
at different levels. A simpler Ultra prompt produced fuller text but introduced
unsupported scene/volume details. Earlier records remain under the root, `v2/`
and `v3/`; two sequential runs were interrupted when the approach changed.

The final model was `nvidia/nemotron-3-ultra-550b-a55b`. The hosted API
[documents `reasoning_effort: none`](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-ultra-550b-a55b-infer),
and the actual final calls accepted that setting. The full source context plus
corrective feedback substantially improved the observed drafts, including the
earlier stones/ground/loudness examples. This is not an isolated causal experiment:
prompt, context and reasoning settings changed across the exploratory versions.
Formatting checks and model self-review do not prove semantic accuracy.

The final run used 18 recorded requests, capped at two per batch. The complete
investigation has [27 recorded HTTP-200 requests](request-summary.json), with up
to two additional interrupted in-flight attempts possibly absent. Only NVIDIA
was used. No new software, model downloads, skills, agents or paid providers were
used. Account entitlement and remaining free-tier allowance were not verified.

**Main-session source-text editing was still necessary:** 88 of 201 fields were
edited across 48 of 67 labels. Edits shorten wording, explain sound words, remove
remaining unsupported details and create useful distinctions where the source
and brief interval permit them. These are AI-assisted, edited captions, not
untouched model output. [All before/after edits and review scope](v4/source-text-review.json),
[reviewed labels](v4/reviewed-labels.json), [wording checks](wording-checks.json).
This was not independent review, human listening or DHH readability validation.

## Result and selection

The separate track has **87 cues** based on 67 unique labels. All source events,
simultaneous lines, timestamps and credits remain intact. Three text levels share
fixed expression; these are not nine independently generated semantic variants.
Scene adaptation is disabled for this track so selecting Rich does not silently
switch back to Essential. The underlying failed acoustic gate remains unchanged.

| Reference | Essential | Balanced | Rich |
| --- | --- | --- | --- |
| FLY BUZZES | Buzzing fly | A fly buzzes | A fly makes a buzzing sound |
| MUSIC CRESCENDOS | Music | Music gets louder | Music builds up and gets louder |
| BOW STRING PINGS | Ping | Bow string pings | Bow string makes a ping |

66 of 67 labels have distinct text at all three levels; the very brief squirrel
pain cue retains the same full wording in Balanced/Rich. Every atomic caption
has at most eight words. This measures wording, not understanding. There remain
25 cue/level flags under the 28-character/second **editing heuristic**, which is
not a validated DHH reading-speed standard. Source intervals are never stretched;
very brief simultaneous cues need listening/timing/readability review.

Choose **Use source-guided captions** for Big Buck Bunny. Reference baseline and
Show reference display the original fetched wording. The existing default and
experimental media-only tracks stay separately available. The new option is
absent for Sintel and Tears of Steel because their fetched files have no sound
caption references. Three SRTs and caption JSON are available below the player.

Rebuild from saved outputs with no new calls:

```sh
/Users/hamza/runtimes/scenecaptions-nim-asr/bin/python scripts/generate-source-richness.py --limit 0 --collect-drafts --assemble
```

The source-text review is bound to the raw generated-label SHA256 and every edit
checks its before-value. Strict final word/character/jargon checks and source
identity/coverage guards run before the app receives the track. A bounded draft
can be preserved for editing but cannot bypass those final checks.

## Verification

29 Node tests, 46 offline Python tests, caption validation and the production
build passed. Browser checks verified keyboard/time-preserving source switching,
all three detail levels on four representative cues (including simultaneous
sounds), correct pressed states, fetched comparison, three downloads, rehearsal
locking and export provenance, and a 390-CSS-pixel viewport without horizontal
overflow. Existing media-only mode was also checked on all three films.
No physical mobile, full accessibility audit, participant study or caption-accuracy
percentage is claimed. [Checks](checks/), [desktop](screenshots/desktop.png),
[mobile viewport](screenshots/mobile.png), [synthetic export](exports/rehearsal.json).

The source is Demuxed / big-buck-captions contributors, CC BY 3.0, pinned at
`e490383ca58f53507cfa18a64e1324f28d77c65a`. Film © 2008 Blender Foundation,
CC BY 3.0. Source author mood labels remain interpretations. Full listening and
DHH readability review are pending. No push or deployment was performed.
