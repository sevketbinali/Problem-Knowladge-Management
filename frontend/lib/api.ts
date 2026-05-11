const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface APIResponse<T> {
  status: "success" | "error";
  data: T | null;
  error: string | null;
  message: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    role: string;
  };
}

export interface SessionResponse {
  session_id: string;
  methodology: string;
  current_step: number;
  next_prompt?: string;
  status?: string;
  total_steps?: number;
  similar_problems?: SimilarProblem[];
  message?: string;
}

export interface SimilarProblem {
  score: number;
  payload: {
    title: string;
    methodology: string;
    root_cause: string;
    resolution_status: string;
  };
}

export interface ProblemRecord {
  id: string;
  title: string;
  problem_description: string;
  methodology: string;
  root_cause: string;
  lessons_learned: string;
  resolution_status: string;
  created_at: string;
  updated_at: string;
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    return {
      status: "error",
      data: null,
      error: errorData?.error || errorData?.detail || `HTTP ${res.status}`,
      message: null,
    };
  }

  return res.json();
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

// ─── Auth ────────────────────────────────────────────────────────────────────
export async function login(email: string, password: string) {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

// ─── Sessions ────────────────────────────────────────────────────────────────
export async function createSession(
  token: string,
  problemDescription: string,
  methodology: string
) {
  return apiRequest<SessionResponse>("/sessions", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({
      problem_description: problemDescription,
      methodology,
    }),
  });
}

export async function submitStep(
  token: string,
  sessionId: string,
  response: string
) {
  return apiRequest<SessionResponse>(`/sessions/${sessionId}/steps`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ response }),
  });
}

export async function stepBack(token: string, sessionId: string) {
  return apiRequest<SessionResponse>(`/sessions/${sessionId}/back`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function finalizeSession(token: string, sessionId: string) {
  return apiRequest<Record<string, unknown>>(`/sessions/${sessionId}/finalize`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function listSessions(token: string) {
  return apiRequest<SessionResponse[]>("/sessions", {
    headers: authHeaders(token),
  });
}

// ─── Knowledge ───────────────────────────────────────────────────────────────
export async function searchKnowledge(
  token: string,
  query: string,
  filters?: { industry?: string; department?: string }
) {
  const params = new URLSearchParams({ query });
  if (filters?.industry) params.set("industry", filters.industry);
  if (filters?.department) params.set("department", filters.department);

  return apiRequest<SimilarProblem[]>(`/knowledge/search?${params}`, {
    headers: authHeaders(token),
  });
}

// ─── Records ─────────────────────────────────────────────────────────────────
export async function listRecords(token: string, skip = 0, limit = 20) {
  return apiRequest<ProblemRecord[]>(`/records?skip=${skip}&limit=${limit}`, {
    headers: authHeaders(token),
  });
}

export async function getRecord(token: string, recordId: string) {
  return apiRequest<ProblemRecord>(`/records/${recordId}`, {
    headers: authHeaders(token),
  });
}

export async function deleteRecord(token: string, recordId: string) {
  return apiRequest<null>(`/records/${recordId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

// ─── Health ──────────────────────────────────────────────────────────────────
export async function healthCheck() {
  return apiRequest<Record<string, string>>("/health/ready");
}
