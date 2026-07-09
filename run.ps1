<#
.SYNOPSIS
    CIMF 管理系统 - 启动/维护脚本 (PowerShell)
.DESCRIPTION
    用法：
      .\run.ps1               进入交互菜单
      .\run.ps1 1             启动开发服务器
      .\run.ps1 2             安装/初始化子菜单
      .\run.ps1 3             维护子菜单
      .\run.ps1 4             初始化海外客户样本数据
      .\run.ps1 5             初始化国内客户样本数据
      .\run.ps1 0 / --help    显示帮助
#>

param([string]$arg = "")

$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = (Get-Location).Path }
Set-Location $ScriptRoot

# === 颜色定义 ===
$Colors = @{}
if ($Host.UI.RawUI.ForegroundColor) {
    $Colors.Red    = [ConsoleColor]::Red
    $Colors.Green  = [ConsoleColor]::Green
    $Colors.Yellow = [ConsoleColor]::Yellow
    $Colors.Blue   = [ConsoleColor]::Blue
    $Colors.Cyan   = [ConsoleColor]::Cyan
    $Colors.White  = [ConsoleColor]::White
}

function Write-Color($color, $text) {
    if ($Colors.ContainsKey($color)) {
        Write-Host $text -ForegroundColor $Colors.$color -NoNewline
    } else { Write-Host $text -NoNewline }
}
function Write-Line($color, $text) { Write-Color $color $text; Write-Host "" }

function Write-Info($text)    { Write-Host "[信息] $text" -ForegroundColor Cyan }
function Write-Success($text) { Write-Host "[成功] $text" -ForegroundColor Green }
function Write-Warn($text)    { Write-Host "[警告] $text" -ForegroundColor Yellow }
function Write-Error($text)   { Write-Host "[错误] $text" -ForegroundColor Red }

# === 配置 ===
$VENV_DIR        = Join-Path $ScriptRoot "venv"
$PIP_INDEX_DEF   = "https://pypi.tuna.tsinghua.edu.cn/simple"
$APP_PORT        = 8000
$DB_PATH         = "instance\django.db"
$BACKUP_DIR      = Join-Path $ScriptRoot "storage\backups"

# 解析 config.env
$configEnv = Join-Path $ScriptRoot "config.env"
if (Test-Path $configEnv) {
    Get-Content $configEnv | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_]\w*)\s*=\s*(.*?)\s*$') {
            $key = $matches[1]
            $val = $matches[2]
            Set-Variable -Name $key -Value $val -Scope Script -ErrorAction SilentlyContinue
            if ($key -eq "DJANGO_PORT" -and $val) { $Script:APP_PORT = [int]$val }
        }
    }
}
if (-not $Script:PIP_INDEX) { $Script:PIP_INDEX = $PIP_INDEX_DEF }

# === 辅助函数 ===

