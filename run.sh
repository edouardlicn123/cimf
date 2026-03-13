#!/usr/bin/env bash

# FFE 项目跟进系统 - Linux / macOS 统一管理脚本 (run.sh)
#
# 更新日期：2026-02-12
# 主要改进：
#   - 选项重新连续编号（1~5 + 0/h）
#   - 原选项 2 和 4 对调：
#     - 2 → 生成 code2ai 审查文件（原 4）
#     - 4 → 初始化数据库（原 2）
#   - 使用 db.create_all() 方式初始化数据库
#   - 移除所有 Migrate 相关代码
#   - 菜单精简，数字无空隙

set -euo pipefail

# ───────────────────────────────────────────────
# 颜色定义（OpenCode 深色终端风格）
# ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BRIGHT_CYAN='\033[1;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

OPCODE_BG='\033[48;5;236m'
OPCODE_ACCENT='\033[38;5;79m'
OPCODE_GREEN='\033[38;5;76m'
OPCODE_CYAN='\033[38;5;73m'

clear

echo -e "${CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀${NC}"
echo -e "  ${WHITE}🔧 内部管理系统 🔧${NC}"
echo -e "    ${WHITE}启动/维护终端${NC}"
echo -e "${CYAN}▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄${NC}"
echo

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || { echo -e "${RED}无法进入项目目录${NC}"; exit 1; }

VENV_DIR="venv"
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
DEFAULT_WAIT=3
APP_PORT=5001
DB_PATH="instance/site.db"

show_help() {
    echo "用法："
    echo "  ./run.sh                进入交互菜单"
    echo "  ./run.sh 1              运行开发服务器"
    echo "  ./run.sh 2              日常维护"
    echo "  ./run.sh 3              系统初始化"
    echo "  ./run.sh 0 / --help     退出 / 显示帮助"
    echo
    exit 0
}

# ───────────────────────────────────────────────
# 准备虚拟环境 + 激活 + 安装依赖
# ───────────────────────────────────────────────
prepare_venv() {
    echo -e "${BLUE}[准备]${NC} 检查并准备虚拟环境..."

    if [[ ! -d "$VENV_DIR" || ! -f "$VENV_DIR/bin/activate" ]]; then
        echo "  创建虚拟环境..."
        python3 -m venv "$VENV_DIR" || {
            echo -e "${RED}创建虚拟环境失败，请检查 python3 是否安装${NC}"
            exit 1
        }
    fi

    echo "  激活虚拟环境..."
    source "$VENV_DIR/bin/activate"

    echo "  升级 pip..."
    pip install --upgrade pip -i "$PIP_INDEX" --no-color --quiet

    if [[ -f "requirements.txt" ]]; then
        echo "  安装/更新依赖..."
        pip install -r requirements.txt -i "$PIP_INDEX" --no-color
    else
        echo -e "${YELLOW}警告：未找到 requirements.txt，跳过依赖安装${NC}"
    fi

    echo -e "${GREEN}虚拟环境准备完成${NC}"
}

# ───────────────────────────────────────────────
# 运行开发服务器
# ───────────────────────────────────────────────
run_app() {
    echo -e "\n${GREEN}>>> 启动 FFE 项目跟进系统 (开发模式)${NC}\n"

    mkdir -p instance persistent_uploads

    echo "  监听地址 : http://0.0.0.0:${APP_PORT}"
    echo "  本地访问 : http://127.0.0.1:${APP_PORT}"
    echo "  按 Ctrl+C 停止服务"
    echo "  数据库：由 db.create_all() 自动管理"
    echo

    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export FLASK_APP=run.py

    exec flask run --host=0.0.0.0 --port "${APP_PORT}"
}

# ───────────────────────────────────────────────
# 生成 code2ai 源码审查文件（原选项 4 → 新选项 2）
# ───────────────────────────────────────────────
run_code2ai() {
    echo -e "\n${GREEN}>>> 生成代码审查文件 (code2ai)${NC}\n"

    if [[ -f "app/utils/code2ai.py" && -f "code2ai_config.toml" ]]; then
        python app/utils/code2ai.py
        echo -e "${GREEN}源码汇总文件已生成${NC}"
    else
        echo -e "${RED}缺少必要的文件：app/utils/code2ai.py 和 code2ai_config.toml${NC}"
    fi
}

