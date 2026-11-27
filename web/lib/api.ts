"use client";

// Cliente de la API (solo navegador). El JWT vive en localStorage en el MVP;
// mejora futura: cookie httpOnly (ver ROADMAP de seguridad).
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Job {
  id: number;
  batch_id: number | null;
  document_type: string;
  provider: string;
  status: string;
  source: string | null;
  error_code: string | null;
  result: {
    status: string;
    data: Record<string, unknown>;
    source: string;
    consulted_at: string;
    live: boolean;
  } | null;
  created_at: string | null;
}

export interface Batch {
  id: number;
  filename: string;
  status: string;
  total_records: number;
  processed_records: number;
  success_count: number;
  error_count: number;
  jobs: { id: number; document_type: string; status: string; error_code: string | null }[];
  validation_errors?: { fila: number; errores: string[] }[];
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("gds_token");
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const resp = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (resp.status === 401 && !path.startsWith("/auth/login")) {
    window.localStorage.removeItem("gds_token");
    window.location.href = "/";
    throw new Error("Sesión expirada");
  }
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(body.detail ?? `Error ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export const DOC_TYPE_LABEL: Record<string, string> = {
  ADRES_AFFILIATION_REPORT: "ADRES (afiliación EPS)",
  SISBEN_IV_CERTIFICATE: "SISBÉN IV",
  RUI_CERTIFICATE: "RUI",
};

export const STATUS_LABEL: Record<string, string> = {
  COMPLETED: "Completada",
  FAILED: "Fallida",
  NOT_FOUND: "No encontrado",
  PENDING: "Pendiente",
  PROCESSING: "Procesando",
  EXCLUDED: "Excluida (sin autorización)",
  MANUAL_ACTION_REQUIRED: "Requiere acción manual",
};
