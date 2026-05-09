#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# CIMF 管理系统 - 启动/维护脚本
#
# 用法：
#   ./run.sh                进入交互菜单
#   ./run.sh 1              启动开发服务器
#   ./run.sh 2              安装/初始化子菜单
#   ./run.sh 3              维护子菜单
#   ./run.sh 0 / --help     显示帮助
#

set -euo pipefail

# Python 命令兼容性处理
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}错误：未找到 python 或 python3 命令${NC}"
    exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# 打字机效果函数
# $1: 颜色变量 (如 $BLUE)
# $2: 文本内容
# $3: 每字符延迟 (默认 0.02)
typewrite() {
    local color="$1"
    local text="$2"
    local delay="${3:-0.02}"
    
    for ((i=0; i<${#text}; i++)); do
        echo -n -e "${color}${text:$i:1}${NC}"
        sleep $delay
    done
    echo
}

clear

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || { echo -e "${RED}无法进入项目目录${NC}"; exit 1; }

# 加载环境变量
if [[ -f "$PROJECT_ROOT/config.env" ]]; then
    source "$PROJECT_ROOT/config.env"
fi

VENV_DIR="venv"
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
APP_PORT=${DJANGO_PORT:-8000}
DB_PATH="instance/django.db"
BACKUP_DIR="storage/backups"

# 优先使用项目内 venv
if [[ -d "$PROJECT_ROOT/venv" ]]; then
    VENV_DIR="$PROJECT_ROOT/venv"
fi

# 安装虚拟环境
install_venv() {
    echo -e "${BLUE}[准备]${NC} 创建虚拟环境..."
    
    if [[ -d "$PROJECT_ROOT/venv" ]]; then
        echo -e "${YELLOW}虚拟环境已存在${NC}"
        read -p "是否重新创建？(y/N) " answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_ROOT/venv"
        else
            echo "取消创建"
            return 0
        fi
    fi
    
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv "$PROJECT_ROOT/venv"
    
    echo "安装依赖..."
    local venv_pip
    venv_pip="$PROJECT_ROOT/venv/bin/pip"
    $venv_pip install --upgrade pip -i "$PIP_INDEX" -q
    
    # 读取 requirements.txt 获取包列表
    local requirements_file="$PROJECT_ROOT/requirements.txt"
    if [[ -f "$requirements_file" ]]; then
        # 过滤空行和注释，获取有效包名
        local packages=()
        while IFS= read -r line; do
            # 跳过空行和注释
            [[ -z "$line" || "$line" == \#* ]] && continue
            # 提取包名（忽略版本号）
            pkg=$(echo "$line" | sed 's/[>=<!\[].*//; s/#.*//')
            packages+=("$pkg")
        done < "$requirements_file"
        
        local total=${#packages[@]}
        local current=0
        
        echo "共 $total 个依赖包"
        echo
        
        for pkg in "${packages[@]}"; do
            current=$((current + 1))
            printf "  [%d/%d] %-30s" "$current" "$total" "$pkg"
            if $venv_pip install "$pkg" -i "$PIP_INDEX" -q 2>/dev/null; then
                echo -e " ${GREEN}✓${NC}"
            else
                echo -e " ${RED}✗${NC}"
            fi
        done
    else
        echo -e "${YELLOW}未找到 requirements.txt${NC}"
    fi
    
    echo -e "${GREEN}虚拟环境创建完成${NC}"
}

show_help() {
    echo "用法："
    echo "  ./run.sh                进入交互菜单"
    echo "  ./run.sh 1              启动开发服务器"
    echo "  ./run.sh 2              安装/初始化"
    echo "  ./run.sh 3              维护"
    echo "  ./run.sh 4              杀死服务器进程"
    echo "  ./run.sh 0 / --help     显示帮助"
    echo
    echo "环境变量："
    echo "  DJANGO_PORT             服务器端口 (默认: 8000)"
    echo
    exit 0
}

# 激活虚拟环境
activate_venv() {
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        source "$VENV_DIR/bin/activate"
    fi
}

# 获取 venv 中的 Python
get_venv_python() {
    if [[ -f "$VENV_DIR/bin/python" ]]; then
        echo "$VENV_DIR/bin/python"
    elif [[ -f "$VENV_DIR/bin/python3" ]]; then
        echo "$VENV_DIR/bin/python3"
    else
        echo "$PYTHON_CMD"
    fi
}

# pip 命令兼容性处理
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${YELLOW}警告：未找到 pip 命令${NC}"
    PIP_CMD=""
fi

# 启动开发服务器
run_server() {
    echo -e "\n${GREEN}>>> 启动 CIMF 管理系统 (开发模式)${NC}\n"
    
    mkdir -p storage/uploads storage/backups instance
    
    echo "  监听地址 : http://0.0.0.0:${APP_PORT}"
    echo "  本地访问 : http://127.0.0.1:${APP_PORT}"
    echo "  后台管理 : http://127.0.0.1:${APP_PORT}/admin/"
    echo "  按 Ctrl+C 停止服务"
    echo
    
    export DJANGO_SETTINGS_MODULE=cimf_django.settings
    
    local venv_python
    venv_python=$(get_venv_python)
    $venv_python run.py
}

# 初始化系统（重建数据库+创建管理员）
init_system() {
    echo -e "\n${GREEN}>>> 初始化系统${NC}\n"
    
    activate_venv
    
    # 备份现有数据库
    if [[ -f "$DB_PATH" ]]; then
        echo -e "${YELLOW}检测到已存在数据库文件${NC}"
        read -p "是否备份现有数据库？(Y/n) " answer
        if [[ "$answer" =~ ^[Nn]$ ]]; then
            echo "跳过备份..."
        else
            backup_database
        fi
    fi
    
    # 执行初始化（init_db.py 统一管理 migrations）
    local venv_python
    venv_python=$(get_venv_python)
    
    echo -e "${BLUE}[1/2]${NC} 初始化数据（migrations + 初始数据）..."
    $venv_python init_db.py --with-data --force
    
    echo -e "${GREEN}初始化完成！${NC}"
}

# 初始化海外客户样本数据
init_overseas_customers() {
    echo -e "\n${GREEN}>>> 初始化海外客户样本数据${NC}\n"
    
    activate_venv
    
    local venv_python
    venv_python=$(get_venv_python)
    
    $venv_python manage.py init_overseas_customers
    
    echo -e "${GREEN}海外客户样本数据初始化完成！${NC}"
}

# 初始化国内客户样本数据
init_domestic_customers() {
    echo -e "\n${GREEN}>>> 初始化国内客户样本数据${NC}\n"
    
    activate_venv
    
    local venv_python
    venv_python=$(get_venv_python)
    
    $venv_python manage.py init_domestic_customers
    
    echo -e "${GREEN}国内客户样本数据初始化完成！${NC}"
}

# 数据库备份
backup_database() {
    echo -e "\n${GREEN}>>> 数据库备份${NC}\n"
    
    mkdir -p "$BACKUP_DIR"
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    if [[ -f "$DB_PATH" ]]; then
        backup_file="${BACKUP_DIR}/django_${timestamp}.db"
        cp "$DB_PATH" "$backup_file"
        echo -e "${GREEN}数据库已备份到: $backup_file${NC}"
    else
        echo -e "${YELLOW}数据库文件不存在，跳过备份${NC}"
    fi
}

# 清理缓存
clean_cache() {
    echo -e "\n${GREEN}>>> 清理缓存${NC}\n"
    
    echo "删除 __pycache__、.pyc..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    rm -rf .pytest_cache .coverage .mypy_cache .ruff_cache 2>/dev/null || true
    rm -rf storage/staticfiles/.cache 2>/dev/null || true
    
    echo -e "${GREEN}缓存清理完成${NC}"
}

# 杀死服务器进程
kill_server() {
    echo -e "\n${GREEN}>>> 杀死服务器进程 (端口: ${APP_PORT})${NC}\n"
    
    local pids
    pids=$(lsof -ti:${APP_PORT} 2>/dev/null || true)
    
    if [[ -z "$pids" ]]; then
        echo -e "${YELLOW}端口 ${APP_PORT} 上没有运行的进程${NC}"
        return 0
    fi
    
    echo "找到进程 PID: $pids"
    echo "正在杀死进程..."
    
    for pid in $pids; do
        if kill -9 "$pid" 2>/dev/null; then
            echo -e "${GREEN}进程已杀死 (PID: $pid)${NC}"
        else
            echo -e "${RED}杀死进程失败 (PID: $pid)${NC}"
        fi
    done
}

# 查看当前环境变量
show_env_vars() {
    echo -e "\n${GREEN}>>> 查看环境变量${NC}\n"
    echo "  DJANGO_ENV=${DJANGO_ENV:-未设置}"
    echo "  DJANGO_DEBUG=${DJANGO_DEBUG:-未设置}"
    echo "  DJANGO_HOST=${DJANGO_HOST:-未设置}"
    echo "  DJANGO_PORT=${DJANGO_PORT:-未设置}"
    echo "  SECRET_KEY=${SECRET_KEY:+已设置}"
    echo
}

# 创建 config.env 文件
create_env_file() {
    echo -e "\n${GREEN}>>> 创建 config.env 文件${NC}\n"
    
    if [[ -f "config.env" ]]; then
        echo -e "${YELLOW}config.env 已存在${NC}"
        read -p "是否覆盖？(y/N) " answer
        if [[ ! "$answer" =~ ^[Yy]$ ]]; then
            echo "取消创建"
            return 0
        fi
    fi
    
    if [[ -f "config.env.sample" ]]; then
        # 选择数据库类型
        echo "请选择数据库类型："
        echo "  1 → SQLite（默认，适合开发和测试）"
        echo "  2 → MySQL（适合生产环境）"
        read -p "请输入选项 (1/2): " db_choice
        
        case "$db_choice" in
            1)
                # SQLite 配置
                sed 's/^# DB_TYPE=mysql/DB_TYPE=sqlite/' config.env.sample > config.env
                echo -e "${GREEN}已创建 config.env（SQLite）${NC}"
                ;;
            2)
                # MySQL 配置
                echo "请输入 MySQL 配置："
                read -p "  数据库名 [cimf]: " db_name
                read -p "  用户名 [root]: " db_user
                read -s -p "  密码: " db_pass; echo
                read -p "  主机 [localhost]: " db_host
                read -p "  端口 [3306]: " db_port
                
                # 生成配置
                cp config.env.sample config.env
                sed -i 's/^DB_TYPE=sqlite/DB_TYPE=mysql/' config.env
                sed -i "s/^# DB_NAME=cimf/DB_NAME=${db_name:-cimf}/" config.env
                sed -i "s/^# DB_USER=root/DB_USER=${db_user:-root}/" config.env
                sed -i "s/^# DB_PASSWORD=$/DB_PASSWORD=${db_pass}/" config.env
                sed -i "s/^# DB_HOST=localhost/DB_HOST=${db_host:-localhost}/" config.env
                sed -i "s/^# DB_PORT=3306/DB_PORT=${db_port:-3306}/" config.env
                
                # 取消注释 MySQL 配置行
                sed -i 's/^# \(DB_TYPE=mysql\)/\1/' config.env
                sed -i 's/^# \(DB_NAME=\)/\1/' config.env
                sed -i 's/^# \(DB_USER=\)/\1/' config.env
                sed -i 's/^# \(DB_PASSWORD=\)/\1/' config.env
                sed -i 's/^# \(DB_HOST=\)/\1/' config.env
                sed -i 's/^# \(DB_PORT=\)/\1/' config.env
                
                echo -e "${GREEN}已创建 config.env（MySQL）${NC}"
                ;;
            *)
                cp config.env.sample config.env
                echo -e "${YELLOW}使用默认配置（SQLite）${NC}"
                ;;
        esac
    else
        echo -e "${RED}config.env.sample 不存在${NC}"
    fi
}

# 生成随机 SECRET_KEY
generate_secret_key() {
    echo -e "\n${GREEN}>>> 生成随机 SECRET_KEY${NC}\n"
    
    local new_key
    new_key=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    
    if [[ -f "config.env" ]]; then
        if grep -q "^SECRET_KEY=" config.env; then
            sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$new_key|" config.env
        else
            echo "SECRET_KEY=$new_key" >> config.env
        fi
        echo -e "${GREEN}SECRET_KEY 已更新到 config.env${NC}"
    else
        echo -e "${YELLOW}请先创建 config.env 文件${NC}"
    fi
}

# 下载/更新省市区数据
update_china_regions() {
    echo -e "\n${GREEN}>>> 下载/更新省市区数据${NC}\n"
    
    activate_venv
    
    local venv_python
    venv_python=$(get_venv_python)
    
    echo -e "${BLUE}[1/2]${NC} 从网络下载最新省市区数据..."
    $venv_python -c "
from core.services.china_region_service import ChinaRegionService
result = ChinaRegionService.download_to_file()
if result['success']:
    print(f\"  ✓ {result['message']}\")
    print(f\"  文件路径: {result['file_path']}\")
else:
    print(f\"  ✗ 下载失败: {result['error']}\")
"
    
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}下载失败${NC}"
        return 1
    fi
    
    echo -e "${BLUE}[2/2]${NC} 更新数据库..."
    $venv_python -c "
from core.services.china_region_service import ChinaRegionService
result = ChinaRegionService.import_from_file()
if result['success']:
    print(f\"  ✓ 数据库更新成功\")
    print(f\"  统计: {result['provinces']} 省, {result['cities']} 市, {result['districts']} 县\")
else:
    print(f\"  ✗ 更新失败: {result['error']}\")
"
    
    echo -e "${GREEN}省市区数据更新完成！${NC}"
}

# 初始化子菜单
show_init_menu() {
    clear
    typewrite "$CYAN" "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀" 0.01
    typewrite "$WHITE" "安装/初始化" 0.01
    typewrite "$CYAN" "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄" 0.01
    echo
    echo "  1 → 创建虚拟环境并安装依赖"
    echo "  2 → 初始化系统（重建数据库+创建管理员）"
    echo "  3 → 创建 config.env 文件"
    echo "  4 → 生成随机 SECRET_KEY"
    echo "  0 → 返回主菜单"
    echo
}

run_init_menu() {
    while true; do
        show_init_menu
        read -p "请输入选项 (0/1/2/3/4): " raw_input
        
        choice=$(echo "$raw_input" | sed 's/[^0-9]//g' | head -c 1)
        
        case "$choice" in
            0) break ;;
            1) echo "→ 创建虚拟环境"; install_venv ;;
            2) echo "→ 初始化系统"; init_system ;;
            3) echo "→ 创建 .env 文件"; create_env_file ;;
            4) echo "→ 生成 SECRET_KEY"; generate_secret_key ;;
            *) echo -e "${YELLOW}无效选项 '$choice'${NC}" ;;
        esac
        
        echo
        echo "按回车键返回菜单..."
        read -s -r
    done
}

# 维护子菜单
show_maint_menu() {
    clear
    typewrite "$CYAN" "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀" 0.01
    typewrite "$WHITE" "维护" 0.01
    typewrite "$CYAN" "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄" 0.01
    echo
    echo "  1 → 数据库备份"
    echo "  2 → 清理缓存"
    echo "  3 → 查看环境变量"
    echo "  4 → 杀死服务器进程"
    echo "  5 → 下载/更新省市区数据（从网络更新本地文件）"
    echo "  0 → 返回主菜单"
    echo
}

run_maint_menu() {
    while true; do
        show_maint_menu
        read -p "请输入选项 (0/1/2/3/4/5): " raw_input
        
        choice=$(echo "$raw_input" | sed 's/[^0-9]//g' | head -c 1)
        
        case "$choice" in
            0) break ;;
            1) echo "→ 数据库备份"; backup_database ;;
            2) echo "→ 清理缓存"; clean_cache ;;
            3) echo "→ 查看环境变量"; show_env_vars ;;
            4) echo "→ 杀死服务器进程"; kill_server ;;
            5) echo "→ 更新省市区数据"; update_china_regions ;;
            *) echo -e "${YELLOW}无效选项 '$choice'${NC}" ;;
        esac
        
        echo
        echo "按回车键返回菜单..."
        read -s -r
    done
}

