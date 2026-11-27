"use client";

import { useCallback, useEffect, useState } from "react";
import { api, DOC_TYPE_LABEL, Job, STATUS_LABEL } from "@/lib/api";

export default function HistorialPage() {
  const [jobs, setJobs] = useState<Job[]>([]);

  const cargar = useCallback(async () => {
    setJobs(await api<Job[]>("/api/v1/lookups?limit=200"));
  }, []);

  useEffect(() => {
    cargar().catch(() => {});
  }, [cargar]);

  function badge(s: string): string {
    if (s === "COMPLETED") return "badge verde";
    if (s === "FAILED" || s === "EXCLUDED") return "badge rojo";
    if (s === "NOT_FOUND") return "badge ambar";
    return "badge gris";
  }

  return (
    <div>
      <h2>Historial de consultas</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Tipo</th><th>Estado</th><th>Fuente</th><th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id}>
                <td>{j.id}</td>
                <td>{DOC_TYPE_LABEL[j.document_type] ?? j.document_type}</td>
                <td><span className={badge(j.status)}>{STATUS_LABEL[j.status] ?? j.status}</span></td>
                <td>{j.source}</td>
                <td>{j.created_at?.slice(0, 16).replace("T", " ")}</td>
              </tr>
            ))}
            {jobs.length === 0 && (
              <tr><td colSpan={5}>Sin consultas registradas</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
