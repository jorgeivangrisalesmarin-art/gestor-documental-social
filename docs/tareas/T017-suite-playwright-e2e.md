# T017 — Suite Playwright de Regresión (6 Flujos E2E)

**Asignado:** Yeison (Junior Developer)  
**Revisor:** Jorge (Tech Lead)  
**Prioridad:** P0 · **Herramienta:** Antigravity + Playwright  
**Resultado esperado:** Suite automatizada de pruebas de regresión E2E que valide los 6 flujos del MVP descritos en `docs/TEST_REPORT.md` ejecutándose en modo desatendido.

---

## 1. Contexto

El Gestor Documental Social cuenta con el backend FastAPI y el frontend Next.js en producción local. Para asegurar que ninguna modificación futura rompa los flujos críticos del funcionario (consulta ciudadana, procesamiento de lotes masivos y auditoría), Yeison automatiza la suite de regresión E2E con **Playwright**.

---

## 2. Los 6 Flujos de Regresión E2E

1. **Flujo 1 — Autenticación y Dashboard:**  
   Login con credenciales de desarrollo (`admin@local.test` / `admin1234`) y redirección exitosa al panel principal `/dashboard`.
2. **Flujo 2 — Consulta Individual:**  
   Ingreso de documento `CC 123456789`, selección de ADRES + SISBÉN IV, finalidad registrada. Verificación de 2 jobs `COMPLETED` con advertencia de datos ficticios y enmascaramiento `***789`.
3. **Flujo 3 — Carga Masiva y Validación:**  
   Carga de archivo CSV con 4 filas y validación automática de registros con exclusión de no autorizados (`SIN_AUTORIZACION`).
4. **Flujo 4 — Procesamiento de Lote y Prevención 409:**  
   Ejecución del lote, transición a `COMPLETED` y verificación de control anti-doble procesamiento (HTTP 409 en clic duplicado).
5. **Flujo 5 — Historial de Auditoría:**  
   Navegación a `/dashboard/historial` y verificación de trazabilidad de consultas registradas.
6. **Flujo 6 — Estado de Proveedores:**  
   Navegación a `/dashboard/proveedores` y verificación de estado operativo de ADRES, SISBÉN y RUI en modo fixture.

---

## 3. Criterios de Aceptación (EARS)

- **AC-1:** CUANDO se ingresan las credenciales válidas en `/`, EL SISTEMA DEBERÁ autenticar al operador y navegar a `/dashboard`.
- **AC-2:** CUANDO se ejecuta la consulta individual de prueba, EL SISTEMA DEBERÁ generar los jobs correspondientes y mostrar la información con documento redactado.
- **AC-3:** CUANDO se carga un archivo CSV en `/dashboard/masiva`, EL SISTEMA DEBERÁ detectar los registros no autorizados y marcarlos como excluidos.
- **AC-4:** CUANDO se procesa el lote, EL SISTEMA DEBERÁ completar el lote y bloquear solicitudes de reprocesamiento redundantes.
- **AC-5:** CUANDO se visita `/dashboard/historial`, EL SISTEMA DEBERÁ mostrar la lista cronológica de consultas.
- **AC-6:** CUANDO se visita `/dashboard/proveedores`, EL SISTEMA DEBERÁ mostrar los proveedores en estado operativo.
- **AC-7:** LA SUITE COMPLETA DEBERÁ correr de manera reproducible mediante `npm run test:e2e` con 6/6 tests en PASS.
