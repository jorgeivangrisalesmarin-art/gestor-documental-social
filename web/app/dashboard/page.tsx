"use client";

import { useCallback, useEffect, useState } from "react";
import { api, DOC_TYPE_LABEL, Job, STATUS_LABEL } from "@/lib/api";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);

  const cargar = useCallback(async () => {
    setJobs(await api<Job[]>("/api/v1/lookups?limit=200"));
  }, []);

  useEffect(() => {
    cargar().catch(() => {});
  }, [cargar]);

  const total = jobs.length;
  const exitosas = jobs.filter((j) => j.status === "COMPLETED").length;
  const fallidas = jobs.filter((j) => j.status === "FAILED" || j.status === "EXCLUDED").length;
  const pendientes = total - exitosas - fallidas;

  function badge(status: string): string {
    if (status === "COMPLETED") return "badge verde";
    if (status === "FAILED" || status === "EXCLUDED") return "badge rojo";
    if (status === "NOT_FOUND") return "badge ambar";
    return "badge gris";
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <p className="aviso">
        Modo actual de proveedores: fixture (datos FICTICIOS etiquetados). Las consultas
        reales requieren PLACAPI_API_KEY.
      </p>
      <div className="card">
        <div className="indicadores">
          <div className="indicador"><div className="valor">{total}</div>Consultas totales</div>
          <div className="indicador"><div className="valor">{exitosas}</div>Exitosas</div>
          <div className="indicador"><div className="valor">{pendientes}</div>Pendientes</div>
          <div className="indicador"><div className="valor">{fallidas}</div>Errores</div>
        </div>
      </div>
      <div className="card">
        <h3>Últimas consultas</h3>
        <table>
          <thead>
            <tr><th>ID</th><th>Tipo</th><th>Proveedor</th><th>Estado</th><th>Fuente</th></tr>
          </thead>
          <tbody>
            {jobs.slice(0, 10).map((j) => (
              <tr key={j.id}>
                <td>{j.id}</td>
                <td>{DOC_TYPE_LABEL[j.document_type] ?? j.document_type}</td>
                <td>{j.provider}</td>
                <td><span className={badge(j.status)}>{STATUS_LABEL[j.status] ?? j.status}</span></td>
                <td>{j.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
