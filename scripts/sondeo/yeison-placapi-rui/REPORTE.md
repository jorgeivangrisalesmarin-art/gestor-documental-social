# Reporte de Hallazgos — Sondeo PlacApi RUI (T001)

**Desarrollador:** Yeison (Junior Developer)  
**Endpoint:** `POST https://placapi.com/api/rui`  
**Proveedor:** PlacApi  
**Fecha de ejecución:** 2026-11-26 (UTC)  
**Estado final:** `completo`

---

## 1. Endpoint y propósito

* **Endpoint:** `POST https://placapi.com/api/rui`
* **Módulo de negocio:** Registro Universal de Ingresos (RUI) y Clasificación Sisbén IV (Ventanilla Social del Departamento Nacional de Planeación - DNP).
* **Propósito en el Gestor Documental Social:**  
  Permite consultar la clasificación socioeconómica de una persona natural ante los registros sociales del Estado colombiano. El RUI es el instrumento de focalización que complementa y actualiza la clasificación del Sisbén IV para determinar la elegibilidad y asignación de subsidios y programas sociales.
* **Documento del negocio que cubre:**  
  Reporte de grupo y nivel socioeconómico en el Registro Universal de Ingresos (RUI) y grupo Sisbén IV por número y tipo de documento de identidad.

---

## 2. Autenticación observada

* **Header requerido:** `x-api-key: <PROBE_API_KEY>` (o alternativamente `Authorization: Bearer <PROBE_API_KEY>`).
* **Tipo de autenticación:** API Key de servidor a servidor (sin soporte CORS).
* **Comportamiento observado:**
  * **Sin header de autenticación (Caso a):**  
    Responde HTTP `401 Unauthorized` con latencia promedio de ~398 ms:
    ```json
    {
      "error": "Falta autenticación. Envía tu API key en el header 'x-api-key' (o 'Authorization: Bearer pk_live_…'). Genera una en /integracion.",
      "code": "unauthorized"
    }
    ```
  * **Header con API Key inválida (Caso b):**  
    Responde HTTP `401 Unauthorized` con latencia promedio de ~382 ms:
    ```json
    {
      "error": "API key inválida o revocada.",
      "code": "unauthorized"
    }
    ```

---

## 3. Contrato de respuesta

Fuente: **Evidencia real (Caso e) contrastada y validada con OpenAPI oficial (`https://placapi.com/openapi.json`)**.

### Estructura del cuerpo de respuesta (HTTP 200)

| Campo | Tipo | Fuente | Descripción |
| :--- | :--- | :---: | :--- |
| `source` | `string` | Evidencia real | Identificador de la fuente oficial (`"clasificacion-social"`). |
| `fetchedAt` | `string (ISO-8601)` | Evidencia real | Fecha y hora UTC en que se consultó la fuente oficial. |
| `mode` | `string` | Evidencia real | Modo de ejecución del proveedor (`"live"` o `"cached"`). |
| `status` | `string` | Evidencia real | Estado de la respuesta (`"ok"`, `"info"` o `"unknown"`). |
| `cost` | `integer` | Evidencia real | Créditos cobrados por la consulta (1 crédito si hay datos). |
| `data` | `object` | Evidencia real | Contenedor principal con los datos del ciudadano. |
| `data.documento` | `string` | Evidencia real | Número del documento consultado. |
| `data.tipoDocumento`| `string` | Evidencia real | Tipo de documento (`CC`, `TI`, `CE`, etc.). |
| `data.persona` | `object` | Evidencia real | Datos demográficos de la persona. |
| `data.persona.nombre` | `string` | Evidencia real | Nombre completo según registro oficial. |
| `data.persona.sexo` | `string` | Evidencia real | Sexo de la persona (`"Masculino"` / `"Femenino"`). |
| `data.persona.edad` | `integer` | Evidencia real | Edad en años de la persona. |
| `data.ubicacion` | `object` | Evidencia real | Ubicación geográfica del registro social. |
| `data.ubicacion.departamento` | `string` | Evidencia real | Nombre del departamento (ej. `"ANTIOQUIA"`). |
| `data.ubicacion.municipio` | `string` | Evidencia real | Nombre del municipio. |
| `data.ubicacion.codigoMunicipio` | `string` | Evidencia real | Código DANE municipal (ej. `"05001"`). |
| `data.sisben` | `object` | Evidencia real | Clasificación SISBÉN IV asociada. |
| `data.sisben.grupo` | `string` | Evidencia real | Letra del grupo Sisbén (`"A"`, `"B"`, `"C"`, `"D"`). |
| `data.sisben.nivel` | `string` | Evidencia real | Nivel específico (ej. `"B6"`, `"C15"`). |
| `data.sisben.descripcion` | `string` | Evidencia real | Categoría de pobreza/vulnerabilidad. |
| `data.rui` | `object` | Evidencia real | Registro Universal de Ingresos. |
| `data.rui.tieneClasificacion` | `boolean` | Evidencia real | `true` si la persona tiene grupo RUI activo. |
| `data.rui.grupo` | `string` | Evidencia real | Grupo RUI asignado. |
| `data.rui.nivel` | `string` | Evidencia real | Nivel RUI específico. |
| `data.rui.grupoIngresos` | `string` | Evidencia real | Descripción del grupo de ingresos. |

### Respuesta cuando no existe registro (HTTP 404)
Observada en el Caso (c) con documento ficticio:
```json
{
  "source": "clasificacion-social",
  "fetchedAt": "2026-11-27T00:47:58.200Z",
  "mode": "live",
  "status": "unknown",
  "data": null,
  "error": "La persona no se encuentra registrada",
  "errorCode": "consulta_sin_resultado",
  "code": "consulta_sin_resultado"
}
```

