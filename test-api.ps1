# Run this when docker-compose is up to verify the API works
# Usage: .\test-api.ps1

$base = "http://localhost:8000"

Write-Host "1. Testing health..." -ForegroundColor Cyan
try {
    $r = Invoke-RestMethod -Uri "$base/health" -Method GET
    Write-Host "   OK: $($r | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   FAIL: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Testing register..." -ForegroundColor Cyan
$body = '{"email":"test@example.com","username":"testuser","password":"test123"}'
try {
    $r = Invoke-RestMethod -Uri "$base/api/auth/register" -Method POST -ContentType "application/json" -Body $body
    Write-Host "   OK: User created" -ForegroundColor Green
} catch {
    Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Yellow
    if ($_.ErrorDetails.Message) { Write-Host "   Detail: $($_.ErrorDetails.Message)" -ForegroundColor Yellow }
}

Write-Host "`n3. Testing login..." -ForegroundColor Cyan
$form = @{username="testuser"; password="test123"}
try {
    $r = Invoke-RestMethod -Uri "$base/api/auth/login" -Method POST -Body $form
    Write-Host "   OK: Token received" -ForegroundColor Green
    Write-Host "   Token: $($r.access_token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "   FAIL: $_" -ForegroundColor Red
    if ($_.ErrorDetails.Message) { Write-Host "   Detail: $($_.ErrorDetails.Message)" -ForegroundColor Yellow }
}

Write-Host "`nDone. If all 3 passed, backend works. Check frontend if auth still fails." -ForegroundColor Cyan
