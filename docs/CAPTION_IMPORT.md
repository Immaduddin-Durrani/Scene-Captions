# Preparing your own video

1. Finish the exact video edit. Use browser-compatible MP4/H.264 with AAC audio. Keep rights and participant permissions clear.
2. Measure duration, for example `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 your-video.mp4` if ffmpeg is available.
3. Copy the downloadable template from `public/research/caption-template.json`. Set title, source URL, license, attribution, exact duration and stable video_id.
4. Annotate each non-speech cue with start_s, end_s, original_text, scene_context, a recurring sound_key, and a scene_load of quiet, balanced or dense. Scene load is manually tagged in this prototype; it is not inferred during playback.
5. Provide all nine grid entries `1-1` through `3-3` (detail-expressiveness). Supply `representations.plain`; optional onomatopoeic text falls back to descriptive when missing. Keep captions factual; review interpretive wording with DHH collaborators.
6. Sort cues by start time, use unique cue IDs and keep them within the declared video duration. Overlap is allowed for simultaneous sounds. The viewer will show all active cues, so avoid excessive overlapping text.
7. Set annotation_status to draft while reviewing. Set reviewed only after an actual sound/timing/wording review against the exact edit. A passing schema check is not caption review.
8. Validate: `npm run validate:captions -- path/to/your-captions.json`.
9. Open your video in the app, then choose its matching JSON. The app keeps files on your device. Duration mismatch suppresses captions, but matching duration alone does not prove that you selected the correct film/edit; verify manually.

The downloadable template is an example, not film annotations. The bundled Big Buck Bunny JSON now contains 87 licensed source intervals and source-anchored wording variants. Its annotation status remains draft pending full review. Failed model candidates with quality_gate=failed are still rejected on import. There are no viewing-time model calls. For a deployed study, commit reviewed JSON and serve the actual video directly from a rights-clear external host, never through Render's API.


## Source-first workflow

Use a licensed non-speech SRT when available, or retain a sound-event log while editing your own video. The sample importer (`npm run setup:captions`) is specific to the pinned Big Buck Bunny SRT and exact video hash; it is not a general automatic caption generator. Its editorial lexicon is in `data/authoring/`. Unknown labels fail instead of receiving invented fallback text. `scene_load_basis: "cue-density"` and `scene_load_method: "cue-density"` disclose density-based selection; omit that claim when you manually tag scenes. See [caption provenance](CAPTION_GENERATION_STATUS.md).
