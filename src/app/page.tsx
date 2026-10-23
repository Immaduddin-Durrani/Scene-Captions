import data from "../../data/captions/big-buck-bunny.json";
import { videoSchema } from "@/lib/captions";
import { Header } from "@/components/header";
import { Workspace } from "@/components/workspace";
export default function Home() {
  return <><Header /><Workspace initialVideo={videoSchema.parse(data)} demoSource={process.env.DEMO_VIDEO_URL || "/media/big-buck-bunny.mp4"} /></>;
}
