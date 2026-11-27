"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setCargando(true);
    setError("");
    try {
      const data = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      window.localStorage.setItem("gds_token", data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error de autenticación");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="login">
      <h1>Gestor Documental Social</h1>
      <form onSubmit={onSubmit}>
        <label htmlFor="email">Correo</label>
        <input id="email" type="text" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label htmlFor="password">Contraseña</label>
        <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button className="primario" type="submit" disabled={cargando}>
          {cargando ? "Ingresando…" : "Ingresar"}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
