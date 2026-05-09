#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
文件：update_progress.py
路径：/home/edo/cimf-v2/update_progress.py
============================================================================

功能说明：
    更新 progress.md 并自动递增版本号
    
用法：
    python update_progress.py "修改内容描述"        # 默认追加模式
    python update_progress.py --append "内容"      # 追加模式（默认）
    python update_progress.py --overwrite "内容"    # 覆盖模式（清空当天记录）

版本：
    - 1.1: 支持追加模式，同一天多次修改自动追加记录
"""

import sys
import os
import re
from datetime import datetime

VERSION_FILE = 'core/constants.py'
PROGRESS_FILE = 'docs/progress.md'
FOOTER_FILE = 'core/templates/includes/footer.html'


def read_version():
    """读取当前版本号"""
    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r"VERSION_MINOR = (\d+)", content)
    if match:
        return int(match.group(1))
    return 1


def increment_version(current_minor):
    """递增版本号"""
    new_minor = current_minor + 1
    
    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        f"VERSION_MINOR = {current_minor}",
        f"VERSION_MINOR = {new_minor}"
    )
    
    today = datetime.now().strftime('%Y-%m-%d')
    old_history = f"    - 1.00{current_minor}: 首次迭代"
    new_history = f"    - 1.00{new_minor}: {today}"
    content = content.replace(old_history, new_history)
    
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return new_minor


def get_version_display(minor):
    """获取格式化的版本号"""
    return f"v1.{minor:03d}"


def get_today_date():
    """获取今天的日期字符串"""
    return datetime.now().strftime('%Y-%m-%d')


def read_existing_progress():
    """读取现有 progress.md 内容"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def split_by_dates(content):
    """按日期分割内容，返回 (today_records, other_records)"""
    today = get_today_date()
    today_header = f"# {today} 修改记录"
    
    # 找到今天的记录部分
    today_pos = content.find(today_header)
    
    if today_pos == -1:
        # 今天没有记录
        return None, content
    
    # 找到下一个日期标题（下一个 # YYYY-MM-DD 开头）
    remaining = content[today_pos + len(today_header):]
    next_date_match = re.search(r'\n# \d{4}-\d{2}-\d{2} 修改记录', remaining)
    
    if next_date_match:
        today_section = content[today_pos:today_pos + len(today_header) + next_date_match.start()]
    else:
        today_section = content[today_pos:]
    
    other_records = content[:today_pos].rstrip('\n')
    
    return today_section, other_records


def get_next_number_in_section(section):
    """从记录部分获取下一条编号"""
    max_num = 0
    for match in re.finditer(r'^(\d+)\. ', section, re.MULTILINE):
        max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def update_progress_append(content_text):
    """追加模式：向今天的记录追加内容"""
    today = get_today_date()
    existing = read_existing_progress()
    
    today_section, other_records = split_by_dates(existing)
    
    if today_section:
        # 今天已有记录，追加新行
        next_num = get_next_number_in_section(today_section)
        new_line = f"{next_num}. {content_text}\n"
        today_section = today_section.rstrip() + '\n' + new_line
        
        # 重新组合
        if other_records:
            new_content = other_records + '\n\n' + today_section + '\n'
        else:
            new_content = today_section + '\n'
    else:
        # 今天没有记录，创建新记录
        new_section = f"# {today} 修改记录\n\n1. {content_text}\n"
        if other_records:
            new_content = other_records + '\n\n' + new_section
        else:
            new_content = new_section
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)


def update_progress_overwrite(content_text):
    """覆盖模式：用新内容替换今天的记录"""
    today = get_today_date()
    existing = read_existing_progress()
    
    today_section, other_records = split_by_dates(existing)
    
    new_section = f"# {today} 修改记录\n\n1. {content_text}\n"
    
    if other_records:
        new_content = other_records + '\n\n' + new_section
    else:
        new_content = new_section
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)


def update_footer_version(new_version):
    """更新页脚版本号"""
    with open(FOOTER_FILE, 'r', encoding='utf-8') as f:
        footer_content = f.read()
    
    footer_content = re.sub(
        r'(id="app-version">)v\d+\.\d+(</span>)',
        rf'\1{new_version}\2',
        footer_content
    )
    
    with open(FOOTER_FILE, 'w', encoding='utf-8') as f:
        f.write(footer_content)


def main():
    mode = 'append'
    content = None
    
    for arg in sys.argv[1:]:
        if arg == '--append':
            mode = 'append'
        elif arg == '--overwrite':
            mode = 'overwrite'
        elif not arg.startswith('--'):
            content = arg
    
    if not content:
        print("用法:")
        print("  python update_progress.py \"修改内容描述\"        # 默认追加模式")
        print("  python update_progress.py --append \"内容\"       # 追加模式")
        print("  python update_progress.py --overwrite \"内容\"    # 覆盖模式")
        sys.exit(1)
    
    current_minor = read_version()
    old_version = get_version_display(current_minor)
    print(f"当前版本: {old_version}")
    
    new_minor = increment_version(current_minor)
    new_version = get_version_display(new_minor)
    print(f"新版本: {new_version}")
    
    if mode == 'overwrite':
        update_progress_overwrite(content)
        print(f"[覆盖模式] 已更新: {content}")
    else:
        update_progress_append(content)
        print(f"[追加模式] 已追加: {content}")
    
    update_footer_version(new_version)
    print(f"已更新页脚版本号: {new_version}")
    print("\n完成!")


if __name__ == '__main__':
    main()
