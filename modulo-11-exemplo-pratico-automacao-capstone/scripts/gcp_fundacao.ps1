# P5 — GCP fundação Capstone (AR auto; SQL/WIF HITL gated)
param(
  [ValidateSet('artifact','sql','wif','firebase','all-safe')]
  [string]$Phase = 'all-safe',
  [switch]$ConfirmSql,
  [switch]$ConfirmWif,
  [string]$ProjectId = 'ai-researcher-cap-pedro',
  [string]$BillingAccount = '014662-97FB95-F155D4',
  [string]$Region = 'us-central1',
  [string]$InstanceId = 'ai-researcher-db',
  [string]$DbName = 'ai_researcher',
  [string]$AppUser = 'app_user',
  [int]$ProxyPort = 5435
)
. "$PSScriptRoot\lib_common.ps1"
Ensure-PreflightDir
Use-GcloudEnv
$prevEa = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
& gcloud config set project $ProjectId 2>&1 | Out-Null
$ErrorActionPreference = $prevEa

$out = [ordered]@{ project = $ProjectId; region = $Region; instance = $InstanceId; steps = @() }

function Add-Step($name, $ok, $detail) {
  $script:out.steps += @{ name = $name; ok = [bool]$ok; detail = "$detail" }
  Write-Host ("[{0}] {1} — {2}" -f $(if($ok){'OK'}else{'SKIP'}), $name, $detail)
}

function New-SecureDbPassword([int]$Length = 36) {
  $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
  $bytes = New-Object byte[] $Length
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })
}

function Get-ConnectionName {
  return "${ProjectId}:${Region}:${InstanceId}"
}

function Invoke-SqlViaProxy {
  param(
    [Parameter(Mandatory)][string]$Password,
    [Parameter(Mandatory)][string]$User,
    [Parameter(Mandatory)][string]$Sql,
    [string]$Database = $DbName
  )
  $env:PGPASSWORD = $Password
  try {
    $img = 'postgres:16-alpine'
    $args = @(
      'run','--rm',
      '-e',"PGPASSWORD=$Password",
      $img,
      'psql',
      '-h','host.docker.internal',
      '-p',"$ProxyPort",
      '-U',$User,
      '-d',$Database,
      '-v','ON_ERROR_STOP=1',
      '-c',$Sql
    )
    & docker @args 2>&1
    return ($LASTEXITCODE -eq 0)
  } finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
  }
}

