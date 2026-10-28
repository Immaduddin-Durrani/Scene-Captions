## Media-only experimental option — 28 October 2026

All three films now offer **Use media-only AI subtitles**. These were generated
from the complete film audio without fetched captions, plot or supplied scene
text. Three sound-detail levels and generated dialogue are available. Sound
captions span 15-second analysis windows, not detected event boundaries.

Known acoustic tests remain failed. Sounds, words and timings can be wrong,
missing or invented. The existing captions stay available as a separate default.
Downloads: [Big Buck Bunny](media-only/big-buck-bunny-detail-2.srt),
[Sintel](media-only/sintel-detail-2.srt),
[Tears of Steel](media-only/tears-of-steel-detail-2.srt).
These are experimental drafts, not verified accessibility captions.

# Caption generation status — 26 October 2026

Big Buck Bunny's Personalized track uses 87 AI-assisted, source-assisted draft captions from the earlier local Qwen2.5-1.5B run, with extensive editorial corrections. Reference baseline and Show reference display the actual fetched Demuxed sound captions at the same timestamps. Source events and timing are credited under CC BY 3.0; no independent audio recognition is claimed.

A subsequent NVIDIA NIM investigation made 42 bounded requests. Novel speech transcription worked, but sound/silence controls failed, including sound claims on two verified muted clips. Some Super VL reference-plus-visible-context expansions were useful drafts. No full NIM-generated track has been accepted or installed. Capacity errors are separate from wrong answers.

The latest caption-free follow-up made twelve more requests with natural sounds, exact audio shifts and digital silence: six HTTP 200, five capacity errors and one timeout. A fresh speech control worked again, but the model reported a tone on all-zero audio. No correctly identified timed pair completed, so relative timing remains unscorable. The independent sound-caption gate remains failed.

Three detail descriptions and three punctuation styles form nine saved combinations in the current local draft. They are not nine independently generated semantic variants. Full listening, timing, reading-time and DHH usability review remains pending. No participant study or accessibility improvement is established.

[Generated draft JSON](/research/demo-captions.json) · [Generated fixed SRT](/research/big-buck-bunny.srt)

Sintel and Tears of Steel retain source dialogue only; full sound-caption tracks are not prepared. No model runs during viewing. No paid fallback was invoked.
