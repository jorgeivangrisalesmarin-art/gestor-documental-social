import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gestor Documental Social",
  description: "Motor documental ADRES / SISBÉN IV / RUI para organizaciones territoriales",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