function Get-VenvPython {
    $paths = @(
        Join-Path $VENV_DIR "Scripts\python.exe",
        Join-Path $VENV_DIR "Scripts\python3.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return "python"
}

function Test-Command($cmd) {
    try { Get-Command $cmd -ErrorAction Stop; return $true }
    catch { return $false }
}

function Pause-Message {
    Write-Host ""
    Write-Host "按回车键继续..." -NoNewline
    $null = Read-Host
}

# === 主功能函数 ===

function Run-Server {
    Write-Host ""
    Write-Line Green ">>> 启动 CIMF 管理系统 (开发模式)"

    @("storage\uploads", "storage\backups", "instance") | ForEach-Object {
        $dir = Join-Path $ScriptRoot $_
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    }

    Write-Host "  监听地址 : http://0.0.0.0:$APP_PORT"
    Write-Host "  本地访问 : http://127.0.0.1:$APP_PORT"
    Write-Host "  后台管理 : http://127.0.0.1:$APP_PORT/admin/"
    Write-Host "  按 Ctrl+C 停止服务"
    Write-Host ""

    $env:DJANGO_SETTINGS_MODULE = "cimf_django.settings"
    & (Get-VenvPython) run.py
}

function Install-Venv {
    Write-Host ""
    Write-Info "创建虚拟环境..."

    if (Test-Path $VENV_DIR) {
        Write-Warn "虚拟环境已存在"
        $ans = Read-Host "是否重新创建？(y/N) "
        if ($ans -eq "y" -or $ans -eq "Y") { Remove-Item -Recurse -Force $VENV_DIR }
        else { Write-Host "取消创建"; return }
    }

    Write-Host "创建虚拟环境..."
    python -m venv $VENV_DIR

    Write-Host "安装依赖..."
    $venvPip = Join-Path $VENV_DIR "Scripts\pip.exe"
    & $venvPip install --upgrade pip -i $Script:PIP_INDEX -q

    $reqFile = Join-Path $ScriptRoot "requirements.txt"
    if (-not (Test-Path $reqFile)) { Write-Warn "未找到 requirements.txt"; return }

    $lines = Get-Content $reqFile | Where-Object { $_ -and $_ -notmatch '^\s*#' }
    $total = $lines.Count
    Write-Host "共 $total 个依赖包"
    Write-Host ""

    $current = 0
    foreach ($line in $lines) {
        $current++
        $pkgName = ($line -split '[>=<!\[\]]')[0].Trim()
        Write-Host "  [$current/$total] $pkgName " -NoNewline
        & $venvPip install $line -i $Script:PIP_INDEX -q 2>$null
        if ($LASTEXITCODE -eq 0) { Write-Host "[OK]" -ForegroundColor Green }
        else { Write-Host "[FAIL]" -ForegroundColor Red }
    }
    Write-Success "虚拟环境创建完成"
}

function Invoke-Python($scriptBlock) {
    $python = Get-VenvPython
    $script = $scriptBlock.ToString()
    & $python -c $script
    return $LASTEXITCODE
}

function Init-System {
    Write-Host ""
    Write-Line Green ">>> 初始化系统"

    $python = Get-VenvPython
    $dbFile = Join-Path $ScriptRoot $DB_PATH

    if (Test-Path $dbFile) {
        Write-Warn "检测到已存在数据库文件"
        $ans = Read-Host "是否备份现有数据库？(Y/n) "
        if ($ans -ne "n" -and $ans -ne "N") { Backup-Database }
    }

    Write-Info "[1/2] 初始化数据 (migrations + 初始数据)..."
    & $python init_db.py --with-data --force
    Write-Success "初始化完成！"
}

function Init-OverseasCustomers {
    Write-Host ""
    Write-Line Green ">>> 初始化海外客户样本数据"
    $python = Get-VenvPython
    & $python manage.py init_overseas_customers
    Write-Success "海外客户样本数据初始化完成！"
}

function Init-DomesticCustomers {
    Write-Host ""
    Write-Line Green ">>> 初始化国内客户样本数据"
    $python = Get-VenvPython
    & $python manage.py init_domestic_customers
    Write-Success "国内客户样本数据初始化完成！"
}

function Backup-Database {
    if (-not (Test-Path $BACKUP_DIR)) { New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null }
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $dbFile = Join-Path $ScriptRoot $DB_PATH
    if (Test-Path $dbFile) {
        $backupFile = Join-Path $BACKUP_DIR "django_$timestamp.db"
        Copy-Item $dbFile $backupFile
        Write-Success "数据库已备份到: $backupFile"
    } else { Write-Warn "数据库文件不存在，跳过备份" }
}

function Clean-Cache {
    Write-Host ""
    Write-Line Green ">>> 清理缓存"
    Write-Host "删除 __pycache__、.pyc..."

    Get-ChildItem -Path $ScriptRoot -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue }
    Get-ChildItem -Path $ScriptRoot -Filter "*.pyc" -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue }
    Get-ChildItem -Path $ScriptRoot -Filter "*.pyo" -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue }

    @(".pytest_cache", ".coverage", ".mypy_cache", ".ruff_cache",
      "storage\staticfiles\.cache") | ForEach-Object {
        $p = Join-Path $ScriptRoot $_
        if (Test-Path $p) { Remove-Item -Recurse -Force $p -ErrorAction SilentlyContinue }
    }
    Write-Success "缓存清理完成"
}

