# Runbook de despliegue GCP (T010/T011) — ejecución SOLO con checkpoint N1 de Jorge

Pre-requisitos: gcloud instalado y autenticado con la cuenta del proyecto,
billing habilitado, Docker instalado.

## T010 — Recursos (SOLO con aprobación Cn)

```bash
# Variables (definir PROJECT_ID real antes)
export PROJECT_ID=<project-id-gcp>
export REGION=us-central1

# 1. Habilitar APIs
gcloud services enable run.googleapis.com sqladmin.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com \
  storage.googleapis.com --project $PROJECT_ID

# 2. Artifact Registry
gcloud artifacts repositories create gds --repository-format=docker \
  --location=$REGION --project $PROJECT_ID

# 3. Cloud SQL (PostgreSQL 16) — ~$10-30/mes
gcloud sql instances create gds-db --database-version=POSTGRES16 \
  --tier=db-f1-micro --region=$REGION --no-assign-ip --project $PROJECT_ID

# 4. Bucket privado de documentos
gcloud storage buckets create gs://$PROJECT_ID-docs --location=$REGION \
  --uniform-bucket-level-access --public-access-prevention --project $PROJECT_ID

# 5. Secret Manager: API keys y claves de cifrado (valores NO van aquí)
gcloud secrets create placapi-api-key --project $PROJECT_ID   # luego: gcloud secrets versions add
gcloud secrets create doc-encryption-key --project $PROJECT_ID
gcloud secrets create doc-hmac-key --project $PROJECT_ID
gcloud secrets create jwt-secret --project $PROJECT_ID

## Deploy de servicios (T011, staging)

# Build y push de imágenes
gcloud builds submit --config cloudbuild.yaml --project $PROJECT_ID

# O manual (staging):
gcloud run deploy gds-api-staging \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/gds/api:$TAG \
  --region $REGION --allow-unauthenticated --port 8080 \
  --set-env-vars WEB_ORIGIN=https://<url-web-staging> \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://gds:PASS@<ip-privada>:5432/gds \
  --set-env-vars APP_ENV=staging \
  --set-secrets PLACAPI_API_KEY=placapi-api-key:latest \
  --set-secrets DOC_ENCRYPTION_KEY=doc-encryption-key:latest \
  --set-secrets DOC_HMAC_KEY=doc-hmac-key:latest
