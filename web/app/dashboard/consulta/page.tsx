"use client";

import { FormEvent, useState } from "react";
import { api, DOC_TYPE_LABEL, Job } from "@/lib/api";

const TIPOS_DOC = ["CC", "TI", "CE", "PA", "NIT"];
const TIPOS_DOCUMENTAL = [
  "ADRES_AFFILIATION_REPORT",
  "SISBEN_IV_CERTIFICATE",
  "RUI_CERTIFICATE",
];

export default function ConsultaPage() {
  const [tipoDocumento, setTipoDocumento] = useState("CC");
  const [numero, setNumero] = useState("");
  const [tipos, setTipos] = useState<string[]>(["ADRES_AFFILIATION_REPORT"]);
  const [finalidad, setFinalidad] = useState("");
  const [autorizo, setAutorizo] = useState(false);
  const [resultados, setResultados] = useState<Job[]>([]);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  function toggle(t: string) {
    setTipos((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : prev.concat(t),
    );
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setCargando(true);
    setError("");
    setResultados([]);
    try {
      const data = await api<Job[]>("/api/v1/lookups", {
        method: "POST",
        body: JSON.stringify({
          tipo_documento: tipoDocumento,
          numero_documento: numero,
          document_types: tipos,
          finalidad,
          autorizacion_confirmada: autorizo,
        }),
      });
      setResultados(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la consulta");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div>
      <h2>Consulta individual</h2>
      <div className="card">
        <form onSubmit={onSubmit}>
          <label htmlFor="tipo">Tipo de documento</label>
          <select
            id="tipo"
            value={tipoDocumento}
            onChange={(e) => setTipoDocumento(e.target.value)}
          >
            {TIPOS_DOC.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <label htmlFor="numero">Número de documento</label>
          <input
            id="numero"
            value={numero}
            onChange={(e) => setNumero(e.target.value)}
            required
          />
          <div className="checks">
            {TIPOS_DOCUMENTAL.map((t) => (
              <label key={t}>
                <input
                  type="checkbox"
                  checked={tipos.includes(t)}
                  onChange={() => toggle(t)}
                />
                {DOC_TYPE_LABEL[t]}
              </label>
            ))}
          </div>
          <label htmlFor="finalidad">Finalidad de la consulta</label>
          <input
            id="finalidad"
            value={finalidad}
            onChange={(e) => setFinalidad(e.target.value)}
            required
          />
          <div className="checks">
            <label>
              <input
                type="checkbox"
                checked={autorizo}
                onChange={(e) => setAutorizo(e.target.checked)}
                required
              />
              Confirmo la autorización del titular para esta consulta
            </label>
          </div>
          <button className="primario" disabled={cargando}>
            {cargando ? "Consultando…" : "Consultar"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      </div>
      {resultados.length > 0 && (
        <div className="card">
          <h3>Resultados</h3>
          {resultados.map((r) => (
            <div key={r.id}>
              <p>
                <strong>{DOC_TYPE_LABEL[r.document_type]}</strong> —{" "}
                <span className={r.status === "COMPLETED" ? "badge verde" : "badge ambar"}>
                  {r.status}
                </span>{" "}
                fuente: {r.source} {r.result?.live === false && "(fixture: datos FICTICIOS)"}
              </p>
              <pre>{JSON.stringify(r.result?.data, null, 2)}</pre>
              <hr />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
