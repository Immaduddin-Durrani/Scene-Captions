# Vercel deployment

Requested 25 October 2026. Live: https://scene-captions.vercel.app, deployed and verified on 25 October 2026. The HCI Hobby workspace contains project `scene-captions` and public Blob store `scenecaptions-media` (IAD1). See [deployment evidence](verification/deployment-2026-10-25/README.md).

The app is a standard Next.js project. Import this repository with the Next.js framework preset, root directory `.`, install command `npm ci`, build command `npm run build` and the default output directory. Select Node.js 24.x in the project settings. Vercel documents [supported Node versions](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions) and [Git deployments](https://vercel.com/docs/deployments).

## Access

For assisted CLI deployment, create a short-lived token scoped to the intended workspace at [Account Settings → Tokens](https://vercel.com/account/tokens). Store it privately as `VERCEL_TOKEN` in local `.env`; never commit it, paste it in chat or add it to the deployed application's environment. Vercel supports [token authentication for CLI deployment](https://vercel.com/docs/cli). The alternative is importing the repository directly in the Vercel dashboard without sharing a token.

## Video hosting prerequisite

The three local MP4 files total approximately 1.1 GB and are excluded from Git. They must stream directly from a public HTTPS video/object-storage host with byte-range seeking support. Upload the prepared MP4s, preserving their timing and credits. The hosted Sintel derivative compresses the picture only; its audio, frame count and full duration are preserved, and frame timestamps differ by at most 0.334 ms. Do not substitute another edit merely because its title matches. Vercel Blob now hosts the videos directly. Total prepared upload size is 630,993,877 bytes, below the documented Hobby allowance of 1 GB; monthly Blob transfer allowance is 10 GB. No plan upgrade was enabled. These are allowances, not unlimited streaming: monitor usage in Vercel. See [pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing) and [media verification](verification/deployment-2026-10-25/media.json).

Set these **build-time** environment variables in Vercel before deploying:

| Variable | Local source to upload |
| --- | --- |
| `DEMO_VIDEO_URL` | `public/media/big-buck-bunny.mp4` |
| `SINTEL_VIDEO_URL` | `public/media/sintel.mp4` |
| `TEARS_OF_STEEL_VIDEO_URL` | `public/media/tears-of-steel.mp4` |

The URLs are public playback addresses, not credentials. Use stable public URLs rather than expiring signed links because the home page is statically generated. Changing a URL requires redeployment. Builds on Vercel fail with a named missing-variable error if any film URL is absent; this prevents publishing a catalogue whose videos point to absent local files. Local development retains its local media defaults. The three small posters are included in source.

Do not deploy local `.env`, NVIDIA/Gemini keys, model weights, analysis audio or diagnostic runtime caches. No model inference occurs during playback and no AI API key is needed. Vercel project metadata under `.vercel/` is ignored.

## Release verification

After deployment, check `/`, `/experiment`, `/api/ping`, all three posters, and each film's playback, audio, seeking and subtitle display. Check each external host's partial-content response and the actual decoded video duration. Verify title changes clear the prior track and the Big Buck Bunny controls still work. Sintel/Tears of Steel currently have dialogue only; deployment does not complete their missing sound-effect tracks. Participant session exports remain local; this deployment does not introduce centralized research-data storage.

## Updating this deployment

The initial release was deployed with Vercel CLI 65.2.0 from a clean staging copy. The user subsequently connected `hamzahisam/Scene-Captions` in Vercel; the local `origin` now points to that transferred repository. Future pushes use that Git integration. `.vercelignore` explicitly excludes credentials, media and local artifacts. The first CLI upload list unexpectedly included Git-ignored artifacts, so it was stopped before deployment; the successful release was assembled only from tracked app source and the intended deployment edits/posters. The earlier upload log did not list either generated credential file as uploaded. The successful staging inventory was checked for all current local private credential values before upload. No private credentials were copied into that source. HTTP checks confirm local secret/artifact paths return 404, which is a limited path check rather than an exhaustive security audit.

For future releases, use a clean source checkout with `.vercelignore`, the linked project, and the existing production media variables. Do not re-upload unchanged film files. The account token remains in the user-managed local `.env` only; temporary CLI-generated OIDC environment files were removed after verification. No AI API credentials were added to Vercel.