# 显示主菜单
show_menu() {
    clear
    echo -e "${CYAN}  ______     __     __    __     ______  ${NC}"
    echo -e "${CYAN} /\  ___\   /\ \   /\  -./  \   /\  ___\ ${NC}"
    echo -e "${CYAN} \ \ \____  \ \ \  \ \-./\  \  \ \  __\ ${NC}"
    echo -e "${CYAN}  \ \_____\  \ \_\  \ \_\ \_\  \ \_\   ${NC}"
    echo -e "${CYAN}   \/_____/   \/_/   \/_/  \/_/   \/_/   ${NC}"
    echo
    typewrite "$CYAN" "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀" 0.01
    typewrite "$WHITE" "CIMF 管理系统 - 管理菜单" 0.01
    typewrite "$CYAN" "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄" 0.01
    echo
    echo "  1 → 启动服务器"
    echo "  2 → 安装/初始化"
    echo "  3 → 维护"
    echo "  0 → 退出"
    echo
    echo "  h → 显示帮助"
    echo
}

# 主逻辑
if [[ $# -ge 1 ]]; then
    case "$1" in
        1) activate_venv; run_server ;;
        2) run_init_menu ;;
        3) run_maint_menu ;;
        4) kill_server ;;
        0|-h|--help) show_help ;;
        *) echo -e "${RED}未知选项: $1${NC}"; show_help ;;
    esac
    exit 0
fi

# 激活虚拟环境
if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
fi

# 进入交互菜单
while true; do
    show_menu
    
    read -p "请输入选项 (0/1/2/3/h): " raw_input
    
    choice=$(echo "$raw_input" | sed 's/[^0-9hH]//g' | head -c 1 | tr '[:upper:]' '[:lower:]')
    
    case "$choice" in
        0) echo -e "${GREEN}感谢使用，再见！${NC}"; exit 0 ;;
        1) echo "→ 启动系统"; run_server; break ;;
        2) echo "→ 安装/初始化"; run_init_menu ;;
        3) echo "→ 维护"; run_maint_menu ;;
        h) show_help ;;
        *) echo -e "${YELLOW}无效选项 '$choice'${NC}" ;;
    esac
    
    echo
    echo "按回车键返回菜单..."
    read -s -r
done
