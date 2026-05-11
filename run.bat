@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ============================================
REM CIMF 管理系统 - Windows 启动/维护脚本
REM ============================================
REM 用法：
REM   run.bat               进入交互菜单
REM   run.bat 1             启动开发服务器
REM   run.bat 2             安装/初始化子菜单
REM   run.bat 3             维护子菜单
REM   run.bat 0 / --help    显示帮助
REM ============================================

cd /d "%~dp0"

REM === ANSI 颜色（Windows 10 1607+）===
set "ESC="
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
if defined ESC (
    set "RED=%ESC%[31m"
    set "GREEN=%ESC%[32m"
    set "YELLOW=%ESC%[33m"
    set "BLUE=%ESC%[34m"
    set "CYAN=%ESC%[36m"
    set "WHITE=%ESC%[37m"
    set "NC=%ESC%[0m"
) else (
    REM 不支持的终端：无色
    set "RED="
    set "GREEN="
    set "YELLOW="
    set "BLUE="
    set "CYAN="
    set "WHITE="
    set "NC="
)

set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "VENV_DIR=%PROJECT_ROOT%\venv"
set "PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple"
set "APP_PORT=8000"
set "DB_PATH=instance\django.db"
set "BACKUP_DIR=%PROJECT_ROOT%\storage\backups"

REM === 解析 config.env（跳过注释行）===
if exist "%PROJECT_ROOT%\config.env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%a in ("%PROJECT_ROOT%\config.env") do (
        set "%%a=%%b"
        if "%%a"=="DJANGO_PORT" set "APP_PORT=%%b"
    )
)

REM ============ 辅助函数 ============

REM === 获取 venv 中的 Python ===
:get_venv_python
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo %VENV_DIR%\Scripts\python.exe
    exit /b 0
)
if exist "%VENV_DIR%\Scripts\python3.exe" (
    echo %VENV_DIR%\Scripts\python3.exe
    exit /b 0
)
where python >nul 2>&1
if !errorlevel! equ 0 (
    where python
    exit /b 0
)
echo python
exit /b 0

REM === 激活虚拟环境 ===
:activate_venv
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
)
goto :eof

REM ============ 主功能函数 ============

REM === 启动开发服务器 ===
:run_server
echo.
echo %GREEN%^>^>^> 启动 CIMF 管理系统（开发模式）%NC%
echo.
if not exist "%PROJECT_ROOT%\storage\uploads" mkdir "%PROJECT_ROOT%\storage\uploads" 2>nul
if not exist "%PROJECT_ROOT%\storage\backups" mkdir "%PROJECT_ROOT%\storage\backups" 2>nul
if not exist "%PROJECT_ROOT%\instance" mkdir "%PROJECT_ROOT%\instance" 2>nul

echo   监听地址 : http://0.0.0.0:%APP_PORT%
echo   本地访问 : http://127.0.0.1:%APP_PORT%
echo   后台管理 : http://127.0.0.1:%APP_PORT%/admin/
echo   按 Ctrl+C 停止服务
echo.

set "DJANGO_SETTINGS_MODULE=cimf_django.settings"
for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"
%VENV_PYTHON% run.py
goto :eof

REM === 安装虚拟环境 ===
:install_venv
echo.
echo %BLUE%[准备]%NC% 创建虚拟环境...
echo.
if exist "%VENV_DIR%" (
    echo %YELLOW%虚拟环境已存在%NC%
    set /p "answer=是否重新创建？(y/N) "
    if /i "!answer!"=="y" (
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo 取消创建
        goto :eof
    )
)
echo 创建虚拟环境...
python -m venv "%VENV_DIR%"

echo 安装依赖...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip -i "%PIP_INDEX%" -q

