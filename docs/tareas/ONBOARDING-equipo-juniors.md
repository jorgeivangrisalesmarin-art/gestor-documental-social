# ONBOARDING — Equipo juniors (Jhon, Markos, Yeison, Pepito)

Sesión de arranque para trabajar en el **Gestor Documental Social** con tu agente
(Antigravity). Tiempo de setup: ~30 min. Antes de empezar, lee al final de este
documento las REGLAS — son de cumplimiento estricto.

## 1. Requisitos

- Git, **Python 3.12+**, **Node 22+**, editor (Antigravity), cuenta GitHub con acceso al repo.
- Acceso: `github.com/jorgeivangrisalesmarin-art/gestor-documental-social` (si no puedes clonar, avísale a Jorge para que te agregue como colaborador).

## 2. Clonar y actualizarte

```bash
git clone https://github.com/jorgeivangrisalesmarin-art/gestor-documental-social.git
cd gestor-documental-social
git checkout main && git pull origin main
```

## 3. Backend (FastAPI) — 10 min

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e "./api[dev]"
cp .env.example api/.env           # NO pongas keys reales en ese archivo
cd api && uvicorn app.main:app --reload --port 8000
```

Verifica: abre `http://localhost:8000/health` → `{"status":"ok"}`.
Si el puerto 8000 está ocupado, usa otro (ej. `--port 8001`) y en el paso 4
reconstruye el frontend con `NEXT_PUBLIC_API_URL=http://localhost:8001 npm run build`.

## 4. Frontend (Next.js) — 10 min

```bash
cd web
npm install
npm run dev     # http://localhost:3000
```

Login inicial de desarrollo: `admin@local.test` / `admin1234`.

## 5. Modo de los proveedores (IMPORTANTE)

Sin API key configurada, el sistema corre en **modo fixture**: los datos son
FICTICIOS y aparecen etiquetados así en pantalla. Es el modo correcto para
desarrollar. La API key real de PlacApi es de Jorge — **nunca la compartas por
chat/WhatsApp ni la subas al repo**. Si Jorge te autoriza una key para tu
tarea, se usa SOLO como variable de entorno en tu terminal:

```bash
export PROBE_API_KEY="<la que Jorge te indique>"
```

## 6. Tu tarea actual

| Quién | Tarea | Documento |
|---|---|---|
| Todos | **T001 — sondeo de APIs** (script + reporte + PR) | `docs/tareas/T001-sondeo-apis-proveedores-juniors.md` |
| Jhon | T015: export ZIP de lotes + pulir normalizador eps | ticket en canal del equipo |
| Markos | T016: XLSX masivo + separar EXCLUDED del conteo de errores | ídem |
| Yeison | T017: suite Playwright de regresión (6 flujos E2E) | ídem |
| Pepito | T018: adaptador Árbol ADRES + matriz comparativa | ídem |

Empieza T001 aunque tengas asignada una tarea T01x: el contrato real que
produzcas alimenta a todo el equipo.

## 7. Flujo de trabajo obligatorio

1. Rama desde `main` actualizada: `git checkout -b tarea/T001-<tu-nombre>-<slug>`
2. Trabaja con Antigravity, **validando todo lo que el agente produce** (tú respondes por el resultado).
3. Antes de abrir PR: `make check` (ruff + pytest) y, si tocaste el web, `npm run build`.
4. Commit: `feat|docs|test(T001): resumen` — nunca `git add .` (sube basura/secretos).
5. Push de tu rama + Pull Request hacia `main` con el cuerpo definido en el documento de tu tarea.
6. **Jorge revisa y aprueba el merge.** Los juniors NO hacen merge ni despliegan.

## 8. Reglas inviolables (resumen — el detalle está en `PROMPT-EQUIPO-DESARROLLO.md`)

1. Documentos de terceros: SOLO con autorización escrita del titular. El autocercicio (tu propio documento) vale para validar.
2. Ninguna key/secret en código, tests, reportes o commits.
3. Los datos fixture son FICTICIOS: jamás los presentes como reales.
4. No consultes endpoints internos de portales oficiales ni evas controles (CAPTCHA, etc.).
5. Si tu agente propone algo prohibido, recházalo y regístralo en tu reporte.

Dudas de alcance: canal del equipo citando el criterio (E#/AC#) — no se improvisa.
