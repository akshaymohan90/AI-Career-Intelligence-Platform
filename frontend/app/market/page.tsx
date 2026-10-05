"use client";

import { FormEvent, useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { Alert, Badge, Button, Card, Input, Label, Spinner } from "@/components/ui";
import * as api from "@/lib/api";
import type { MarketScan, Resume } from "@/lib/api";
import { ApiError } from "@/lib/api";

function Stat({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

function MarketContent() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState<number | null>(null);
  const [role, setRole] = useState("backend engineer");
  const [location, setLocation] = useState("Bangalore, Karnataka, India");
  const [scan, setScan] = useState<MarketScan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getResumes().then((list) => {
      setResumes(list);
      if (list.length > 0) setResumeId(list[0].id);
    });
  }, []);

  async function handleScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resumeId) return;
    setLoading(true);
    setError(null);
    setScan(null);
    try {
      setScan(await api.runMarketScan({ role, location, resume_id: resumeId }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Market scan failed.");
    } finally {
      setLoading(false);
    }
  }

  const maxJobsPerWeek = scan?.recommendations[0]?.jobs_per_week || 1;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Live market scan</h1>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Every posting below is live from Google Jobs via SerpApi. We rank the skills
          you&apos;re missing by how many real jobs each one unlocks per week of learning,
          and every number links back to the postings that produced it.
        </p>
      </div>

      <Card>
        <form onSubmit={handleScan} className="grid gap-4 sm:grid-cols-4">
          <div>
            <Label>Target role</Label>
            <Input value={role} onChange={(e) => setRole(e.target.value)} required />
          </div>
          <div>
            <Label>Location</Label>
            <Input value={location} onChange={(e) => setLocation(e.target.value)} required />
          </div>
          <div>
            <Label>Your resume</Label>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              value={resumeId ?? ""}
              onChange={(e) => setResumeId(Number(e.target.value))}
              disabled={resumes.length === 0}
            >
              {resumes.length === 0 && <option>Upload a resume first</option>}
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.original_filename}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button type="submit" disabled={loading || !resumeId} className="w-full">
              {loading ? "Scanning live market…" : "Run live market scan"}
            </Button>
          </div>
        </form>
        {error && <Alert className="mt-4">{error}</Alert>}
      </Card>

      {loading && (
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <Spinner />
          Querying Google Jobs through SerpApi…
        </div>
      )}

      {scan && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Live postings scanned" value={scan.postings_scanned} hint={`${scan.postings_analyzed} with readable requirements`} />
            <Stat label="Already qualified for" value={scan.already_qualified} hint="postings you fully meet today" />
            <Stat label="Reachable with a few skills" value={scan.near_matches} hint="you cover 25%+ of the requirements" />
            <Stat label="SerpApi usage" value={`${scan.serpapi_live_calls} live · ${scan.serpapi_cache_hits} cached`} hint="cached results cost no credits" />
          </div>

          <Card>
            <h2 className="text-base font-semibold text-slate-900">Agent trace</h2>
            <ol className="mt-4 space-y-3">
              {scan.agent_trace.map((step, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-semibold text-white">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">{step.step}</p>
                    <p className="text-slate-600">{step.detail}</p>
                  </div>
                  <span className="text-xs text-slate-400">{step.ms} ms</span>
                </li>
              ))}
            </ol>
          </Card>

          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Learn this next</h2>
              <p className="text-sm text-slate-500">
                Ranked by jobs unlocked per week of learning. Click any evidence link to verify it.
              </p>
            </div>

            {scan.recommendations.length === 0 && (
              <Alert tone="warning">
                No skill gaps found in this market sample. Try a broader role or location.
              </Alert>
            )}

            {scan.recommendations.map((rec, index) => (
              <Card key={rec.skill}>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <span className="text-3xl font-bold text-slate-300">#{index + 1}</span>
                    <div>
                      <p className="flex items-center gap-2 text-lg font-semibold text-slate-900">
                        {rec.skill}
                        <Badge
                          tone={
                            rec.trend_direction === "rising"
                              ? "success"
                              : rec.trend_direction === "falling"
                                ? "danger"
                                : "neutral"
                          }
                        >
                          {rec.trend_direction === "unknown" ? "trend n/a" : rec.trend_direction}
                        </Badge>
                      </p>
                      <p className="text-sm text-slate-500">
                        Unlocks {rec.jobs_unlocked.toFixed(2)} postings · about {rec.estimated_weeks} weeks to learn
                      </p>
                    </div>
                  </div>
                  <div className="min-w-[180px] text-right">
                    <p className="text-2xl font-semibold text-brand-600">{rec.jobs_per_week.toFixed(3)}</p>
                    <p className="text-xs text-slate-500">jobs unlocked per week</p>
                    <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-brand-600"
                        style={{ width: `${Math.round((rec.jobs_per_week / maxJobsPerWeek) * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>

                {rec.evidence.length > 0 && (
                  <div className="mt-4 border-t border-slate-100 pt-4">
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Evidence</p>
                    <ul className="space-y-2">
                      {rec.evidence.map((ev, i) => (
                        <li key={i} className="flex flex-wrap items-center justify-between gap-2 text-sm">
                          <span className="text-slate-700">
                            {ev.title} · <span className="text-slate-500">{ev.company}</span>
                          </span>
                          <span className="flex items-center gap-2">
                            <Badge>{ev.gaps_in_posting} gap{ev.gaps_in_posting === 1 ? "" : "s"} in this posting</Badge>
                            {ev.link && (
                              <a href={ev.link} target="_blank" rel="noreferrer" className="text-brand-600 underline">
                                View posting
                              </a>
                            )}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function MarketPage() {
  return (
    <RequireAuth>
      <MarketContent />
    </RequireAuth>
  );
}
