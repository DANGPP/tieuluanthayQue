param(
    [switch]$KeepDb,
    [switch]$NoBuild,
    [switch]$SkipSeed,
    [int]$TimeoutSeconds = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$services = [ordered]@{
    "user-service"     = 8001
    "product-service"  = 8002
    "cart-service"     = 8003
    "order-service"    = 8004
    "payment-service"  = 8005
    "shipping-service" = 8006
    "ai-service"       = 8007
    "gateway-service"  = 8008
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Compose {
    param([string[]]$ArgsList)

    & docker compose @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose $($ArgsList -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Wait-PostgresHealthy {
    param([int]$Timeout)

    $deadline = (Get-Date).AddSeconds($Timeout)
    do {
        $status = (& docker inspect --format "{{.State.Health.Status}}" tieuluan_postgres 2>$null)
        if ($LASTEXITCODE -eq 0 -and $status -eq "healthy") {
            Write-Host "PostgreSQL is healthy." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 3
    } while ((Get-Date) -lt $deadline)

    throw "PostgreSQL did not become healthy within $Timeout seconds."
}

function Wait-HttpOk {
    param(
        [string]$Name,
        [int]$Port,
        [int]$Timeout
    )

    $deadline = (Get-Date).AddSeconds($Timeout)
    $url = "http://localhost:$Port/admin/"
    do {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Host "$Name is responding on port $Port." -ForegroundColor Green
                return
            }
        }
        catch {
            Start-Sleep -Seconds 3
        }
    } while ((Get-Date) -lt $deadline)

    throw "$Name did not respond at $url within $Timeout seconds."
}

function Show-ContainerLogsHint {
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  docker compose ps"
    Write-Host "  docker compose logs -f gateway-service"
    Write-Host "  docker compose logs -f seed-data"
}

function Test-DockerEngine {
    $oldErrorActionPreference = $ErrorActionPreference
    try {
        $script:ErrorActionPreference = "Continue"
        & docker info *> $null
        return ($LASTEXITCODE -eq 0)
    }
    finally {
        $script:ErrorActionPreference = $oldErrorActionPreference
    }
}

try {
    Write-Step "Checking Docker Desktop"
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker CLI was not found. Install/open Docker Desktop and try again."
    }

    if (-not (Test-DockerEngine)) {
        throw "Docker Desktop is not running or the Docker engine is unavailable."
    }

    & docker compose version
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose plugin is unavailable."
    }

    Write-Step "Cleaning previous containers"
    if ($KeepDb) {
        Invoke-Compose -ArgsList @("--profile", "tools", "down", "--remove-orphans")
    }
    else {
        Write-Host "Resetting PostgreSQL Docker volume for a clean demo database." -ForegroundColor Yellow
        Invoke-Compose -ArgsList @("--profile", "tools", "down", "--remove-orphans", "-v")
    }

    Write-Step "Deploying PostgreSQL and creating service databases"
    Invoke-Compose -ArgsList @("up", "-d", "postgres")
    Wait-PostgresHealthy -Timeout $TimeoutSeconds

    Write-Step "Deploying all Django microservices"
    $upArgs = @("up", "-d")
    if (-not $NoBuild) {
        $upArgs += "--build"
    }
    $upArgs += @(
        "user-service",
        "product-service",
        "cart-service",
        "order-service",
        "shipping-service",
        "payment-service",
        "ai-service",
        "gateway-service"
    )
    Invoke-Compose -ArgsList $upArgs

    Write-Step "Waiting for services to finish migrations and start"
    foreach ($svc in $services.GetEnumerator()) {
        Wait-HttpOk -Name $svc.Key -Port $svc.Value -Timeout $TimeoutSeconds
    }

    if (-not $SkipSeed) {
        Write-Step "Inserting demo data"
        $seedArgs = @("--profile", "tools", "run", "--rm")
        if (-not $NoBuild) {
            $seedArgs += "--build"
        }
        $seedArgs += "seed-data"
        Invoke-Compose -ArgsList $seedArgs
    }
    else {
        Write-Host "Skipping seed data because -SkipSeed was provided." -ForegroundColor Yellow
    }

    Write-Step "Checking gateway status"
    try {
        $status = Invoke-WebRequest -Uri "http://localhost:8008/ui/api/status" -UseBasicParsing -TimeoutSec 10
        Write-Host $status.Content
    }
    catch {
        Write-Host "Gateway status endpoint was not available yet: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Step "Final Docker status"
    Invoke-Compose -ArgsList @("ps")

    Write-Host ""
    Write-Host "Done. Open http://localhost:8008" -ForegroundColor Green
    Write-Host "Demo accounts: customer1/admin1/staff1/shipper1, password: password123" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Show-ContainerLogsHint
    exit 1
}
