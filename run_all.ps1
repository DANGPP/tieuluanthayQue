# run_all.ps1 - Run all microservices locally in the background and redirect output to logs with unbuffered output

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

Write-Host "Creating logs directory if it doesn't exist..." -ForegroundColor Green
$logDir = "d:\2026\thayque\tieuluan\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

Write-Host "Stopping existing Django servers from this workspace..." -ForegroundColor Yellow
$ports = $services.Values
$portPattern = ($ports | ForEach-Object { [regex]::Escape($_.ToString()) }) -join "|"
foreach ($port in $ports) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ -gt 0 } |
        ForEach-Object {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }
}

Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -like "*manage.py runserver*" -and
        $_.CommandLine -match "0\.0\.0\.0:($portPattern)"
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

Write-Host "Starting all 8 Django microservices..." -ForegroundColor Green

foreach ($svc in $services.Keys) {
    $port = $services[$svc]
    Write-Host "Starting $svc on port $port..." -ForegroundColor Cyan
    
    # Run django server without autoreload so each service owns one stable process.
    Start-Process -FilePath "d:\2026\thayque\tieuluan\.venv\Scripts\python.exe" `
                  -ArgumentList "-u manage.py runserver 0.0.0.0:$port --noreload" `
                  -WorkingDirectory "d:\2026\thayque\tieuluan\services\$svc" `
                  -RedirectStandardOutput "$logDir\$svc.log" `
                  -RedirectStandardError "$logDir\$svc-error.log" `
                  -WindowStyle Hidden
}

Write-Host "All services started successfully! Logs are written to $logDir" -ForegroundColor Green
