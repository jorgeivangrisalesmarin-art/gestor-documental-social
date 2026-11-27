# Tasks — Motor Documental (MVP)

Cada paquete termina con verificación explícita contra `requirements.md`.

- [x] T002 ADRs 0001–0007 (adr-kit, aprobados)
- [ ] T003 Scaffold repo (api/, web/, compose, Makefile, .env.example) — verificar: `make check` corre lint sin código roto
- [ ] T004 Contrato DocumentProvider + errores tipados + fixtures (E8) — verificar: pytest unit de contrato
- [ ] T005 Adaptadores PlacApi eps/sisben/rui con reintentos (E6, E7) — verificar: pytest con respx/httpx mock + modo real bloqueado sin key
- [ ] T006 Modelos + seguridad + storage (E10, E12) — verificar: pytest de security y storage
- [ ] T007 API REST auth/lookups/documents (E1–E5, E9–E12, E17, E18) — verificar: pytest integración
- [ ] T009 Lotes CSV in-process (E13–E16) — verificar: pytest con CSV de prueba
- [ ] T008 Frontend Next.js (login, dashboard, consulta, masiva, historial) — verificar: build + Playwright
- [ ] T013 E2E + TEST_REPORT + README — verificar: suite completa verde + capturas
