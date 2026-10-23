# Current caption gate checks

2026-10-23, local manual engineering verification.

- Type checking, eight unit tests, caption schema validation and optimized production build passed.
- Browser checks passed for film playback, no captions at 1:18, empty withdrawn track, unavailable-track notice, disabled caption controls/rehearsal, failed-candidate import rejection, restoring the empty track, local synthetic-fixture import and original selection, mobile width, and the experimental plan route. Synthetic fixture checks test interface mechanics only.
- Browser reported zero errors and one Next.js smooth-scroll configuration warning. Earlier screenshots and 32-cue checks are historical. Current screenshots are caption-gate-desktop.png and caption-gate-mobile.png.
- Full-film generation --install exits before network access due to the saved failed gate.
- Local .env is gitignored; private comparison found no key in the 22 built browser JavaScript assets or saved verification files.
- Silent control source verified as all-zero PCM; metadata/hash in nim-silence-control-source.json. Its model responses reported sounds. These results do not validate sound-caption accuracy.

No skills, agents or external workers were activated for this follow-up.
