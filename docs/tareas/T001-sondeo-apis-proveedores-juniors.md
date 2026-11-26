# T001 — Sondeo de APIs de proveedores (primera tarea juniors)

**Asignados:** Jhon · Markos · Yeison · Pepito · **Revisor:** Jorge
**Tiempo estimado:** 2–3 h por persona · **Prioridad:** P0 · **Herramienta agéntica:** Antigravity
**Resultado esperado:** un script reproducible + un reporte de hallazgos por endpoint, entregados vía PR.

---

## 0. Lee antes de empezar (obligatorio)

1. `docs/plan-desarrollo-despliegue-gcp.md` §4 (contrato de proveedor).
2. Reglas inviolables §4 del `PROMPT-EQUIPO-DESARROLLO.md`. Las más importantes aquí:
   - **Consulta real autorizada (SÍ está permitida):** el caso (e) permite UNA
     consulta real con **tu propio documento** (autocercicio) o con un
     documento cuyo titular haya dado **autorización escrita** registrada en
     tu reporte. Esta es la validación que demuestra que el flujo completo
     funciona (respuesta 200 con datos reales).
   - **PROHIBIDO consultar documentos de terceros** sin autorización escrita
     del titular registrada en el reporte: familiares, amigos o números
     inventados que coincidan con personas reales por azar. Los datos de
     salud son sensibles (Ley 1581 de 2012) y el brief lo prohíbe (§15).
   - Por defecto los casos (a)–(d) usan documentos de prueba ficticios y
     pruebas de contrato que NO consumen datos (401/400/404); solo el caso
     (e) es la consulta real autorizada (máximo 1 intento, sin reintentos).
   - **PROHIBIDO subir a Git datos personales reales**: en `results.json`
     todo valor personal (nombre, número de documento, EPS, etc.) se
     redacta como `***` conservando el tipo y la estructura del campo. La
     respuesta cruda queda en `raw_response.json`, archivo en `.gitignore`.
   - **PROHIBIDO escribir la API key en el código, en el reporte o en el commit.** La key vive SOLO en una variable de entorno.

## 1. Asignación (un endpoint por desarrollador)

| Dev | Proveedor | Endpoint a sondear | Docs |
| --- | --- | --- | --- |
| **Jhon** | PlacApi | `POST https://placapi.com/api/eps` — afiliación en salud (ADRES/BDUA) | https://placapi.com/docs · https://placapi.com/openapi.json |
| **Markos** | PlacApi | `POST https://placapi.com/api/sisben` — clasificación SISBÉN IV (Ventanilla Social DNP) | ídem |
| **Yeison** | PlacApi | `POST https://placapi.com/api/rui` — grupo RUI (Ventanilla Social DNP) | ídem |
| **Pepito** | Árbol | `POST https://api.getarbol.com/v1/adres/affiliations/lookup` — ADRES | https://docs.getarbol.com/api/adres/ + `openapi.json` |

Pepito adicionalmente elabora la **matriz comparativa PlacApi vs Árbol** (sección 6.4) con los datos de los otros tres.

> Nota verificada 2026-11-26: el brief decía "PlacApi SISBÉN/RUI: /api/sisben".
> La documentación viva confirma endpoints **separados**: `/api/sisben` y
> `/api/rui`. Autenticación PlacApi: header `x-api-key` (sin CORS — la API es
> servidor-a-servidor). Árbol: header `Authorization: Bearer <token>` y
> requiere activar ADRES en Integrations de la cuenta.

## 2. Preparación (30 min)

1. Verifica acceso al repo y clónalo:
   ```bash
   git clone https://github.com/jorgeivangrisalesmarin-art/gestor-documental-social.git
   cd gestor-documental-social
   ```
2. Crea tu rama (reemplaza TU-NOMBRE y TU-ENDPOINT):
   ```bash
   git checkout -b tarea/T001-<tu-nombre>-<slug-endpoint>
   # ej: tarea/T001-jhon-placapi-eps
   ```
