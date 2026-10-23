# Sourced caption verification

2026-10-23, local engineering checks in the main session.

- Pinned source README declares CC BY 3.0. Exact source and commit preserved under data/sources/big-buck-captions/. Attribution and changes are disclosed in the app and media credits.
- Twelve unit tests passed, including strict SubRip parsing and rejection, exact preservation of all 87 source intervals/text, multiline cues, baseline behavior, density rationale, failed-model rejection and the old 1:18 mismatch.
- Dataset schema validation, TypeScript and optimized production build passed.
- Chrome browser checks passed for all 87 intervals after actual media seeks, including the final cue and multiline sound effects. Original text matched the source in every checked interval. This verifies import/playback mechanics, not a complete listening review.
- Browser also checked play/pause, timeline jump, original override, detail/expression preview and apply, persistent preferences, keyboard seek, cue-density adaptation/rationale, local video clearing, invalid-quality import rejection, duration mismatch suppression, valid import/restoration, consent/export, mobile width and the experimental plan route.
- Screenshots sourced-captions-desktop.png and sourced-captions-mobile.png were visually inspected. The apple caption is visible with enabled controls. Browser reported zero errors and one existing Next.js smooth-scroll configuration warning.
- Six visual sync anchors match the source events, as recorded in sourced-caption-import.json. No complete listening review or participant study was performed.
- No runtime API calls or new keys needed; generation/import is local. The failed NVIDIA candidates remain outside playback.

No skills or agents were activated for this follow-up. The earlier extracted code graph remains a snapshot; the new importer/parser path is manually documented in CODEBASE_MAP.md.
