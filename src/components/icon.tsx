import type { CSSProperties } from "react";
const paths = {
  play: "m9 5 11 7-11 7Z", pause: "M8 5v14M16 5v14", volume: "m11 5-6 4H2v6h3l6 4ZM15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14", mute: "m11 5-6 4H2v6h3l6 4ZM17 9l5 6M22 9l-5 6", expand: "M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5", settings: "M4 7h16M4 17h16M9 3v8m6 2v8", arrow: "M5 12h14m-5-5 5 5-5 5", back: "M19 12H5m5-5-5 5 5 5", check: "m5 12 4 4L19 6", chevron: "m9 5 7 7-7 7", book: "M12 5C8 2 3 3 2 4v16c4-2 7-2 10 0 3-2 6-2 10 0V4c-3-1-6-2-10 1Zm0 0v15", sound: "M3 10v4m4-7v10m5-14v18m5-14v10m4-7v4", info: "M12 11v6m0-10v.1M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0", download: "M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4", folder: "M3 7V4h6l2 3h10v13H3Z", film: "M3 3h18v18H3ZM7 3v18m10-18v18M3 8h4m-4 8h4M17 8h4m-4 8h4", leaf: "M5 20C1 7 12 3 21 3c0 9-3 18-12 16M5 20 16 9", close: "m6 6 12 12M6 18 18 6", reset: "M3 10a9 9 0 1 1 2 9M3 3v7h7", clock: "M12 8v5l3 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0", shield: "m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6ZM8 12l3 3 5-6",
};
export type IconName = keyof typeof paths;
export function Icon({ name, size = 20, style }: { name: IconName; size?: number; style?: CSSProperties }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={style}><path d={paths[name]} /></svg>;
}
