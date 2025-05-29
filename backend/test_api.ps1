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
# Create a new chat first to get a chat_id
$chatResp = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chats" -Method POST -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json"
$chat_id = $chatResp.id
Invoke-RestMethod -Uri ("http://127.0.0.1:5000/api/chats/$chat_id/message") -Method POST `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body (@{ content = "I have fatigue and a mild fever" } | ConvertTo-Json) `
  -ContentType "application/json"
