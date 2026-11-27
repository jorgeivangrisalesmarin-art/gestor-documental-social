# Especificación EARS — Motor Documental

## 1. Contrato DocumentProvider
- **CUANDO** el backend recibe una solicitud de consulta individual o en lote **EL SISTEMA DEBERÁ** delegarla al adaptador correspondiente que implemente la interfaz `DocumentProvider`.
- **CUANDO** se invoca el método `lookup(doc_type, doc_number)` **EL ADAPTADOR DEBERÁ** devolver una estructura unificada `LookupResult` conteniendo datos normalizados, timestamp de consulta y referencia de fuente.
- **CUANDO** un proveedor responda un error de autenticación (401/403) o saldo insuficiente (402) **EL ADAPTADOR DEBERÁ** mapear el fallo a un error de dominio tipado (`ProviderAuthError`, `ProviderQuotaExceededError`) sin exponer credenciales en logs.

## 2. Protección de Datos (Ley 1581 de 2012)
- **CUANDO** se registra cualquier consulta en bitácora o auditoría **EL SISTEMA DEBERÁ** almacenar el número de documento como un hash HMAC-SHA256, sin persistir el documento en texto plano.
- **CUANDO** una consulta retorna datos en JSON **EL SISTEMA DEBERÁ** marcar el documento con estado `DOCUMENT_PENDING` a menos que exista un mecanismo de emisión oficial de PDF.
