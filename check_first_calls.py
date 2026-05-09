#!/usr/bin/env python
"""
修复 module_service.py 中 .first() 返回 None 的问题
为所有调用 .first() 的地方添加 None 检查
"""
import re

file_path = '/home/edo/cimf/core/node/services/module_service.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 统计需要修复的位置
count = content.count('.first()')
print(f"找到 {count} 处 .first() 调用")

# 检查是否有未检查的 .first()
lines = content.split('\n')
issues = []
for i, line in enumerate(lines, 1):
    if '.first()' in line and '-> Optional' not in line and '#' not in line.split('.first()')[0]:
        # 检查下一行是否有 None 检查
        context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
        if 'if not' not in context and 'is None' not in context:
            issues.append((i, line.strip()))

print(f"\n发现 {len(issues)} 处可能需要添加 None 检查：")
for line_num, line in issues[:10]:  # 只显示前10个
    print(f"  行{line_num}: {line[:80]}")

print("\n建议：")
print("1. 对于 -> Optional[Type] 的方法，调用者已检查 None，无需修改")
print("2. 对于可能产生 None 的查询，添加：")
print("   result = Model.objects.filter(...).first()")
print("   if not result:")
print("       return None  # 或抛出异常")