if exist "%PROJECT_ROOT%\requirements.txt" (
    set /a count=0
    for /f "usebackq eol=# tokens=*" %%a in ("%PROJECT_ROOT%\requirements.txt") do (
        set "_line=%%a"
        if not "!_line!"=="" set /a count+=1
    )
    echo 共 !count! 个依赖包
    echo.
    for /f "usebackq eol=# tokens=*" %%a in ("%PROJECT_ROOT%\requirements.txt") do (
        set "_line=%%a"
        if not "!_line!"=="" (
            <nul set /p "=  %%a "
            "%VENV_DIR%\Scripts\python.exe" -m pip install "%%a" -i "%PIP_INDEX%" -q 2>nul
            if !errorlevel! equ 0 (echo %GREEN%[OK]%NC%) else (echo %RED%[FAIL]%NC%)
        )
    )
    echo.
    echo %GREEN%虚拟环境创建完成%NC%
) else (
    echo %YELLOW%未找到 requirements.txt%NC%
)
goto :eof

REM === 初始化系统 ===
:init_system
echo.
echo %GREEN%^>^>^> 初始化系统%NC%
echo.

call :activate_venv

for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"

if exist "%PROJECT_ROOT%\%DB_PATH%" (
    echo %YELLOW%检测到已存在数据库文件%NC%
    set /p "answer=是否备份现有数据库？(Y/n) "
    if /i not "!answer!"=="n" (
        call :backup_database
    )
)
echo %BLUE%[1/2]%NC% 初始化数据（migrations + 初始数据）...
%VENV_PYTHON% init_db.py --with-data --force
echo %GREEN%初始化完成！%NC%
goto :eof

REM === 初始化海外客户样本数据 ===
:init_overseas_customers
echo.
echo %GREEN%^>^>^> 初始化海外客户样本数据%NC%
echo.
for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"
%VENV_PYTHON% manage.py init_overseas_customers
echo %GREEN%海外客户样本数据初始化完成！%NC%
goto :eof

REM === 初始化国内客户样本数据 ===
:init_domestic_customers
echo.
echo %GREEN%^>^>^> 初始化国内客户样本数据%NC%
echo.
for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"
%VENV_PYTHON% manage.py init_domestic_customers
echo %GREEN%国内客户样本数据初始化完成！%NC%
goto :eof

REM === 数据库备份 ===
:backup_database
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul

set "timestamp=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "timestamp=%timestamp: =0%"

if exist "%PROJECT_ROOT%\%DB_PATH%" (
    set "backup_file=%BACKUP_DIR%\django_%timestamp%.db"
    copy /y "%PROJECT_ROOT%\%DB_PATH%" "!backup_file!" >nul
    echo %GREEN%数据库已备份到: !backup_file!%NC%
) else (
    echo %YELLOW%数据库文件不存在，跳过备份%NC%
)
goto :eof

REM === 清理缓存 ===
:clean_cache
echo.
echo %GREEN%^>^>^> 清理缓存%NC%
echo.
echo 删除 __pycache__、.pyc...
for /d /r "%PROJECT_ROOT%" %%i in (__pycache__) do if exist "%%i" rmdir /s /q "%%i" 2>nul
del /s /q "%PROJECT_ROOT%\*.pyc" 2>nul
del /s /q "%PROJECT_ROOT%\*.pyo" 2>nul
if exist "%PROJECT_ROOT%\.pytest_cache" rmdir /s /q "%PROJECT_ROOT%\.pytest_cache" 2>nul
if exist "%PROJECT_ROOT%\.coverage" del /q "%PROJECT_ROOT%\.coverage" 2>nul
if exist "%PROJECT_ROOT%\.mypy_cache" rmdir /s /q "%PROJECT_ROOT%\.mypy_cache" 2>nul
if exist "%PROJECT_ROOT%\.ruff_cache" rmdir /s /q "%PROJECT_ROOT%\.ruff_cache" 2>nul
if exist "%PROJECT_ROOT%\storage\staticfiles\.cache" rmdir /s /q "%PROJECT_ROOT%\storage\staticfiles\.cache" 2>nul
echo %GREEN%缓存清理完成%NC%
goto :eof

