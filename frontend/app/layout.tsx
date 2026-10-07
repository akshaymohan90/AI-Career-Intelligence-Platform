import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "SkillRadar",
  description:
    "Learn the skill that unlocks the most jobs. SkillRadar ranks the skills you're missing using live job-market data, then builds an ATS-ready CV.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <AuthProvider>
          <Navbar />
          <div className="mx-auto max-w-6xl px-6 py-8">{children}</div>
        </AuthProvider>
      </body>
    </html>
  );
}