# ───────────────────────────────────────────────
# 初始化数据库（原选项 2 → 新选项 4）
# ───────────────────────────────────────────────
run_init_db() {
    echo -e "\n${GREEN}>>> 初始化数据库（db.create_all() 版）${NC}\n"

    prepare_venv

    perform_init=false

    if [[ -f "$DB_PATH" ]]; then
        echo -e "${YELLOW}检测到已存在数据库文件：$DB_PATH${NC}"
        read -p "是否删除现有数据库并重建？(y/N) " answer1
        if [[ "$answer1" =~ ^[Yy]$ ]]; then
            echo "备份旧数据库文件..."
            timestamp=$(date +%Y%m%d_%H%M%S)
            mv "$DB_PATH" "${DB_PATH}.${timestamp}.bak"
            perform_init=true
        else
            echo "取消初始化。"
            return
        fi
    else
        perform_init=true
    fi

    mkdir -p instance

    if $perform_init; then
        if [[ -f "init_schema.py" ]]; then
            echo "执行数据库初始化脚本（会自动创建表 + admin）..."
            python init_schema.py --with-data
            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}数据库初始化完成${NC}"
            else
                echo -e "${RED}初始化脚本执行失败，请检查 init_schema.py${NC}"
            fi
        else
            echo -e "${RED}错误：未找到 init_schema.py 文件${NC}"
            echo "请确认文件是否存在于项目根目录"
        fi
    fi
}

# ───────────────────────────────────────────────
# 初始化环境变量文件（新增选项 6）
# ───────────────────────────────────────────────
run_init_env() {
    echo -e "\n${GREEN}>>> 初始化环境变量文件${NC}\n"

    if [[ -f "config.env" ]]; then
        echo -e "${YELLOW}检测到已存在 config.env 文件${NC}"
        read -p "是否覆盖现有 config.env？(y/N) " answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            echo "备份现有 config.env..."
            timestamp=$(date +%Y%m%d_%H%M%S)
            mv config.env "config.env.${timestamp}.bak"
        else
            echo "取消初始化。"
            return
        fi
    fi

    if [[ -f "config.env.sample" ]]; then
        cp config.env.sample config.env
        echo -e "${GREEN}config.env 已创建${NC}"
        echo "请编辑 config.env 文件，设置必要的环境变量"
    else
        echo -e "${RED}错误：未找到 config.env.sample 文件${NC}"
    fi
}