---

## 4. Resultados de los 5 casos

| Caso | Descripción | Status HTTP | Latencia (ms) | Conclusión / Resultado |
| :---: | :--- | :---: | :---: | :--- |
| **(a)** | Sin header de autenticación | **401** | 398.07 ms | **PASS** — Rechazo inmediato por falta de credenciales. |
| **(b)** | Header con `x-api-key: PROBE-INVALID` | **401** | 382.50 ms | **PASS** — Rechazo controlado con mensaje `API key inválida o revocada`. |
| **(c)** | Payload válido con doc ficticio (`99999999999`) | **404** | 376.51 ms (caché) / 7,675 ms (live) | **PASS** — Retorna `consulta_sin_resultado`, `data: null`, sin consumo de crédito. |
| **(d)** | Payload malformado (sin `docNumber`) | **400** | 387.44 ms | **PASS** — Error de validación estructurado con `details.fieldErrors.docNumber`. |
| **(e)** | Validación real autorizada (autocercicio) | **200** | 2,085.38 ms | **PASS** — Retorna datos completos RUI + SISBÉN IV. Datos redactados en `results.json`. |

> **Registro de autorización del Caso (e):**  
> * Modalidad: **Autocercicio** (propio documento del desarrollador junior Yeison).  
> * Consulta realizada: Exactamente **1 intento** (sin reintentos).  
> * Consumo de créditos: **1 crédito**.  
> * Protección: Valores personales redactados como `***` en `results.json`; respuesta cruda resguardada en `raw_response.json` (protegida por `.gitignore`).

---

## 5. Rate limits y errores

* **Rate limit declarado:**  
  1,000 consultas por minuto por API Key. Al excederse, responde HTTP `429 Too Many Requests` con header `Retry-After` y código `rate_limited`.
* **Errores observados y mapeados:**
  * `400 Bad Request` (`code: bad_request`): Fallo de esquema (falta `docNumber`, tipo de documento no soportado).
  * `401 Unauthorized` (`code: unauthorized`): Ausencia de credencial o clave revocada.
  * `402 Payment Required` (`code: no_credits`): Saldo insuficiente de créditos prepagados.
  * `404 Not Found` (`code: consulta_sin_resultado`): Persona no encontrada en el DNP.
  * `502 Bad Gateway` (`code: source_error`): Falla o timeout en la conexión hacia la Ventanilla Social del DNP.

---

## 6. Costos y créditos

* **Modelo:** Prepago por créditos (`x-credits: 1`).
* **Costo por consulta con datos (200):** 1 crédito ($349 COP aprox.).
* **Consultas sin resultado (404):** Incluye 10 consultas gratuitas al mes por código de sin-resultado; a partir de la 11 se cobra 1 crédito.
* **Caché y duplicados:**
  * Consultas repetidas idénticas devuelven `fromCache: true` sin costo dentro de la ventana de vigencia (hasta 30 días).
  * Reintentos dentro de los 10 segundos son reembolsados bajo el motivo `duplicado_reciente`.
* **Consumo durante este sondeo:**  
  * Casos (a), (b), (c) y (d): **0 créditos consumidos**.  
  * Caso (e) (validación real autorizada): **1 crédito consumido**.  
  * **Total créditos consumidos:** 1 crédito.

---

## 7. Riesgos y limitaciones para T005 (Adaptadores)

1. **Ausencia de PDF oficial:**  
   El endpoint entrega únicamente datos en JSON estructurado; **no emite un certificado oficial en PDF emitido por el DNP**.  
   * *Mitigación para T005/T006:* Mantener el documento en estado `DOCUMENT_PENDING` según la regla inviolable #4 del proyecto, o generar un reporte institucional de consulta aclarando expresamente que es un reporte informativo y no un certificado oficial del DNP.
2. **Latencia variable de la fuente oficial:**  
   La primera consulta a la Ventanilla Social del DNP puede tardar entre 2 y 8 segundos si no está en caché.  
   * *Mitigación:* Configurar timeout mínimo de 15s y encolamiento asíncrono para consultas masivas.
3. **Sin CORS:**  
   La API rechaza peticiones directas desde navegadores web. Todas las consultas deben intermediarse obligatoriamente a través del backend FastAPI.
4. **Endpoint unificado RUI + SISBÉN:**  
   Aunque el endpoint se denomina `/api/rui`, PlacApi retorna el objeto unificado de clasificación social conteniendo simultáneamente los nodos `sisben` y `rui`.  
   * *Mitigación:* El adaptador de T005 debe parsear y normalizar ambos bloques independientemente según el tipo de documento solicitado en el contrato `DocumentProvider`.

---

## 8. Desviaciones del agente

Durante el desarrollo de esta tarea con Antigravity, se presentaron y corrigieron las siguientes situaciones:
1. **Evaluación booleana de `requests.Response`:**  
   Inicialmente el código evaluaba `status_code = resp.status_code if resp else 0`. En Python, la librería `requests` sobreescribe el operador `__bool__` devolviendo `False` para respuestas con códigos HTTP 4xx y 5xx (`self.ok`). Se corrigió a `if resp is not None:` para capturar fielmente el status 401 en el Caso (a) sin generar reportes erróneos.
2. **Mapeo de nombres de atributos (`docNumber` vs `numero_documento`):**  
   El prompt sugería enviar `numero_documento`, pero la especificación OpenAPI de PlacApi exige estrictamente `docNumber` (o alias `doc`). El script fue ajustado para enviar `docNumber`, asegurando el cumplimiento exacto del contrato del proveedor.

---

## 9. Estado final

`completo`
