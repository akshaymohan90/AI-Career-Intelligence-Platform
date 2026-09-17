"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import RequireAuth from "@/components/RequireAuth";
import CareerAnalysisResult from "@/components/CareerAnalysis";
import { Alert, Badge, Button, Card, Spinner, Textarea } from "@/components/ui";
import * as api from "@/lib/api";
import type { CareerAnalysis, Job, Resume } from "@/lib/api";
import { ApiError } from "@/lib/api";

function JobDetailContent() {
  const params = useParams<{ id: string }>();
  const jobId = Number(params.id);

  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [analysis, setAnalysis] = useState<CareerAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const [advice, setAdvice] = useState<string | null>(null);
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [adviceError, setAdviceError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    Promise.all([api.getJob(jobId), api.getResumes()])
      .then(([jobData, resumeData]) => {
        setJob(jobData);
        setResumes(resumeData);
        if (resumeData.length > 0) setSelectedResumeId(resumeData[0].id);
      })
      .catch((err) =>
        setLoadError(err instanceof ApiError ? err.message : "Failed to load job.")
      );
  }, [jobId]);

  async function runAnalysis() {
    if (!selectedResumeId) return;
    setAnalysisLoading(true);
    setAnalysisError(null);
    setAnalysis(null);
    try {
      const result = await api.getCareerAnalysis(jobId, selectedResumeId);
      setAnalysis(result);
    } catch (err) {
      setAnalysisError(
        err instanceof ApiError ? err.message : "Failed to run career analysis."
      );
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function runAdvice() {
    if (!selectedResumeId) return;
    setAdviceLoading(true);
    setAdviceError(null);
    setAdvice(null);
    try {
      const result = await api.getAiAdvice(jobId, selectedResumeId);
      setAdvice(result.advice);
    } catch (err) {
      setAdviceError(
        err instanceof ApiError
          ? err.message
          : "AI advice is unavailable right now."
      );
    } finally {
      setAdviceLoading(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedResumeId || !question.trim()) return;
    setAskLoading(true);
    setAskError(null);
    setAnswer(null);
    try {
      const result = await api.askAssistant(jobId, selectedResumeId, question);
      setAnswer(result.answer);
    } catch (err) {
      setAskError(
        err instanceof ApiError ? err.message : "The assistant is unavailable."
      );
    } finally {
      setAskLoading(false);
    }
  }

  if (loadError) {
    return <Alert>{loadError}</Alert>;
  }

  if (!job) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <h1 className="text-2xl font-semibold text-slate-900">{job.title}</h1>
        <p className="mt-1 text-sm text-slate-500">
          {job.company}
          {job.location ? ` · ${job.location}` : ""}
          {job.experience_required ? ` · ${job.experience_required}` : ""}
        </p>
        {job.required_skills && (
          <div className="mt-3 flex flex-wrap gap-2">
            {job.required_skills.split(",").map((skill) => (
              <Badge key={skill}>{skill.trim()}</Badge>
            ))}
          </div>
        )}
        <p className="mt-4 whitespace-pre-line text-sm text-slate-600">
          {job.description}
        </p>
      </Card>

      <Card>
        <h2 className="text-base font-semibold text-slate-900">
          Analyze against a resume
        </h2>

        {resumes.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">
            You don&apos;t have any resumes yet. Upload one on the{" "}
            <a href="/resumes" className="font-medium text-brand-600">
              Resumes page
            </a>{" "}
            first.
          </p>
        ) : (
          <>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <select
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={selectedResumeId ?? ""}
                onChange={(e) => setSelectedResumeId(Number(e.target.value))}
              >
                {resumes.map((resume) => (
                  <option key={resume.id} value={resume.id}>
                    {resume.original_filename}
                  </option>
                ))}
              </select>
              <Button onClick={runAnalysis} disabled={analysisLoading}>
                {analysisLoading ? "Analyzing..." : "Run career analysis"}
              </Button>
              <Button
                variant="secondary"
                onClick={runAdvice}
                disabled={adviceLoading}
              >
                {adviceLoading ? "Thinking..." : "Get AI advice"}
              </Button>
            </div>

            {analysisError && <Alert className="mt-4">{analysisError}</Alert>}
            {adviceError && <Alert className="mt-4" tone="warning">{adviceError}</Alert>}
          </>
        )}
      </Card>

      {analysis && <CareerAnalysisResult data={analysis} />}

      {advice && (
        <Card>
          <h2 className="text-base font-semibold text-slate-900">AI advice</h2>
          <p className="mt-2 whitespace-pre-line text-sm text-slate-600">
            {advice}
          </p>
        </Card>
      )}

      {resumes.length > 0 && (
        <Card>
          <h2 className="text-base font-semibold text-slate-900">
            Ask the career assistant
          </h2>
          <form onSubmit={handleAsk} className="mt-3 space-y-3">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Which skill should I prioritize learning first?"
              rows={3}
            />
            <Button type="submit" disabled={askLoading || !question.trim()}>
              {askLoading ? "Asking..." : "Ask"}
            </Button>
          </form>
          {askError && <Alert className="mt-4" tone="warning">{askError}</Alert>}
          {answer && (
            <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
              {answer}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

export default function JobDetailPage() {
  return (
    <RequireAuth>
      <JobDetailContent />
    </RequireAuth>
  );
}
