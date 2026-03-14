# =============================================================================
# 文件路径：app/utils/progress_utils.py
# =============================================================================
# 
# =============================================================================
# 设计思路
# =============================================================================
# 
# 本模块用于自动管理 docs/progress.md 文档，实现以下功能：
# 
# 1. 自动日期分类
#    - 每次添加记录时，自动获取当前日期（如 2026-03-14）
#    - 自动创建对应日期的区块（# 2026-03-14 修改记录）
#    - 无需手动指定日期
# 
# 2. 最新日期优先
#    - 文件中日期区块按倒序排列（最新的在最前面）
#    - 自动处理新旧日期的排序
# 
# 3. 自动编号
#    - 每个日期区块内自动从 1 开始编号
#    - 重复添加时自动累加编号
#    - 无需手动管理编号
# 
# 4. 文件格式兼容
#    - 解析现有 progress.md 文件结构
#    - 保留原有历史记录
#    - 支持任意日期数量的文件
# 
# =============================================================================
# 文件格式示例
# =============================================================================
# 
# # 2026-03-14 修改记录
# 
# 1. 第一条记录
# 2. 第二条记录
# 3. 第三条记录
# 
# # 2026-03-13 修改记录
# 
# 1. 历史记录...
# 2. 历史记录...
# 
# =============================================================================
# 使用方法
# =============================================================================
# 
# 方式一：在 Python 代码中导入使用
# -----------------------------------
# 
#     from app.utils.progress_utils import add_progress
# 
#     # 添加单条记录
#     add_progress("完成了用户认证功能")
# 
#     # 批量添加记录
#     add_progress_batch([
#         "修复了导出功能",
#         "添加了新字段",
#         "优化了性能"
#     ])
# 
# 方式二：命令行调用
# -----------------------------------
# 
#     # 单条记录
#     python -c "from app.utils.progress_utils import add_progress; add_progress('message')"
# 
#     # 批量记录（不支持）
# 
# =============================================================================
# 注意事项
# =============================================================================
# 
# 1. 本模块不依赖 Flask 应用，直接使用 pathlib 操作文件
# 2. PROGRESS_FILE 路径基于本文件位置自动计算，无需手动配置
# 3. 每次调用 add_progress 会重写整个文件，请勿在多进程/多线程环境下同时调用
# 4. 记录内容建议简洁明确，包含文件名和主要改动
# 
# =============================================================================

import re
from datetime import datetime
from pathlib import Path

PROGRESS_FILE = Path(__file__).parent.parent.parent / "docs" / "progress.md"


def get_today_date() -> str:
    """获取当前日期，如 '2026-03-14'"""
    return datetime.now().strftime("%Y-%m-%d")


def read_progress_file() -> str:
    """读取 progress.md 内容"""
    if PROGRESS_FILE.exists():
        return PROGRESS_FILE.read_text(encoding="utf-8")
    return ""


def parse_existing_dates(content: str) -> dict:
    """
    解析现有的日期区块
    返回: { "2026-03-14": [记录列表] }
    """
    dates = {}
    if not content:
        return dates
    
    lines = content.split("\n")
    current_date = None
    current_items = []

    for line in lines:
        match = re.match(r"^# (\d{4}-\d{2}-\d{2}) 修改记录$", line.strip())
        if match:
            if current_date:
                dates[current_date] = current_items
            current_date = match.group(1)
            current_items = []
        elif current_date and re.match(r"^\d+\.", line.strip()):
            current_items.append(line.strip())

    if current_date:
        dates[current_date] = current_items

    return dates


def get_next_item_number(items: list) -> int:
    """获取下一个编号"""
    max_num = 0
    for item in items:
        match = re.match(r"^(\d+)\.", item)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def rebuild_file(dates_data: dict):
    """重建整个文件，保持最新日期优先"""
    sorted_dates = sorted(dates_data.keys(), reverse=True)
    
    sections = []
    
    for date in sorted_dates:
        items = dates_data[date]
        section_lines = ["# " + date + " 修改记录", ""]
        section_lines.extend(items)
        sections.append("\n".join(section_lines))
    
    new_content = "\n\n".join(sections)
    PROGRESS_FILE.write_text(new_content + "\n", encoding="utf-8")


def add_progress(message: str):
    """
    添加进度记录
    - 自动获取当前日期
    - 自动编号
    - 保持最新日期优先
    """
    today = get_today_date()
    content = read_progress_file()
    dates_data = parse_existing_dates(content)
    
    if today in dates_data:
        next_num = get_next_item_number(dates_data[today])
        dates_data[today].append(str(next_num) + ". " + message)
    else:
        dates_data[today] = ["1. " + message]
    
    rebuild_file(dates_data)


def add_progress_batch(messages: list):
    """批量添加进度记录"""
    today = get_today_date()
    content = read_progress_file()
    dates_data = parse_existing_dates(content)
    
    start_num = 1
    if today in dates_data:
        start_num = get_next_item_number(dates_data[today])
    
    new_items = []
    for i, msg in enumerate(messages):
        new_items.append(str(start_num + i) + ". " + msg)
    
    if today in dates_data:
        dates_data[today].extend(new_items)
    else:
        dates_data[today] = new_items
    
    rebuild_file(dates_data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            for msg in sys.argv[2:]:
                add_progress(msg)
        else:
            add_progress(" ".join(sys.argv[1:]))