REM === 杀死服务器进程 ===
:kill_server
echo.
echo %GREEN%^>^>^> 杀死服务器进程（端口: %APP_PORT%）%NC%
echo.
set "FOUND_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%APP_PORT%" ^| findstr "LISTENING" 2^>nul') do set "FOUND_PID=%%a"
if not defined FOUND_PID (
    echo %YELLOW%端口 %APP_PORT% 上没有运行的进程%NC%
    goto :eof
)
echo 找到进程 PID: !FOUND_PID!
taskkill /F /PID !FOUND_PID! >nul 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%进程已杀死（PID: !FOUND_PID!）%NC%
) else (
    echo %RED%杀死进程失败（PID: !FOUND_PID!）%NC%
)
goto :eof

REM === 查看当前环境变量 ===
:show_env_vars
echo.
echo %GREEN%^>^>^> 查看环境变量%NC%
echo.
echo   DJANGO_ENV=%DJANGO_ENV%
echo   DJANGO_DEBUG=%DJANGO_DEBUG%
echo   DJANGO_HOST=%DJANGO_HOST%
echo   DJANGO_PORT=%DJANGO_PORT%
echo   SECRET_KEY=已设置
goto :eof

REM === 创建 config.env 文件 ===
:create_env_file
echo.
echo %GREEN%^>^>^> 创建 config.env 文件%NC%
echo.
if exist "%PROJECT_ROOT%\config.env" (
    echo %YELLOW%config.env 已存在%NC%
    set /p "answer=是否覆盖？(y/N) "
    if /i not "!answer!"=="y" (
        echo 取消创建
        goto :eof
    )
)
if not exist "%PROJECT_ROOT%\config.env.sample" (
    echo %RED%config.env.sample 不存在%NC%
    goto :eof
)
echo 请选择数据库类型：
echo   1 ^> SQLite（默认，适合开发和测试）
echo   2 ^> MySQL（适合生产环境）
set /p "db_choice=请输入选项 (1/2): "

if "!db_choice!"=="2" (
    set /p "db_name=  数据库名 [cimf]: "
    set /p "db_user=  用户名 [root]: "
    set /p "db_pass=  密码: "
    set /p "db_host=  主机 [localhost]: "
    set /p "db_port=  端口 [3306]: "
    if "!db_name!"=="" set "db_name=cimf"
    if "!db_user!"=="" set "db_user=root"
    if "!db_host!"=="" set "db_host=localhost"
    if "!db_port!"=="" set "db_port=3306"

    copy /y "%PROJECT_ROOT%\config.env.sample" "%PROJECT_ROOT%\config.env" >nul
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^DJANGO_DB_TYPE=sqlite', 'DJANGO_DB_TYPE=mysql' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# DJANGO_DB_NAME=cimf', 'DJANGO_DB_NAME=%db_name%' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# DJANGO_DB_USER=root', 'DJANGO_DB_USER=%db_user%' | Set-Content '%PROJECT_ROOT%\config.env'"
    if not "!db_pass!"=="" (
        powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# DJANGO_DB_PASSWORD=$', 'DJANGO_DB_PASSWORD=%db_pass%' | Set-Content '%PROJECT_ROOT%\config.env'"
    )
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# DJANGO_DB_HOST=localhost', 'DJANGO_DB_HOST=%db_host%' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# DJANGO_DB_PORT=3306', 'DJANGO_DB_PORT=%db_port%' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_TYPE=mysql)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_NAME=)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_USER=)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_PASSWORD=)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_HOST=)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    powershell -Command "(Get-Content '%PROJECT_ROOT%\config.env') -replace '^# (DJANGO_DB_PORT=)', '$1' | Set-Content '%PROJECT_ROOT%\config.env'"
    echo %GREEN%已创建 config.env（MySQL）%NC%
) else (
    if "!db_choice!"=="1" (
        copy /y "%PROJECT_ROOT%\config.env.sample" "%PROJECT_ROOT%\config.env" >nul
        echo %GREEN%已创建 config.env（SQLite）%NC%
    ) else (
        copy /y "%PROJECT_ROOT%\config.env.sample" "%PROJECT_ROOT%\config.env" >nul
        echo %YELLOW%使用默认配置（SQLite）%NC%
    )
)
goto :eof

