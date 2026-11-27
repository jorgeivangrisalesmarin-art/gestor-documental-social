"use client";

import { FormEvent, useRef, useState } from "react";
import { api, Batch, STATUS_LABEL } from "@/lib/api";

export default function MasivaPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [batch, setBatch] = useState<Batch | null>(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  function badge(s: string): string {
    if (s === "COMPLETED" || s === "PARTIAL_SUCCESS") return "badge verde";
    if (s === "FAILED") return "badge rojo";
    if (s === "EXCLUDED") return "badge ambar";
    return "badge gris";
  }

  async function subir(e: FormEvent) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setCargando(true);
    setError("");
    setBatch(null);
    const form = new FormData();
    form.append("file", file);
    const token = window.localStorage.getItem("gds_token");
    const resp = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/batches`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      },
    );
    const body = await resp.json();
    if (!resp.ok) {
      setError(body.detail ?? `Error ${resp.status}`);
      setCargando(false);
      return;
    }
    setBatch(body as Batch);
    setCargando(false);
}


  async function procesar(batchId: number) {
    try {
      const data = await api<Batch>(`/api/v1/batches/${batchId}/process`, { method: "POST" });
      setBatch(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al procesar el lote");
    }
  }

  return (
    <div>
      <h2>Consulta masiva</h2>
      <p className="aviso">
        Formato del CSV: tipo_documento, numero_documento, adres, sisben_iv, rui,
        autorizacion_confirmada, referencia_autorizacion. Máximo 100 registros (MVP).
        Registros sin autorización confirmada quedan EXCLUIDOS y no se consultan.
      </p>
      <div className="card">
        <form onSubmit={subir}>
          <label htmlFor="archivo">Archivo CSV o Excel</label>
          <input id="archivo" type="file" accept=".csv,.xlsx" ref={fileRef} required />
          <button className="primario" disabled={cargando}>
            {cargando ? "Validando…" : "Cargar y validar"}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
      {batch && (
        <div className="card">
          <h3>Lote #{batch.id} — {batch.status}</h3>
          <div className="indicadores">
            <div className="indicador"><div className="valor">{batch.total_records}</div>Registros</div>
            <div className="indicador"><div className="valor">{batch.processed_records}</div>Procesados</div>
            <div className="indicador"><div className="valor">{batch.success_count}</div>Exitosos</div>
            <div className="indicador"><div className="valor">{batch.error_count}</div>Errores</div>
          </div>
          <h4>Detalle por documento</h4>
          <table>
            <thead>
              <tr><th>Job</th><th>Tipo</th><th>Estado</th><th>Error</th></tr>
            </thead>
            <tbody>
              {batch.jobs.map((j) => (
                <tr key={j.id}>
                  <td>{j.id}</td>
                  <td>{j.document_type}</td>
                  <td><span className={badge(j.status)}>{STATUS_LABEL[j.status] ?? j.status}</span></td>
                  <td>{j.error_code}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="primario" onClick={() => procesar(batch.id)}>
            {batch.status === "VALIDATING" ? "Iniciar procesamiento" : "Reprocesar pendientes"}
          </button>
        </div>
      )}
    </div>
  );
}
