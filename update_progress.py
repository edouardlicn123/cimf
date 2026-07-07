#!/usr/bin/env python3
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

import re
import sys
from datetime import datetime
from pathlib import Path

VERSION_FILE = "core/constants.py"
PROGRESS_FILE = "docs/progress.md"
FOOTER_FILE = "core/templates/includes/footer.html"
ARCHIVE_DIR = Path("docs/progress_archive")
MAX_ENTRIES = 300


def read_version():
    """读取当前版本号，返回 (major, minor)"""
    content = Path(VERSION_FILE).read_text(encoding="utf-8")

    match_major = re.search(r'VERSION_MAJOR = "(\d+)"', content)
    match_minor = re.search(r"VERSION_MINOR = (\d+)", content)
    major = int(match_major.group(1)) if match_major else 2
    minor = int(match_minor.group(1)) if match_minor else 1
    return major, minor


def increment_version(current_major, current_minor):
    """递增版本号"""
    new_minor = current_minor + 1
    new_major = current_major

    content = Path(VERSION_FILE).read_text(encoding="utf-8")

    content = content.replace(f"VERSION_MINOR = {current_minor}", f"VERSION_MINOR = {new_minor}")

    today = datetime.now().strftime("%Y-%m-%d")
    old_pattern = rf"    - {current_major}\.{current_minor:03d}: .+"
    new_history = f"    - {new_major}.{new_minor:03d}: {today}"
    content = re.sub(old_pattern, new_history, content, count=1)

    Path(VERSION_FILE).write_text(content, encoding="utf-8")

    return new_major, new_minor


def get_version_display(major, minor):
    """获取格式化的版本号"""
    return f"v{major}.{minor:03d}"


