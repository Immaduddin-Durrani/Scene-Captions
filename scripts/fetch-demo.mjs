import { mkdir, writeFile, readFile, rename, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { extractDemoArchive } from "./media/archive.mjs";
const target = "public/media/big-buck-bunny.mp4";
const expected = "738e2f999860553d056dd79c952f58f63cbb73892a57c72342ce9e5330d9d2d7";
const matches = async (file) => createHash("sha256").update(await readFile(file)).digest("hex") === expected;
if (existsSync(target)) {
  if (!await matches(target)) throw new Error("Existing sample video does not match the expected edit. Inspect it before replacing it.");
  console.log("Demo video present; exact edit verified."); process.exit(0);
}
await mkdir("public/media", { recursive: true });
const source = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_640x360.m4v.zip";
// This script only downloads the licensed demo; no API keys or model calls.
const cache = process.env.SCENECAPTIONS_MEDIA_CACHE || ".media-cache";
await mkdir(cache, { recursive: true });
const zip = `${cache}/bunny.zip`;
if (!existsSync(zip)) {
  const response = await fetch(source);
  if (!response.ok) throw new Error(`Download failed (${response.status})`);
  await writeFile(`${zip}.download`, Buffer.from(await response.arrayBuffer()));
  await rename(`${zip}.download`, zip);
}
const pending = `${target}.pending`;
try {
  extractDemoArchive(zip, pending);
  if (!await matches(pending)) throw new Error("Downloaded movie hash does not match the captioned edit. Nothing installed.");
  await rename(pending, target);
} finally { await rm(pending, { force: true }); }
console.log("Downloaded Big Buck Bunny; © 2008 Blender Foundation, CC BY 3.0. See public/media/ATTRIBUTION.md.");
