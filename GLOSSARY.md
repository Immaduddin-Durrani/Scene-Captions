# SceneCaptions

Language for viewer-controlled non-speech captions and the planned study.

## Language

**Sound cue**: A time-bounded non-speech sound event represented by one or more captions. Simultaneous sounds may have overlapping cues.

**Original caption**: The fixed source text attached to a sound cue, used as the reference for comparison and viewer override. It may come from a caption contributor rather than the film creator; an original caption is not automatically a reviewed or accurate caption.

**Caption variant**: A prewritten alternative for one sound cue at a chosen detail and expressiveness level.

**Caption profile**: The viewer's saved preferences for caption content and readability.

**Caption detail limit**: The greatest level of descriptive detail the viewer permits. Adaptation may reduce detail but must not exceed this limit.
_Avoid_: Treating the selected detail as an unrestricted starting point.

**Scene-aware adaptation**: Adjusting caption detail using information about the scene while respecting the viewer's profile and detail limit. Its usefulness is a research question, not an established benefit.

**Cue-density adaptation**: Adjusting caption detail according to how closely sound cues occur together. Cue density is distinct from visual complexity, sound loudness and the importance of off-screen sounds.
_Avoid_: Calling cue density measured scene complexity or cognitive load.

**Sound key**: A stable label grouping recurring sound types so their wording can be reviewed for consistency.

**Baseline condition**: Viewing with the same fixed original non-speech captions throughout.

**Personalized condition**: Viewing with a saved caption profile, optional scene adaptation, preview and original-caption override.

**Preview**: A candidate caption shown before preferences are applied to the viewing experience.

**On-video preview**: A temporary display of draft caption preferences in the player that returns to the saved preferences without applying the draft. Original-caption override remains authoritative.

**Sound detection**: Identifying and locating sound events in a recording. This is distinct from rewriting an existing sound caption.

**Caption variant generation**: Producing alternative wording for an already identified sound cue while preserving its supported meaning.

**Audio corroboration**: Checking a source caption's sound description and timing against the corresponding recording. A model's agreement is supporting evidence to review, not proof that the caption is correct.

**Rehearsal**: An opt-in technical trial of the app and its export flow. It is not an approved participant study or research evidence.

**Human-review receipt**: A record binding a reviewer’s stated listening, timing, wording, simultaneous-event, reading-time and per-variant decisions to exact video/caption/cue content. Completeness checking is not proof of sound correctness, independent review, participant approval or automatic installation. A partial packet cannot approve a whole track.
