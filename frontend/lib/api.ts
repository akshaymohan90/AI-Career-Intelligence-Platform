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

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
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
      detail = body.detail || detail;
    } catch {
      // no JSON body
    }
    throw new ApiError(detail, response.status);
  }

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
