export interface SrtCue { id: string; start_s: number; end_s: number; text: string }

/** Parse strict SubRip without silently dropping malformed or multiline cues. */
export function parseSrt(input: string): SrtCue[] {
  const blocks = input.replace(/^\uFEFF/, "").replace(/\r\n?/g, "\n").trim().split(/\n(?:[ \t]*\n)+/);
  const seen = new Set<string>();
  const timestamp = "(\\d{2,}):([0-5]\\d):([0-5]\\d),(\\d{3})";
  const timing = new RegExp(`^${timestamp} --> ${timestamp}$`);
  return blocks.map((block, index) => {
    const [id, line, ...lines] = block.split("\n").map((line) => line.trim());
    const match = line?.match(timing);
    if (!/^\d+$/.test(id) || seen.has(id) || !match || !lines.length || lines.some((line) => !line)) throw new Error(`Malformed SubRip block ${index + 1}.`);
    seen.add(id);
    const seconds = (offset: number) => Number(match[offset]) * 3600 + Number(match[offset + 1]) * 60 + Number(match[offset + 2]) + Number(match[offset + 3]) / 1000;
    const start_s = seconds(1), end_s = seconds(5);
    if (end_s <= start_s) throw new Error(`Invalid cue interval in block ${index + 1}.`);
    return { id, start_s, end_s, text: lines.join("\n") };
  });
}