3. Crea tu carpeta de trabajo: `scripts/sondeo/<tu-nombre>-<slug-endpoint>/`
4. Si Jorge te entregó una API key, expórtala SOLO en tu sesión:
   ```bash
   export PROBE_API_KEY="pegala-aqui"   # no la pegues en ningún archivo
   ```
   Si **no** tienes key, tu sondeo es **modo contrato (sin credencial)**:
   verificas esquemas, OpenAPI, errores 401/400 y documentación. Es un
   entregable válido y esperado — NO pidas keys por tu cuenta, NO pruebes
   con claves encontradas en internet.

## 3. Qué hacer con Antigravity (y qué no)

Dale a tu agente UNA tarea a la vez. Prompt inicial sugerido (cópialo y ajusta el endpoint):

```
En scripts/sondeo/<tu-nombre>-<slug>/ crea un script en Python 3.12 (requests)
llamado probe.py que pruebe el endpoint <URL> con estas reglas:
1. Lee la credencial de la variable de entorno PROBE_API_KEY (nunca hardcode).
2. Ejecuta 4 casos y guarda resultados: (a) sin header de auth → espera 401;
   (b) auth inválida "PROBE-INVALID" → espera 401/403; (c) payload JSON válido
   con numero_documento "99999999999" (ficticio, 11 nueves) → espera 404/400 o
   respuesta "no encontrado" y registra el CONTRATO de respuesta (campos y tipos);
   (d) payload malformado (sin numero_documento) → espera 400/422.
3. Por cada caso registra: HTTP status, latencia ms, cuerpo completo (recortado
   a 2000 chars), timestamp UTC en ISO-8601.
4. Escribe salida en results.json (structured) y no imprimas la key jamás.
5. Timeout 15 s por request, máximo 2 reintentos solo en 429/5xx con backoff 5 s.
6. Si un caso consume créditos (respuesta 200 real), DETENTE tras el primer 200
   y márcalo en results.json como "consumo_credito: true".
7. SOLO si la variable de entorno PROBE_REAL_DOC está definida: ejecuta UNA
   única consulta real con ese documento (validación autorizada: autocercicio
   o titular con autorización escrita). Sin reintentos. En results.json los
   valores personales se reemplazan por "***" conservando tipo y estructura;
   la respuesta cruda va a raw_response.json y ese archivo se agrega a
   .gitignore. Guarda en results.json "validacion_real": {"ejecutada": true,
   "documento": "<tipo>+últimos 3 dígitos", "autorizacion": "autocercicio"}.
   Si PROBE_REAL_DOC no está definida, escribe "validacion_real":
   {"ejecutada": false} y no hagas la consulta real.
No agregues dependencias fuera de requests. Explica cada cambio antes de hacerlo.
```

**No permitas que el agente:** invente credenciales, consulte documentos de
terceros o repita la consulta real autorizada (el caso (e) es UN solo intento
y solo cuando `PROBE_REAL_DOC` esté definida), suba archivos `.env` o
`raw_response.json`, ni "complete" datos que no existen en la respuesta real.
Si el agente propone algo de eso, recházalo y anótalo en tu reporte (sección
"desviaciones del agente").

**Valida tú mismo:** ejecuta el script, revisa el código línea por línea (debes
poder explicarlo en la revisión con Jorge), y verifica que `results.json` no
contenga la key ni datos personales.

## 4. Ejecución y evidencia

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install requests
python scripts/sondeo/<tu-carpeta>/probe.py

