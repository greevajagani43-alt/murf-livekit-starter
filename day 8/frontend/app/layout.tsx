import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Voice Agent Performance Dashboard — Day 8",
  description: "Real-time call performance dashboard for Murf AI 10 Days of Voice Agents challenge (Local Commerce Track).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <style>{`
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b0f19;
            color: #f3f4f6;
            min-height: 100vh;
          }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
