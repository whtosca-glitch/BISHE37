$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$loginUrl = "http://127.0.0.1:8000/login.html"
$pythonPath = $null
$pythonStartArgs = @("device_service.py")
$requirementsFile = Join-Path $projectRoot "requirements.txt"

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonPath = (& py -3 -c "import sys; print(sys.executable)").Trim()
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonPath = (Get-Command python).Source
}

if (-not $pythonPath) {
    Write-Host "[错误] 未检测到 Python，请先安装 Python 3 并加入 PATH。" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

& $pythonPath -c "import pymysql, requests, openpyxl" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[提示] 正在安装项目依赖，请稍候..." -ForegroundColor Yellow
    if (Test-Path $requirementsFile) {
        & $pythonPath -m pip install -r $requirementsFile
    } else {
        & $pythonPath -m pip install pymysql requests openpyxl
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 项目依赖安装失败，请检查网络或 Python 环境。" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $listening) {
    $stdoutLog = Join-Path $projectRoot "start_project.stdout.log"
    $stderrLog = Join-Path $projectRoot "start_project.stderr.log"
    Start-Process -FilePath $pythonPath `
        -ArgumentList $pythonStartArgs `
        -WorkingDirectory $projectRoot `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -WindowStyle Hidden | Out-Null
}

$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        Invoke-WebRequest -Uri $loginUrl -UseBasicParsing -TimeoutSec 2 | Out-Null
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($ready) {
    Start-Process $loginUrl | Out-Null
    exit 0
}

Write-Host "[错误] 服务启动失败，请检查弹出的服务窗口。" -ForegroundColor Red
Read-Host "按回车键退出"
exit 1