# ───────────────────────────────────────────────
# 清理所有临时文件 & 缓存
# ───────────────────────────────────────────────
clean_all_temp() {
    echo -e "\n${GREEN}>>> 清理所有临时文件 & 缓存${NC}\n"

    echo "删除 __pycache__、.pyc、.pyo..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete

    echo "删除 pytest、coverage、mypy 等缓存..."
    rm -rf .pytest_cache .coverage htmlcov coverage.xml .mypy_cache .ruff_cache 2>/dev/null || true

    echo "删除 Flask 相关临时文件..."
    rm -rf instance/.flask_cache instance/*.log instance/*.db-journal 2>/dev/null || true

    echo "删除其他常见临时目录..."
    rm -rf build dist *.egg-info .eggs .tox 2>/dev/null || true

    echo -e "${GREEN}所有临时文件 & 缓存清理完成${NC}"
    echo "建议：重启服务以确保使用最新代码"
}

# ───────────────────────────────────────────────
# 安装/更新依赖
# ───────────────────────────────────────────────
run_update_deps() {
    echo -e "\n${GREEN}>>> 更新项目依赖${NC}\n"
    prepare_venv
    echo -e "${GREEN}依赖更新完成${NC}"
}

# ───────────────────────────────────────────────
# 显示菜单
# ───────────────────────────────────────────────
show_menu() {
    clear
    echo -e "${CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀${NC}"
    echo -e "  ${WHITE}🔧 内部管理系统 🔧${NC}"
    echo -e "    ${WHITE}启动/维护终端${NC}"
    echo -e "${CYAN}▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄${NC}"
    echo
    echo -e "  ${OPCODE_CYAN}1${NC} → 启动开发服务器"
    echo -e "  ${OPCODE_CYAN}2${NC} → 日常维护（子菜单）"
    echo -e "  ${OPCODE_CYAN}3${NC} → 系统初始化（子菜单）"
    echo -e "  ${OPCODE_CYAN}0${NC} → 退出脚本"
    echo
    echo -e "  ${OPCODE_CYAN}h${NC} → 显示帮助"
    echo
}

# ───────────────────────────────────────────────
# 显示日常维护子菜单
# ───────────────────────────────────────────────
show_maintenance_menu() {
    clear
    echo -e "${CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀${NC}"
    echo -e "    ${WHITE}日常维护${NC}"
    echo -e "${CYAN}▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄${NC}"
    echo
    echo -e "  ${OPCODE_CYAN}1${NC} → 生成 code2ai 审查文件"
    echo -e "  ${OPCODE_CYAN}2${NC} → 清理所有临时文件 & 缓存"
    echo -e "  ${OPCODE_CYAN}0${NC} → 返回主菜单"
    echo
}

# ───────────────────────────────────────────────
# 显示系统初始化子菜单
# ───────────────────────────────────────────────
show_init_menu() {
    clear
    echo -e "${CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀${NC}"
    echo -e "    ${WHITE}系统初始化${NC}"
    echo -e "${CYAN}▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄${NC}"
    echo
    echo -e "  ${OPCODE_CYAN}1${NC} → 安装/更新依赖"
    echo -e "  ${OPCODE_CYAN}2${NC} → 初始化数据库（建表 + admin）"
    echo -e "  ${OPCODE_CYAN}3${NC} → 初始化环境变量文件（config.env）"
    echo -e "  ${OPCODE_CYAN}0${NC} → 返回主菜单"
    echo
}

# ───────────────────────────────────────────────
# 主逻辑
# ───────────────────────────────────────────────
run_maintenance_menu() {
    while true; do
        show_maintenance_menu

        printf "${BRIGHT_CYAN}请输入选项 (0/1/2) 并按回车: ${NC}"
        read -r raw_input

        choice=$(echo "$raw_input" | sed 's/[^0-9]//g' | head -c 1)

        case "$choice" in
            0) echo "返回主菜单"; break ;;
            1) echo "→ 生成 code2ai 审查文件"; run_code2ai ;;
            2) echo "→ 清理所有临时文件 & 缓存"; clean_all_temp ;;
            *) echo -e "${YELLOW}无效选项 '$choice'，请重新输入${NC}" ;;
        esac

        echo
        echo -e "${GRAY}按回车键返回菜单...${NC}"
        read -s -r
    done
}

run_init_menu() {
    while true; do
        show_init_menu

        printf "${BRIGHT_CYAN}请输入选项 (0/1/2/3) 并按回车: ${NC}"
        read -r raw_input

        choice=$(echo "$raw_input" | sed 's/[^0-9]//g' | head -c 1)

        case "$choice" in
            0) echo "返回主菜单"; break ;;
            1) echo "→ 安装/更新依赖"; run_update_deps ;;
            2) echo "→ 初始化数据库"; run_init_db ;;
            3) echo "→ 初始化环境变量文件"; run_init_env ;;
            *) echo -e "${YELLOW}无效选项 '$choice'，请重新输入${NC}" ;;
        esac

        echo
        echo -e "${GRAY}按回车键返回菜单...${NC}"
        read -s -r
    done
}

if [[ $# -ge 1 ]]; then
    case "$1" in
        1) prepare_venv; run_app ;;
        2) run_maintenance_menu ;;
        3) run_init_menu ;;
        0|-h|--help) show_help ;;
        *) echo -e "${RED}未知选项: $1${NC}"; show_help ;;
    esac
    exit 0
fi

# 进入交互菜单
prepare_venv

while true; do
    show_menu

    printf "${BRIGHT_CYAN}请输入选项 (0/1/2/3/h) 并按回车: ${NC}"
    read -r raw_input

    choice=$(echo "$raw_input" | sed 's/[^0-9a-zA-ZhH]//g' | head -c 1 | tr '[:upper:]' '[:lower:]')

    case "$choice" in
        0) echo -e "${GREEN}感谢使用，再见！${NC}"; exit 0 ;;
        1) echo "→ 启动系统"; run_app; break ;;
        2) echo "→ 日常维护"; run_maintenance_menu ;;
        3) echo "→ 系统初始化"; run_init_menu ;;
        h) show_help ;;
        *) echo -e "${YELLOW}无效选项 '$choice'，请重新输入${NC}" ;;
    esac

    echo
    echo -e "${GRAY}按回车键返回菜单...${NC}"
    read -s -r
done

echo -e "\n${OPCODE_GREEN}脚本执行结束${NC}\n"
