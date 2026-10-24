"use client";
import { DEFAULT_PROFILE } from "@/lib/captions";
import type { CaptionProfile } from "@/lib/captions";
import { Icon } from "./icon";

export function CaptionReadability({ profile, onApply }: { profile: CaptionProfile; onApply: (profile: CaptionProfile) => void }) {
  return (
    <details className="readability"><summary>Caption readability</summary><label htmlFor="size">Text size</label><select id="size" value={profile.size} onChange={(e) => onApply({ ...profile, size: e.target.value as CaptionProfile["size"] })}><option value="standard">Standard</option><option value="large">Large</option><option value="extra-large">Extra large</option></select><label htmlFor="position">Position on the video</label><select id="position" value={profile.position} onChange={(e) => onApply({ ...profile, position: e.target.value as CaptionProfile["position"] })}><option value="bottom">Bottom</option><option value="top">Top</option></select><button className="text-button" onClick={() => onApply({ ...profile, size: DEFAULT_PROFILE.size, position: DEFAULT_PROFILE.position })}><Icon name="reset" size={14} />Reset readability</button></details>
  );
}