function Kill-Server {
    Write-Host ""
    Write-Line Green ">>> 杀死服务器进程 (端口: $APP_PORT)"
    try {
        $connections = netstat -ano | Select-String ":$APP_PORT"
        if (-not $connections) { Write-Warn "端口 $APP_PORT 上没有运行的进程"; return }

        $pids = @()
        foreach ($conn in $connections) {
            $parts = $conn.ToString() -split '\s+'
            if ($parts.Count -ge 5 -and $parts[4] -match '^\d+$') { $pids += [int]$parts[4] }
        }
        $pids = $pids | Select-Object -Unique

        foreach ($pid in $pids) {
            Write-Host "正在杀死进程 PID: $pid"
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Success "进程已杀死 (PID: $pid)"
        }
    } catch { Write-Error "杀死进程失败: $_" }
}

function Show-EnvVars {
    Write-Host ""
    Write-Line Green ">>> 查看环境变量"
    $vars = @("DJANGO_ENV", "DJANGO_DEBUG", "DJANGO_HOST", "DJANGO_PORT", "SECRET_KEY")
    foreach ($v in $vars) {
        $val = if ($v -eq "SECRET_KEY") {
            if ((Get-Variable -Name $v -Scope Script -ErrorAction SilentlyContinue).Value) { "已设置" } else { "未设置" }
        } else {
            $val = (Get-Variable -Name $v -Scope Script -ErrorAction SilentlyContinue).Value
            if ($val) { $val } else { "未设置" }
        }
        Write-Host "  $v = $val"
    }
}

function Create-EnvFile {
    Write-Host ""
    Write-Line Green ">>> 创建 config.env 文件"

    $configFile = Join-Path $ScriptRoot "config.env"
    $configSample = Join-Path $ScriptRoot "config.env.sample"

    if (-not (Test-Path $configSample)) { Write-Error "config.env.sample 不存在"; return }

    if (Test-Path $configFile) {
        Write-Warn "config.env 已存在"
        $ans = Read-Host "是否覆盖？(y/N) "
        if ($ans -ne "y" -and $ans -ne "Y") { Write-Host "取消创建"; return }
    }

    Write-Host "请选择数据库类型："
    Write-Host "  1 → SQLite (默认，适合开发和测试)"
    Write-Host "  2 → MySQL (适合生产环境)"
    $dbChoice = Read-Host "请输入选项 (1/2)"

    if ($dbChoice -eq "2") {
        $dbName = Read-Host "  数据库名 [cimf]"
        $dbUser = Read-Host "  用户名 [root]"
        $dbPass = Read-Host "  密码"
        $dbHost = Read-Host "  主机 [localhost]"
        $dbPort = Read-Host "  端口 [3306]"
        if (-not $dbName) { $dbName = "cimf" }
        if (-not $dbUser) { $dbUser = "root" }
        if (-not $dbHost) { $dbHost = "localhost" }
        if (-not $dbPort) { $dbPort = "3306" }

        Copy-Item $configSample $configFile -Force
        $content = Get-Content $configFile -Raw

        $replacements = @(
            @{old='^DJANGO_DB_TYPE=sqlite'; new="DJANGO_DB_TYPE=mysql"}
            @{old='^# DJANGO_DB_NAME=cimf'; new="DJANGO_DB_NAME=$dbName"}
            @{old='^# DJANGO_DB_USER=root'; new="DJANGO_DB_USER=$dbUser"}
            @{old='^# DJANGO_DB_PASSWORD=$'; new="DJANGO_DB_PASSWORD=$dbPass"}
            @{old='^# DJANGO_DB_HOST=localhost'; new="DJANGO_DB_HOST=$dbHost"}
            @{old='^# DJANGO_DB_PORT=3306'; new="DJANGO_DB_PORT=$dbPort"}
        )
        foreach ($r in $replacements) { $content = $content -replace $r.old, $r.new }

        $uncomment = @("DJANGO_DB_TYPE=mysql", "DJANGO_DB_NAME=", "DJANGO_DB_USER=",
                       "DJANGO_DB_PASSWORD=", "DJANGO_DB_HOST=", "DJANGO_DB_PORT=")
        foreach ($key in $uncomment) { $content = $content -replace "(?m)^# ($key)", '$1' }

        Set-Content -Path $configFile -Value $content
        Write-Success "已创建 config.env (MySQL)"
    } else {
        Copy-Item $configSample $configFile
        Write-Success "已创建 config.env (SQLite)"
    }
}

