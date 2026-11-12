# Seta variáveis do Actions no repo Capstone (precisa write/admin)
param(
  [string]$Repo = 'pedroaugustogti/capstone-project-ai-researcher',
  [string]$ProjectId = 'ai-researcher-cap-pedro'
)
$ErrorActionPreference = 'Stop'
$ProjectNumber = (gcloud projects describe $ProjectId --format='value(projectNumber)').Trim()
$Wif = "projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider"
$Sa = "github-actions-deployer@$ProjectId.iam.gserviceaccount.com"

gh variable set GCP_PROJECT_ID --body $ProjectId --repo $Repo
gh variable set GCP_WIF_PROVIDER --body $Wif --repo $Repo
gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body $Sa --repo $Repo
gh variable list --repo $Repo
Write-Host "OK — vars set on $Repo"
