# **Documento de dirección técnica y plan de desarrollo**

## **MVP: Sistema de consulta y descarga de reportes ADRES \+ SISBÉN IV / RUI**

Especificación para desarrollo  
Claude Code / Antigravity

**Decisión de producto:** no vamos a desarrollar inicialmente un chatbot ni una integración con WhatsApp. Primero construiremos un motor de automatización documental que funcione de manera independiente, tanto para consultas individuales como para procesamiento masivo controlado.

La visión es convertirlo posteriormente en el motor de un asistente de IA que atienda a los ciudadanos por WhatsApp Business.

## **1\. Entendimiento del negocio**

Hay un caso de uso concreto que debe orientar todas las decisiones técnicas.

**Marques trabaja en el área del SISBÉN de la Alcaldía de Andes, Antioquia.**

Actualmente, los ciudadanos llegan a su ventanilla y solicitan dos documentos:

1. Reporte de afiliación a EPS, consultado en ADRES.  
2. Documento que acredita su puntaje o clasificación SISBÉN.

Marques debe realizar las consultas, obtener los documentos y entregarlos al ciudadano.

El problema no es que el funcionario no sepa realizar las consultas. El problema es que debe invertir tiempo en ejecutar repetidamente un proceso administrativo que podría automatizarse.

La oportunidad comercial consiste en ofrecerle un servicio que permita delegar esa tarea.

**Flujo actual**

**Ciudadano**

Solicita documentos en la ventanilla

**Marques – Funcionario SISBÉN**

Recibe los datos y realiza las consultas

**ADRES**

Reporte de afiliación EPS

**SISBÉN**

Certificado de clasificación

**Entrega de documentos al ciudadano**

**Flujo futuro**

Marques solicita el documento mediante WhatsApp Business y un asistente realiza el proceso, recupera los documentos oficiales y los entrega por el mismo canal, cuando se hayan validado la identidad, autorización y finalidad de la consulta.

**Marques – WhatsApp Business**

Solicita el documento autorizado

**Asistente de IA**

Identifica la solicitud y obtiene los datos necesarios

**Motor de automatización documental**

Consulta ADRES y SISBÉN/RUI

**Entrega de documentos**

PDF oficiales, identificados y organizados

## **2\. Estrategia de desarrollo: separar el producto en fases**

Hay una decisión arquitectónica fundamental: el motor de automatización no debe depender de WhatsApp, de un modelo de IA ni de un proveedor específico.

| Fase | Producto | Objetivo |
| ----- | ----- | ----- |
| 1 | Motor documental | Consultar y descargar documentos ADRES y SISBÉN/RUI |
| 2 | Asistente de IA | Interpretar solicitudes y coordinar el motor |
| 3 | WhatsApp Business | Atender solicitudes desde WhatsApp |
| 4 | SaaS empresarial | Incorporar otras alcaldías y organizaciones |

Objetivo inmediato  
**Fase 1: MVP funcional en 3 horas.**

Una aclaración importante: tres horas es un objetivo de construcción de una primera versión funcional, no una garantía de que podamos resolver en ese tiempo los accesos institucionales, la autorización jurídica o la descarga automática de ambos PDF oficiales. Si alguna fuente impone una restricción, el MVP debe mostrar ese estado y conservar la capacidad de continuar cuando se habilite el acceso.

## **3\. Precisión funcional: los tres documentos deben estar separados**

No vamos a crear una función genérica llamada `generar_certificado_sisben`.

El sistema tendrá tres tipos documentales independientes:

