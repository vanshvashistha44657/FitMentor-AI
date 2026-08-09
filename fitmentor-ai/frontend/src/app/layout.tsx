import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "FitMentor AI — Your Personal AI Trainer, Nutritionist, Coach",
  description:
    "AI-powered fitness coaching that builds workout plans, diet plans, and coaches you live — personalized entirely to you.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
