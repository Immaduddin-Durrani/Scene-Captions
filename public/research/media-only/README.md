# Experimental media-only subtitles

NVIDIA generated these tracks from film audio without fetched subtitles,
reference timestamps, plot or supplied scene descriptions. They are unverified
and known sound-recognition tests failed. Sound display times are 15-second
analysis windows, not precise event boundaries. Dialogue uses ASR word offsets;
words and times can be wrong. Full-film processing does not mean full event recall.

| Film | Sound windows | Dialogue cues |
| --- | ---: | ---: |
| Big Buck Bunny | 40 | 0 |
| Sintel | 59 | 71 |
| Tears of Steel | 49 | 68 |

Each film has JSON and detail-1/2/3 SRT files. Detail changes acoustic wording;
expression stays fixed. The webapp offers an explicit media-only subtitle button
and a separate option to restore existing captions. No inference runs in playback.

Films © Blender Foundation, 2008/2010/2012, CC BY 3.0. Caption wording generated
by SceneCaptions; not creator-authored or human-reviewed.
