import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "SceneCaptions — Stay in the story", description: "A research prototype for viewer-controlled, personalized non-speech captions." };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><a className="skip-link" href="#main">Skip to main content</a>{children}</body></html>;
}
