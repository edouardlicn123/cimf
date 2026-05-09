@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: CIMF 管理系统 - Windows 启动/维护脚本
::
:: 用法：
::   run.bat              进入交互菜单
::   run.bat 1            启动开发服务器
::   run.bat 2            安装/初始化子菜单
::   run.bat 3            维护子菜单
::   run.bat 0 / --help   显示帮助

:: 颜色定义
set RED=[0;31m
set GREEN=[0;32m
set YELLOW=[1;33m
set BLUE=[0;34m
set CYAN=[0;36m
set WHITE=[1;37m
set NC=[0m

:: 项目根目录
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%" || exit /b 1

:: 加载环境变量
if exist "%PROJECT_ROOT%config.env" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%PROJECT_ROOT%config.env") do (
        set %%a=%%b
    )
)

set VENV_DIR=venv
set APP_PORT=8000
if defined DJANGO_PORT set APP_PORT=%DJANGO_PORT%
set DB_PATH=instance\django.db
set BACKUP_DIR=storage\backups

:: 设置 pip 镜像
set PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple

:: ============ 辅助函数 ============

:color_echo
echo %*
goto :eof

:show_help
echo 用法：
echo   run.bat              进入交互菜单
echo   run.bat 1            启动开发服务器
echo   run.bat 2            安装/初始化
echo   run.bat 3            维护
echo   run.bat 4            杀死服务器进程
echo   run.bat 0 / --help   显示帮助
echo.
echo 环境变量：
echo   DJANGO_PORT         服务器端口 ^(默认: 8000^)
exit /b 0

:: 获取 venv 中的 Python
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

:: 激活虚拟环境
:activate_venv
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call %VENV_DIR%\Scripts\activate.bat
)
goto :eof

:: ============ 主功能函数 ============

:: 启动开发服务器
:run_server
echo.
echo [1;32m>>> 启动 CIMF 管理系统 ^(开发模式^)[0m
echo.

if not exist "storage\uploads" mkdir storage\uploads
if not exist "storage\backups" mkdir storage\backups
if not exist "instance" mkdir instance

echo   监听地址 : http://0.0.0.0:%APP_PORT%
echo   本地访问 : http://127.0.0.1:%APP_PORT%
echo   后台管理 : http://127.0.0.1:%APP_PORT%/admin/
echo   按 Ctrl+C 停止服务
echo.

set DJANGO_SETTINGS_MODULE=cimf_django.settings

call :get_venv_python
set VENV_PYTHON=!result!
!VENV_PYTHON! run.py
goto :eof

:: 安装虚拟环境
:install_venv
echo.
echo [1;34m[准备][0m 创建虚拟环境...

if exist "%VENV_DIR%" (
    echo [1;33m虚拟环境已存在[0m
    set /p answer="是否重新创建？ (y/N): "
    if /i "!answer!"=="y" (
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo 取消创建
        exit /b 0
    )
)

echo 创建虚拟环境...
python -m venv "%VENV_DIR%"

echo 安装依赖...
call %VENV_DIR%\Scripts\pip install --upgrade pip -i %PIP_INDEX% -q

if exist "requirements.txt" (
    echo 共 N 个依赖包
    echo.
    call %VENV_DIR%\Scripts\pip install -r requirements.txt -i %PIP_INDEX% -q
    echo [1;32m虚拟环境创建完成[0m
) else (
    echo [1;33m未找到 requirements.txt[0m
)
goto :eof

:: 初始化系统
:init_system
echo.
echo [1;32m>>> 初始化系统[0m
echo.

call :activate_venv

call :get_venv_python
set VENV_PYTHON=!result!

if exist "%DB_PATH%" (
    echo [1;33m检测到已存在数据库文件[0m
    set /p answer="是否备份现有数据库？ (Y/n): "
    if /i not "!answer!"=="n" (
        call :backup_database
    )
)

echo [1;34m[1/2][0m 初始化数据（migrations + 初始数据）...
!VENV_PYTHON! init_db.py --with-data --force

echo [1;32m初始化完成！[0m
goto :eof

:: 数据库备份
:backup_database
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATESTAMP=%%a_%%b_%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set DATESTAMP=!DATESTAMP:~0,8!_%%a%%b
set DATESTAMP=!DATESTAMP:~2,13!

if exist "%DB_PATH%" (
    set BACKUP_FILE=%BACKUP_DIR%\django_!DATESTAMP!.db
    copy /y "%DB_PATH%" "!BACKUP_FILE!" >nul
    echo [1;32m数据库已备份到: !BACKUP_FILE![0m
) else (
    echo [1;33m数据库文件不存在，跳过备份[0m
)
goto :eof

:: 清理缓存
:clean_cache
echo.
echo [1;32m>>> 清理缓存[0m
echo.

echo 删除 __pycache__、*.pyc...
for /d /r . %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .coverage del /q .coverage
if exist .mypy_cache rmdir /s /q .mypy_cache
if exist storage\staticfiles\.cache rmdir /s /q storage\staticfiles\.cache

echo [1;32m缓存清理完成[0m
goto :eof

:: 杀死服务器进程
:kill_server
echo.
echo [1;32m>>> 杀死服务器进程 ^(端口: %APP_PORT%^)[0m
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":!APP_PORT!" ^| findstr "LISTENING"') do set PID=%%a

if not defined PID (
    echo [1;33m端口 %APP_PORT% 上没有运行的进程[0m
    exit /b 0
)

echo 找到进程 PID: !PID!
echo 正在杀死进程...
taskkill /F /PID !PID! >nul 2>&1
if !errorlevel! equ 0 (
    echo [1;32m进程已杀死 ^(PID: !PID!^)[0m
) else (
    echo [1;31m杀死进程失败 ^(PID: !PID!^)[0m
)
goto :eof

:: 显示环境变量
:show_env_vars
echo.
echo [1;32m>>> 查看环境变量[0m
echo   DJANGO_ENV=!DJANGO_ENV!
echo   DJANGO_DEBUG=!DJANGO_DEBUG!
echo   DJANGO_HOST=!DJANGO_HOST!
echo   DJANGO_PORT=!DJANGO_PORT!
if defined SECRET_KEY (
    echo   SECRET_KEY=已设置
) else (
    echo   SECRET_KEY=未设置
)
goto :eof

:: 创建 config.env 文件
:create_env_file
echo.
echo [1;32m>>> 创建 config.env 文件[0m
echo.

if exist "config.env" (
    echo [1;33mconfig.env 已存在[0m
    set /p answer="是否覆盖？ (y/N): "
    if /i not "!answer!"=="y" (
        echo 取消创建
        exit /b 0
    )
)

if not exist "config.env.sample" (
    echo [1;31mconfig.env.sample 不存在[0m
    exit /b 1
)

echo 请选择数据库类型：
echo   1 ^> SQLite（默认，适合开发和测试）
echo   2 ^> MySQL（适合生产环境）
set /p db_choice="请输入选项 (1/2): "

if "!db_choice!"=="2" (
    echo 请输入 MySQL 配置：
    set /p db_name="  数据库名 [cimf]: "
    set /p db_user="  用户名 [root]: "
    set /p db_pass="  密码: "
    set /p db_host="  主机 [localhost]: "
    set /p db_port="  端口 [3306]: "

    copy config.env.sample config.env
    findstr /v "^#" config.env > config.env.tmp
    move /y config.env.tmp config.env
    echo.>>config.env
    echo DB_TYPE=mysql>>config.env
    echo DB_NAME=!db_name!:>>config.env
    echo DB_USER=!db_user!:>>config.env
    echo DB_PASSWORD=!db_pass!:>>config.env
    echo DB_HOST=!db_host!:>>config.env
    echo DB_PORT=!db_port!:>>config.env

    echo [1;32m已创建 config.env（MySQL）[0m
) else (
    copy config.env.sample config.env
    echo [1;32m已创建 config.env（SQLite）[0m
)
goto :eof

:: ============ 菜单函数 ============

:: 显示主菜单
:show_menu
cls
echo.
echo   ______     __     __    __     ______
echo  /\  ___\   /\ \   /\  -./  \   /\  ___\
echo  \ \ \____  \ \ \  \ \-./\  \  \ \  __\
echo   \_____\  \ \_\  \ \_\ \_\  \ \_\ 
echo    \/_____/   \/_/   \/_/  \/_/   \/_/
echo.
echo ========================================
echo   CIMF 管理系统 - 管理菜单
echo ========================================
echo.
echo   1 ^> 启动服务器
echo   2 ^> 安装/初始化
echo   3 ^> 维护
echo   4 ^> 杀死服务器进程
echo   0 ^> 退出
echo.
echo   h ^> 显示帮助
echo.
goto :eof

:: 安装/初始化子菜单
:show_init_menu
cls
echo ========================================
echo   安装/初始化
echo ========================================
echo   1 ^> 创建虚拟环境并安装依赖
echo   2 ^> 初始化系统（重建数据库+创建管理员）
echo   3 ^> 创建 config.env 文件
echo   0 ^> 返回主菜单
echo.
goto :eof

:: 维护子菜单
:show_maint_menu
cls
echo ========================================
echo   维护
echo ========================================
echo   1 ^> 数据库备份
echo   2 ^> 清理缓存
echo   3 ^> 查看环境变量
echo   4 ^> 杀死服务器进程
echo   0 ^> 返回主菜单
echo.
goto :eof

:: ============ 主逻辑 ============

:main
if "%~1" neq "" (
    if "%~1"=="1" call :activate_venv ^& call :run_server ^& exit /b 0
    if "%~1"=="2" call :run_init_menu ^& exit /b 0
    if "%~1"=="3" call :run_maint_menu ^& exit /b 0
    if "%~1"=="4" call :kill_server ^& exit /b 0
    if "%~1"=="0" call :show_help ^& exit /b 0
    if "%~1"=="-h" call :show_help ^& exit /b 0
    if "%~1"=="--help" call :show_help ^& exit /b 0
    echo 未知选项: %~1
    call :show_help
    exit /b 1
)

:: 激活虚拟环境
if exist "%VENV_DIR%\Scripts\activate.bat" call %VENV_DIR%\Scripts\activate.bat

:: 交互菜单
:menu_loop
call :show_menu
set /p choice="请输入选项 (0/1/2/3/4/h): "

if /i "!choice!"=="0" goto exit_app
if /i "!choice!"=="1" echo ^> 启动系统 ^& call :run_server ^& goto menu_end
if /i "!choice!"=="2" call :run_init_menu ^& goto menu_loop
if /i "!choice!"=="3" call :run_maint_menu ^& goto menu_loop
if /i "!choice!"=="4" call :kill_server ^& goto menu_end
if /i "!choice!"=="h" call :show_help ^& goto menu_end
if /i "!choice!"=="x" goto exit_app

echo 无效选项: !choice!
:menu_end
echo.
pause
goto :menu_loop

:run_init_menu
call :show_init_menu
set /p choice="请输入选项 (0/1/2/3): "

if "!choice!"=="0" goto :eof
if "!choice!"=="1" echo ^> 创建虚拟环境 ^& call :install_venv ^& goto run_init_menu
if "!choice!"=="2" echo ^> 初始化系统 ^& call :init_system ^& goto run_init_menu
if "!choice!"=="3" echo ^> 创建 .env 文件 ^& call :create_env_file ^& goto run_init_menu
echo 无效选项: !choice!
goto run_init_menu

:run_maint_menu
call :show_maint_menu
set /p choice="请输入选项 (0/1/2/3/4): "

if "!choice!"=="0" goto :eof
if "!choice!"=="1" echo ^> 数据库备份 ^& call :backup_database ^& goto run_maint_menu
if "!choice!"=="2" echo ^> 清理缓存 ^& call :clean_cache ^& goto run_maint_menu
if "!choice!"=="3" echo ^> 查看环境变量 ^& call :show_env_vars ^& goto run_maint_menu
if "!choice!"=="4" echo ^> 杀死服务器进程 ^& call :kill_server ^& goto run_maint_menu
echo 无效选项: !choice!
goto run_maint_menu

:exit_app
echo.
echo [1;32m��谢��用，再见！[0m
exit /b 0

:main %*