# Artifact Registry
if ($Phase -in @('artifact','all-safe')) {
  $ErrorActionPreference = 'Continue'
  $desc = & gcloud artifacts repositories describe ai-researcher --location=$Region --format='value(name)' 2>&1
  $descCode = $LASTEXITCODE
  if ($descCode -eq 0 -and "$desc" -match 'ai-researcher') {
    Add-Step 'artifact-registry' $true 'exists'
  } else {
    $create = & gcloud artifacts repositories create ai-researcher `
      --repository-format=docker `
      --location=$Region `
      --description='Capstone AI Researcher' 2>&1
    $create | Out-Host
    Add-Step 'artifact-registry' ($LASTEXITCODE -eq 0) ("created exit=" + $LASTEXITCODE)
  }
  $ErrorActionPreference = $prevEa
}

# Cloud SQL — HITL (cena 5 + 6)
if ($Phase -eq 'sql' -or ($Phase -eq 'all-safe' -and $ConfirmSql)) {
  if (-not $ConfirmSql) {
    Add-Step 'cloud-sql' $false 'HITL: re-run with -ConfirmSql (db-f1-micro ~cost)'
  } else {
    $ErrorActionPreference = 'Continue'
    $connName = Get-ConnectionName
    $rootPassword = $null
    $appPassword = $null

    $exists = & gcloud sql instances describe $InstanceId --format='value(name)' 2>&1
    if ($LASTEXITCODE -eq 0 -and "$exists" -match $InstanceId) {
      Add-Step 'cloud-sql-instance' $true 'exists'
    } else {
      Write-Host 'Creating Cloud SQL (often 10-20+ min)...'
      $rootPassword = New-SecureDbPassword 40
      & gcloud sql instances create $InstanceId `
        --project=$ProjectId `
        --database-version=POSTGRES_16 `
        --edition=ENTERPRISE `
        --tier=db-f1-micro `
        --region=$Region `
        --root-password=$rootPassword `
        --no-backup `
        --assign-ip `
        --storage-size=10GB `
        --database-flags=cloudsql.iam_authentication=on 2>&1 | Out-Host
      Add-Step 'cloud-sql-instance' ($LASTEXITCODE -eq 0) ("create exit=$LASTEXITCODE")
      if ($LASTEXITCODE -ne 0) {
        Update-State 'P5' 'sql_create_failed'
        Write-PhaseEvidence 'P5-gcp' $out | Out-Null
        Write-Host 'P5=sql_create_failed'
        exit 1
      }
    }

    # Database
    $dbList = & gcloud sql databases list --instance=$InstanceId --format='value(name)' 2>&1
    if ("$dbList" -match "(?m)^${DbName}$") {
      Add-Step 'cloud-sql-db' $true 'exists'
    } else {
      & gcloud sql databases create $DbName --instance=$InstanceId 2>&1 | Out-Host
      Add-Step 'cloud-sql-db' ($LASTEXITCODE -eq 0) $DbName
    }

    # App user — password only if creating; if exists, secret may already hold it
    $users = & gcloud sql users list --instance=$InstanceId --format='value(name)' 2>&1
    if ("$users" -match "(?m)^${AppUser}$") {
      Add-Step 'cloud-sql-user' $true 'app_user exists (password not rotated)'
    } else {
      $appPassword = New-SecureDbPassword 40
      & gcloud sql users create $AppUser --instance=$InstanceId --password=$appPassword 2>&1 | Out-Host
      Add-Step 'cloud-sql-user' ($LASTEXITCODE -eq 0) 'created'
    }

    # If user existed but we need vector/secret, require app password via env CAPSTONE_SQL_APP_PASSWORD
    if (-not $appPassword) {
      if ($env:CAPSTONE_SQL_APP_PASSWORD) {
        $appPassword = $env:CAPSTONE_SQL_APP_PASSWORD
        Add-Step 'cloud-sql-password-source' $true 'CAPSTONE_SQL_APP_PASSWORD'
      } else {
        # Try read existing secret to reuse
        $sec = & gcloud secrets versions access latest --secret=database-url 2>&1
        if ($LASTEXITCODE -eq 0 -and "$sec" -match 'postgresql://([^:]+):([^@]+)@') {
          $appPassword = $Matches[2]
          Add-Step 'cloud-sql-password-source' $true 'from secret database-url'
        } else {
          Add-Step 'cloud-sql-password-source' $false 'set CAPSTONE_SQL_APP_PASSWORD to continue vector/secret'
        }
      }
    }

    # Proxy + vector + grants (needs app or root password)
    $proxyOk = $false
    $vectorOk = $false
    if ($appPassword -or $rootPassword) {
      $proxyCmd = Get-Command cloud-sql-proxy -ErrorAction SilentlyContinue
      $proxyExe = if ($proxyCmd) { $proxyCmd.Source } else { $null }
      if (-not $proxyExe) {
        $proxyExe = Join-Path $env:LOCALAPPDATA 'Google\Cloud SDK\google-cloud-sdk\bin\cloud-sql-proxy.exe'
      }
      if (-not (Test-Path $proxyExe)) {
        Add-Step 'cloud-sql-proxy' $false 'cloud-sql-proxy not found'
      } else {
        $proxyOut = Join-Path $Script:Preflight 'cloud-sql-proxy.out.log'
        $proxyErr = Join-Path $Script:Preflight 'cloud-sql-proxy.err.log'
        $proxyArgs = @($connName, '--port', "$ProxyPort", '--address', '127.0.0.1')
        $proxyProc = Start-Process -FilePath $proxyExe -ArgumentList $proxyArgs -PassThru -WindowStyle Hidden `
          -RedirectStandardOutput $proxyOut -RedirectStandardError $proxyErr
        Start-Sleep -Seconds 5
        if (-not $proxyProc -or $proxyProc.HasExited) {
          Add-Step 'cloud-sql-proxy' $false ("exited early; see $proxyErr")
        } else {
          $proxyOk = $true
          Add-Step 'cloud-sql-proxy' $true "127.0.0.1:$ProxyPort pid=$($proxyProc.Id)"

          $adminUser = if ($rootPassword) { 'postgres' } else { $AppUser }
          $adminPass = if ($rootPassword) { $rootPassword } else { $appPassword }

          # Ensure app_user can create extension / use schema
          if ($rootPassword) {
            $null = Invoke-SqlViaProxy -Password $rootPassword -User 'postgres' -Sql "GRANT ALL PRIVILEGES ON DATABASE $DbName TO $AppUser;"
            $null = Invoke-SqlViaProxy -Password $rootPassword -User 'postgres' -Database $DbName -Sql "GRANT ALL ON SCHEMA public TO $AppUser; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $AppUser;"
          }

          $vectorSql = 'CREATE EXTENSION IF NOT EXISTS vector;'
          $vectorOk = Invoke-SqlViaProxy -Password $adminPass -User $adminUser -Database $DbName -Sql $vectorSql
          if (-not $vectorOk -and $appPassword -and $adminUser -ne $AppUser) {
            $vectorOk = Invoke-SqlViaProxy -Password $appPassword -User $AppUser -Database $DbName -Sql $vectorSql
          }
          Add-Step 'pgvector' $vectorOk 'CREATE EXTENSION vector'

          try { Stop-Process -Id $proxyProc.Id -Force -ErrorAction SilentlyContinue } catch {}
        }
      }
    } else {
      Add-Step 'pgvector' $false 'skipped — no password available'
    }

    # Secret Manager database-url (Unix socket — Cloud Run)
    if ($appPassword) {
      $socketUrl = "postgresql://${AppUser}:${appPassword}@/${DbName}?host=/cloudsql/${connName}"
      $secExists = & gcloud secrets describe database-url --format='value(name)' 2>&1
      if ($LASTEXITCODE -ne 0) {
        & gcloud secrets create database-url --replication-policy=automatic 2>&1 | Out-Host
        Add-Step 'secret-create' ($LASTEXITCODE -eq 0) 'database-url'
      } else {
        Add-Step 'secret-create' $true 'database-url exists'
      }
      # UTF-8 file (PowerShell pipe to native cmds is UTF-16 and corrupts the secret)
      $tmpSecret = Join-Path $env:TEMP ("capstone-dburl-" + [guid]::NewGuid() + ".txt")
      try {
        [System.IO.File]::WriteAllText($tmpSecret, $socketUrl, [System.Text.UTF8Encoding]::new($false))
        & gcloud secrets versions add database-url --data-file=$tmpSecret 2>&1 | Out-Host
        Add-Step 'secret-version' ($LASTEXITCODE -eq 0) 'database-url latest (unix socket)'
      } finally {
        Remove-Item $tmpSecret -Force -ErrorAction SilentlyContinue
      }

      Write-Host ''
      Write-Host "Cloud SQL ready: connectionName=$connName secret=database-url proxyPort=$ProxyPort"
      Write-Host 'Local migrate/seed: start cloud-sql-proxy, then DATABASE_URL from Secret Manager (do not commit).'
      Write-Host ''
      $out.connectionName = $connName
      $out.secret = 'database-url'
      $out.proxyPort = $ProxyPort
    } else {
      Add-Step 'secret-version' $false 'no app password — secret not updated'
    }

    $ErrorActionPreference = $prevEa
  }
} elseif ($Phase -eq 'all-safe') {
  Add-Step 'cloud-sql' $false 'pending HITL (-ConfirmSql)'
}

