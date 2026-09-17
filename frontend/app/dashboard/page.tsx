"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import RequireAuth from "@/components/RequireAuth";
import { useAuth } from "@/lib/auth-context";
import { Button, Card } from "@/components/ui";
import * as api from "@/lib/api";

function DashboardContent() {
  const { user } = useAuth();
  const [resumeCount, setResumeCount] = useState<number | null>(null);
  const [jobCount, setJobCount] = useState<number | null>(null);

  useEffect(() => {
    api.getResumes().then((r) => setResumeCount(r.length)).catch(() => setResumeCount(0));
    api.getJobs().then((j) => setJobCount(j.length)).catch(() => setJobCount(0));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Welcome back{user ? `, ${user.full_name}` : ""}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Here&apos;s a quick overview of your account.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <p className="text-sm text-slate-500">Resumes uploaded</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">
            {resumeCount ?? "…"}
          </p>
          <Link href="/resumes">
            <Button variant="ghost" className="mt-4 px-0">
              Manage resumes →
            </Button>
          </Link>
        </Card>

        <Card>
          <p className="text-sm text-slate-500">Jobs available</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">
            {jobCount ?? "…"}
          </p>
          <Link href="/jobs">
            <Button variant="ghost" className="mt-4 px-0">
              Browse jobs →
            </Button>
          </Link>
        </Card>
      </div>

      <Card>
        <h2 className="text-base font-semibold text-slate-900">
          How it works
        </h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-600">
          <li>Upload a resume on the Resumes page.</li>
          <li>Browse or add a job posting on the Jobs page.</li>
          <li>
            Open a job and run career analysis against one of your resumes
            to see your match score, missing skills, and AI advice.
          </li>
        </ol>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}