REM === 生成随机 SECRET_KEY ===
:generate_secret_key
echo.
echo %GREEN%^>^>^> 生成随机 SECRET_KEY%NC%
echo.
for /f "delims=" %%a in ('python -c "import secrets; print(secrets.token_urlsafe(50))"') do set "new_key=%%a"
if exist "%PROJECT_ROOT%\config.env" (
    powershell -Command "$c = Get-Content '%PROJECT_ROOT%\config.env'; if ($c -match '^SECRET_KEY=') { $c -replace '^SECRET_KEY=.*', 'SECRET_KEY=%new_key%' } else { $c + 'SECRET_KEY=%new_key%' } | Set-Content '%PROJECT_ROOT%\config.env'"
    echo %GREEN%SECRET_KEY 已更新到 config.env%NC%
) else (
    echo %YELLOW%请先创建 config.env 文件%NC%
)
goto :eof

REM === 显示帮助 ===
:show_help
echo.
echo 用法：
echo   run.bat               进入交互菜单
echo   run.bat 1             启动开发服务器
echo   run.bat 2             安装/初始化
echo   run.bat 3             维护
echo   run.bat 4             杀死服务器进程
echo   run.bat 0 / --help    显示帮助
echo.
echo 环境变量：
echo   DJANGO_PORT           服务器端口（默认: 8000）
echo.
goto :eof

REM === 下载/更新省市区数据 ===
:update_china_regions
echo.
echo %GREEN%^>^>^> 下载/更新省市区数据%NC%
echo.
for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"
echo %BLUE%[1/2]%NC% 从网络下载最新省市区数据...
%VENV_PYTHON% -c "from core.services.china_region_service import ChinaRegionService; r = ChinaRegionService.download_to_file(); print('  ' + ('[OK]' if r['success'] else '[FAIL]') + ' ' + r.get('message', r.get('error', '')))"
if !errorlevel! neq 0 (
    echo %RED%下载失败%NC%
    goto :eof
)
echo %BLUE%[2/2]%NC% 更新数据库...
%VENV_PYTHON% -c "from core.services.china_region_service import ChinaRegionService; r = ChinaRegionService.import_from_file(); print('  ' + ('[OK]' if r['success'] else '[FAIL]'))"
echo %GREEN%省市区数据更新完成！%NC%
goto :eof

REM === Ruff 代码检查 ===
:run_ruff_check
for /f "delims=" %%a in ('call :get_venv_python') do set "VENV_PYTHON=%%a"
%VENV_PYTHON% -m ruff --version >nul 2>&1
if !errorlevel! neq 0 (
    echo %YELLOW%Ruff 未安装，正在安装...%NC%
    "%VENV_DIR%\Scripts\python.exe" -m pip install ruff -q
)
if not exist "%PROJECT_ROOT%\storage\reports" mkdir "%PROJECT_ROOT%\storage\reports"

set "timestamp=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "timestamp=%timestamp: =0%"
set "report_file=%PROJECT_ROOT%\storage\reports\riff_%timestamp%.txt"

echo %CYAN%正在扫描代码...%NC%
%VENV_PYTHON% -m ruff check core/ modules/ cimf_django/ --output-format=concise > "%report_file%" 2>&1
type "%report_file%"
findstr "^Found" "%report_file%" >nul 2>&1
if !errorlevel! equ 0 (
    echo %YELLOW%检测完成（发现代码问题）%NC%
) else (
    echo %GREEN%[OK] 未发现问题%NC%
)
echo %CYAN%报告已保存: %report_file%%NC%
goto :eof

REM ============ 菜单函数 ============

REM === 显示主菜单 ===
:show_menu
cls
echo %CYAN%  ______     __     __    __     ______%NC%
echo %CYAN% /\  ___\   /\ \   /\  -./  \   /\  ___\%NC%
echo %CYAN% \ \ \____  \ \ \  \ \-./\  \  \ \  __\%NC%
echo %CYAN%  \ \_____\  \ \_\  \ \_\ \_\  \ \_\%NC%
echo %CYAN%   \/_____/   \/_/   \/_/  \/_/   \/_/%NC%
echo.
echo %CYAN%================================%NC%
echo %WHITE%  CIMF 管理系统 - 管理菜单%NC%
echo %CYAN%================================%NC%
echo.
echo   1 → 启动服务器
echo   2 → 安装/初始化
echo   3 → 维护
echo   0 → 退出
echo.
echo   h → 显示帮助
echo.
goto :eof

