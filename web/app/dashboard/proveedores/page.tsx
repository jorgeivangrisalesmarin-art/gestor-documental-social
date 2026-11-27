"use client";

import { useCallback, useEffect, useState } from "react";
import { api, DOC_TYPE_LABEL } from "@/lib/api";

interface ProviderHealth {
  provider: string;
  document_type: string | null;
  ok: boolean;
  detail: string;
}

export default function ProveedoresPage() {
  const [checks, setChecks] = useState<ProviderHealth[]>([]);

  const cargar = useCallback(async () => {
    const data = await api<{ providers: ProviderHealth[] }>("/health/providers");
    setChecks(data.providers);
  }, []);

  useEffect(() => {
    cargar().catch(() => {});
  }, [cargar]);

  return (
    <div>
      <h2>Estado de proveedores</h2>
      <div className="card">
        <table>
          <thead>
            <tr><th>Proveedor</th><th>Tipo documental</th><th>Estado</th><th>Detalle</th></tr>
          </thead>
          <tbody>
            {checks.map((h) => (
              <tr key={h.provider + (h.document_type ?? "")}>
                <td>{h.provider}</td>
                <td>{h.document_type ? DOC_TYPE_LABEL[h.document_type] : "-"}</td>
                <td>
                  <span className={h.ok ? "badge verde" : "badge ambar"}>
                    {h.ok ? "OK" : "Configurar"}
                  </span>
                </td>
                <td>{h.detail}</td>
              </tr>
            ))}
            {checks.length === 0 && (
              <tr><td colSpan={4}>Cargando…</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
