#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# The _SERVICE variable is passed in from the Cloud Build trigger
SERVICE_NAME="$_SERVICE"
REGION="$_GOOGLE_CLOUD_LOCATION"
PROJECT_ID="$_GOOGLE_CLOUD_PROJECT"
IMAGE_REPO_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/rumi-analytica"
IMAGE_TAG="${IMAGE_REPO_URL}/${SERVICE_NAME}:latest"

echo "--- Starting build for service: ${SERVICE_NAME} ---"

# Change to the service's directory
cd "${SERVICE_NAME}"

# --- Conditional Build Steps ---
if [ "$SERVICE_NAME" == "frontend" ]; then
  echo "--- Building Frontend ---"
  npm install
  # Pass the backend URL as a build-time variable to Vite
  VITE_BACKEND_URL="${_BACKEND_URL}" npm run build

elif [ "$SERVICE_NAME" == "backend" ]; then
  echo "--- Building Backend (no special build steps needed) ---"
  # Python/FastAPI doesn't have a "build" step like Node, so we just proceed

else
  echo "ERROR: Unknown service name: $SERVICE_NAME"
  exit 1
fi

# --- Common Steps: Docker Build, Push, and Deploy ---
echo "--- Building Docker image: ${IMAGE_TAG} ---"
docker build -t "${IMAGE_TAG}" .

echo "--- Pushing Docker image ---"
docker push "${IMAGE_TAG}"

echo "--- Deploying to Cloud Run ---"
# The flags for deployment are different for frontend and backend
if [ "$SERVICE_NAME" == "frontend" ]; then
  gcloud run deploy "rumi-analytica-frontend" \
    --image="${IMAGE_TAG}" \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated

elif [ "$SERVICE_NAME" == "backend" ]; then
  gcloud run deploy "rumi-analytica-backend" \
    --image="${IMAGE_TAG}" \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated \
    --service-account="rumi-app-runner-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --set-env-vars="SIMPLE_AUTH_USERNAME=${_SIMPLE_AUTH_USERNAME},GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},FRONTEND_URL=${_FRONTEND_URL}" \
    --set-secrets="SIMPLE_AUTH_PASSWORD_HASH=RUMI_PASSWORD_HASH:latest,JWT_SECRET_KEY=RUMI_JWT_SECRET:latest"
fi

echo "--- Deployment Complete ---"