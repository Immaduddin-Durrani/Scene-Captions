import bunny from "../../data/captions/big-buck-bunny.json";
import sintel from "../../data/captions/sintel.json";
import tears from "../../data/captions/tears-of-steel.json";
import generatedBunny from "../../data/experimental-captions/big-buck-bunny.json";
import generatedSintel from "../../data/experimental-captions/sintel.json";
import generatedTears from "../../data/experimental-captions/tears-of-steel.json";
import { videoSchema } from "@/lib/captions";
import { experimentalTrackFor } from "@/lib/experimental-captions";
import { Header } from "@/components/header";
import { ScreeningRoom } from "@/components/screening-room";

function mediaSource(variable: string, localPath: string) {
  const configured = process.env[variable]?.trim();
  if (configured) {
    const url = new URL(configured);
    if (url.protocol !== "https:") throw new Error(`${variable} must be a public HTTPS video URL.`);
    return url.href;
  }
  if (process.env.VERCEL === "1") {
    throw new Error(`Set ${variable} to the hosted, caption-matched MP4 before deploying. Local video files are excluded from Git.`);
  }
  return localPath;
}

export default function Home() {
  const films = [
    { data: videoSchema.parse(bunny), experimentalData: experimentalTrackFor(videoSchema.parse(bunny), generatedBunny), source: mediaSource("DEMO_VIDEO_URL", "/media/big-buck-bunny.mp4"), poster: "/media/bunny-poster.jpg", credit: "Blender Foundation · 2008" },
    { data: videoSchema.parse(sintel), experimentalData: experimentalTrackFor(videoSchema.parse(sintel), generatedSintel), source: mediaSource("SINTEL_VIDEO_URL", "/media/sintel.mp4"), poster: "/media/sintel-poster.jpg", credit: "Blender Foundation · 2010" },
    { data: videoSchema.parse(tears), experimentalData: experimentalTrackFor(videoSchema.parse(tears), generatedTears), source: mediaSource("TEARS_OF_STEEL_VIDEO_URL", "/media/tears-of-steel.mp4"), poster: "/media/tears-of-steel-poster.jpg", credit: "Blender Foundation · 2012" },
  ];
  return <><Header /><ScreeningRoom films={films} /></>;
}
