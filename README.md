# Gestor Documental Social

**Sistema de Automatización Documental ADRES + SISBÉN IV + RUI**  
Solución de consulta, verificación y generación documental sobre registros sociales y de salud de Colombia, desplegada en **Google Cloud**.

---

## 🏛️ Arquitectura del Monorepo

```
├── .github/workflows/ci.yml       # Integración Continua (GitHub Actions)
├── .kiro/specs/                   # Especificaciones EARS (Capa 3)
│   └── motor-documental/          # Contrato DocumentProvider y reglas
├── api/                           # Backend FastAPI (Python 3.12+)
│   ├── app/
│   │   ├── main.py                # Aplicación FastAPI y middlewares
│   │   ├── core/config.py         # Configuración y settings Pydantic
│   │   └── api/                   # Routers y endpoints REST
│   └── tests/                     # Suite de pruebas automatizadas con pytest
├── web/                           # Frontend Web estático / Cloud Run
│   ├── index.html                 # Interfaz de funcionario público
│   ├── app.js                     # Lógica de cliente y verificación de salud
│   └── style.css                  # Estilos responsivos
├── docs/                          # Documentación técnica, ADRs y tareas
├── scripts/                       # Scripts de sondeo de proveedores (T001)
├── .env.example                   # Plantilla de configuración segura
└── Makefile                       # Automatización de tareas de desarrollo
```

---

## 🚀 Puesta en Marcha Local

### 1. Requisitos Previos
* Python 3.12 o superior.
* Entorno virtual de Python.

### 2. Instalación de Dependencias
```bash
python -m venv .venv
# En Windows:
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate

pip install -r api/requirements.txt
```

### 3. Configuración del Entorno
Copia la plantilla y configura tus credenciales locales:
```bash
cp .env.example .env
```

### 4. Ejecución del Backend
```bash
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* **API Documentación OpenAPI (Swagger):** `http://localhost:8000/docs`
* **Endpoint de Salud:** `http://localhost:8000/health`

### 5. Ejecución de Pruebas
```bash
cd api
pytest -v
```

### 6. Frontend Web
Abre directamente `web/index.html` en tu navegador o sírvelo con un servidor estático local. Se conectará automáticamente al endpoint `/health` de la API en el puerto 8000.

---

## 🛡️ Seguridad y Datos Personales (Ley 1581 de 2012)
* Ninguna API key ni secreto vive en el código fuente.
* Los números de identificación se procesan mediante HMAC-SHA256 para auditoría.
* Las consultas con datos reales exigen autorización previa del titular.
