"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/resumes", label: "Resumes" },
  { href: "/jobs", label: "Jobs" },
];

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold text-slate-900">
          AI Career Intelligence
        </Link>

        {!loading && user && (
          <nav className="hidden gap-6 sm:flex">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium ${
                  pathname?.startsWith(link.href)
                    ? "text-brand-600"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-3">
          {!loading && user ? (
            <>
              <span className="hidden text-sm text-slate-500 sm:inline">
                {user.full_name}
              </span>
              <Button
                variant="secondary"
                onClick={() => {
                  logout();
                  router.push("/");
                }}
              >
                Sign out
              </Button>
            </>
          ) : (
            !loading && (
              <>
                <Link href="/login">
                  <Button variant="ghost">Sign in</Button>
                </Link>
                <Link href="/register">
                  <Button>Get started</Button>
                </Link>
              </>
            )
          )}
        </div>
      </div>
    </header>
  );
}
