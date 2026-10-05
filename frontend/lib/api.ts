const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function send(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (!(options.body instanceof FormData) && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        detail = body.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join("; ");
      }
    } catch {
      // no JSON body
    }
    throw new ApiError(detail, response.status);
  }

  return response;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await send(path, options);
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

// ---- Types ----

export type User = {
  id: number;
  full_name: string;
  email: string;
};

export type Job = {
  id: number;
  title: string;
  description: string;
  company: string;
  location: string | null;
  experience_required: string | null;
  required_skills: string | null;
};

export type JobCreateInput = {
  title: string;
  description: string;
  company: string;
  location?: string;
  experience_required?: string;
  required_skills?: string;
};

export type Resume = {
  id: number;
  original_filename: string;
  file_path: string;
  file_type: string;
  status: string;
  created_at: string;
};

export type ResumeAnalysis = {
  name: string | null;
  skills: string[];
};

export type JobMatch = {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
};

export type CareerAnalysis = {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  skill_gap_count: number;
  recommendations: { skill: string; priority: string }[];
};

// ---- Auth ----

export function registerUser(data: {
  full_name: string;
  email: string;
  password: string;
}) {
  return request<User>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(email: string, password: string) {
  return request<{ access_token: string; token_type: string }>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );
}

export function getMe() {
  return request<User>("/api/v1/users/me");
}

export function updateProfile(data: { full_name?: string; email?: string }) {
  return request<User>("/api/v1/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// ---- Jobs ----

export function getJobs() {
  return request<Job[]>("/api/v1/jobs/");
}

export function getJob(jobId: number) {
  return request<Job>(`/api/v1/jobs/${jobId}`);
}

export function createJob(data: JobCreateInput) {
  return request<Job>("/api/v1/jobs/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getJobSkills(jobId: number) {
  return request<string[]>(`/api/v1/jobs/${jobId}/skills`);
}

export function matchJob(jobId: number, resumeId: number) {
  return request<JobMatch>(`/api/v1/jobs/${jobId}/match/${resumeId}`, {
    method: "POST",
  });
}

export function getCareerAnalysis(jobId: number, resumeId: number) {
  return request<CareerAnalysis>(
    `/api/v1/jobs/${jobId}/career-analysis/${resumeId}`,
    { method: "POST" }
  );
}

export function getAiAdvice(jobId: number, resumeId: number) {
  return request<{ advice: string }>(
    `/api/v1/jobs/${jobId}/ai-advice/${resumeId}`,
    { method: "POST" }
  );
}

export function askAssistant(
  jobId: number,
  resumeId: number,
  question: string
) {
  const params = new URLSearchParams({ question });
  return request<{ answer: string }>(
    `/api/v1/jobs/${jobId}/assistant/${resumeId}?${params.toString()}`,
    { method: "POST" }
  );
}

// ---- Market intelligence ----

export type MarketEvidence = {
  title: string;
  company: string;
  location: string | null;
  link: string | null;
  gaps_in_posting: number;
};

export type MarketRecommendation = {
  skill: string;
  jobs_unlocked: number;
  estimated_weeks: number;
  jobs_per_week: number;
  trend_direction: "rising" | "stable" | "falling" | "unknown";
  trend_momentum: number | null;
  score: number;
  evidence: MarketEvidence[];
};

export type MarketAgentStep = {
  step: string;
  detail: string;
  ms: number;
};

export type MarketScan = {
  role: string;
  location: string;
  postings_scanned: number;
  postings_analyzed: number;
  your_skills: string[];
  already_qualified: number;
  near_matches: number;
  recommendations: MarketRecommendation[];
  agent_trace: MarketAgentStep[];
  serpapi_live_calls: number;
  serpapi_cache_hits: number;
};

export function runMarketScan(data: {
  role: string;
  location: string;
  resume_id: number;
}) {
  return request<MarketScan>("/api/v1/market/scan", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---- CV builder ----

export type CVExperience = {
  role: string | null;
  company: string | null;
  location: string | null;
  start: string | null;
  end: string | null;
  bullets: string[];
};

export type TailoredCV = {
  full_name: string;
  headline: string;
  email: string | null;
  phone: string | null;
  location: string | null;
  links: string[];
  summary: string;
  skills: string[];
  experience: CVExperience[];
  projects: { name: string; bullets: string[] }[];
  education: { degree: string | null; institution: string | null; year: string | null; details: string | null }[];
  certifications: string[];
};

export type ATSReport = {
  keywords: string[];
  matched_before: string[];
  matched_after: string[];
  missing: string[];
  coverage_before: number;
  coverage_after: number;
};

export type CVTailorResult = {
  cv: TailoredCV;
  ats: ATSReport;
  removed_skills: string[];
  warnings: string[];
};

export type JobPosting = {
  title: string;
  company: string;
  location: string | null;
  description: string;
  link: string | null;
};

export function tailorCV(data: {
  resume_id: number;
  job_title: string;
  company: string;
  job_description: string;
}) {
  return request<CVTailorResult>("/api/v1/cv/tailor", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function searchJobPostings(q: string, location: string) {
  const params = new URLSearchParams({ q, location });
  return request<JobPosting[]>(`/api/v1/cv/job-search?${params.toString()}`);
}

export async function downloadCV(cv: TailoredCV, format: "pdf" | "docx") {
  const response = await send(`/api/v1/cv/render/${format}`, {
    method: "POST",
    body: JSON.stringify(cv),
  });
  const blob = await response.blob();
  const stem = (cv.full_name || "CV").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "") || "CV";
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${stem}_CV.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

// ---- Resumes ----

export function getResumes() {
  return request<Resume[]>("/api/v1/resumes/");
}

export function uploadResume(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<Resume>("/api/v1/resumes/upload", {
    method: "POST",
    body: formData,
  });
}

export function analyzeResume(resumeId: number) {
  return request<ResumeAnalysis>(`/api/v1/resumes/${resumeId}/analysis`);
}
