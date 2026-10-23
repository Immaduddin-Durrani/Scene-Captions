# SceneCaptions design foundation

The player is the primary surface: a quiet, readable viewing workspace for DHH viewers, not a marketing landing page. A warm-neutral canvas, muted green controls and a dark video frame keep attention on the story and captions. Serif headings add character without changing the highly legible caption and control text.

The design workflow considered a cinema-wide player with controls below and a player with a right-hand settings panel. The latter gives immediate preview and explicit application of preferences while preserving the video's space; on small screens it stacks beneath the player. Controls and longer content remain left-aligned; caption text is centered inside an opaque high-contrast backing.

Reuse the CSS variables in src/app/globals.css for color, borders, type and surfaces. Keep viewer-facing language about sounds and preferences. Distinguish the fixed baseline, saved profile and unapplied preview. Never redesign these patterns merely to add a feature.

Caption readability, visible keyboard focus, original-caption override and explanatory disclosure outrank decorative effects. Playback controls are always visible. Readability controls exist in both conditions. Sound cues are also available as a navigable text timeline. No animation is needed to understand the interface; reduced-motion preferences disable transitions and smooth scrolling.

Demo notes must remain visible until verified study material replaces the illustrative cues. Rehearsal recording stays opt-in, local and separate from actual approved study consent.