def get_today_date():
    """获取今天的日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def read_existing_progress():
    """读取现有 progress.md 内容"""
    if Path(PROGRESS_FILE).exists():
        return Path(PROGRESS_FILE).read_text(encoding="utf-8")
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
    remaining = content[today_pos + len(today_header) :]
    next_date_match = re.search(r"\n# \d{4}-\d{2}-\d{2} 修改记录", remaining)

    if next_date_match:
        today_section = content[today_pos : today_pos + len(today_header) + next_date_match.start()]
    else:
        today_section = content[today_pos:]

    other_records = content[:today_pos].rstrip("\n")

    return today_section, other_records


def get_next_number_in_section(section):
    """从记录部分获取下一条编号"""
    max_num = 0
    for match in re.finditer(r"^(\d+)\. ", section, re.MULTILINE):
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
        today_section = today_section.rstrip() + "\n" + new_line

        # 重新组合
        new_content = other_records + "\n\n" + today_section + "\n" if other_records else today_section + "\n"
    else:
        # 今天没有记录，创建新记录
        new_section = f"# {today} 修改记录\n\n1. {content_text}\n"
        new_content = other_records + "\n\n" + new_section if other_records else new_section

    new_content = ensure_archive_limit(new_content)
    Path(PROGRESS_FILE).write_text(new_content, encoding="utf-8")


def update_progress_overwrite(content_text):
    """覆盖模式：用新内容替换今天的记录"""
    today = get_today_date()
    existing = read_existing_progress()

    _, other_records = split_by_dates(existing)

    new_section = f"# {today} 修改记录\n\n1. {content_text}\n"

    new_content = other_records + "\n\n" + new_section if other_records else new_section

    new_content = ensure_archive_limit(new_content)
    Path(PROGRESS_FILE).write_text(new_content, encoding="utf-8")


def update_footer_version(new_version):
    """更新页脚版本号"""
    footer_content = Path(FOOTER_FILE).read_text(encoding="utf-8")

    footer_content = re.sub(r'(id="app-version">)v\d+\.\d+(</span>)', rf"\1{new_version}\2", footer_content)

    Path(FOOTER_FILE).write_text(footer_content, encoding="utf-8")


def count_entries(content):
    """统计 progress.md 中的记录条目数"""
    return len(re.findall(r"^\d+\. ", content, re.MULTILINE))


def get_date_blocks(content):
    """将 progress.md 按日期分组，返回 [(date_str, block_text), ...]"""
    pattern = re.compile(r"^# (\d{4}-\d{2}-\d{2}) 修改记录\n", re.MULTILINE)
    matches = list(pattern.finditer(content))
    if not matches:
        return []

    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        blocks.append((m.group(1), content[start:end]))
    return blocks


def archive_oldest_block(content):
    """将最旧的日期组归档到 docs/progress_archive/"""
    blocks = get_date_blocks(content)
    if not blocks:
        return content

    oldest_date, oldest_block = blocks[0]
    month = oldest_date[:7]  # YYYY-MM

    # Determine end of this month's data (find last block in same month)
    end_date = oldest_date
    for date_str, _ in blocks[1:]:
        if date_str[:7] == month:
            end_date = date_str
        else:
            break

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all blocks from this month
    to_archive = []
    remaining_blocks = list(blocks)
    for date_str, block in list(blocks):
        if date_str[:7] == month:
            to_archive.append((date_str, block))
            remaining_blocks.pop(0)
        else:
            break

    archive_name = f"{month}.md"
    archive_path = ARCHIVE_DIR / archive_name

    if archive_path.exists():
        existing = archive_path.read_text(encoding="utf-8")
    else:
        existing = f"# 历史修改记录 ({month})\n\n> 自动归档自 progress.md\n\n---\n\n"

    for date_str, block in to_archive:
        existing += "\n" + block.strip() + "\n"
    archive_path.write_text(existing, encoding="utf-8")

    print(f"  自动归档: 共 {len(to_archive)} 天 ({to_archive[0][0]} ~ {to_archive[-1][0]}) → {archive_name}")

    # Reconstruct content without archived blocks
    header_end = content.find("\n# ")
    preamble = content[:header_end + 1] if header_end != -1 else ""
    remaining = preamble + "\n".join(b for _, b in remaining_blocks) + "\n" if remaining_blocks else preamble + "\n"
    return remaining

    # Remove oldest block from content
    remaining = content[len(oldest_block):].strip()
    # Re-add preamble (everything before first date header)
    header_end = content.find("\n# ")
    if header_end != -1:
        preamble = content[:header_end + 1]
        remaining = preamble + "\n" + remaining
    else:
        remaining = content

    return remaining


def ensure_archive_limit(content):
    """确保 progress.md 不超过 MAX_ENTRIES 条记录"""
    while count_entries(content) > MAX_ENTRIES:
        content = archive_oldest_block(content)
    return content


def main():
    mode = "append"
    content = None

    for arg in sys.argv[1:]:
        if arg == "--append":
            mode = "append"
        elif arg == "--overwrite":
            mode = "overwrite"
        elif not arg.startswith("--"):
            content = arg

    if not content:
        print("用法:")
        print('  python update_progress.py "修改内容描述"        # 默认追加模式')
        print('  python update_progress.py --append "内容"       # 追加模式')
        print('  python update_progress.py --overwrite "内容"    # 覆盖模式')
        sys.exit(1)

    current_major, current_minor = read_version()
    old_version = get_version_display(current_major, current_minor)
    print(f"当前版本: {old_version}")

    new_major, new_minor = increment_version(current_major, current_minor)
    new_version = get_version_display(new_major, new_minor)
    print(f"新版本: {new_version}")

    if mode == "overwrite":
        update_progress_overwrite(content)
        print(f"[覆盖模式] 已更新: {content}")
    else:
        update_progress_append(content)
        print(f"[追加模式] 已追加: {content}")

    update_footer_version(new_version)
    print(f"已更新页脚版本号: {new_version}")
    print("\n完成!")


if __name__ == "__main__":
    main()