# Validación real autorizada (opcional pero recomendada): tu propio documento.
# NUNCA el documento de un tercero. Un solo intento, sin reintentos.
export PROBE_REAL_DOC='CC,<tu-numero-de-cedula>'
python scripts/sondeo/<tu-carpeta>/probe.py
```

- Con el caso (e) en 200: registra el **contrato completo real** (nombres de
  campos, tipos, anidación de la respuesta) — es el insumo definitivo para
  T005. NO repitas la consulta: un solo consumo por endpoint.
- Antes de commitear, verifica la redacción: `grep -v '***' results.json` no
  debe mostrar tu nombre, número de documento ni EPS. `raw_response.json`
  debe estar en `.gitignore` (nunca se sube).
- Si **no** hay key o el endpoint responde 401/402: completa el modo contrato
  (OpenAPI + errores) y marca `blocked_by: "credencial"` en el reporte.
- Guarda `results.json` y las respuestas crudas (sin key) en tu carpeta.

## 5. Reporte de hallazgos

Escribe `scripts/sondeo/<tu-carpeta>/REPORTE.md` con estas secciones exactas:

1. **Endpoint y propósito** (qué documento del negocio cubre).
2. **Autenticación observada** (header, errores de auth).
3. **Contrato de respuesta** (tabla campo/tipo/descripción según evidencia real u OpenAPI; indicar cuál fuente).
4. **Resultados de los 5 casos** (tabla caso/status/latencia/conclusión; el
   caso (e) solo si ejecutaste la validación real autorizada).
5. **Rate limits y errores** (lo que la documentación declara + lo observado).
6. **Costos/créditos** (lo documentado; indicar si algún caso consumió créditos).
7. **Riesgos y limitaciones para T005** (ej. "no entrega PDF oficial", "sin CORS").
8. **Desviaciones del agente** (qué tuviste que corregirle a Antigravity).
9. **Estado final**: `completo` / `completo-modo-contrato` / `blocked_by: credencial`.

## 6. Entregables y flujo Git

| # | Entregable | Ruta |
| --- | --- | --- |
| 1 | Script reproducible | `scripts/sondeo/<tu-carpeta>/probe.py` |
| 2 | Resultados estructurados | `scripts/sondeo/<tu-carpeta>/results.json` |
| 3 | Reporte de hallazgos | `scripts/sondeo/<tu-carpeta>/REPORTE.md` |
| 4 | (Solo Pepito) Matriz comparativa | `docs/T001-matriz-proveedores.md` |

```bash
git add scripts/sondeo/<tu-carpeta>/   # NUNCA git add . (evita subir .env)
git commit -m "feat(T001): sondeo <endpoint> — <estado>"
git push -u origin tarea/T001-<tu-nombre>-<slug-endpoint>
```

Abre el PR hacia `main` con este cuerpo:

```
T001 — Sondeo <proveedor>/<endpoint>
Dev: <nombre> · Estado: <completo | completo-modo-contrato | blocked_by>
Validación real autorizada: <sí (autocercicio) | no>
Qué se hizo: <2 líneas>
Cómo se verificó: <los casos + evidencia; datos personales redactados>
Criterios: AC-1..AC-7 [PASS|FAIL por cada uno]
Riesgos para T005: <1 línea>
```

## 7. Criterios de aceptación (EARS — los revisa Jorge en el PR)

- **AC-1** CUANDO se ejecuta `probe.py` sin `PROBE_API_KEY` EL SCRIPT DEBERÁ
  ejecutar el caso (a), reportar el status recibido y terminar sin errores no
  controlados (exit code 0 o 1 con mensaje claro, nunca traceback crudo).
- **AC-2** CUANDO se define `PROBE_API_KEY` EL SCRIPT DEBERÁ ejecutar los 4
  casos y escribir `results.json` con status, latencia y timestamp por caso.
- **AC-3** EL SCRIPT DEBERÁ fallar de inmediato (sin hacer requests) si
  detecta su propia key escrita en el código (chequeo anti-hardcode).
- **AC-4** EL REPORTE DEBERÁ documentar el contrato del endpoint con fuente
  citada (respuesta real u OpenAPI) y declarar explícitamente si algún caso
  consumió créditos o si el sondeo quedó bloqueado por credencial.
- **AC-5** CUANDO `PROBE_REAL_DOC` está definida EL SCRIPT DEBERÁ realizar
  exactamente UNA consulta real sin reintentos y escribir en `results.json`
  todo valor personal redactado como `***` conservando tipo y estructura,
  además del registro `validacion_real` con tipo de autorización.
- **AC-6** CUANDO `PROBE_REAL_DOC` no está definida EL SCRIPT DEBERÁ completar
  los casos (a)–(d), marcar `validacion_real.ejecutada = false` y NO efectuar
  ninguna consulta con documento real.
- **AC-7** EL PR DEBERÁ contener `raw_response.json` en `.gitignore` y ningún
  archivo versionado con datos personales sin redactar.

## 8. Definition of Done de T001

Script + results.json + REPORTE.md en tu rama → PR abierto → revisión de
Jorge (PASS/FAIL por AC) → merge a `main` lo aprueba **solo Jorge**. Cualquier
duda de alcance se consulta en el canal del equipo citando el número de
criterio — no se improvisa.
