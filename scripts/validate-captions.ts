import { readFileSync, readdirSync } from "node:fs";
import { videoSchema } from "../src/lib/captions.ts";
const files = process.argv.slice(2);
for (const file of files.length ? files : readdirSync("data/captions").filter((f) => f.endsWith(".json")).map((f) => `data/captions/${f}`)) {
  const video = videoSchema.parse(JSON.parse(readFileSync(file, "utf8")));
  console.log(`${file}: ${video.cues.length} sound cues, 9 variants each; ${video.dialogue?.length || 0} dialogue cues; ${video.annotation_status}`);
}
