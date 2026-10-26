# Generated caption demonstration — 26 October 2026

The new local Big Buck Bunny track has **87 AI-assisted generated fixed captions**, used by Personalized and the downloadable generated SRT. Source timestamps and event coverage are retained. Reference baseline and Show reference display the actual licensed fetched wording for comparison.

## How to describe it tomorrow

“We use an anchored generation pipeline: licensed sound-caption references provide event labels and timing, a local Qwen model drafts new descriptions, source-text checks and editorial corrections remove errors, and the player selects precomputed variants from viewer preferences. This is a source-assisted generation prototype; it does not independently recognize all sounds from arbitrary video.”

The model is `mlx-community/Qwen2.5-1.5B-Instruct-4bit`, pinned to `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, run with MLX-LM 0.32.2 on this Mac. The approximately 869 MB model artifact was downloaded and checksum verified. This earlier Qwen generation ran offline, with no cloud call or API key. The subsequent NIM investigation made 42 calls but accepted no full track; see [the current findings](verification/nim-phase1-2026-10-26/README.md). The [model card](https://huggingface.co/mlx-community/Qwen2.5-1.5B-Instruct-4bit) documents the underlying local load/generate interface; it does not establish our caption quality.

## What actually happened

There were 68 local generations: one rejected overcomplicated prompt, then drafts for all 67 distinct reference labels using a simpler three-description prompt. Every raw response is preserved with its full prompt, completion status, model revision and timing in [evidence](verification/generated-captions-2026-10-26/). The first full pass exposed unsupported loudness, changed source identities and fabricated actions. These were not accepted unchanged.

**63 of 67 labels required editorial changes, affecting 120 of 201 fields.** This was extensive main-assistant source-text correction, not an independent reviewer or human listening review. [The authoring record](../data/authoring/big-buck-bunny-generated.json) gives each field's before/after text and exact raw-response location. The result is AI-assisted and edited, not claimed as untouched model output or fully automatic success.

The final fixed captions differ from the fetched text at all 87 intervals. Each cue retains separate `reference_text`. Three generated/edited descriptions supply detail levels; punctuation rules create the three expression styles (minimal, sentence, emphatic). The nine stored combinations are **not nine independently generated semantic variants**. Expression styles do not infer emotion or additional loudness. Same-sound wording is reused consistently.

## Show the running app

```sh
npm run dev
```

1. Select Big Buck Bunny and jump to the apple cue near 1:23. Personalized displays generated wording; Reference baseline displays `[APPLE THUDS]`.
2. Change detail, preview temporarily, then apply. Toggle expression to demonstrate punctuation styling; explain this limited mechanism accurately.
3. Choose Reference baseline or Show reference to compare the fetched caption without changing the video timestamp. Return to Personalized or turn the reference override off to restore generated variants.
4. Download generated SRT or JSON from the notice beneath the player. Compare the export with the live caption.
5. Open the experimental plan for the proposed research procedure. No participant findings are claimed.

Downloads in this checkout: [SRT](../public/research/big-buck-bunny.srt), [WebVTT](../public/research/big-buck-bunny.vtt), [JSON](../public/research/demo-captions.json).

## Rebuild and provenance

`npm run setup:captions` deterministically assembles the track from the saved generation/editorial record and licensed reference. It makes no model or network calls. The historical reference importer requires explicit `--restore-reference` to prevent accidentally replacing generated playback with fetched text. Fresh generation uses `scripts/generate-local-source-captions.py` in the isolated runtime under `~/runtimes/scenecaptions-text`; setup/package/model pins are under `~/skill-library/setup-records`. Candidate generation cannot install a playback track.

The reference remains attributed to Demuxed / big-buck-captions contributors under CC BY 3.0, pinned to the original repository revision. New wording is a derivative; do not claim independent event annotation or remove credit. Big Buck Bunny remains © Blender Foundation, CC BY 3.0. Neither source timestamps nor the movie changed.

## Limits before presenting or studying

Full listening review remains pending. A complete contextual listening packet with all 87 cues and variants is prepared under `artifacts/caption-review/generated-bbb-2026-10-26-final/`; open `index.html`. Every approval starts pending. A source-text check is not evidence that a sound occurs at that moment. Existing failed audio-model gates remain unchanged.

A 20-character/second editing heuristic flags 7 generated fixed-export intervals, versus 10 in the old fetched baseline. This is not a validated DHH threshold; the lower flag count is not proof of improved reading speed or objectively better caption quality. Preserve timing for this draft and review those cases, rather than silently stretching cues. Study use requires listening/timing/readability review and appropriate study approval.

This draft is local. Updating the Vercel site requires a new push/publish request under the user's workflow rules.
