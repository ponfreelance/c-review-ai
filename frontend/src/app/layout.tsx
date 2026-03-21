import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "c-review-ai",
  description: "C言語コードの危険箇所を検出するレビューAI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-gray-50 text-gray-900 min-h-screen">{children}</body>
    </html>
  );
}
