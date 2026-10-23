import Link from "next/link";
import { Icon } from "./icon";
export function Header({ page = "watch" }: { page?: "watch" | "experiment" }) {
  return <header className="site-header"><div className="header-inner"><Link href="/" className="brand" aria-label="SceneCaptions home"><span className="brand-mark"><Icon name="sound" size={24} /></span><span>scene<span className="brand-light">captions</span><span className="brand-period">.</span></span></Link><nav aria-label="Main navigation"><Link href="/" aria-current={page === "watch" ? "page" : undefined}>Watch</Link><Link href="/experiment" aria-current={page === "experiment" ? "page" : undefined}>Experimental plan</Link></nav><span className="phase-label">PHASE 01 <span>Research prototype</span></span></div></header>;
}
