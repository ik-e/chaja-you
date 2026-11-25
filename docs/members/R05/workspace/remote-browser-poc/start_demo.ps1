# 원격 브라우저 PoC - 두 PC 시연용 실행 스크립트 (Windows PowerShell)
# 사용법: 이 폴더에서  powershell -ExecutionPolicy Bypass -File .\start_demo.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1) 이 폴더 전용 가상환경과 패키지 (공통 루트 의존성은 건드리지 않음)
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $py -m pip install -q -r requirements.txt

# 2) Chrome이 없으면 Playwright 번들 Chromium 사용
$chromePaths = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
if (-not ($chromePaths | Where-Object { Test-Path $_ })) {
  Write-Host "Chrome이 없어 Chromium을 설치합니다..."
  & $py -m playwright install chromium
  $env:CHROME_CHANNEL = ""
}

# 3) 다른 PC가 접속할 이 PC의 주소
$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
  Sort-Object -Property InterfaceMetric | Select-Object -First 1).IPAddress

# 4) 모의 사이트(이 PC 안에서만 사용)와 제어 서버(다른 PC 접속 허용) 실행
$mock = Start-Process -FilePath $py -ArgumentList "-m uvicorn mock_site.app:app --port 8001 --no-access-log" -WorkingDirectory $PSScriptRoot -PassThru -WindowStyle Minimized
$env:MOCK_BASE = "http://127.0.0.1:8001"
Write-Host ""
Write-Host "=============================================================="
Write-Host " 다른 PC(팀장님)에서 열 주소:  http://${ip}:8002"
Write-Host " 가상 계정: tutor_a / Mock-Pass-A!2026  (시험 전용)"
Write-Host " 종료: 이 창에서 Ctrl+C"
Write-Host "=============================================================="
Write-Host ""
try {
  & $py -m uvicorn control_server.app:app --host 0.0.0.0 --port 8002 --no-access-log
} finally {
  Stop-Process -Id $mock.Id -ErrorAction SilentlyContinue
}
