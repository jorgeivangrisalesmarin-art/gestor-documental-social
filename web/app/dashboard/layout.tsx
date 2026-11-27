"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken } from "@/lib/api";

const LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/consulta", label: "Consulta individual" },
  { href: "/dashboard/masiva", label: "Consulta masiva" },
  { href: "/dashboard/historial", label: "Historial" },
  { href: "/dashboard/proveedores", label: "Proveedores" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (!getToken()) {
      router.push("/");
    }
    setEmail(window.localStorage.getItem("gds_email") ?? "funcionario");
  }, [router]);

  function logout() {
    window.localStorage.removeItem("gds_token");
    window.localStorage.removeItem("gds_email");
    router.push("/");
  }

  return (
    <div className="layout">
      <nav className="sidebar">
        <h1>Gestor Documental Social</h1>
        {LINKS.map((l) => (
          <Link key={l.href} href={l.href}>
            {l.label}
          </Link>
        ))}
        <span className="spacer-user">{email}</span>
        <button onClick={logout}>Salir</button>
      </nav>
      <main className="contenido">{children}</main>
    </div>
  );
}
