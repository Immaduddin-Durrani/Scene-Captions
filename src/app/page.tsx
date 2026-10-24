import bunny from "../../data/captions/big-buck-bunny.json";
import sintel from "../../data/captions/sintel.json";
import tears from "../../data/captions/tears-of-steel.json";
import { videoSchema } from "@/lib/captions";
import { Header } from "@/components/header";
import { ScreeningRoom } from "@/components/screening-room";
export default function Home() {
  const films = [
    { data: videoSchema.parse(bunny), source: process.env.DEMO_VIDEO_URL || "/media/big-buck-bunny.mp4", poster: "/media/bunny-poster.jpg", credit: "Blender Foundation · 2008" },
    { data: videoSchema.parse(sintel), source: "/media/sintel.mp4", poster: "/media/sintel-poster.jpg", credit: "Blender Foundation · 2010" },
    { data: videoSchema.parse(tears), source: "/media/tears-of-steel.mp4", poster: "/media/tears-of-steel-poster.jpg", credit: "Blender Foundation · 2012" },
  ];
  return <><Header /><ScreeningRoom films={films} /></>;
}
