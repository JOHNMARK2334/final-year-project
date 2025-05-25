Write-Host "Logging in..."
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body (@{
  username = "john"
  password = "pass"
} | ConvertTo-Json) -ContentType "application/json"

if (-not $response.access_token) {
  Write-Host "❌ Login failed. Check credentials."
  exit
}

$token = $response.access_token
Write-Host "✅ Token retrieved: $token"

Write-Host "Sending query..."
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/query" -Method POST `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body (@{ text = "I have fatigue and a mild fever" } | ConvertTo-Json) `
  -ContentType "application/json"
