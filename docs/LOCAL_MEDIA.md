# Local demo media

The user explicitly requested agent downloads and integration for this follow-up on 24 October 2026, superseding the earlier user-download-only restriction for these two films. Both official 720p sources were downloaded in the macOS checkout and prepared locally. Nothing downloads on app startup or while watching. No services, accounts or API keys were added.

Keep the existing Big Buck Bunny sample (9:56) and optionally add Sintel (about 15 minutes, animation) and Tears of Steel (about 12 minutes, live action/science fiction). The preparation script measures exact durations and rejects files longer than 30 minutes without trimming credits. All three films are now selectable. The additional films have official dialogue subtitles; complete non-speech caption coverage remains unfinished. See [caption coverage](LIBRARY_CAPTIONS.md).

## Preparation commands

On macOS/Linux, the equivalent explicit offline command is `python3 scripts/media/prepare-library.py --film all` (Python standard library, existing ffmpeg/ffprobe). It reuses completed sources, preserves compatible H.264 picture bytes, encodes stereo AAC and extracts tagged English subtitles/posters. Then run `node --experimental-strip-types scripts/import-library-captions.ts` to bind official subtitle datasets to the resulting exact MP4 hashes. Do not run downloads during playback.

### PowerShell

Requires `curl.exe`, `ffmpeg` and `ffprobe` on PATH. The script checks these before downloading. From the project folder:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\media\prepare-library.ps1 -Film all
```

`Bypass` applies only to that PowerShell process; it does not change your saved execution policy. To download one film at a time, replace `all` with `sintel` or `tears-of-steel`.

If the existing Big Buck Bunny file is absent, the separate user-run command is `npm run setup:demo`. The library script does not replace that verified sample.

The user successfully ran the library script on 24 October 2026. Local checks confirmed both MP4s contain H.264 video and AAC audio, matching resource-record hashes, posters and English VTT files. Sintel is 1280x544, 888.032 seconds; Tears of Steel is 1280x534, 734.167 seconds. These are the widescreen picture dimensions of their 720p releases. See [local verification](verification/fixes-2026-10-24/reports/local-media.json). Full listening and subtitle-timing review remain pending. That older Windows preparation was performed by the user; the newer macOS downloads above were explicitly authorized.

The script preserves the original dimensions of each official 720p release; widescreen films can have fewer than 720 picture rows. It does not stretch or upscale them. Completed source downloads are reused. Existing 480p or incomplete browser copies are rebuilt from the cached source and replaced only after resolution, codec, audio and duration checks pass. An interrupted download ending in `.partial` is downloaded again; an interrupted conversion restarts without downloading the completed source again.

## Files and storage

| Location | Purpose |
| --- | --- |
| `.media-cache/library/` | Original downloads, extracted Sintel MKV and temporary conversion files; ignored by Git |
| `public/media/sintel.mp4`, `tears-of-steel.mp4` | H.264/AAC browser copies preserving the original 720p-release dimensions, sound and full credits |
| `public/media/<film>-poster.jpg` | Still extracted at 60 seconds |
| `public/media/<film>-en.vtt` | Available English dialogue subtitles; timing and coverage need review |
| `public/media/<film>.resources.json` | Actual duration, output hash/size, source, credit, modifications and caption readiness |

The checked original downloads total 1,053,464,109 bytes (about 1 GB); allow several GB free for the archive, extracted source and browser copies. Final compressed sizes depend on the films. The script retains the originals so a failed conversion can be retried without downloading again. After checking playback, subtitles and credits, the cached originals can be removed manually if space is needed. None belong in Git. Generated posters, subtitles and resource records are also ignored until deliberately reviewed for inclusion.

Only an explicitly tagged English track is extracted from the Sintel archive. If none is present, the script warns rather than labeling another track as English. Tears of Steel uses the official English SRT. HTTP failures, unexpected download sizes and conversion failures stop the script. File sizes and generated hashes are useful reproducibility records; they are not publisher-provided integrity signatures.

## Sources and attribution

- Sintel: [official download directory](https://download.blender.org/durian/movies/), [project and CC BY 3.0 license](https://durian.blender.org/about/). Credit: © 2010 Blender Foundation / durian.blender.org.
- Tears of Steel: [official movie directory](https://download.blender.org/demo/movies/ToS/), [official subtitles](https://download.blender.org/demo/movies/ToS/subtitles/), [project and CC BY 3.0 license](https://mango.blender.org/about/). Credit: © 2012 Blender Foundation / mango.blender.org. Retain the credit scroll. The directory's `copyright.txt` concerns the standalone soundtrack and is not the movie-license reference.
- [CC BY 3.0 terms](https://creativecommons.org/licenses/by/3.0/). Browser conversion, audio downmix and poster extraction are modifications; keep their attribution with the assets. No logos are downloaded.
- Existing Big Buck Bunny credits: [media attribution](../public/media/ATTRIBUTION.md).

## Application status and next step

The application now has a title selector for Big Buck Bunny, Sintel and Tears of Steel. The new films have 26 and 76 source dialogue cues respectively, rendered from the precomputed datasets with a jumpable transcript. Each film has its own poster, credits and exact video hash. Dialogue wording is independent of sound preferences. Only Big Buck Bunny currently has a sourced non-speech track.

Title changes remount the viewing workspace, clearing old cues, local imports, previews and override state. Stored preferences remain available. Film selection is disabled after rehearsal starts, including after stopping, until reload. Matching reviewed non-speech JSON is still required before these new titles can support the sound-caption study. Source subtitle intervals are preserved and rendering is checked at each cue; that is not a full listening or accessibility review.

Phase 2 may add external hosting/discovery and metadata retrieval. No streaming service integration is part of this step.
