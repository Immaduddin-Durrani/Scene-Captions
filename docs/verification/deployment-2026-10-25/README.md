# Vercel deployment — 25 October 2026

Live application: https://scene-captions.vercel.app
Experimental plan: https://scene-captions.vercel.app/experiment

Project: `scene-captions`, HCI Hobby workspace. Deployment: `dpl_HjDjLktKw92y1gswMir4ryomiu74`, production, READY. Node.js 24.x; Next.js production build succeeded on Vercel. Videos use the public `scenecaptions-media` Blob store in IAD1. No paid plan upgrade, model inference, agents, telemetry activation or Git auto-deployment was enabled.

## Verification

- Local production build and 18 existing tests passed. Manual configuration checks passed for local fallback, missing Vercel variables, HTTPS validation and hosted URL overrides.
- [Browser checks](browser.json): actual Chrome playback advancement, media seek/decode, and a representative source caption for each film; 596.461678 / 888.032 / 734.166667 second durations. Big Buck Bunny uses the apple-thud sound cue, the other films use official dialogue. No browser page errors. Experimental-plan heading and mobile horizontal-overflow check passed.
- [HTTP checks](http.json): home, experimental plan, API ping and all posters return 200; `.env` and the generated credential-artifact path return 404. No user authentication was supplied to these production-URL checks.
- [Hosted video checks](remote-media.json): all three URLs return 206, expected byte counts, MP4 content type, CORS and matching initial bytes. These are transport checks, not exhaustive remote-file hash verification.
- [Sintel derivative verification](media.json): full duration, frame count and compressed AAC audio packet hash retained. The maximum frame presentation-time difference is 0.000333 seconds from MP4 time-base quantization; picture quality changes through H.264 CRF25 compression. All credits retained. Total stored video bytes: 630,993,877.
- [Build output](build.txt), [deployment status](deployment.json) and [source inventory](source-manifest.json) record this release. Deployment used clean staging after stopping an initial CLI upload that included ignored artifacts. No credentials were present in the successful staged source. Current local credential values were checked before staging; this is not an exhaustive historical secret audit.

## Limits

Sintel and Tears of Steel still have dialogue only; full sound-effect tracks remain unfinished. Big Buck Bunny retains its 87 licensed sound intervals. These deployment checks do not constitute complete listening or participant-study validation. The 1 GB Blob storage and 10 GB monthly transfer allowances are finite; monitor usage in Vercel. No central participant-data store was added. Existing graph/map evidence is stale for the media-source configuration change; no mapping/audit skill was invoked.

The initial CLI release uses the staged source inventory above. The user subsequently connected `hamzahisam/Scene-Captions` in Vercel, and local `origin` now points to that transferred repository. This follow-up records the deployment edits and evidence in Git.
