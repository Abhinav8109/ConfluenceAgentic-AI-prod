# Automated GCP Cloud Run Deployment Script
param (
    [string]$ProjectId = "project-4d6820e9-87df-40e6-92a",
    [string]$Region = "us-central1",
    [string]$ServiceName = "cloudops-ai-assistant",
    [string]$RepoName = "cloudops-repo"
)

Write-Host "Starting Cloud Run Deployment for: $ServiceName in $ProjectId ($Region)" -ForegroundColor Cyan

# 1. Ensure required APIs are enabled
Write-Host "[1/5] Verifying GCP APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com secretmanager.googleapis.com --project=$ProjectId

# 2. Ensure Artifact Registry repository exists
Write-Host "[2/5] Checking Artifact Registry..." -ForegroundColor Yellow
$repoExists = gcloud artifacts repositories describe $RepoName --location=$Region --project=$ProjectId 2>$null
if (-not $repoExists) {
    Write-Host "Creating Artifact Registry repository '$RepoName'..." -ForegroundColor Green
    gcloud artifacts repositories create $RepoName --repository-format=docker --location=$Region --description="CloudOps AI Assistant repository" --project=$ProjectId
}

# 3. Trigger Cloud Build
Write-Host "[3/5] Submitting Cloud Build..." -ForegroundColor Yellow
$imageTag = "$Region-docker.pkg.dev/$ProjectId/$RepoName/${ServiceName}:latest"
gcloud builds submit --tag $imageTag --project=$ProjectId

# 4. Deploy to Cloud Run
Write-Host "[4/5] Deploying container to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $imageTag `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "GCP_PROJECT_ID=$ProjectId,GCP_REGION=$Region,GEMINI_MODEL=gemini-2.5-flash" `
    --project=$ProjectId

# 5. Get Service URL
$serviceUrl = gcloud run services describe $ServiceName --region $Region --project=$ProjectId --format="value(status.url)"
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
