"use client";

import { ChangeEvent, useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { Alert, Badge, Button, Card, EmptyState, Spinner } from "@/components/ui";
import * as api from "@/lib/api";
import type { Resume, ResumeAnalysis } from "@/lib/api";
import { ApiError } from "@/lib/api";

function statusTone(status: string) {
  if (status === "processed" || status === "completed") return "success";
  if (status === "failed" || status === "error") return "danger";
  return "warning";
}

function ResumesContent() {
  const [resumes, setResumes] = useState<Resume[] | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analyses, setAnalyses] = useState<Record<number, ResumeAnalysis | "loading" | "error">>({});

  function loadResumes() {
    api
      .getResumes()
      .then(setResumes)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load resumes.")
      );
  }

  useEffect(loadResumes, []);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setError(null);
    setUploading(true);
    try {
      await api.uploadResume(file);
      loadResumes();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAnalyze(resumeId: number) {
    setAnalyses((prev) => ({ ...prev, [resumeId]: "loading" }));
    try {
      const result = await api.analyzeResume(resumeId);
      setAnalyses((prev) => ({ ...prev, [resumeId]: result }));
    } catch {
      setAnalyses((prev) => ({ ...prev, [resumeId]: "error" }));
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Resumes</h1>
          <p className="mt-1 text-sm text-slate-500">
            Upload a PDF resume to use it for job matching and career
            analysis.
          </p>
        </div>
        <label>
          <input
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading}
          />
          <span
            className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors ${
              uploading
                ? "cursor-not-allowed bg-slate-300"
                : "cursor-pointer bg-brand-600 hover:bg-brand-700"
            }`}
          >
            {uploading ? "Uploading..." : "Upload resume"}
          </span>
        </label>
      </div>

      {error && <Alert>{error}</Alert>}

      {resumes === null && (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      )}

      {resumes?.length === 0 && (
        <EmptyState
          title="No resumes yet"
          description="Upload your first resume to get started."
        />
      )}

      <div className="grid gap-4">
        {resumes?.map((resume) => {
          const analysis = analyses[resume.id];
          return (
            <Card key={resume.id}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">
                    {resume.original_filename}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    Uploaded {new Date(resume.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge tone={statusTone(resume.status)}>{resume.status}</Badge>
                  <Button
                    variant="secondary"
                    onClick={() => handleAnalyze(resume.id)}
                    disabled={analysis === "loading"}
                  >
                    {analysis === "loading" ? "Analyzing..." : "Extract skills"}
                  </Button>
                </div>
              </div>

              {analysis && analysis !== "loading" && analysis !== "error" && (
                <div className="mt-4 border-t border-slate-100 pt-4">
                  {analysis.name && (
                    <p className="text-sm text-slate-600">
                      Detected name: {analysis.name}
                    </p>
                  )}
                  <div className="mt-2 flex flex-wrap gap-2">
                    {analysis.skills.length === 0 && (
                      <span className="text-sm text-slate-500">
                        No skills detected.
                      </span>
                    )}
                    {analysis.skills.map((skill) => (
                      <Badge key={skill}>{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {analysis === "error" && (
                <p className="mt-4 text-sm text-red-600">
                  Could not analyze this resume.
                </p>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

export default function ResumesPage() {
  return (
    <RequireAuth>
      <ResumesContent />
    </RequireAuth>
  );
}