function Generate-SecretKey {
    Write-Host ""
    Write-Line Green ">>> 生成随机 SECRET_KEY"

    $newKey = python -c "import secrets; print(secrets.token_urlsafe(50))"
    $configFile = Join-Path $ScriptRoot "config.env"

    if (-not (Test-Path $configFile)) { Write-Warn "请先创建 config.env 文件"; return }

    $content = Get-Content $configFile -Raw
    if ($content -match '(?m)^SECRET_KEY=.*') {
        $content = $content -replace '(?m)^SECRET_KEY=.*', "SECRET_KEY=$newKey"
    } else {
        $content += "`r`nSECRET_KEY=$newKey"
    }
    Set-Content -Path $configFile -Value $content
    Write-Success "SECRET_KEY 已更新到 config.env"
}

function Update-ChinaRegions {
    Write-Host ""
    Write-Line Green ">>> 下载/更新省市区数据"

    $python = Get-VenvPython

    Write-Info "[1/2] 从网络下载最新省市区数据..."
    & $python -c @"
from core.services.china_region_service import ChinaRegionService
r = ChinaRegionService.download_to_file()
print('  ' + ('[OK]' if r['success'] else '[FAIL]') + ' ' + r.get('message', r.get('error', '')))
"@
    if ($LASTEXITCODE -ne 0) { Write-Error "下载失败"; return }

    Write-Info "[2/2] 更新数据库..."
    & $python -c @"
from core.services.china_region_service import ChinaRegionService
r = ChinaRegionService.import_from_file()
print('  ' + ('[OK]' if r['success'] else '[FAIL]') + ' 省份:' + str(r.get('provinces',0)) + ' 城市:' + str(r.get('cities',0)) + ' 区县:' + str(r.get('districts',0)))
"@
    Write-Success "省市区数据更新完成！"
}

function Run-RuffCheck {
    $python = Get-VenvPython

    & $python -m ruff --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Ruff 未安装，正在安装..."
        & $python -m pip install ruff -q
    }

    $reportDir = Join-Path $ScriptRoot "storage\reports"
    if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = Join-Path $reportDir "ruff_$timestamp.txt"

    Write-Info "正在扫描代码..."
    & $python -m ruff check core/ modules/ cimf_django/ --output-format=concise *>"$reportFile"
    $exitCode = $LASTEXITCODE

    Get-Content $reportFile | Write-Host

    if ($exitCode -ne 0) { Write-Host "[完成] 发现代码问题" -ForegroundColor Yellow }
    else { Write-Host "[OK] 未发现问题" -ForegroundColor Green }
    Write-Info "报告已保存: $reportFile"
}

# === 菜单 ===

function Show-Menu {
    Clear-Host
    Write-Host @"

  ______     __     __    __     ______
 /\  ___\   /\ \   /\  -./  \   /\  ___\
 \ \ \____  \ \ \  \ \-./\  \  \ \  __\
  \ \_____\  \ \_\  \ \_\ \_\  \ \_
   \/_____/   \/_/   \/_/  \/_/   \/_/

"@ -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "  CIMF 管理系统 - 管理菜单" -ForegroundColor White
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1 → 启动服务器"
    Write-Host "  2 → 安装/初始化"
    Write-Host "  3 → 维护"
    Write-Host "  0 → 退出"
    Write-Host ""
    Write-Host "  h → 显示帮助"
    Write-Host ""
}

