import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "AI Career Intelligence",
  description:
    "Upload your resume, match it against job postings, and get AI-powered skill-gap analysis and career advice.",
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
