"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { Alert, Badge, Button, Card, Input, Label, Spinner, Textarea } from "@/components/ui";
import * as api from "@/lib/api";
import type { CVTailorResult, JobPosting, Resume } from "@/lib/api";
import { ApiError } from "@/lib/api";

const MIN_JD_CHARS = 50;

function errorMessage(err: unknown, fallback: string) {
  return err instanceof ApiError ? err.message : fallback;
}

function CVPreview({ cv }: { cv: CVTailorResult["cv"] }) {
  const contact = [cv.email, cv.phone, cv.location, ...cv.links].filter(Boolean).join(" | ");
  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-800">
      <div>
        <p className="text-xl font-bold text-slate-900">{cv.full_name}</p>
        {cv.headline && <p className="text-slate-600">{cv.headline}</p>}
        {contact && <p className="text-xs text-slate-500">{contact}</p>}
      </div>
      {cv.summary && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Summary</p>
          <p className="mt-2">{cv.summary}</p>
        </section>
      )}
      {cv.skills.length > 0 && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Skills</p>
          <p className="mt-2">{cv.skills.join(", ")}</p>
        </section>
      )}
      {cv.experience.length > 0 && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Experience</p>
          {cv.experience.map((job, i) => (
            <div key={i} className="mt-3">
              <p className="font-semibold">{[job.role, job.company].filter(Boolean).join(" - ")}</p>
              <p className="text-xs text-slate-500">
                {[[job.start, job.end].filter(Boolean).join(" - "), job.location].filter(Boolean).join(" | ")}
              </p>
              <ul className="mt-1 list-disc space-y-1 pl-5">
                {job.bullets.map((b, j) => <li key={j}>{b}</li>)}
              </ul>
            </div>
          ))}
        </section>
      )}
      {cv.projects.length > 0 && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Projects</p>
          {cv.projects.map((p, i) => (
            <div key={i} className="mt-3">
              {p.name && <p className="font-semibold">{p.name}</p>}
              <ul className="mt-1 list-disc space-y-1 pl-5">
                {p.bullets.map((b, j) => <li key={j}>{b}</li>)}
              </ul>
            </div>
          ))}
        </section>
      )}
      {cv.education.length > 0 && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Education</p>
          {cv.education.map((e, i) => (
            <div key={i} className="mt-2">
              <p className="font-semibold">{[e.degree, e.institution].filter(Boolean).join(" - ")}</p>
              <p className="text-xs text-slate-500">{[e.year, e.details].filter(Boolean).join(" | ")}</p>
            </div>
          ))}
        </section>
      )}
      {cv.certifications.length > 0 && (
        <section>
          <p className="border-b border-slate-200 pb-1 text-xs font-bold uppercase tracking-wide">Certifications</p>
          <ul className="mt-2 list-disc pl-5">
            {cv.certifications.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </section>
      )}
    </div>
  );
}

