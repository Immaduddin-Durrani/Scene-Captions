# Local film integration — 24 October 2026

The user explicitly requested downloading and integrating Sintel/Tears of Steel, superseding the prior download-only-by-user instruction for these films. Work stayed in the main session. No skills were newly activated, agents/services installed, model requests made, dependencies added, or commits/pushes performed.

**Three videos are now selectable. The two added films have official English dialogue subtitles, not complete reviewed non-speech captions.** This request is only partially fulfilled with respect to full sound-caption coverage. See [per-title coverage](../../LIBRARY_CAPTIONS.md).

## Sources and outcomes

| Film | Official source / local result | Subtitles |
| --- | --- | --- |
| Sintel | `https://download.blender.org/durian/movies/Sintel.2010.720p.mkv.zip`, 681,285,470 bytes; MP4 625,173,895 bytes, 1280×544, 888.032 s | 26 source cues from the explicitly tagged English MKV stream |
| Tears of Steel | `https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov`, 372,178,639 bytes; MP4 366,404,677 bytes, 1280×534, 734.166667 s | 76 cues from the [official English SRT](https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt) |

Both movies are Blender Foundation CC BY 3.0 works. Original H.264 picture bytes and full credits were retained in MP4; audio was encoded as stereo AAC, with extracted posters/subtitles. These dimensions preserve each widescreen 720p release without stretching. [Media records](reports/media.json) include source/output SHA-256, duration, sizes, codecs and attribution. Hashes and expected sizes are local reproducibility checks, not publisher signatures. Large local sources and MP4s remain ignored by Git; small subtitle sources, data and preparation code are reviewable.

The repository contained no ready non-speech track for either film. A 141-cue Sintel teaching-example VTT was found at `https://mainline.i3s.unice.fr/mooc/sintel-captions.vtt`. Its separate reuse terms and audio timing were not verified; unusually short displayed intervals also need review. The candidate remains under ignored `artifacts/library-sources/`, outside playback. A public streaming vendor [explicitly describes its Tears of Steel caption-signalling demo as lacking proper captions](https://www.unified-streaming.com/blog/broaden-your-audience-accessibility-features-in-video-streaming); signalling alone was not treated as sound-caption data. No universal claim that a proper track exists nowhere is made.

The default licensed Big Buck Bunny sound dataset and failed NVIDIA gate were left unchanged. Full sound annotations for the new titles still need an appropriate source or genuine listening/wording preparation. No hearing-impaired accessibility completeness or participant benefit is claimed.

## Implementation and verification

- `ScreeningRoom` selects one film and remounts `Workspace`, clearing old captions, imports, seek/preview/override and playback state. Saved viewing preferences remain in browser storage. Selection is fixed after rehearsal starts, including after stopping, until reload.
- Dialogue has its own validated, fixed text/timestamps and jumpable transcript. It shares caption readability styling and cannot be rewritten by sound preferences. Duration mismatch hides both dialogue and sound overlays. Missing non-speech data uses explicit `not-prepared` status, without inventing a failed inference or approving sound cues.
- Official Tears of Steel SRT has extra blank separators. The strict parser now accepts runs of blank separators while retaining malformed-block, timestamp and duplicate-ID rejection. Source files and all 102 dialogue intervals/texts are preserved.
- [Browser results](reports/browser-results.json): every imported dialogue cue checked after an actual seek with a decoded frame available; gaps clear, playback/pause work, posters/credits follow title, old preview/sound cues clear, transcript jump works, narrow layout has no overflow, and rehearsal locks selection. This checks rendering/transport, not a full audio-listening review.
- [Existing browser regressions](reports/legacy-browser.txt) passed for all 87 Big Buck Bunny source intervals, draft/readability, preview timeout/manual return, original priority, persistence, imports, rehearsal/export and plan route.
- [Byte-range checks](reports/byte-ranges.json): both new videos return HTTP 206. 18 [Node tests](reports/node-tests.txt), 22 Python offline tests, types, all dataset validation and production build have outputs/command records in `reports/`.
- A synthetic-only import additionally verified one shared dialogue/sound stack, fixed dialogue through sound preference changes, and suppression of both types on duration mismatch. No synthetic dialogue entered the real datasets.
- Desktop and 390 px screenshots in `screenshots/` were visually inspected. An initial screenshot was taken before decoded seek completion; final checks wait for media readiness. The initial automated range fill also used a value incompatible with step 0.1; that test input was rounded, with its failure retained as `browser-initial.txt`.

## Reproduction

Requires the existing Node/Python/ffmpeg/ffprobe tools; no API key. Explicit preparation: `python3 scripts/media/prepare-library.py --film all`, then `node --experimental-strip-types scripts/import-library-captions.ts`. Cached complete downloads are reused. The browser checks use the already-installed isolated Playwright runtime; `scripts/verification/library-regression.mjs` is a manually invoked local check, not part of app startup. Run a local app at 127.0.0.1:3000 first. Its `PLAYWRIGHT_MODULE` environment variable can point to another existing module installation; it installs nothing.

The earlier Fallow report and Graphify manifest predate this integration; current docs mark them stale for changed files. No current cleanliness or complete-map claim is made. Historical investigation evidence remains intact.
