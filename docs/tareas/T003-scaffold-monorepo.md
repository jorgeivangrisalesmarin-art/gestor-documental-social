# T003 — Scaffold del Monorepo (FastAPI + Web + Specs + CI)

**Asignados:** Jorge (Tech Lead) · Yeison (Junior Developer)  
**Tiempo estimado:** 6 h · **Prioridad:** P0 · **Herramienta agéntica:** Antigravity  
**Resultado esperado:** Estructura monorepo reproducible con backend FastAPI (`api/`), frontend web (`web/`), especificaciones EARS (`.kiro/specs/`), CI base (`.github/workflows/ci.yml`), `.env.example`, `Makefile` y suite de pruebas en verde.

---

## 1. Contexto y Objetivos

Con base en el plan de desarrollo de Google Cloud (`docs/plan-desarrollo-despliegue-gcp.md`) y el brief del producto:
1. El backend debe estructurarse como un monolito modular con **Python 3.12+ y FastAPI**, async nativo y validación estricta con **Pydantic v2**.
2. El frontend debe residir en `web/` listo para servirse de forma estática o montarse en Cloud Run `web`.
3. La configuración debe seguir el estándar de 12 factores: variables de entorno con fallback seguro, documentadas en `.env.example` sin quemar secretos.
4. El repositorio debe poder inicializarse y probarse con comandos reproducibles (`make dev`, `make test`).

---

## 2. Criterios de Aceptación (EARS)

- **AC-1:** CUANDO un desarrollador clona el repositorio e instala las dependencias de `api/`, EL BACKEND DEBERÁ iniciar localmente con `uvicorn` exponiendo los endpoints `/health` y `/docs` (OpenAPI).
- **AC-2:** CUANDO se consulta el endpoint `GET /health`, EL SISTEMA DEBERÁ responder HTTP 200 con JSON conteniendo `status: "ok"`, versión de la aplicación y timestamp UTC.
- **AC-3:** CUANDO se ejecutan las pruebas automatizadas con `pytest`, EL SISTEMA DEBERÁ ejecutar la suite de pruebas unitarias y finalizar con 100% de tests en verde.
- **AC-4:** EL REPOSITORIO DEBERÁ contener un archivo `.env.example` con todas las variables requeridas (claves de proveedores, secretos HMAC, conexiones de DB y Redis) con valores de ejemplo ficticios.
- **AC-5:** EL MONOREPO DEBERÁ contener la especificación EARS base en `.kiro/specs/motor-documental/` definiendo el contrato `DocumentProvider`.
- **AC-6:** EL REPOSITORIO DEBERÁ incluir la configuración de CI (`.github/workflows/ci.yml`) que ejecute linting y testing automáticamente en cada Push o Pull Request.

---

## 3. Estructura de Archivos Objetivo

```
├── .github/workflows/ci.yml        # CI Pipeline en GitHub Actions
├── .kiro/specs/                    # Especificaciones EARS Capa 3
│   └── motor-documental/
│       ├── requirements.md
│       └── design.md
├── api/                            # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Aplicación FastAPI
│   │   ├── core/                   # Configuración y seguridad
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   └── api/                    # Endpoints REST
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── health.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py
│   └── requirements.txt
├── web/                            # Frontend Web (UI funcionario)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .env.example                    # Plantilla de variables de entorno
├── Makefile                        # Automatización make dev / test
└── README.md                       # Documentación principal de puesta en marcha
```

---

## 4. Entregables y Verificación

1. Rama Git: `tarea/T003-yeison-scaffold-monorepo`
2. Ejecución de `pytest` en `api/` con resultado 100% PASS.
3. Ejecución local del servidor FastAPI verificando `http://localhost:8000/health`.
4. PR hacia `main` con verificación EARS completa.