# WIF — HITL (cena 7 + 8)
if ($Phase -eq 'wif' -or ($Phase -eq 'all-safe' -and $ConfirmWif)) {
  if (-not $ConfirmWif) {
    Add-Step 'wif' $false 'HITL: re-run with -ConfirmWif'
  } else {
    $ErrorActionPreference = 'Continue'
    $Pool = 'github-actions-pool'
    $Provider = 'github-actions-provider'
    $SaId = 'github-actions-deployer'
    $Repo = 'pedroaugustogti/capstone-project-ai-researcher'
    $ProjectNumber = (& gcloud projects describe $ProjectId --format='value(projectNumber)' 2>&1 | Out-String).Trim()
    $SaEmail = "$SaId@$ProjectId.iam.gserviceaccount.com"

    & gcloud services enable iamcredentials.googleapis.com sts.googleapis.com iam.googleapis.com --project=$ProjectId 2>&1 | Out-Null

    $poolExists = & gcloud iam workload-identity-pools describe $Pool --location=global --project=$ProjectId --format='value(name)' 2>&1
    if ($LASTEXITCODE -eq 0 -and "$poolExists") {
      Add-Step 'wif-pool' $true 'exists'
    } else {
      & gcloud iam workload-identity-pools create $Pool --project=$ProjectId --location=global --display-name='GitHub Actions Pool' 2>&1 | Out-Host
      Add-Step 'wif-pool' ($LASTEXITCODE -eq 0) 'created'
    }

    $provExists = & gcloud iam workload-identity-pools providers describe $Provider --location=global --workload-identity-pool=$Pool --project=$ProjectId --format='value(name)' 2>&1
    if ($LASTEXITCODE -eq 0 -and "$provExists") {
      Add-Step 'wif-provider' $true 'exists'
    } else {
      & gcloud iam workload-identity-pools providers create-oidc $Provider `
        --project=$ProjectId `
        --location=global `
        --workload-identity-pool=$Pool `
        --display-name='GitHub Actions Provider' `
        --issuer-uri='https://token.actions.githubusercontent.com' `
        --attribute-mapping='google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner' `
        --attribute-condition="assertion.repository=='$Repo'" 2>&1 | Out-Host
      Add-Step 'wif-provider' ($LASTEXITCODE -eq 0) "repo=$Repo"
    }

    $saExists = & gcloud iam service-accounts describe $SaEmail --project=$ProjectId --format='value(email)' 2>&1
    if ($LASTEXITCODE -eq 0 -and "$saExists") {
      Add-Step 'wif-sa' $true $SaEmail
    } else {
      & gcloud iam service-accounts create $SaId --project=$ProjectId --display-name='GitHub Actions Deployer' 2>&1 | Out-Host
      Add-Step 'wif-sa' ($LASTEXITCODE -eq 0) $SaEmail
    }

    $roles = @(
      'roles/run.admin',
      'roles/artifactregistry.writer',
      'roles/iam.serviceAccountUser',
      'roles/cloudsql.client',
      'roles/secretmanager.secretAccessor',
      'roles/cloudbuild.builds.editor',
      'roles/firebasehosting.admin'
    )
    $rolesOk = $true
    foreach ($role in $roles) {
      & gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:$SaEmail" --role=$role --condition=None --quiet 2>&1 | Out-Null
      if ($LASTEXITCODE -ne 0) { $rolesOk = $false }
    }
    Add-Step 'wif-sa-roles' $rolesOk ($roles -join ',')

    $member = "principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/$Pool/attribute.repository/$Repo"
    & gcloud iam service-accounts add-iam-policy-binding $SaEmail `
      --project=$ProjectId `
      --role='roles/iam.workloadIdentityUser' `
      --member=$member `
      --quiet 2>&1 | Out-Null
    Add-Step 'wif-impersonation' ($LASTEXITCODE -eq 0) 'workloadIdentityUser'

    $ComputeSa = "$ProjectNumber-compute@developer.gserviceaccount.com"
    & gcloud secrets add-iam-policy-binding database-url `
      --project=$ProjectId `
      --member="serviceAccount:$ComputeSa" `
      --role='roles/secretmanager.secretAccessor' `
      --quiet 2>&1 | Out-Null
    Add-Step 'compute-secret-accessor' ($LASTEXITCODE -eq 0) $ComputeSa

    $ProviderResource = (& gcloud iam workload-identity-pools providers describe $Provider --location=global --workload-identity-pool=$Pool --project=$ProjectId --format='value(name)' 2>&1 | Out-String).Trim()
    $out.wifProvider = $ProviderResource
    $out.deploySa = $SaEmail
    $out.githubRepo = $Repo

    # GitHub Variables (needs push on repo)
    $ghOk = $false
    if (Get-Command gh -ErrorAction SilentlyContinue) {
      & gh variable set GCP_PROJECT_ID --body $ProjectId --repo $Repo 2>&1 | Out-Null
      $e1 = $LASTEXITCODE
      & gh variable set GCP_WIF_PROVIDER --body $ProviderResource --repo $Repo 2>&1 | Out-Null
      $e2 = $LASTEXITCODE
      & gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body $SaEmail --repo $Repo 2>&1 | Out-Null
      $e3 = $LASTEXITCODE
      $ghOk = ($e1 -eq 0 -and $e2 -eq 0 -and $e3 -eq 0)
      Add-Step 'github-variables' $ghOk $(if ($ghOk) { 'set' } else { '403 — precisa write no repo; ver evidencias/preflight/p5-wif.json' })
    } else {
      Add-Step 'github-variables' $false 'gh CLI missing'
    }

    $ErrorActionPreference = $prevEa
  }
} elseif ($Phase -eq 'all-safe') {
  Add-Step 'wif' $false 'pending HITL (-ConfirmWif)'
}

if ($Phase -eq 'firebase') {
  Add-Step 'firebase' $false 'Use: npx firebase-tools projects:addfirebase / login (HITL)'
}

$okCount = @($out.steps | Where-Object { $_.ok }).Count
$failSql = @($out.steps | Where-Object { $_.name -like 'cloud-sql*' -and -not $_.ok }).Count
$status = if ($okCount -ge 1) { 'partial' } else { 'pending' }
if (($out.steps | Where-Object { $_.name -eq 'artifact-registry' -and $_.ok })) {
  $status = 'partial_ar_ok'
}
if ($Phase -eq 'sql' -and $ConfirmSql) {
  $need = @('cloud-sql-instance','cloud-sql-db','cloud-sql-user','pgvector','secret-version')
  $okNames = @($out.steps | Where-Object { $_.ok } | ForEach-Object { $_.name })
  $allNeed = ($need | Where-Object { $_ -in $okNames }).Count -eq $need.Count
  $status = if ($allNeed) { 'sql_ok' } elseif ($failSql -gt 0) { 'sql_partial' } else { 'sql_partial' }
}
Update-State 'P5' $status
# Evidence without secrets
$safeOut = $out.PSObject.Copy()
Write-PhaseEvidence 'P5-gcp' $out | Out-Null
Write-Host "P5=$status"
