import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Health OS",
  description: "Evidence-first Garmin health command center"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
