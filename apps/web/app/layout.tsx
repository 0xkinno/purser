import "./globals.css";
import type { Metadata } from "next";
import { Instrument_Serif } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "Purser · Autonomous Refund Operations",
  description: "Purser clears your refund queue overnight, and if it crashes at ticket 73, it still knows exactly who was paid. Once.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${instrumentSerif.variable} ${GeistSans.variable} ${GeistMono.variable}`}
    >
      <body className="antialiased selection:bg-signal selection:text-white bg-paper text-ink">
        {children}
      </body>
    </html>
  );
}