REM === 安装/初始化子菜单 ===
:show_init_menu
cls
echo %CYAN%================================%NC%
echo %WHITE%   安装/初始化%NC%
echo %CYAN%================================%NC%
echo.
echo   1 → 创建 config.env 文件
echo   2 → 创建虚拟环境并安装依赖
echo   3 → 初始化系统（重建数据库+创建管理员）
echo   4 → 生成随机 SECRET_KEY
echo   0 → 返回主菜单
echo.
goto :eof

:run_init_menu
:init_menu_loop
call :show_init_menu
set /p "raw_input=请输入选项 (0/1/2/3/4): "
set "choice=%raw_input:~0,1%"
if "%choice%"=="0" goto :eof
if "%choice%"=="1" echo. && call :create_env_file
if "%choice%"=="2" echo. && call :install_venv
if "%choice%"=="3" echo. && call :init_system
if "%choice%"=="4" echo. && call :generate_secret_key
echo.
pause
goto init_menu_loop

REM === 维护子菜单 ===
:show_maint_menu
cls
echo %CYAN%================================%NC%
echo %WHITE%   维护%NC%
echo %CYAN%================================%NC%
echo.
echo   1 → 数据库备份
echo   2 → 清理缓存
echo   3 → 查看环境变量
echo   4 → 杀死服务器进程
echo   5 → 下载/更新省市区数据
echo   6 → Ruff 代码检查
echo   0 → 返回主菜单
echo.
goto :eof

:run_maint_menu
:maint_menu_loop
call :show_maint_menu
set /p "raw_input=请输入选项 (0/1/2/3/4/5/6): "
set "choice=%raw_input:~0,1%"
if "%choice%"=="0" goto :eof
if "%choice%"=="1" echo. && call :backup_database
if "%choice%"=="2" echo. && call :clean_cache
if "%choice%"=="3" echo. && call :show_env_vars
if "%choice%"=="4" echo. && call :kill_server
if "%choice%"=="5" echo. && call :update_china_regions
if "%choice%"=="6" echo. && call :run_ruff_check
echo.
pause
goto maint_menu_loop

REM ============ 主逻辑 ============

:main
if "%~1" neq "" (
    if "%~1"=="1" call :activate_venv && call :run_server && exit /b 0
    if "%~1"=="2" call :run_init_menu && exit /b 0
    if "%~1"=="3" call :run_maint_menu && exit /b 0
    if "%~1"=="4" call :kill_server && exit /b 0
    if "%~1"=="0" call :show_help && exit /b 0
    if "%~1"=="/?" call :show_help && exit /b 0
    if "%~1"=="-h" call :show_help && exit /b 0
    if "%~1"=="--help" call :show_help && exit /b 0
    echo %RED%未知选项: %~1%NC%
    call :show_help
    exit /b 1
)

if exist "%VENV_DIR%\Scripts\activate.bat" call "%VENV_DIR%\Scripts\activate.bat"

:menu_loop
call :show_menu
set /p "raw_input=请输入选项 (0/1/2/3/h): "
set "choice=%raw_input:~0,1%"

if /i "%choice%"=="0" goto exit_app
if /i "%choice%"=="1" echo. && call :run_server && goto menu_end
if /i "%choice%"=="2" call :run_init_menu && goto menu_loop
if /i "%choice%"=="3" call :run_maint_menu && goto menu_loop
if /i "%choice%"=="h" call :show_help && goto menu_end
echo %YELLOW%无效选项 '%choice%'%NC%
:menu_end
echo.
pause
goto menu_loop

:exit_app
echo.
echo %GREEN%感谢使用，再见！%NC%
exit /b 0

call :main %*
