"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import RequireAuth from "@/components/RequireAuth";
import {
  Alert,
  Button,
  Card,
  EmptyState,
  Input,
  Label,
  Spinner,
  Textarea,
} from "@/components/ui";
import * as api from "@/lib/api";
import type { Job } from "@/lib/api";
import { ApiError } from "@/lib/api";

const emptyForm = {
  title: "",
  company: "",
  location: "",
  experience_required: "",
  required_skills: "",
  description: "",
};

function JobsContent() {
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  function loadJobs() {
    api
      .getJobs()
      .then(setJobs)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load jobs.")
      );
  }

  useEffect(loadJobs, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await api.createJob({
        title: form.title,
        company: form.company,
        description: form.description,
        location: form.location || undefined,
        experience_required: form.experience_required || undefined,
        required_skills: form.required_skills || undefined,
      });
      setForm(emptyForm);
      setShowForm(false);
      loadJobs();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create job.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Jobs</h1>
          <p className="mt-1 text-sm text-slate-500">
            Browse postings or add one to analyze it against your resume.
          </p>
        </div>
        <Button onClick={() => setShowForm((s) => !s)}>
          {showForm ? "Cancel" : "Add job"}
        </Button>
      </div>

      {error && <Alert>{error}</Alert>}

      {showForm && (
        <Card>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Title</Label>
                <Input
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label>Company</Label>
                <Input
                  value={form.company}
                  onChange={(e) => setForm({ ...form, company: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label>Location</Label>
                <Input
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                />
              </div>
              <div>
                <Label>Experience required</Label>
                <Input
                  value={form.experience_required}
                  onChange={(e) =>
                    setForm({ ...form, experience_required: e.target.value })
                  }
                  placeholder="e.g. 3+ years"
                />
              </div>
            </div>
            <div>
              <Label>Required skills (comma-separated)</Label>
              <Input
                value={form.required_skills}
                onChange={(e) =>
                  setForm({ ...form, required_skills: e.target.value })
                }
                placeholder="Python, SQL, React"
              />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                rows={5}
                required
              />
            </div>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create job"}
            </Button>
          </form>
        </Card>
      )}

      {jobs === null && (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      )}

      {jobs?.length === 0 && (
        <EmptyState
          title="No jobs yet"
          description="Add a job posting to start matching it against your resumes."
        />
      )}

      <div className="grid gap-4">
        {jobs?.map((job) => (
          <Link key={job.id} href={`/jobs/${job.id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-slate-900">{job.title}</p>
                  <p className="text-sm text-slate-500">
                    {job.company}
                    {job.location ? ` · ${job.location}` : ""}
                  </p>
                </div>
                {job.experience_required && (
                  <span className="text-xs text-slate-500">
                    {job.experience_required}
                  </span>
                )}
              </div>
              <p className="mt-3 line-clamp-2 text-sm text-slate-600">
                {job.description}
              </p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <RequireAuth>
      <JobsContent />
    </RequireAuth>
  );
}
