# ============================================================
#  One-command update of the HR bot on the server.
#  Usage: from the project folder run:  .\deploy.ps1
#  It packs the code (WITHOUT .env), uploads to the server,
#  extracts and rebuilds the Docker container.
#  The database (candidates) and the server's .env are kept.
# ============================================================

# Настройки (при смене сервера правь здесь):
$Server    = "root@103.195.6.247"
$Key       = "$env:USERPROFILE\.ssh\id_ed25519"
$Project   = "D:\pythonProject\hr_bot_project"
$Archive   = "$env:TEMP\hr_bot_update.tar.gz"

function Check($step) {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED at: $step (exit $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[1/4] Packing code (excluding .env and junk)..." -ForegroundColor Cyan
Get-ChildItem -Path $Project -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
if (Test-Path $Archive) { Remove-Item $Archive -Force }
tar -czf $Archive `
    --exclude=venv --exclude=.idea --exclude=.git `
    --exclude=__pycache__ --exclude=.env --exclude="*.tar.gz" `
    -C $Project .
Check "pack archive"

Write-Host "[2/4] Uploading to server..." -ForegroundColor Cyan
scp -i $Key -o BatchMode=yes $Archive "${Server}:/root/hr_bot_update.tar.gz"
Check "scp upload"

Write-Host "[3/4] Extracting and rebuilding container..." -ForegroundColor Cyan
$remote = @'
set -e
tar -xzf /root/hr_bot_update.tar.gz -C /root/hr_bot_project
cd /root/hr_bot_project
docker compose up -d --build
echo "=== DONE ==="
docker compose ps --format 'table {{.Name}}\t{{.Status}}'
docker compose logs --tail 3 bot
'@
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($remote -replace "`r","")))
ssh -i $Key -o BatchMode=yes $Server "echo $b64 | base64 -d | bash"
Check "server rebuild"

Write-Host "[4/4] Update complete! Bot restarted with the new code." -ForegroundColor Green
