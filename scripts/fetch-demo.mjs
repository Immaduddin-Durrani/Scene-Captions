import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
const target = "public/media/big-buck-bunny.mp4";
if (existsSync(target)) { console.log("Demo video already present."); process.exit(0); }
await mkdir("public/media", { recursive: true });
const source = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_640x360.m4v.zip";
// This script only downloads the licensed demo; no API keys or model calls.
const cache = process.env.SCENECAPTIONS_MEDIA_CACHE || ".media-cache";
await mkdir(cache, { recursive: true });
const zip = `${cache}/bunny.zip`;
if (!existsSync(zip)) {
  const response = await fetch(source);
  if (!response.ok) throw new Error(`Download failed (${response.status})`);
  await writeFile(zip, Buffer.from(await response.arrayBuffer()));
}
const entries = spawnSync("unzip", ["-Z1", zip], { encoding: "utf8" });
if (entries.status !== 0) throw new Error("Install unzip to extract the demo video.");
const entry = entries.stdout.split("\n").find((line) => line.endsWith(".m4v"));
if (!entry) throw new Error("The official archive did not contain an M4V video.");
const extraction = spawnSync("unzip", ["-p", zip, entry], { maxBuffer: 160 * 1024 * 1024 });
if (extraction.status !== 0) throw new Error("Video extraction failed.");
await writeFile(target, extraction.stdout);
console.log("Downloaded Big Buck Bunny; © 2008 Blender Foundation, CC BY 3.0. See public/media/ATTRIBUTION.md.");
