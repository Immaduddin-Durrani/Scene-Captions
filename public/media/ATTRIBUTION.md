# Big Buck Bunny demonstration asset

© 2008 Blender Foundation / peach.blender.org.

- Film and license information: https://peach.blender.org/about/
- License: Creative Commons Attribution 3.0, https://creativecommons.org/licenses/by/3.0/
- Official download: https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_640x360.m4v.zip
- Original movie bytes extracted from the official ZIP and stored with an `.mp4` extension; video/audio are unchanged.
- `bunny-poster.jpg` is a still extracted at 65 seconds using ffmpeg; a derivative under the same attribution requirement.
- Sound captions: Demuxed / big-buck-captions contributors, CC BY 3.0; https://github.com/demuxed/big-buck-captions at e490383ca58f53507cfa18a64e1324f28d77c65a. Source text/timestamps preserved. Wording variants and cue-density metadata added by SceneCaptions. See docs/CAPTION_GENERATION_STATUS.md and data/sources/big-buck-captions/README.md for the source license.
- This short film is temporary demo material. The team will create the actual 20–30 minute study video.

The official about page was checked during setup; it identifies the project's published data as CC BY 3.0 and excludes trademarks/logos. No Blender logo is used in the app.

## Optional catalogue assets

The local library includes these films, prepared from the official sources using `scripts/media/prepare-library.py`. Large film files remain outside Git.

- Sintel: © 2010 Blender Foundation / durian.blender.org. [Project license](https://durian.blender.org/about/), CC BY 3.0.
- Tears of Steel: © 2012 Blender Foundation / mango.blender.org. [Project license](https://mango.blender.org/about/), CC BY 3.0. Retain the complete credit scroll.
- Preparation changes: H.264 video preserving original 720p-release dimensions, stereo AAC sound, extracted poster and available subtitles converted to WebVTT. Full film duration is retained. Generated per-film `.resources.json` records the exact file hash, source and modifications.

See [local media preparation](../../docs/LOCAL_MEDIA.md) for official sources and the outstanding subtitle/sound-caption review. Both films are integrated into the title selector with official dialogue. Full sound-effect tracks remain unfinished.

For Vercel playback, Sintel has an additional H.264 CRF25 picture compression pass, with unchanged AAC audio, full credits and duration. Frame presentation timestamps differ from the local source by at most 0.334 ms because of the MP4 time base. Big Buck Bunny and Tears of Steel are uploaded without modification. See the deployment verification record for hashes and hosting URLs.
