# Local source-assisted caption generation — 26 October 2026

The user requested new generated Big Buck Bunny captions, with fetched captions used only as reference. The previous local-only constraint remains active. This work used no skill, cloud inference, model-generation API call, agent, service installation or deployment. Model/runtime artifacts were downloaded into isolated runtimes; no media was uploaded.

## Outcome

The local player and exports now use **87 new fixed captions**, covering all source intervals. Separate reference_text preserves the licensed source words for provenance; playback baseline uses newly generated-and-edited original_text. The final fixed captions differ from fetched text at all intervals, while timestamps and separate simultaneous sound lines are preserved. The source remains CC BY credited, rather than represented as independent event annotation.

[Model](model.json): local Qwen2.5-1.5B Instruct, MLX 4-bit, pinned revision and weight SHA-256; MLX-LM 0.32.2, deterministic temperature zero. Runtime/model setup and dependency freeze are under ~/skill-library/setup-records; isolated runtime is ~/runtimes/scenecaptions-text. Local downloads are outside Git. [Summary](summary.json) reports actual counts and limitations.

## Raw evidence and substantial corrections

- [Initial probe](probe.json): one overcomplicated nine-cell prompt produced padding and unsupported location claims. It was rejected and is not used.
- [Simplified probe](probe-v2.json): four labels, three descriptions each. Meanings were checked against reference text before continuing.
- [First continuation](full-v2.json): four labels, then stopped on an invalid snore description.
- [Remaining drafts](rest-v2.json): 59 labels collected, including rejected output for editorial comparison. The generator cannot install a player track.

There were **68 local generations**, with drafts for 67 distinct labels and zero cloud inference calls. All used rows completed with stop. Some complete responses had extra text after the first JSON object; its removal is explicitly recorded, not treated as a structural pass. Raw outputs invented loudness, changed singular/plural sources, changed sounds/actions and added locations. Do not claim a fully automatic source-fidelity success.

**63 of 67 labels needed main-assistant source-text edits, affecting 120 of 201 fields.** [The authoring record](../../../data/authoring/big-buck-bunny-generated.json) contains raw-response locations and each field's before/after text. This is extensive AI-assisted editorial correction, not a human listening approval or independent review. The installed draft must be described as locally generated **and edited**.

[Installation evidence](installation.json) binds the final authoring record, player JSON and SRT by hash. Three descriptions supply detail levels; deterministic punctuation styling supplies minimal/sentence/emphatic expression. The nine cached combinations are not nine independent semantic generations. No instruments, volume claims or inferred emotions are introduced by the punctuation mechanism. Existing failed audio-model gates are unchanged.

## Verification and reproduction

- Final production build and TypeScript passed; 19 Node tests and 22 offline Python tests passed. Regression checks cover generated baseline/export agreement, reference/timing preservation, simultaneous sounds, provenance requirements and failed-generation rejection.
- [Chrome browser check](browser.json) exercised every generated cue after actual seek/decode, the former 1:18 gap, fixed generated baseline, override, preview/apply, persistence, cue-density adaptation, imports/mismatch/failed-candidate rejection, rehearsal/export, mobile layout and the experimental plan. The served SRT matched the generated file byte-for-byte. These are technical checks, not listening approval.
- `npm run setup:captions` reproduced all four installed track/export files byte-for-byte. It assembles saved records without inference or network access. The old source importer now requires an explicit --restore-reference rollback flag.
- Full pending listening packet: artifacts/caption-review/generated-bbb-2026-10-26-final/index.html. All 87 cues are included and all review decisions remain pending. No source times were stretched.
- A 20-character/second heuristic flags 7 final fixed captions versus 10 in the fetched baseline (13 in the first generated draft). This is a review heuristic, not a validated DHH measure, accuracy score or evidence of better accessibility.

The two other film datasets and failed NVIDIA audio gate remain unchanged. The codebase map is stale for the new caption schema/generation/viewer changes. Model weights, listening clips, temporary server artifacts and private .env are excluded from Git. Current private credential values/JWT patterns were checked in pending text artifacts; this is a bounded check, not an exhaustive security audit.

This draft has not been committed, pushed or published. The live Vercel release remains the previous version until a fresh explicit publish request. See [presentation wording and local demonstration](../../GENERATED_CAPTIONS_DEMO.md).
