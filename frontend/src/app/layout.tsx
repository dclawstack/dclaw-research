import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DClaw Research",
  description: "Deep Research Agent",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <nav className="border-b px-6 py-3 flex items-center justify-between">
          <div className="font-bold text-lg tracking-tight">DClaw Research</div>
          <div className="flex gap-4 text-sm">
            <a href="/" className="hover:underline">New Research</a>
            <a href="/library" className="hover:underline">Library</a>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}