[Verificaciones \- ECAT](https://images.openai.com/static-rsc-4/4Vjzf9cjF5rW-Ij_aGU-5cW5AD8b0EVE2vD9Bm27bX1mPpWn5iq16IEouRfAh4siYIOlKbC-8sYcUiaoR-J1TJCN6DD5R2u_3oBJEA8iGSINPfL8M6ESV_AAzuhg-r6A7rNSvIWahUI9Hd9lKvIj01BX4HUVBExNDpRivwK-_1k?purpose=inline)

**1\. Reporte de afiliación ADRES**

ADRES / BDUA

* Fuente: ADRES.  
* Consulta: tipo y número de documento.  
* Resultado: EPS, régimen, estado y demás datos publicados.  
* Documento: reporte de consulta de afiliación.

[Actualizar información en Sisbén IV: cómo hacerlo de forma presencial o virtual \- NoticiasCaracol](https://images.openai.com/static-rsc-4/s35aCaVGcqA6Z1gdkTXcu468UfJNWtN_uol7JAe_-86dGY5mPIX5gmlwUde7MCUkfL56KzuB_vJ8RYqBoxx1QCH196UqB1TKgsMLQpfx4rLsmPj82xATXucLKipYhLaoLiGdUFLSHxs7-wLI75BcgzR2Hsfreg6kyZjkYRO9wmw?purpose=inline)

**2\. Certificado de clasificación SISBÉN IV**

SISBÉN IV

* Fuente: consulta tradicional SISBÉN.  
* Resultado: grupo A, B, C o D y subgrupo.  
* Documento: certificado o consulta oficial de clasificación SISBÉN IV.

[Portal del Sistema de Informacion Territorial SIT del Archipielago San Andres, Providencia y Santa Catalina](https://images.openai.com/static-rsc-4/4vPwgN9PXAIOEDPCd3iMw16N5bojqBNEwfaA1PPV3V7zDqLP2NIzWKnr2qW43SX0D5JaZLerG6nYTNt1yQUFqlFLPfGO_92t4cXf9HtnU28HEbaYTnThEL7F7zVaRbtvQw7EaRyluAsKJz1wLEDD7-9YXBZVrTcBUgRM4vPS_aA?purpose=inline)

**3\. Certificado del Registro Universal de Ingresos**

RUI / Ventanilla Social

* Fuente: Ventanilla Social del DNP.  
* Resultado: clasificación socioeconómica del hogar.  
* Documento: certificado del RUI.

Los tres documentos deben tener identificadores, conectores, metadatos y estados independientes. El sistema no debe sustituir uno por otro ni asumir que obtener los datos JSON equivale a descargar el documento oficial.

Esta separación también es coherente con el Decreto 1621 de 2026: el SISBÉN IV continúa durante el régimen de transición, previsto hasta el 31 de diciembre de 2027\.

Gestor Normativo+2

## **4\. Evaluación de las dos herramientas para construir el motor propio**

He revisado los repositorios que compartiste. Mi recomendación es utilizarlos, pero con funciones diferentes.

### **4.1. Replica Skill**

[Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill?utm_source=chatgpt.com)  
Recomendado para arquitectura y reconstrucción funcional

Este proyecto ofrece once habilidades para investigar y reconstruir funcionalidades de aplicaciones.

Las que más nos interesan son:

| Skill | Aplicación en nuestro proyecto |
| ----- | ----- |
| `replica-recon` | Investigar el flujo de ADRES y SISBÉN |
| `replica-architect` | Diseñar los conectores propios |
| `replica-backend` | Construir las integraciones |
| `replica-build` | Implementar la aplicación |
| `replica-test` | Validar consultas y descargas |
| `replica-diff` | Comparar nuestros flujos con las fuentes de referencia |

Replicar las funcionalidades del siguiente referente: [https\://placapi.com/](https://placapi.com/)

Replicar las funcionalidades del siguiente referente: [https\://www\.getarbol.com/developers/](https://www.getarbol.com/developers/)

El repositorio indica que sus habilidades reconstruyen funcionalidades y flujos mediante un enfoque clean-room: no copian código, marca, textos ni contenido propietario de las aplicaciones analizadas. Su licencia es MIT.

GitHub+1

**Cómo lo utilizaría:** para analizar las funcionalidades de los proveedores y diseñar una implementación propia que tenga una interfaz de consulta y un sistema de gestión documental equivalentes en comportamiento, pero con nuestro código y diseño.

### **4.2. REA – Reverse Engineer Anything**

[morluto/rea](https://github.com/morluto/rea?utm_source=chatgpt.com)  
Recomendado como herramienta de investigación técnica

REA es más interesante para investigar el comportamiento técnico de las aplicaciones.

Puede ayudar a:

* Inspeccionar la estructura DOM de los portales.  
* Identificar scripts y recursos.  
* Analizar bundles JavaScript.  
* Observar metadatos de red de sesiones autorizadas.  
* Investigar candidatos de endpoints.  
* Examinar aplicaciones web sin tener su código fuente.  
* Obtener evidencia técnica de los hallazgos.

REA se integra con agentes mediante MCP y dispone de instrucciones para Claude Code y otros agentes compatibles.

GitHub+2

Instalación:

```
npx rea-agents setup
```

**Advertencia técnica importante:** REA no es una herramienta general de automatización de formularios ni un sistema para eludir CAPTCHA. Su observación de páginas mediante CDP es pasiva. Para automatizar navegadores, usaremos Playwright de forma independiente.

### **4.3. Cómo combinarlos**

**REA**

Investigación técnica de fuentes y proveedores y replicar funcionalidades de componentes de proveedores referentes.

**Replica Skill**

Reconstrucción funcional y arquitectura propia

**Motor propio ADRES \+ SISBÉN \+ RUI**

Conectores independientes y proveedores intercambiables

Una distinción esencial para el desarrollo: nuestro motor propio no debe intentar copiar los mecanismos privados de los proveedores ni extraer credenciales o replicar endpoints internos sin autorización. Debe implementar los contratos funcionales de consulta, normalización, validación y gestión documental mediante fuentes y mecanismos legítimos.

# **PROJECT BRIEF \+ MASTER DEVELOPMENT PROMPT**

# **Sistema de automatización documental ADRES \+ SISBÉN IV \+ RUI**

**Versión:** 1.0  
**Fecha:** 21 de noviembre de 2026  
**Prioridad:** MVP funcional en 3 horas  
**Agentes de desarrollo:** Claude Code / Antigravity  
**Tipo de producto:** Aplicación web empresarial \+ API REST  
**Mercado inicial:** Alcaldías y organizaciones territoriales de Colombia  
**Primer usuario piloto:** Funcionario del área del SISBÉN de la Alcaldía de Andes, Antioquia.

---

# **PARTE I. CONTEXTO DEL PROYECTO**

## **1\. Visión**

Construir un motor de automatización documental que permita consultar, recuperar y descargar de manera individual o masiva controlada los documentos relacionados con:

1. Reporte de afiliación al sistema de salud (ADRES/BDUA).  
2. Certificado de clasificación SISBÉN IV.  
3. Certificado del Registro Universal de Ingresos (RUI).

El producto nace de una necesidad operativa real de los funcionarios que atienden ciudadanos en las oficinas municipales del SISBÉN.

El primer caso de uso corresponde a un funcionario de la Alcaldía de Andes que recibe ciudadanos solicitando estos documentos y debe realizar manualmente las consultas en diferentes plataformas.

La oportunidad consiste en automatizar este proceso.

## **2\. Estrategia del producto**

El desarrollo se dividirá en cuatro fases independientes.

### **Fase 1\. Motor de automatización documental (MVP actual)**

Aplicación web que permita:

* Consultar una persona individualmente.  
* Consultar múltiples personas mediante Excel/CSV.  
* Obtener los resultados ADRES.  
* Obtener la clasificación SISBÉN IV.  
* Obtener la clasificación RUI.  
* Recuperar los documentos oficiales cuando el mecanismo esté disponible y autorizado.  
* Descargar los archivos.  
* Organizar documentos por persona y lote.  
* Consultar el estado de cada operación.  
* Descargar resultados agrupados en ZIP.

### **Fase 2\. Asistente de inteligencia artificial**

Desarrollar un asistente que interprete solicitudes en lenguaje natural.

Ejemplo:

"Necesito el reporte de EPS y el certificado del SISBÉN de esta persona".

El asistente identificará los documentos solicitados y utilizará el motor documental mediante su API interna.

No debe tener acceso directo a las credenciales de los proveedores.

### **Fase 3\. Integración WhatsApp Business**

Utilizar la infraestructura de Meta WhatsApp Business Platform, aprovechando que el fundador dispone de condición de Tech Provider de Meta.

El asistente permitirá:

* Recibir solicitudes.  
* Identificar qué documentos requiere el usuario.  
* Recopilar tipo y número de documento.  
* Solicitar y registrar la autorización correspondiente.  
* Consultar el motor documental.  
* Informar el estado.  
* Entregar los documentos por WhatsApp cuando las políticas y condiciones de entrega lo permitan.

### **Fase 4\. Plataforma SaaS empresarial**

Convertir el sistema en una solución multiempresa para alcaldías, entidades territoriales y organizaciones autorizadas.

Cada organización tendrá sus propios usuarios, permisos, consumo, auditoría y configuración de proveedores.

---

# **PARTE II. REQUISITOS FUNCIONALES**

## **3\. Documentos que debe gestionar el sistema**

IMPORTANTE: no unificar los tres tipos documentales.

### **DOCUMENTO A: Reporte de afiliación ADRES**

Fuente:  
[https\://www\.adres.gov.co/consulte-su-eps](https://www.adres.gov.co/consulte-su-eps)

Objetivo:

Consultar la afiliación de una persona en la Base de Datos Única de Afiliados (BDUA).

Datos de entrada:

* Tipo de documento.  
* Número de documento.

Datos esperados:

* Nombre y apellidos, cuando estén disponibles.  
* EPS.  
* Régimen.  
* Estado de afiliación.  
* Tipo de afiliado.  
* Fechas disponibles.  
* Fuente.  
* Fecha de consulta.

Documento esperado:

Reporte de consulta de afiliación de ADRES.

Advertencia: ADRES no expide certificados de afiliación. El sistema debe identificar el archivo como reporte de consulta y nunca presentarlo como certificado oficial de la EPS.

Fuente de referencia:  
[https\://portal.adres.gov.co/portal-del-ciudadano/preguntas-frecuentes](https://portal.adres.gov.co/portal-del-ciudadano/preguntas-frecuentes)

### **DOCUMENTO B: Certificado SISBÉN IV**

Fuente:  
[https\://www\.sisben.gov.co/](https://www.sisben.gov.co/)

Objetivo:

Consultar la clasificación tradicional del SISBÉN IV.

Datos esperados:

* Grupo A, B, C o D.  
* Subgrupo.  
* Información básica disponible.  
* Municipio.  
* Departamento.  
* Fuente.  
* Fecha de consulta.

Documento esperado:

Certificado o documento oficial de consulta de clasificación SISBÉN IV.

No confundir grupo/subgrupo con un puntaje numérico. La interfaz debe utilizar la denominación que aparezca en la fuente oficial.

### **DOCUMENTO C: Certificado RUI**

Fuente:  
[https\://ventanillasocial.dnp.gov.co/](https://ventanillasocial.dnp.gov.co/)

Objetivo:

Consultar la clasificación socioeconómica en la Ventanilla Social.

Documento esperado:

Certificado oficial del Registro Universal de Ingresos.

Datos esperados:

* Identificación.  
* Información del hogar disponible.  
* Clasificación RUI.  
* Información socioeconómica disponible.  
* Fuente.  
* Fecha de consulta.

IMPORTANTE:

El certificado RUI y el certificado SISBÉN IV son documentos diferentes.

El sistema debe mantener dos flujos de consulta y descarga separados.

## **4\. Modos de operación**

### **Modo individual**

El usuario ingresa:

* Tipo de documento.  
* Número de documento.  
* Documentos solicitados.

El sistema procesa la solicitud y presenta los resultados.

### **Modo masivo controlado**

El usuario carga un archivo Excel o CSV.

Columnas mínimas:

| Campo | Descripción |
| ----- | ----- |
| tipo\_documento | CC, TI, CE, etc. |
| numero\_documento | Identificación |
| adres | true/false |
| sisben\_iv | true/false |
| rui | true/false |
| autorizacion\_confirmada | true/false |
| referencia\_autorizacion | Referencia verificable |

El sistema debe validar los registros antes de iniciar el procesamiento.

El procesamiento masivo tendrá:

* Cola de tareas.  
* Control de concurrencia.  
* Límite de consultas.  
* Control de duplicados.  
* Reintentos controlados.  
* Registro de errores.  
* Estado individual por documento.  
* Descarga consolidada.

No procesar registros que no cumplan las condiciones de autorización y finalidad configuradas.

---

# **PARTE III. INVESTIGACIÓN DE PROVEEDORES Y MOTOR PROPIO**

## **5\. Proveedores iniciales**

### **Proveedor 1: PlacApi**

Documentación:  
[https\://placapi.com/docs](https://placapi.com/docs)

API ADRES:  
[https\://placapi.com/api/eps](https://placapi.com/api/eps)

API SISBÉN/RUI:  
[https\://placapi.com/api/sisben](https://placapi.com/api/sisben)

Características documentadas:

* API REST.  
* Autenticación mediante x-api-key.  
* Respuesta JSON.  
* Consulta ADRES.  
* Consulta SISBÉN IV y RUI.  
* Ejemplos Python y JavaScript.  
* Especificación OpenAPI.

Implementar inicialmente un adaptador PlacApi.

IMPORTANTE: verificar la documentación y los contratos vigentes antes de implementar. No asumir que la API entrega documentos PDF oficiales. Su documentación describe principalmente resultados JSON.

### **Proveedor 2: Árbol**

Documentación ADRES:  
[https\://docs.getarbol.com/api/adres/](https://docs.getarbol.com/api/adres/)

Documentación SISBÉN:  
[https\://docs.getarbol.com/api/sisben/](https://docs.getarbol.com/api/sisben/)

Mantenerlo como proveedor alternativo.

No implementar hasta verificar credenciales, costos, disponibilidad, términos y capacidades de descarga documental.

## **6\. Arquitectura de proveedores intercambiables**

Crear una interfaz común:

```
interface DocumentProvider {
  lookup(input: LookupInput): Promise<LookupResult>;

  healthCheck(): Promise<ProviderHealth>;
}
```

Tipos:

```
type DocumentType =
  | "ADRES_AFFILIATION_REPORT"
  | "SISBEN_IV_CERTIFICATE"
  | "RUI_CERTIFICATE";
```

Proveedores:

```
providers/
    adres/
        placapi-adres.provider.ts
        arbol-adres.provider.ts
        adres-web.provider.ts

    sisben/
        placapi-sisben.provider.ts
        arbol-sisben.provider.ts
        sisben-web.provider.ts

    rui/
        placapi-rui.provider.ts
        arbol-rui.provider.ts
        ventanilla-social.provider.ts
```

Los proveedores web se implementarán solamente después de comprobar que el procedimiento automatizado está permitido.

No asumir que un endpoint interno observado en el navegador es una API pública autorizada.

## **7\. Estrategia para motor propio**

El objetivo a mediano plazo es disponer de conectores propios que reduzcan la dependencia de proveedores privados.

Investigar y documentar los flujos de las plataformas oficiales.

Utilizar:

* Playwright para automatización web autorizada.  
* REA para inspección técnica y observación pasiva.  
* Replica Skill para reconstrucción funcional.  
* HTTPX o Axios para APIs documentadas.  
* Adaptadores independientes.

No copiar código propietario, credenciales, marcas ni mecanismos de seguridad.

No evadir CAPTCHA, autenticación, controles de acceso ni restricciones de consulta.

Si una operación requiere intervención humana, implementar estado `MANUAL_ACTION_REQUIRED`.

No desplegar automatización basada en endpoints internos hasta contar con confirmación de que su uso está permitido.

## **8\. Herramientas de ingeniería inversa**

### **Replica Skill**

[https\://github.com/Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill)

Evaluar:

* replica-recon  
* replica-architect  
* replica-backend  
* replica-build  
* replica-test  
* replica-diff

Utilizar sus habilidades como apoyo al análisis y reconstrucción clean-room.

### **REA**

[https\://github.com/morluto/rea](https://github.com/morluto/rea)

Documentación en español:  
[https\://github.com/morluto/rea/blob/main/docs/readme/README\_es.md](https://github.com/morluto/rea/blob/main/docs/readme/README_es.md)

Evaluar su integración mediante MCP.

Instalación documentada:

```
npx rea-agents setup
```

Usar REA para inspeccionar:

* DOM.  
* JavaScript.  
* Recursos web.  
* Estructura de aplicaciones.  
* Evidencia de comportamiento.  
* Metadatos de tráfico de sesiones autorizadas.

No dedicar las tres horas iniciales a instalar y configurar herramientas auxiliares. Su incorporación debe estar subordinada al MVP funcional.

---

# **PARTE IV. ARQUITECTURA DEL SISTEMA**

## **9\. Principios arquitectónicos**

1. Independencia de WhatsApp.  
2. Independencia del modelo de IA.  
3. Proveedores intercambiables.  
4. Separación entre datos y documentos.  
5. Separación entre SISBÉN IV y RUI.  
6. Seguridad desde el diseño.  
7. Procesamiento asíncrono.  
8. Trazabilidad completa.  
9. Escalabilidad multiempresa.  
10. Facilidad de mantenimiento.

## **10\. Arquitectura propuesta**

Frontend:

* React o Next.js.  
* Interfaz responsive.  
* Panel administrativo.  
* Carga de Excel/CSV.  
* Consulta individual.  
* Descarga de documentos.

Backend:

* Python \+ FastAPI, o la tecnología existente si el repositorio ya tiene una base funcional.  
* API REST.  
* Validación de datos.  
* Gestión de proveedores.  
* Motor documental.  
* Auditoría.

Procesamiento:

* Redis.  
* Celery o alternativa equivalente.  
* Procesamiento asíncrono.  
* Control de concurrencia.

Persistencia:

* PostgreSQL.  
* Almacenamiento local para desarrollo.  
* S3 compatible para producción.

Automatización:

* Playwright.  
* Adaptadores web independientes.

No introducir microservicios innecesarios en el MVP.

La prioridad es construir un monolito modular que permita extraer componentes en el futuro.

## **11\. Modelo de datos mínimo**

Crear las siguientes entidades:

### **organizations**

* id  
* name  
* nit  
* created\_at

### **users**

* id  
* organization\_id  
* email  
* password\_hash  
* role  
* created\_at

### **authorizations**

* id  
* organization\_id  
* subject\_document\_hash  
* purpose  
* authorization\_reference  
* authorized\_at  
* status  
* expires\_at

### **lookup\_jobs**

* id  
* organization\_id  
* created\_by  
* batch\_id  
* document\_type  
* document\_hash  
* provider  
* status  
* started\_at  
* completed\_at  
* error\_code

### **documents**

* id  
* organization\_id  
* lookup\_job\_id  
* document\_type  
* source  
* origin  
* storage\_path  
* mime\_type  
* sha256  
* generated\_at  
* retrieved\_at  
* verification\_status

### **batches**

* id  
* organization\_id  
* filename  
* total\_records  
* processed\_records  
* success\_count  
* error\_count  
* status  
* created\_at

No almacenar números de identificación en logs.

Aplicar cifrado a los datos de identificación y documentos cuando corresponda.

Los hashes de identificación deben utilizar HMAC con clave secreta, no un SHA-256 simple susceptible de ataques por diccionario.

---

# **PARTE V. PLAN DE TRABAJO: MVP EN TRES HORAS**

## **12\. Regla principal de desarrollo**

No construir todas las funcionalidades futuras.

Construir una primera versión funcional que demuestre el proceso completo:

1. Recibir identificación.  
2. Consultar ADRES.  
3. Consultar SISBÉN IV/RUI mediante los mecanismos disponibles.  
4. Obtener el documento oficial cuando sea técnicamente posible y esté autorizado.  
5. Almacenar el resultado.  
6. Permitir descargarlo.

El objetivo de tres horas es conseguir una demostración funcional, no una plataforma lista para comercialización pública.

## **13\. Distribución del tiempo**

### **BLOQUE 1 – 00:00 a 00:20**

Inspección y preparación del proyecto.

Tareas:

1. Inspeccionar el repositorio.  
2. Detectar tecnologías existentes.  
3. Revisar estructura de carpetas.  
4. Identificar variables de entorno.  
5. Verificar credenciales disponibles.  
6. Revisar si ya existen integraciones.  
7. Seleccionar el stack más rápido.

Entregable:

`docs/PROJECT_AUDIT.md`

Debe incluir:

* Estado inicial.  
* Tecnologías.  
* Dependencias.  
* Credenciales disponibles o faltantes.  
* Riesgos.  
* Arquitectura mínima.  
* Plan de ejecución.

No modificar archivos existentes sin entender su función.

### **BLOQUE 2 – 00:20 a 00:45**

Diseño funcional y arquitectura mínima.

Crear:

```
docs/
    PRD.md
    ARCHITECTURE.md
    DATA_MODEL.md
    PROVIDERS.md
    MVP_PLAN.md
```

Diseñar una aplicación web sencilla con dos secciones principales:

* Consulta individual.  
* Consulta masiva.

La selección de documentos tendrá tres opciones independientes:

* ADRES.  
* SISBÉN IV.  
* RUI.

### **BLOQUE 3 – 00:45 a 01:30**

Integración de proveedores.

Implementar:

* PlacApi ADRES.  
* PlacApi SISBÉN IV/RUI.  
* Validación de respuestas.  
* Manejo de errores.  
* Configuración de API Keys.  
* Normalización de datos.

Las credenciales se obtendrán de variables de entorno.

Ejemplo:

```
PLACAPI_API_KEY=
ARBOL_API_KEY=

DATABASE_URL=
REDIS_URL=

DOCUMENT_STORAGE_PATH=
```

No guardar claves en Git ni enviarlas al frontend.

Si las credenciales no están disponibles, construir adaptadores y pruebas con fixtures ficticios. No presentar una respuesta simulada como una consulta real.

### **BLOQUE 4 – 01:30 a 02:10**

Motor documental.

Implementar:

* Identificación de tipo documental.  
* Almacenamiento.  
* Nombres seguros de archivos.  
* Validación MIME.  
* Hash SHA-256.  
* Registro de fuente.  
* Fecha de consulta.  
* Estado del documento.

Crear un flujo específico para recuperar documentos oficiales.

Prioridad:

1. PDF oficial obtenido mediante mecanismo autorizado.  
2. Descarga desde fuente oficial con intervención del usuario, si es necesaria.  
3. Estado pendiente de obtención documental cuando la fuente no ofrezca una descarga automatizable.

No generar documentos que simulen ser certificados oficiales.

Los reportes internos podrán generarse únicamente con una identificación visual clara de que son documentos elaborados por la plataforma y no expedidos por ADRES o DNP.

### **BLOQUE 5 – 02:10 a 02:40**

Interfaz web.

Construir:

**Pantalla principal**

* Nombre del sistema.  
* Indicadores de consultas.  
* Consultas exitosas.  
* Consultas pendientes.  
* Errores.

**Pantalla de consulta individual**

* Tipo de documento.  
* Número de identificación.  
* Selector ADRES.  
* Selector SISBÉN IV.  
* Selector RUI.  
* Confirmación de autorización y finalidad.  
* Botón consultar.

**Pantalla masiva**

* Carga Excel/CSV.  
* Validación de registros.  
* Resumen del lote.  
* Inicio del procesamiento.  
* Barra de progreso.  
* Tabla de resultados.  
* Descarga ZIP.

### **BLOQUE 6 – 02:40 a 03:00**

Pruebas y entrega.

Validar:

1. Consulta individual ADRES.  
2. Consulta individual SISBÉN IV.  
3. Consulta individual RUI, si el proveedor y el acceso lo permiten.  
4. Manejo de documento no encontrado.  
5. Error de API.  
6. Carga de Excel.  
7. Procesamiento de un lote pequeño.  
8. Almacenamiento de documentos.  
9. Descarga de archivos.  
10. Ausencia de exposición de credenciales.

Entregables:

* Aplicación ejecutándose localmente.  
* README de instalación.  
* Variables de entorno de ejemplo.  
* Pruebas básicas.  
* Registro de limitaciones.  
* Lista de tareas pendientes.

---

# **PARTE VI. INTERFAZ DE USUARIO**

## **14\. Diseño funcional**

Crear una interfaz administrativa sencilla, moderna y profesional.

Nombre provisional:

**Gestor Documental Social**

Navegación:

```
Dashboard
├── Consulta individual
├── Consulta masiva
├── Historial
├── Documentos
├── Proveedores
└── Configuración
```

### **Consulta individual**

Campos:

* Tipo de documento.  
* Número de documento.  
* Documentos solicitados.  
* Finalidad.  
* Confirmación de autorización.

Resultados independientes:

ADRES:

* Estado de consulta.  
* EPS.  
* Régimen.  
* Estado de afiliación.  
* Reporte disponible.  
* Descargar.

SISBÉN IV:

* Estado de consulta.  
* Grupo.  
* Subgrupo.  
* Certificado disponible.  
* Descargar.

RUI:

* Estado de consulta.  
* Clasificación.  
* Certificado disponible.  
* Descargar.

### **Consulta masiva**

Flujo:

1. Subir archivo.  
2. Validar columnas.  
3. Mostrar cantidad de registros.  
4. Mostrar documentos solicitados.  
5. Confirmar finalidad y autorización.  
6. Iniciar procesamiento.  
7. Mostrar avance.  
8. Permitir descargar resultados.

Estados:

```
PENDING
VALIDATING
QUEUED
PROCESSING
COMPLETED
PARTIAL_SUCCESS
FAILED
MANUAL_ACTION_REQUIRED
DOCUMENT_PENDING
```

Los estados de cada documento deben ser independientes.

Una consulta ADRES exitosa no implica que el documento SISBÉN también esté disponible.

---

# **PARTE VII. SEGURIDAD Y CUMPLIMIENTO**

## **15\. Requisitos obligatorios**

El sistema manejará información personal y datos sensibles relacionados con salud.

Implementar desde el MVP:

* Confirmación de autorización.  
* Finalidad de consulta.  
* Control de acceso.  
* Separación de organizaciones.  
* Cifrado en tránsito.  
* Protección de credenciales.  
* No exposición de documentos mediante enlaces públicos.  
* Registro de auditoría.  
* Política de conservación.  
* Procedimiento de eliminación.  
* Minimización de datos.

Referencias:

Ley 1581 de 2012\.  
[https\://www\.funcionpublica.gov.co/eva/gestornormativo/](https://www.funcionpublica.gov.co/eva/gestornormativo/)

Decreto 1074 de 2015\.

Condiciones de uso de ADRES y DNP.

No asumir que la consulta pública de una persona habilita la extracción masiva o la comercialización de sus datos.

Antes de realizar consultas productivas para una entidad pública, validar el fundamento jurídico, la finalidad, los permisos institucionales y las condiciones de acceso de cada proveedor.

---

# **PARTE VIII. FASES POSTERIORES**

## **16\. Fase 2 – Motor propio y resiliencia**

Objetivo: disminuir dependencia de proveedores externos.

Tareas:

1. Evaluar el acceso institucional de ADRES.  
2. Investigar los mecanismos de interoperabilidad del DNP.  
3. Analizar las posibilidades de automatización autorizada de las fuentes oficiales.  
4. Implementar conectores web propios cuando sean admisibles.  
5. Implementar fallback entre proveedores.  
6. Crear pruebas de regresión.  
7. Implementar monitoreo de disponibilidad.  
8. Evaluar diferencias de resultados entre proveedores.

Política de fallback:

```
Consulta solicitada
       |
       v
Proveedor principal
       |
       +---- Éxito ----> Normalizar respuesta
       |
       +---- Error recuperable
                  |
                  v
           Proveedor alternativo
                  |
                  +---- Éxito ----> Normalizar
                  |
                  +---- Error
                           |
                           v
                  Revisión / intervención humana
```

No realizar consultas duplicadas a varias fuentes si la primera ya entregó una respuesta válida, salvo que exista una razón de verificación y autorización.

## **17\. Fase 3 – Asistente de IA**

Objetivo: convertir el motor documental en una herramienta conversacional.

El agente podrá utilizar herramientas internas:

```
lookup_adres(document)
lookup_sisben_iv(document)
lookup_rui(document)
get_document(job_id)
get_job_status(job_id)
create_batch(file)
```

El modelo de IA no realizará directamente las consultas externas.

Solo invocará herramientas con permisos y validaciones.

Implementar:

* Identificación de intención.  
* Extracción de tipo de documento.  
* Validación de identificación.  
* Confirmación de finalidad.  
* Solicitud de autorización.  
* Selección de documentos.  
* Seguimiento.  
* Entrega de archivos.

## **18\. Fase 4 – WhatsApp Business**

Objetivo: ofrecer el producto mediante WhatsApp Business Platform.

Arquitectura:

```
WhatsApp Business
       |
       v
Webhook Meta
       |
       v
Conversation Manager
       |
       v
AI Assistant
       |
       v
Document API
       |
       v
ADRES / SISBÉN / RUI
       |
       v
Document Storage
       |
       v
WhatsApp Document Delivery
```

Consideraciones:

* Utilizar la API oficial de Meta.  
* Implementar validación de webhooks.  
* Gestionar ventanas de conversación y plantillas.  
* Validar las políticas aplicables a la categoría de servicio.  
* Evitar exposición de números de documento en conversaciones o logs innecesarios.  
* Implementar control de acceso y autorización.  
* No entregar documentos a números distintos del destinatario autorizado sin validación adicional.

## **19\. Fase 5 – SaaS multiempresa**

Funcionalidades futuras:

* Multi-tenancy.  
* Panel de empresas.  
* Gestión de funcionarios.  
* Consumo por organización.  
* Límites de consultas.  
* Facturación.  
* Planes mensuales.  
* API Keys empresariales.  
* Webhooks.  
* Reportes de consumo.  
* Auditoría.  
* Gestión de políticas de conservación.  
* Integraciones con sistemas administrativos municipales.

---

# **PARTE IX. CRITERIOS DE ÉXITO Y PRIORIZACIÓN**

## **20\. Definición de MVP funcional**

El MVP se considera funcional cuando:

* La aplicación puede iniciarse.  
* Se puede ingresar una identificación.  
* Se puede ejecutar una consulta real mediante un proveedor autorizado.  
* Se puede visualizar la respuesta.  
* Se puede identificar la fuente.  
* Se puede guardar un documento obtenido legítimamente.  
* Se puede registrar el estado.  
* Se puede ejecutar una consulta masiva pequeña.  
* Se puede descargar el resultado.  
* Los errores se manejan correctamente.

No es requisito del MVP de tres horas:

* Integración WhatsApp.  
* Inteligencia artificial.  
* Facturación.  
* Multiempresa completa.  
* Automatización de todos los portales.  
* Acceso institucional pendiente.  
* Descarga automatizada de documentos cuyo mecanismo no esté habilitado.

No declarar completo un flujo de documento si únicamente se obtuvo JSON.

## **21\. Priorización**

| Prioridad | Funcionalidad |
| ----- | ----- |
| P0 | Consulta ADRES mediante proveedor disponible |
| P0 | Consulta SISBÉN IV/RUI mediante proveedor disponible |
| P0 | Gestión diferenciada de documentos |
| P0 | Almacenamiento |
| P0 | Consulta individual |
| P0 | Registro de errores |
| P1 | Carga Excel/CSV |
| P1 | Procesamiento masivo |
| P1 | Descarga ZIP |
| P1 | Conector documental oficial |
| P2 | Segundo proveedor |
| P2 | Automatización web autorizada |
| P2 | Fallback |
| P3 | Agente de IA |
| P3 | WhatsApp |
| P4 | SaaS comercial |

---

# **PARTE X. INSTRUCCIONES PARA EL AGENTE DE DESARROLLO**

## **22\. Tu misión**

Actúa como un equipo integrado por:

* CTO.  
* Arquitecto de software.  
* Ingeniero backend.  
* Ingeniero frontend.  
* Ingeniero de automatización.  
* QA Engineer.  
* Especialista en seguridad.  
* Product Manager.

Tu responsabilidad es planificar y ejecutar el desarrollo del producto descrito en este documento.

## **23\. Orden de ejecución obligatorio**

### **Paso 1\. Auditar**

Inspecciona el entorno y el repositorio.

No comiences a modificar archivos sin comprender el proyecto existente.

### **Paso 2\. Verificar dependencias**

Identifica:

* APIs.  
* Credenciales.  
* Documentación.  
* Repositorios auxiliares.  
* Herramientas instaladas.  
* Servicios disponibles.

No inventes credenciales ni asumas que una API funciona porque existe documentación.

### **Paso 3\. Definir el plan**

Genera un plan técnico de tareas con:

* ID.  
* Descripción.  
* Prioridad.  
* Tiempo estimado.  
* Dependencias.  
* Criterios de aceptación.  
* Estado.

Guardar en:

`docs/IMPLEMENTATION_PLAN.md`

### **Paso 4\. Construir el MVP**

Prioriza un flujo vertical completo.

No inviertas tiempo excesivo en abstracciones, diseño visual o infraestructura que no sea necesaria.

Construye una solución modular, pero sencilla.

### **Paso 5\. Validar**

Ejecuta pruebas automatizadas.

Si no existen credenciales, usa fixtures ficticios identificados como tales.

No declarar que una integración real funciona si no ha sido probada.

### **Paso 6\. Documentar**

Crear:

* README.md  
* .env.example  
* docs/PROJECT\_AUDIT.md  
* docs/IMPLEMENTATION\_PLAN.md  
* docs/ARCHITECTURE.md  
* docs/PROVIDERS.md  
* docs/TEST\_REPORT.md  
* docs/ROADMAP.md

## **24\. Reglas de ingeniería**

1. No sobredimensionar el MVP.  
2. No introducir dependencias innecesarias.  
3. No duplicar lógica de negocio.  
4. No acoplar el backend a PlacApi.  
5. No mezclar SISBÉN IV con RUI.  
6. No confundir datos JSON con documentos oficiales.  
7. No simular resultados reales.  
8. No evadir controles de seguridad.  
9. No almacenar secretos en código.  
10. No exponer identificaciones en logs.  
11. No realizar consultas productivas sin autorización.  
12. Documentar limitaciones y decisiones.  
13. Priorizar pruebas de integración.  
14. Mantener una arquitectura preparada para WhatsApp.

## **25\. Instrucción de autonomía**

No te limites a entregar una propuesta teórica.

Primero presenta un plan de trabajo breve y priorizado, con los riesgos y dependencias que realmente bloquean la ejecución.

Después, comienza inmediatamente la construcción de las tareas P0 que puedan ejecutarse con los recursos disponibles.

No esperes confirmación para decisiones técnicas reversibles y de bajo riesgo.

Solicita aprobación únicamente para acciones que impliquen costos, publicación externa, tratamiento productivo de datos personales, uso de credenciales sensibles o modificaciones irreversibles.

Si una integración está bloqueada por credenciales o permisos, continúa con las demás funcionalidades.

Al finalizar, entrega:

1. Qué quedó implementado.  
2. Qué funciona realmente.  
3. Qué fue probado.  
4. Qué necesita credenciales.  
5. Qué necesita autorización.  
6. Qué quedó pendiente.  
7. Qué debemos desarrollar en la siguiente sesión.

**Objetivo final: entregar en tres horas una primera versión funcional y verificable del motor documental, con una ruta de evolución clara hacia un asistente de IA conectado a WhatsApp Business.**

# **6\. Mi recomendación de ejecución: qué instalar y qué no**

Para no perder las tres horas, utilizaría las herramientas de esta manera:

| Herramienta | Decisión | Momento |
| ----- | ----- | ----- |
| Claude Code / Antigravity | Principal | Inmediato |
| PlacApi | Principal | Inmediato |
| Replica Skill | Complementaria | Arquitectura y análisis |
| REA | Complementaria | Investigación de portales |
| Playwright | Necesaria si hay automatización web | Fase documental |
| Árbol | Alternativa | Fase 2 |
| WhatsApp Cloud API | Fase posterior | Fase 3 |

No instalaría todas las herramientas antes de comenzar. Primero hay que comprobar qué tienes ya instalado y qué credenciales tienes disponibles.

## **7\. Una recomendación comercial importante para el piloto con Marques**

No esperaría a tener WhatsApp para validar el negocio.

Cuando esté funcionando la aplicación web, propondría una demostración a Marques con un proceso real autorizado:

1. Él selecciona una consulta.  
2. El sistema obtiene el reporte ADRES.  
3. El sistema obtiene el documento SISBÉN IV y/o RUI solicitado.  
4. Se registra el resultado.  
5. Descarga los documentos en una carpeta.

Después, pregúntale cuánto tiempo le ahorra y cuántas consultas realiza semanalmente.

Esto permite validar la disposición de pago antes de invertir en el asistente conversacional.

**Una consideración institucional:** que Marques trabaje en una alcaldía no significa automáticamente que pueda contratar el servicio o autorizar el tratamiento de datos en nombre del municipio. Para el piloto comercial habrá que validar las competencias, autorizaciones, contratación y tratamiento de datos aplicables.

## **8\. Hoja de ruta visual**

1. Ahora  
   **MVP documental**  
   Aplicación web, consulta individual, lotes, documentos y almacenamiento.  
   Meta: primera versión en 3 horas.  
2. **Motor propio**  
   Conectores autorizados, redundancia de proveedores, validación y resiliencia.  
3. **Asistente inteligente**  
   Agente capaz de interpretar solicitudes y ejecutar las herramientas documentales.  
4. **WhatsApp Business**  
   Integración con Meta, recepción de solicitudes y entrega documental.  
5. **Producto SaaS**  
   Multiempresa, facturación, gestión de organizaciones y escalabilidad.

**Mi decisión técnica final:** construir primero el motor documental como un producto independiente y convertirlo después en una herramienta del asistente de IA. Así podrás validar el negocio con Marques sin esperar a completar toda la infraestructura de WhatsApp.

