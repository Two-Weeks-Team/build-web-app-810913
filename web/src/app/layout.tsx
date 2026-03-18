import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import "@/app/globals.css";

const heading = Fraunces({ subsets: ["latin"], weight: ["600", "700"] });
const body = Source_Sans_3({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export const metadata: Metadata = {
  title: "Build Web App — Product Planning Studio",
  description: "Turn rough product ideas into structured, saved planning briefs in one pass."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${heading.className} ${body.className} bg-background text-foreground`}>{children}</body>
    </html>
  );
}
