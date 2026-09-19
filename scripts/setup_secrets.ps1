# PowerShell script to store Confluence credentials in Google Secret Manager
param (
    [string]$ProjectId = "project-4d6820e9-87df-40e6-92a",
    [string]$SecretName = "confluence-credentials",
    [string]$ConfluenceUrl = "https://buildcloudwithabhinav.atlassian.net",
    [string]$UserEmail = "buildcloudwithabhinav@gmail.com",
    [string]$ApiToken = ""
)

Write-Host "Configuring Google Secret Manager for Project: $ProjectId" -ForegroundColor Cyan

if (-not $ApiToken) {
    $ApiToken = Read-Host "Enter your Confluence Cloud API Token" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ApiToken)
    $ApiToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

$secretPayload = @{
    url = $ConfluenceUrl
    email = $UserEmail
    token = $ApiToken
    space_key = "AITEST"
} | ConvertTo-Json -Compress

# Create secret if it doesn't exist
$exists = gcloud secrets describe $SecretName --project=$ProjectId 2>$null
if (-not $exists) {
    Write-Host "Creating secret '$SecretName' in project '$ProjectId'..." -ForegroundColor Yellow
    gcloud secrets create $SecretName --replication-policy="automatic" --project=$ProjectId
}

# Add secret version
Write-Host "Adding secret version to '$SecretName'..." -ForegroundColor Green
$secretPayload | gcloud secrets versions add $SecretName --data-file=- --project=$ProjectId

Write-Host "✓ Successfully stored Confluence credentials in Secret Manager ($SecretName)!" -ForegroundColor Green