function CVBuilderContent() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState<number | null>(null);
  const [uploading, setUploading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("backend engineer");
  const [searchLocation, setSearchLocation] = useState("Bangalore, Karnataka, India");
  const [postings, setPostings] = useState<JobPosting[] | null>(null);
  const [searching, setSearching] = useState(false);

  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [result, setResult] = useState<CVTailorResult | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState<"pdf" | "docx" | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadResumes(selectId?: number) {
    api.getResumes().then((list) => {
      setResumes(list);
      if (selectId) setResumeId(selectId);
      else if (list.length > 0) setResumeId((current) => current ?? list[0].id);
    });
  }

  useEffect(() => loadResumes(), []);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const uploaded = await api.uploadResume(file);
      loadResumes(uploaded.id);
    } catch (err) {
      setError(errorMessage(err, "Upload failed."));
    } finally {
      setUploading(false);
    }
  }

  async function handleSearch() {
    setSearching(true);
    setError(null);
    try {
      setPostings(await api.searchJobPostings(searchQuery, searchLocation));
    } catch (err) {
      setError(errorMessage(err, "Job search failed."));
    } finally {
      setSearching(false);
    }
  }

  function selectPosting(posting: JobPosting) {
    setJobTitle(posting.title);
    setCompany(posting.company);
    setJobDescription(posting.description);
    setPostings(null);
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resumeId) return;
    setGenerating(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.tailorCV({
        resume_id: resumeId,
        job_title: jobTitle,
        company,
        job_description: jobDescription,
      }));
    } catch (err) {
      setError(errorMessage(err, "Could not generate the CV."));
    } finally {
      setGenerating(false);
    }
  }

  async function handleDownload(format: "pdf" | "docx") {
    if (!result) return;
    setDownloading(format);
    try {
      await api.downloadCV(result.cv, format);
    } catch (err) {
      setError(errorMessage(err, "Download failed."));
    } finally {
      setDownloading(null);
    }
  }

  const jdTooShort = jobDescription.trim().length < MIN_JD_CHARS;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">ATS CV builder</h1>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Rewrites your CV for one specific job so applicant tracking systems can match it,
          using only facts from your real CV. Anything the AI can&apos;t back up from your
          original is removed or flagged for you to check.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="space-y-4">
            <h2 className="text-base font-semibold text-slate-900">1. Your current CV</h2>
            <div>
              <Label>Choose an uploaded CV</Label>
              <select
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={resumeId ?? ""}
                onChange={(e) => setResumeId(Number(e.target.value))}
                disabled={resumes.length === 0}
              >
                {resumes.length === 0 && <option>No CV uploaded yet</option>}
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>{r.original_filename}</option>
                ))}
              </select>
            </div>
            <label className="block">
              <input type="file" accept=".pdf,application/pdf" className="hidden" onChange={handleUpload} disabled={uploading} />
              <span className={`inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium ${uploading ? "cursor-not-allowed text-slate-400" : "cursor-pointer text-slate-700 hover:bg-slate-50"}`}>
                {uploading ? "Uploading..." : "Upload a new CV (PDF)"}
              </span>
            </label>
          </Card>

          <Card className="space-y-4">
            <h2 className="text-base font-semibold text-slate-900">2. The job you&apos;re applying for</h2>

            <div className="rounded-lg bg-slate-50 p-3">
              <p className="mb-2 text-xs font-medium text-slate-600">
                Find a live posting (Google Jobs via SerpApi), or paste one from LinkedIn below
              </p>
              <div className="flex flex-wrap gap-2">
                <div className="min-w-[140px] flex-1">
                  <Input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Role" />
                </div>
                <div className="min-w-[140px] flex-1">
                  <Input value={searchLocation} onChange={(e) => setSearchLocation(e.target.value)} placeholder="Location" />
                </div>
                <Button type="button" variant="secondary" onClick={handleSearch} disabled={searching || searchQuery.trim().length < 2}>
                  {searching ? "Searching..." : "Search"}
                </Button>
              </div>
              {postings && (
                <ul className="mt-3 max-h-64 space-y-2 overflow-y-auto">
                  {postings.length === 0 && <li className="text-sm text-slate-500">No postings found.</li>}
                  {postings.map((p, i) => (
                    <li key={i} className="flex items-center justify-between gap-2 rounded-md bg-white p-2 text-sm">
                      <span>
                        <span className="font-medium text-slate-900">{p.title}</span>
                        <span className="text-slate-500"> · {p.company}</span>
                      </span>
                      <Button type="button" variant="ghost" onClick={() => selectPosting(p)}>Use this</Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label>Job title</Label>
                <Input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} placeholder="Senior Backend Engineer" />
              </div>
              <div>
                <Label>Company</Label>
                <Input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Company name" />
              </div>
            </div>
            <div>
              <Label>Job description</Label>
              <Textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={9}
                placeholder="Paste the full job description here"
                required
              />
              {jobDescription.length > 0 && jdTooShort && (
                <p className="mt-1 text-xs text-amber-600">Paste the full description (at least {MIN_JD_CHARS} characters).</p>
              )}
            </div>
          </Card>
        </div>

        <div className="flex items-center gap-3">
          <Button type="submit" disabled={generating || !resumeId || jdTooShort} className="px-6 py-3 text-base">
            {generating ? "Tailoring your CV..." : "Generate ATS-friendly CV"}
          </Button>
          {generating && <Spinner />}
        </div>
      </form>

      {error && <Alert>{error}</Alert>}

      {result && (
        <div className="space-y-6">
          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <p className="text-xs uppercase tracking-wide text-slate-500">ATS keyword match</p>
              <p className="mt-2 text-3xl font-semibold text-slate-900">
                {Math.round(result.ats.coverage_before * 100)}%
                <span className="mx-2 text-slate-400">→</span>
                <span className="text-brand-600">{Math.round(result.ats.coverage_after * 100)}%</span>
              </p>
              <p className="mt-1 text-xs text-slate-500">
                of {result.ats.keywords.length} keywords from this job description
              </p>
            </Card>
            <Card className="lg:col-span-2">
              <p className="text-xs uppercase tracking-wide text-slate-500">Keywords your CV now matches</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {result.ats.matched_after.length === 0 && <span className="text-sm text-slate-500">None</span>}
                {result.ats.matched_after.map((k) => (
                  <Badge key={k} tone={result.ats.matched_before.includes(k) ? "success" : "warning"}>
                    {k}{result.ats.matched_before.includes(k) ? "" : " (new)"}
                  </Badge>
                ))}
              </div>
            </Card>
          </div>

          {result.warnings.length > 0 && (
            <Alert tone="warning">
              <p className="font-semibold">Check these before you send it</p>
              <ul className="mt-1 list-disc pl-5">
                {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </Alert>
          )}
          {result.removed_skills.length > 0 && (
            <Alert tone="success">
              Removed skills the AI added that aren&apos;t in your original CV: {result.removed_skills.join(", ")}
            </Alert>
          )}

          {result.ats.missing.length > 0 && (
            <Card>
              <p className="text-sm font-semibold text-slate-900">Gaps this job asks for that your CV doesn&apos;t show</p>
              <p className="mt-1 text-xs text-slate-500">
                If you genuinely have any of these, add them to your original CV and regenerate. Don&apos;t add skills you don&apos;t have -
                interviews will test them. The Market scan page shows which gaps are worth learning first.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {result.ats.missing.map((k) => <Badge key={k} tone="danger">{k}</Badge>)}
              </div>
            </Card>
          )}

          <div className="flex flex-wrap gap-3">
            <Button onClick={() => handleDownload("pdf")} disabled={downloading !== null}>
              {downloading === "pdf" ? "Preparing PDF..." : "Download PDF"}
            </Button>
            <Button variant="secondary" onClick={() => handleDownload("docx")} disabled={downloading !== null}>
              {downloading === "docx" ? "Preparing DOCX..." : "Download editable DOCX"}
            </Button>
            <p className="self-center text-xs text-slate-500">
              The DOCX opens in Google Docs or Word for edits.
            </p>
          </div>

          <CVPreview cv={result.cv} />
        </div>
      )}
    </div>
  );
}

export default function CVBuilderPage() {
  return (
    <RequireAuth>
      <CVBuilderContent />
    </RequireAuth>
  );
}
