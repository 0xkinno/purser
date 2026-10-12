import "./globals.css";
import type { Metadata } from "next";

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
    <html lang="en">
      <body className="antialiased selection:bg-[--color-signal] selection:text-white">
        {children}
      </body>
    </html>
  );
}