function Show-InitMenu {
    Clear-Host
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "   安装/初始化" -ForegroundColor White
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1 → 创建 config.env 文件"
    Write-Host "  2 → 创建虚拟环境并安装依赖"
    Write-Host "  3 → 初始化系统 (重建数据库+创建管理员)"
    Write-Host "  4 → 生成随机 SECRET_KEY"
    Write-Host "  5 → 初始化海外客户样本数据"
    Write-Host "  6 → 初始化国内客户样本数据"
    Write-Host "  0 → 返回主菜单"
    Write-Host ""
}

function Show-MaintMenu {
    Clear-Host
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "   维护" -ForegroundColor White
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1 → 数据库备份"
    Write-Host "  2 → 清理缓存"
    Write-Host "  3 → 查看环境变量"
    Write-Host "  4 → 杀死服务器进程"
    Write-Host "  5 → 下载/更新省市区数据"
    Write-Host "  6 → Ruff 代码检查"
    Write-Host "  0 → 返回主菜单"
    Write-Host ""
}

function Show-Help {
    Write-Host ""
    Write-Host "用法："
    Write-Host "  .\run.ps1               进入交互菜单"
    Write-Host "  .\run.ps1 1             启动开发服务器"
    Write-Host "  .\run.ps1 2             安装/初始化"
    Write-Host "  .\run.ps1 3             维护"
    Write-Host "  .\run.ps1 4             初始化海外客户样本数据"
    Write-Host "  .\run.ps1 5             初始化国内客户样本数据"
    Write-Host "  .\run.ps1 0 / --help    显示帮助"
    Write-Host ""
    Write-Host "环境变量："
    Write-Host "  DJANGO_PORT             服务器端口 (默认: 8000)"
    Write-Host ""
}

function Run-InitMenu {
    :initLoop while ($true) {
        Show-InitMenu
        $choice = Read-Host "请输入选项 (0/1/2/3/4/5/6)"
        switch ($choice) {
            "0" { return }
            "1" { Write-Host ""; Create-EnvFile }
            "2" { Write-Host ""; Install-Venv }
            "3" { Write-Host ""; Init-System }
            "4" { Write-Host ""; Generate-SecretKey }
            "5" { Write-Host ""; Init-OverseasCustomers }
            "6" { Write-Host ""; Init-DomesticCustomers }
            default { Write-Warn "无效选项 '$choice'"; continue }
        }
        Pause-Message
    }
}

function Run-MaintMenu {
    :maintLoop while ($true) {
        Show-MaintMenu
        $choice = Read-Host "请输入选项 (0/1/2/3/4/5/6)"
        switch ($choice) {
            "0" { return }
            "1" { Write-Host ""; Backup-Database }
            "2" { Write-Host ""; Clean-Cache }
            "3" { Write-Host ""; Show-EnvVars }
            "4" { Write-Host ""; Kill-Server }
            "5" { Write-Host ""; Update-ChinaRegions }
            "6" { Write-Host ""; Run-RuffCheck }
            default { Write-Warn "无效选项 '$choice'"; continue }
        }
        Pause-Message
    }
}

# === 主逻辑 ===

if ($arg) {
    switch -Exact ($arg) {
        "1" { Run-Server; break }
        "2" { Run-InitMenu; break }
        "3" { Run-MaintMenu; break }
        "4" { Init-OverseasCustomers; break }
        "5" { Init-DomesticCustomers; break }
        "0" { Show-Help; break }
        "-h" { Show-Help; break }
        "--help" { Show-Help; break }
        default { Write-Error "未知选项: $arg"; Show-Help }
    }
    exit
}

# 交互菜单
:mainLoop while ($true) {
    Show-Menu
    $choice = Read-Host "请输入选项 (0/1/2/3/h)"

    switch -Exact ($choice) {
        "0" { Write-Host ""; Write-Host "感谢使用，再见！" -ForegroundColor Green; exit }
        "1" { Run-Server }
        "2" { Run-InitMenu }
        "3" { Run-MaintMenu }
        "h" { Show-Help; Pause-Message }
        default { Write-Warn "无效选项 '$choice'" }
    }
    Pause-Message
}
