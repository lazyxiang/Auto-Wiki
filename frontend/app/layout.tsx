import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoWiki",
  description: "Self-hosted documentation generator",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-slate-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
