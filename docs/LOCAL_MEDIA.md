# Local demo media

The user runs all video downloads. Agents may prepare code and commands but must not fetch video files themselves. Nothing downloads on app startup or while watching.

Keep the existing Big Buck Bunny sample (9:56) and optionally add Sintel (about 15 minutes, animation) and Tears of Steel (about 12 minutes, live action/science fiction). The preparation script measures exact durations and rejects files longer than 30 minutes without trimming credits. These are catalogue candidates, not yet additional caption-ready demos.

## Run in PowerShell

Requires `curl.exe`, `ffmpeg` and `ffprobe` on PATH. The script checks these before downloading. From the project folder:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\media\prepare-library.ps1 -Film all
```

`Bypass` applies only to that PowerShell process; it does not change your saved execution policy. To download one film at a time, replace `all` with `sintel` or `tears-of-steel`.

If the existing Big Buck Bunny file is absent, the separate user-run command is `npm run setup:demo`. The library script does not replace that verified sample.

The user successfully ran the library script on 24 October 2026. Local checks confirmed both MP4s contain H.264 video and AAC audio, matching resource-record hashes, posters and English VTT files. Sintel is 1280x544, 888.032 seconds; Tears of Steel is 1280x534, 734.167 seconds. These are the widescreen picture dimensions of their 720p releases. See [local verification](verification/fixes-2026-10-24/reports/local-media.json). Full listening and subtitle-timing review remain pending. The agent did not download films.

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

The current application still has one built-in, caption-ready sample. This script prepares additional files; it does not add a title selector or import VTT into the player. The generated resource records are preparation metadata, not a caption dataset or an automatically loaded application catalogue.

Before offering these titles as full demos, implement separate title selection, dialogue subtitle playback and matching reviewed non-speech caption JSON. Always clear the previous title's captions when switching films; never attach Big Buck Bunny cues to another movie. Preserve audio, viewer controls and correct per-film credits. Review subtitle timing against the exact compressed copy. Keep the study stimulus fixed separately from browsing variety.

Phase 2 may add external hosting/discovery and metadata retrieval. No streaming service integration is part of this step.
