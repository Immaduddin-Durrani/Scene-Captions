import { spawnSync } from "node:child_process";
import { openSync, closeSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

export function extractDemoArchive(archive, output) {
  if (process.platform === "win32") {
    const result = spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", fileURLToPath(new URL("./extract-demo.ps1", import.meta.url)), "-ArchivePath", resolve(archive), "-OutputPath", resolve(output)], { encoding: "utf8", windowsHide: true });
    if (result.status !== 0) throw new Error("Windows movie extraction failed. Check that the archive is complete and PowerShell is available.");
    return;
  }
  const listing = spawnSync("unzip", ["-Z1", archive], { encoding: "utf8" });
  if (listing.status !== 0) throw new Error("Install unzip to extract the demo video.");
  const movies = listing.stdout.split(/\r?\n/).filter((name) => name.endsWith(".m4v"));
  if (movies.length !== 1) throw new Error("Expected exactly one movie in the official archive.");
  const descriptor = openSync(output, "w");
  try {
    const extraction = spawnSync("unzip", ["-p", archive, movies[0]], { stdio: ["ignore", descriptor, "pipe"] });
    if (extraction.status !== 0) throw new Error("Movie extraction failed.");
  } finally { closeSync(descriptor); }
}
