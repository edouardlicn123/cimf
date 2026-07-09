# 修改记录

本文档记录项目的每次修改，按日期分组。

---


> 最近 300 条记录。历史记录已归档至 `docs/progress_archive/`。

---


变
63. 新增踊主题(odoru)：基于fukunagaazusa.jp配色，青绿+奶油暖白+暖褐，温暖文艺风
64. 删除青绿主题(teal)，savawoku改名为橙红

# 2026-05-10 修改记录

1. 创建 tais（大正紫）主题，基于 www.tais.ac.jp 配色：主色 #514068 紫 + 强调 #ef8bae 粉
2. 大正紫 → 梵紫 改名
3. tais（梵紫）主题颜色丰富化：添加学部多彩色、渐变 navbar、Bootstrap 变量映射、多种组件样式
4. 修复 tais 主题中 .card-body 独立边框问题，卡片遵守基本卡片规则
5. 修复 tais 主题卡片底部圆角被 card-footer 背景遮挡的问题
6. 修复 tais 主题卡片圆角：header/footer 各自设置 border-radius，不再依赖 overflow 裁剪
7. tais 主题：card-header 背景透明 + 粉色底边 accent 线
8. tais 主题多处添加粉色 accent 线条：表头/分页/tabs/列表组/模态框/分割线/链接悬停/表单焦点/card-icon/卡片悬停等
9. tais 主题卡片右上角改为直角
10. tais 主题卡片右上角改为直角：移除 frame.css 中 !important border-radius 限制，tais.css 接管控制
11. 所有主题：卡片内容区左上角改为直角，frame.css 设 border-radius: 0 var(--radius-sm) var(--radius-sm) var(--radius-sm)
12. 马卡龙主题 navbar 背景加深为 #6A5C8A，菜单文字改为白色
13. 马卡龙 navbar 背景微调 #6A5C8A → #7D71A0 变浅
14. 马卡龙 navbar 改为直角
15. 马卡龙主题：左侧菜单选中文字白色，非选中文字外发光 1px
16. 马卡龙主题：选中菜单白色文字 + 1px 绿色外发光
17. 马卡龙主题：恢复选中菜单原始样式
18. 大正紫主题：卡片内容区右上角改为直角
19. 删除未使用的 node_modules/lunar-javascript
20. structure/types/ 列表改为基本列表风格，列表填满容器
21. structure/taxonomies/ 列表改为基本列表风格
22. 列表卡片增加 card-header 主题主色边框（字段类型+词汇表）
23. structure/types/（节点类型）改为基本列表风格+card-header边框
24. fieldtypes/ 删除返回内容结构按钮
25. fieldtypes/ 增加页面标题
26. 修复卡片四角圆角（frame.css border-radius）
27. 修复卡片border移至card本身，解决四角开口问题
28. card-body边框仅底部圆角，上边平接header
29. 卡片设计改为全宽card-header + card-body仅底部圆角边框
30. 改用box-shadow:inset替代border消除角渲染问题
31. 改用outset box-shadow替代border，由card overflow裁切底部圆角
32. 用clip-path裁剪border底部圆角，避免border-radius渲染缺口
33. 用::before伪元素画border，card-body的overflow:hidden裁切圆角
34. ::before改用inset box-shadow，避免被overflow裁切且不被内容遮挡
35. 双层background填充border区域底色，掩盖Firefox角渲染缺口
36. 修复 Firefox card-body 底部角落边框渲染缺口：使用 inset box-shadow 替代 border
37. 重新生成 structure/types/、taxonomies/、fieldtypes/ 三个页面：边框移到 .card，h5 margin-top:-1px 覆盖顶部边框，避免 Firefox 边框圆角渲染问题
38. 重写结构管理三页面：card-body 内加 card-body-border 容器承载边框，避免 Firefox 圆角渲染缺口
39. 卡片标题区改为透明背景，仅内容区(card-body-border)保留背景色
40. 卡片样式分成两个变体：card-structure(不透明)用于现有页面，card-structure-transparent(透明标题)用于结构列表页
41. 基本卡片1(card-structure)标题区域改为透明，仅内容区保留背景色
42. 提高 card-structure/card-structure-transparent 选择器优先级为 .card.card-structure，重启服务器
43. 修复 system/settings/ 页: _reset_to_default_bulk 不重置bug、save_settings_bulk 缓存频繁清除、BOOL_SETTINGS 硬编码、Logo accept 缺GIF/WEBP
44. 基本卡片1(card-structure): .card-body 添加主色调四周边框 (1px solid var(--primary))
45. /system/settings/ 六个卡片添加 card-structure 类，实现透明标题+主色边框
46. /system/permissions/ 三个卡片添加 card-structure 类
47. /system/smtp/ config+history 卡片添加 card-structure 类
48. node导入导出页: 5模板10卡片重构为基本卡片1(card-structure+card-header)
49. nodes/customer/ 列表页2卡片重构为基本卡片1(card-structure+card-header)
50. 遗留修复: 删除database.py冗余WAL连接; calc eval()替换为AST安全求值器
51. run.sh 维护菜单新增选项6: Ruff代码检查
52. run_ruff_check 增加报告保存到 storage/reports/；更新 .gitignore 和 AGENTS.md
53. Ruff 71个问题全部修复：F821/F823运行时Bug、E402导入位置、F811重复定义、E712 True比较、F541/F701/F841/F401代码清理
54. AGENTS.md 明确区分检查bug与ruff报告读取的触发条件
55. 重构 AGENTS.md 为四段式结构：用户指令响应→启动清单→开发规范→项目参考，删除冗余列表
56. 更新 README.md：主题 7→8、字段类型 24→26、角色名称、主题一览表
57. 首页卡片区域应用 card-structure（基本卡片1）样式
58. 主题重命名：浓重红色→中国红
59. 主题迁移整合：新建 0015_consolidated_theme.py 替换 0008~0014
60. 删除 0008~0014 旧迁移文件
61. 压缩迁移：合并 0005~0007 为 squashed 文件，删除旧文件
62. 重命名 0005_squashed 为 0005_core_module_updates.py
63. 绿岛森林主题：新增金色线条（sidebar竖条 + 按钮聚焦环）
64. 绿岛森林主题：基本按钮加入金色外圈
65. 绿岛森林主题：navbar下加1px金色条
66. 梵紫主题：card-header 背景改为 transparent shorthand
67. 梵紫主题：移除 card-header 自定义规则，与 frame.css 保持一致
68. 梵紫主题：删除 tais.css card-header 规则，frame.css 改为对所有 .card-header 设置 transparent（含 background-color）
69. 梵紫主题：去除 tais.css .card 的 border 和 box-shadow，让 frame.css 接管
70. 梵紫主题：给 card-header 加 2px 粉色底边（与 card-footer 对称）
71. 靛蓝主题：药丸标签水平内边距改为 64px（长度加倍）
72. 靛蓝主题：大幅增强——新增accent色系（navy/blue/violet/gold/teal/coral）、bg-subtle/muted、卡片/表格/分页/进度条/Accordion/按钮/徽标/模态框/导航标签/Alert/下拉菜单/Dashboard卡片/表单焦点等完整组件样式

# 2026-05-11 修改记录

1. frame.css 新增渐进式加载动画：navbar(0s)→sidebar(0.12s)→主内容(0.25s) 淡入
2. 增强渐进加载动画：navbar 下滑、sidebar 左滑、内容上浮，时长 0.55s、间隔 0.2s
3. 升级依赖：django 6.0.5、DRF 3.17.1、requests 2.33.1、gunicorn 26.0.0、pillow 12.2.0、pypdf 6.11.0
4. 依赖升级后兼容性检查通过，无需修改代码
5. A08 Bug检查修复：ClockModel添加__str__、SQLite添加WAL模式、环境变量统一DJANGO_前缀、清理config.env冗余/孤立密钥
6. ruff 集成：requirements.txt + ruff.toml（严格规则），自动修复 2579 个问题，剩余 351 个待审
7. 修复 run.sh ruff 选项因 set -e 强退的问题
8. 修复所有 PTH (flake8-use-pathlib) 问题，涉及 13 个文件：settings.py/database.py/checks.py/marketplace/services.py/module/models.py/module_service.py/views.py/node_type_service.py/china_region_service.py/log_service.py/health.py/settings.py/tools.py
9. 修复所有 ARG (unused argument) 问题：将未使用参数加下划线前缀，视图函数加 noqa 注释
10. Fix all 155 PLC0415 import-at-top-level ruff issues across 48 files
11. ruff 全部 351 个问题修复完成（PTH/ARG/PLC0415/PERF/SIM等），ruff+manage.py check 通过
12. 修复 signal handler 参数名 _sender→sender（ARG 修复的副作用）
13. config.env 改进：修复settings.py错误消息、DB_*统一DJANGO_前缀、更新database.py/run.sh、添加WAL注释；apps.py加noqa
14. IP白名单简化：IP_WHITELIST为空时自动从ALLOWED_HOSTS提取IP
15. 调整 run.sh 安装子菜单顺序 + 重写 run.bat（Windows版，全功能对齐）
16. config.env/env.sample 新增 pip 镜像源配置段；run.sh/run.bat 改为 config.env 驱动
17. 新增 run.ps1 (PowerShell 版启动脚本，全功能对齐 run.sh)

# 2026-05-12 修改记录

1. 修复 clock 模块迁移文件缺少 options 配置导致安装失败的问题
2. 修复 homepage_settings 视图未过滤 frontpage_card 导致所有活跃模块出现在功能卡片设置页
3. 修复功能卡片设置页 CSRF 处理（head_extra 补充 super()，getCsrfToken 增加 hidden input 回退）
4. 修复功能卡片保存失效：Python dict 合并运算符  方向反了，已保存数据被默认值覆盖
5. whatsapp 模块添加 frontpage_card: True，恢复首页功能卡片
6. 修复多个模块问题：whatsapp日志模板状态值/customer表单字段/whatsapp timezone.now/移除重复装饰器和deprecated模式/添加install_on_init/更新文档
7. 修复 customer/__init__.py deprecated default_app_config、customer/forms.py 遗留字段、customer/edit.html 移除不适用的 region_select.js、whatsapp 改用 core.decorators.admin_required_json
8. whatsapp HTML 视图改用 @login_required 替代 @login_required_json
9. 修复 whatsapp 导入路径/未使用导入/ARG001/异常处理，calc calculate 改用 @login_required_json
10. ruff.toml 添加 unsafe-fixes = false，防止 ARG001 自动重命名参数
11. 修复 ruff 配置：unsafe-fixes = false 移至顶层位置
12. AGENTS.md: 补充AR规则说明及3处已知待修复ARG001清单
13. AGENTS.md: 重构AR规则为通用规范，使用✅/❌分类明确fix规则
14. whatsapp/views.py: 3处API视图request参数加# noqa: ARG001
15. whatsapp卡片第二行改为显示海外客户人数
16. customer卡片第二行改为显示当前客户人数
17. 整理.gitignore，分类重组并独立模块排除段
18. SMTP配置：保存后自动检测服务连接状态，服务状态分已禁用/已连接/未连接
19. SMTP服务状态：关闭时不显示服务状态，仅显示已连接/未连接
20. SMTP服务状态三态：未启用(灰)/已连接(绿)/未连接(红)
21. SMTP表单：表单无效时显示错误消息和字段错误提示
22. SMTP表单：顶部显示全部字段错误信息(含字段级)
23. SMTP加密方式：非自定义时隐藏，选择预设自动设加密
24. 修复SMTP状态检测：get_all_settings返回bool导致== 'true'永远False
25. SMTP代理：新增SOCKS5代理开关，保存后可随时启用/关闭
26. SMTP代理开关新增详细使用说明
27. SMTP代理说明改为可折叠，加小问号图标触发
28. SMTP: 发送设置卡片添加发送间隔(默认120s)，修复测试连接按钮不更新状态的问题
29. SMTP代理设置改为填写IP和端口(默认127.0.0.1:10808)，替换原有use_proxy开关
30. SMTP配置页重构：服务商预设合并到服务器配置，服务开关移至左侧状态卡，通知合并到发送设置，代理新增启用开关+说明折叠
31. 修复 _convert_setting_value 误将 IP 地址 127.0.0.1 当作 float 解析的 bug
32. 修复 enabled 复选框在 form 标签外无法提交的问题（添加 form='smtpForm' 属性）
33. 修复 EmailLog._create_log 中 html_body=None 导致 NOT NULL constraint failed（smpt测试工具全部发送失败）
34. 修复 _send_sync 参数名不匹配及删除未使用的 from_email 参数
35. CoreConfig.ready() 启动时自动同步 SMTP Django 运行时配置
36. CoreConfig.ready() 启动时同步 Django EMAIL 运行时配置（用 noqa 避免循环导入）
37. 创建 docs/stage4/01_SMTP邮件发送流程改进方案.md
38. P2: EMAIL_TIMEOUT, contextmanager refactor, EmailLog.status index, update_connection_status dedup, process queue route/button
39. P2.3/P2.6: EmailLog text_body/html_body/error_message default=''
40. Bug全检: header.html block修复 + error页面show_header修复
41. Bug全检第2轮: customer node_delete + @require_POST, JS fetch catch检查

# 2026-05-13 修改记录

1. 参照 system/permission-check/ 设计模式重构 system/smtp/history/：添加分页(paginate_queryset)、统计卡片(总/成功/失败/待发送)、过滤改为 nav-pills-outline 样式、修复 card-header d-flex 违规
2. 模块安装时自动安装 requirements.txt 依赖（新增 _install_requirements 静态方法）
3. 删除 smtp/history 模板顶部统计卡片行，保留主卡片内 nav-pills 统计值
4. WhatsApp 模块模板改用基本卡片1：logs.html/manage.html/send.html 添加 card-structure 类，修复 card-header d-flex 违规
5. 方案A：修复 WhatsApp 模块路由 — modules/urls.py 挂载 tool 类型模块 urls.py，模板中 AJAX URL 改为 /modules/whatsapp/api/... 绝对路径
6. A08 自动化检查完成：所有 13 项检查通过，无 P0/P1 发现
7. 首页卡片 CSS 设计：hover 升起改为白色半透明内发光（inset box-shadow），更新 D01 §5 文档及 2 个模板
8. 首页卡片内发光：缩小扩散至 8px，改为不透明白色 #fff
9. 38号方案文档完善：修正注释措辞、ClockService timestamp 一致化纳入计划
10. 实施38号方案：TimeSyncService持久化+单调时钟、ClockService使用同步时间、API新增timestamp、前端fetchServerTime+getServerDate同步
11. 首页卡片 hover 白色外框 2px → 1px 收窄
12. SMTP 发送间隔合并：删除 rate_limit，send_interval 默认240s ±15s 随机化，前端补充说明
13. Ruff 43项修复：UP009/W292/I001/RUF010/F401 自动修复 + PLC0415/F821 手动移惰性导入至顶层
14. smtp 迁移文件 squash: 0001-0004 → 0001_squashed_0004
15. smtp 迁移合并：删除旧 0001-0004，保留单文件 0001_squashed_0004



# 2026-05-14 修改记录

1. 修复导入XLS模板时MIME类型检查过于严格导致'文件格式不正确'的问题，移除了不可靠的MIME content_type检查

# 2026-05-17 修改记录

1. WhatsApp 模块：发送页和管理页状态卡片添加刷新状态按钮；管理页测试连接后自动刷新状态徽章
2. WhatsApp 模块：修复 SOCKS5 代理导致 httpx 无法连接 wabridge 的问题（_create_wa 临时清除代理环境变量 + trust_env=False）; 发送页/管理页 refreshStatus 增加错误显示和 catch 处理
3. 修复 cimf-whatsapp/runwabridge.sh 启动方式：run_start 改为后台 daemon 模式（nohup+PID 文件）；新增 --stop/--restart/--pid 命令；同步 services.py/templates 修复到 cimf-whatsapp
4. WhatsApp 模块状态卡片重构：徽章/账号/操作/错误四行布局；账号独立一行显示；添加刷新时间戳和加载动画；错误信息独立显示区域
5. WhatsApp 模块：新增 api_customers 视图，调用海外客户模块数据 + SendLog 标注最近发送时间并按发送时间升序排列；send.html 重写客户加载 JS 实现真实数据加载、搜索防抖、勾选功能
6. 修复 send.html 中 templates 变量未 JSON 序列化导致 JS 解析失败（expected expression, got '<'）— views.py 改用 json.dumps 后模板引用 templates_json

# 2026-05-18 修改记录

1. 修复 manage.html：模板保存/编辑/删除 fetch 添加 .catch() 错误提示；onclick 改为 data-* 属性+事件委托，避免模板内容含引号时 HTML 属性断裂
2. 修复 core/node：node_edit 路由缺少 action='edit' 参数，导致编辑请求被 node_view 拦截；module_dispatch 新增 action=='edit' 分发逻辑
3. 修复 manage.html 模板保存 JSON 解析失败：模板 API 视图添加 @csrf_exempt，避免 fetch POST/PUT 因缺少 CSRF token 返回 HTML
4. send.html 发送按钮添加 .catch() 错误提示；manage.html 所有 fetch 添加 .catch()
5. 重写 send.html 客户选择逻辑：移除 selectedCustomers 数组，改为直接读取 DOM 已勾选 checkbox；selectAll/复选框改为事件委托
6. send.html：复选框同时绑定 change+click 事件；loadCustomers fetch 添加 .catch() 错误处理
7. 修复发送时电话号带 + 号导致 WABridge 验证错误：wa.send() 前 lstrip('+')
8. 重排发送页面布局：三卡片从上到下（发送模板/选择客户/服务状态）；模板下拉默认回到请选择
9. 发送页面顶部按钮栏添加「发送消息」按钮，置于发送记录之前
10. Pre-create pending SendLog records on batch start; add 'pending' to STATUS_CHOICES
11. Fix pending log display: add 排队中 badge, show customer_id for pending, update sent_at on status change
12. Fix kill_server in run.sh: add -sTCP:LISTEN; add 杀进程安全规范 to AGENTS.md
13. WhatsApp 发送列表页面改进：表头sticky固定、服务端分页、过滤改造（搜索按钮+排除最近发送下拉）、最近发送只取wabridge成功记录、默认间隔改为300/600秒
14. WhatsApp 批次限制：每批次最多59条
15. WhatsApp 批次截断：超59条自动截断+toast提示+记录页截断提示
16. WhatsApp 管理页新增每批最大条数设置项

# 2026-05-30 修改记录

1. 修复whatsapp模块批量发送：默认间隔从300/600秒改为30/60秒；修复首次发送前sleep问题，改为第一条立即发送、后续间隔发送
2. WhatsApp模块：默认间隔改为61-122秒，设置页添加间隔参考提示；发送记录页新增一键终止发送功能
3. 修复海外客户列表页删除405错误：将删除链接从GET方式的a标签改为POST表单+CSRF
4. WhatsApp发送列表排序改为：未发送优先→发送最远优先→客户名称排序
5. WhatsApp模块默认间隔恢复为300-600秒，更新参考提示
6. WhatsApp模块批次限制默认值从59改为49
7. 创建 docs/stage4/40_WhatsApp发送Cron架构改造方案.md —— 记录懒注册+安装时注册方案
8. 创建 docs/stage4/41_模块Cron任务自动注册机制.md —— 通用 MODULE_INFO.cron_tasks 注册框架
9. 修正文档 39/40/41 冲突：40 重写为依赖 41 通用机制，39 适配 cron 架构并标注执行顺序
10. 实施 41/40/39 三个方案：core cron 自动注册机制、WhatsApp cron 重写（WhatsAppSendTask + services 新函数 + models 新字段 + 0003 迁移 + views/urls 改造）、UI 改进（toast 59条 + cron 调度卡片 + rate_limited 状态展示 + 移除废弃 batch_limit 设置）

# 2026-05-31 修改记录

1. Bug检查：移除 @csrf_exempt(7处) / 修正 CharField null=True(9处)
2. 修复节点详情页卡片样式为基本卡片1(card-structure)
3. 全部修复: node_delete PK类型/P2死代码竞态计数器/F()原子更新/字段白名单/narrow except/select_related
4. 修复 ruff I001: 合并 django.views.decorators.http 导入组



# 2026-06-01 修改记录

1. WhatsApp 三模板随机发送功能：SendBatch 新增 template_ids JSONField、services.py 随机选模板逻辑、views.py api_send 接收数组、send.html 三选择器+三预览、迁移文件

# 2026-06-07 修改记录

1. 修复 whatsapp manage.html CSRF 问题：所有 fetch 调用添加 X-CSRFToken header 和 r.ok 检查（测试连接/删除模板/保存模板/保存设置）
2. 修复 whatsapp send.html 和 logs.html CSRF 问题：发送消息和终止发送 fetch 添加 X-CSRFToken header 和 r.ok 检查
3. whatsapp create_batch 支持追加：同 template_ids 运行中批次自动追加客户，无运行中批次则新建并立即发送第一条
4. 新增 WABridge 健康检查+自动重启机制：WhatsAppService.check_health/restart_wabridge/ensure_healthy，集成到 create_batch 和 send_next_pending；新增 WABridgeRestartTask 每日重启
5. 修复 runwabridge 7处 subprocess.run 缩进丢失; 添加 --login CLI; 修复 ruff 3个警告
6. 添加 WhatsApp 号码检测功能: serve.js /check patch, CustomerFields.has_whatsapp, batch_check_whatsapp, 号码检测页面, 自动修正 customer_name 前缀（电话错误）
7. 修复 batch_check_whatsapp: onWhatsApp 只返回有 WA 的号码, 未命中算 no_wa 而非 errors
8. 客户列表：无 WhatsApp 用户后显示 X 标记
9. 修复检测页面：检测后保持当前页不跳回第一页
10. 检测页面：默认筛选未确认用户，筛选选项改为未确认/有/没有/全部
11. 检测后跳转回「未确认」筛选第一页
12. 修复 WhatsApp 检测：号码长度限制 10->8 位，支持巴林等短号国家
13. 检测后保持当前筛选和页码，让用户直接看到检测结果
14. 修复检测：提取纯数字处理韩国括号/EXT后缀等格式，错误时toast变警告色
15. 修复号码清理：新增 _clean_phone 方法，正确截断分机号并去除括号横线
16. 修复检测：无效号码客户标记为无WhatsApp，不再阻塞整页检测
17. 发现 WABridge 不支持号码检测功能，需要替代方案
18. 合并号码验证到检测功能：无效号码自动标记，WABridge 不可用时仍处理无效号码
19. 号码格式检测：括号、横线、空格、EXT等格式异常号码自动标记为没有WhatsApp并加（电话错误）前缀

# 2026-06-08 修改记录

1. 修复 WABridge 安装位置冲突：删除 /usr/lib 错误版本，保留 /usr/local/lib 正确版本（含补丁），WhatsApp 检测功能恢复正常
2. 修复号码长度验证：将 Python 端验证从 8-15 位改为 10-15 位，与 WABridge 保持一致，9 位号码被正确标记为无效
3. WhatsApp 发送页面添加「仅显示有 WhatsApp」过滤器，翻页时保持过滤状态
4. WhatsApp 检测不再修改客户名称，删除 3083 条记录的「电话错误」前缀
5. WhatsApp 号码检测重构：添加一键验证全部号码功能，每号码检查3次，每批10个间隔60秒，新增验证日志页面（保留4000条）

# 2026-06-10 修改记录

1. 修复 WhatsApp 验证进度显示：total_count 在创建批次时即设置，避免显示 0
2. 修复 WhatsApp 验证错误信息显示：正确获取 check_health() 返回的 error 字段



# 2026-07-04 修改记录

1. 全面代码审计修复：硬编码URL、tool路由、CustomerForm集成、迁移对齐、SQL拼接、路径遍历、export格式校验、tool_slug白名单、dead code清理、ARG001补全、返回值检查、user验证加固、frame死代码移除、console.log清理、文档更新、Ruff零告警

# 2026-07-05 修改记录

1. 后续代码审计修复：whatsapp未包裹.get()、OOM风险、DB级分页、log_service内存优化、删除遗留脚本
2. 创建 core/templates/includes/ 下 10 个共享 Jinja2 模板组件
3. 重构错误页面模板统一使用 error_base.html；BaseService 增加 create/update/delete CRUD 方法
4. 重构 importexport views: 用 @permission_required 装饰器替换手动权限检查；添加 _get_node_type_or_redirect 辅助函数以消除 9 个视图中的重复代码
5. 合并JS文件：统一CSRF Token/showToast/apiPost/DragDrop到common.js，简化toast_messages.html和dashboard_cards脚本
6. 重构8个frame模板，提取sidebar和content_area结构到includes组件
7. 代码清理：共享验证器模块创建、冗余toast容器/CSS移除、is_admin→@admin_required替换、console.log调试代码清理
8. CSS: 新增 --bg-card/--bg-body/--border-light/--radius-md 变量声明到 variables.css 及所有主题; 文档: 表单 BootstrapFormMixin 使用清单
9. 重构 customer/views.py: 提取 _load_customer_form_data() 消除3处重复的分类数据加载；ModuleService: 新增 load_module_info() 公开方法，消除 tools.py/permission_service.py/cards.py/settings.py 中4处重复的 MODULE_INFO 加载逻辑
10. 分页增强、工具侧边栏去重、版本统一至2.001
11. 大型可封装性重构实施：创建10个共享模板组件(sidebar/content_area/entry_card/table_card/status_badge/error_base/filter_bar/form_actions/alert/modal)；重构8个frame模板使用Include减少代码重复；importexport视图迁移@permission_required装饰器+_get_node_type_or_redirect辅助函数；错误页统一为error_base；BaseService扩展CRUD方法；JS统一(window.FFE.getCsrfToken/showToast/apiPost/handleFetchError/DragDrop)；合并dashboard_cards.js；移除冗余toast+flash隐藏CSS；clean_email/clean_username/密码验证共享化；admin_required替换手动is_admin；taxonomy数据加载封装；Module info加载合并；版本号统一v2.001；CSS变量补齐；增强分页组件；工具侧边栏加载合并；Ruff零告警
12. 重构服务层和模型层：使用BaseService.get_by_id、提取_get_user_or_raise/auth_service去重、time_sync helper、水印POSITIONS常量、settings_service简化、db_index索引、模块URL缓存、cron_service拆分
13. 清理JS和表单：硬编码API URL替换为url()标签、dashboard_cards.js使用FFE.apiPost、region_select.js拆分initRegionSelectWidgets、删除空main.js、实现setupGlobalAjaxError、表单Meta widgets去重
14. 重构 Jinja2 模板：pagination/form_actions/modal 提取为 include；show_numbers 分页；frame_importexport 清理；permissions_table 提取；drag-and-drop 改用 makeSortable
15. 重构 Django views/URLs/middleware: 修复中间件死代码, 新增change_password/profile路由, active_section上下文处理器, handle_form_errors装饰器, _get_taxonomy_or_404辅助函数, 聚合get_user_stats查询, 添加重定向URL names, 清理未使用导出
16. CSS consolidation: extract duplicated theme blocks to base.css, replace hardcoded colors with CSS vars, deduplicate nav_cards/dashboard_cards CSS, remove welcome-bar/avatar-placeholder, add -ms-user-select to watermark
17. 第二期全面封装重构：47项可封装机会全部执行。模板层：5模板改用pagination include、4模板改用form_actions、2模板改用modal include、提取system_permissions双表为共享include、4模板移除内联拖放改为window.FFE.DragDrop.makeSortable、移除frame_importexport未用admin_footer。视图层：修复middleware死代码、新增change_password/profile路由、active_section统一为context processor(13处手动移除)、@handle_form_errors装饰器+4视图应用、_get_taxonomy_or_404提取、get_user_stats聚合查询、3重定向添加name。服务层：8处user_service改用get_by_id、3处taxonomy_service改用get_by_id、auth_service login→authenticate去重查询、time_sync_service提取_helper、_get_user_or_raise提取6处替换、watermark POSITIONS常量提取、settings_service简化update_or_create。模型层：User.email/is_active/role + ChinaRegion.level添加db_index。模块层：get_installed_module_slugs添加缓存。CSS层：5公共块从6主题提取到base.css、hardcoded颜色替换为CSS变量、nav_cards/homepage CSS去重、welcome-bar/avatar-placeholder死类移除、-ms-user-select补齐。JS层：7处API URL改用url()、dashboard_cards.js改用apiPost、region_select.js拆分、main.js删除、setupGlobalAjaxError实现。表单层：UserCreateForm/UserEditForm widgets共享字典。Ruff零告警+199文件格式化+makemigrations无变更

# 2026-07-06 修改记录

1. 综合服务层封装：创建 mixins.py (SingletonMixin/CachedServiceMixin/工具函数)，扩展 BaseService (get_or_raise/get_first/get_or_none)，CronTask 基类添加默认 setting_key 属性并精简子类，重构 TaxonomyService/UserService/AuthService/SettingsService/PermissionService/ChinaRegionService 使用 mixins 工具函数
2. 视图层封装重构：创建core/utils/response.py工具函数；重构errors/health/logs/users/taxonomy/regions/cards/time视图及装饰器/中间件；统一JsonResponse→json_success/json_error替换；应用composite decorators模式
3. 全面模板层封装：创建 frame_sidebar_base/card_section/empty_state/form_switch/nav_pills/entry_card_grid/form_errors/stat_card/pagination 组件，重构 7 个 frame 模板扩展 chain，简化 pagination 调用，替换 card/empty/nav-pills/stat 模式到 include，清理 CSRF/Toast JS 重复
4. CSS/Forms/JS consolidation: moved shared CSS patterns to base.css, extended BootstrapFormMixin with SelectMultiple, added UserAwareFormMixin/EmailCleanMixin/UsernameCleanMixin, moved _USER_FORM_WIDGETS to mixins, moved password length check to validator, replaced inline drag-drop with shared makeSortable, added apiGet helper, added populateSelect helper, added handleFetchResponse, moved toast style to CSS
5. 基础设施封装：创建 redirect helpers、扩展 paginate_queryset 返回 page_range、重组 urls.py 使用 include、提取 STORAGE_DIR/LOGS_DIR 常量、合并模块扫描循环、修复 health.py 硬编码版本号、清理 config.env 重复行、优化中间件白名单逻辑、数据驱动旧路径重定向
6. 第三期全面封装重构：116+项完成。视图层：JsonResponse→json_success/json_error统一(14文件)、_error_response工厂(4视图)、_run_check健康检查(7try块)、_parse_page_params(2重复)、_get_user_or_404/_protect_admin(users.py)、_require_fields/_get_taxonomy_item_or_404(taxonomy.py)、_require_param(4参数验证)、@api_get_view/@api_post_view/@admin_post_view复合装饰器(13处)。服务层：SingletonMixin/CachedServiceMixin创建、BaseService扩展get_or_raise/get_first/safe_execute/update_fields/clean_str、CronTask属性自动生成(4任务→3移除重复)、success_response/error_response标准化(4服务)、SettingsService扩展parse_json、retry_with_fallbacks(3网络请求)。模板层：frame_sidebar_base(7框架)、pagination自驱化(7调用)、创建8个新include(card_section/module_card/empty_state/form_switch/nav_pills/entry_card_grid/form_errors/stat_card)、22模板采用。CSS层：10+模式从8主题提取到base.css(admin-sidebar/accordion/btn-info/welcome-title/navbar/login-btn/dropdown/font-family/transition/alert/badge)。JS层：拖放合并→makeSortable、apiGet统一4GET+addErrorHandling、populateSelect消除3重复、setupGlobalAjaxError集成、toast样式移至CSS。表单层：BootstrapFormMixin推广到所有8表单、EmailCleanMixin/UsernameCleanMixin/UserAwareFormMixin、_USER_FORM_WIDGETS共享、密码长度检查合并到validator。基础设施：core/utils/views.py(redirect_with_error/redirect_with_success)、paginate_queryset返回page_range、settings.py扫描合并+STORAGE_DIR/LOGS_DIR常量、middleware whitelist修复、config.env重复移除、健康检查版本硬编码修复。Ruff零告警+202文件格式化+makemigrations无变更
7. 全面Bug修复与封装重构：阶段一 HIGH(9项)：time_sync naive/aware修复、node_list分页、module_dispatch admin检查、customer else缩进修正、resident_info node判空、错误模板变量、modalTitle id、分页括号；阶段二 MEDIUM(19项)：logout_view require_POST、slug唯一性、transaction.atomic多处、except:pass加日志、require_POST导入导出、unique_together、phone长度、tablehead_extra super()、calc generic_visit、空格搜索修复；阶段三 封装重构(6项)：_build_customer_data提取、module_manage链接修正、cache_key命名空间、Node__str__ N+1、dispatch_uid；阶段四 LOW(3项)：JSONField default、cron.py logger导入、indent修复
8. 继续dev-plan-stage4-2: 完成Phase2剩余(items8-12直接查询改用Service, items16 read_log统一success, items17-19 customer事务, items20-21 module事务); Phase4封装(items47 install_module拆分, items48 get_frontpage_modules共享, items49 sync_type合并, items50 enable/disable抽取); Phase5(items52-53 @require_POST, items54 json try/except); Phase3 item22 clock docstring

# 2026-07-07 修改记录

1. 实施4项优化：1)AGENTS.md增加子Agent并行化规范; 2)创建docs/code_snapshot.md代码快照(15模型+30服务类+200方法+4遗留问题); 4)优化AGENTS.md Bug检查为仅默认服务层+视图层; 5)AGENTS.md增加增量Ruff扫描说明; 同步更新A08规范检查层级说明
2. 拆分 A04_模板开发规范.md：快速版（216行，保留规则+清单）和补充材料（734行，完整代码+示例）
3. 拆分 A08_Bug排查技术规范.md 为快速参考版(228行)和补充材料(1126行)
4. 拆分 A02_模块技术规范.md 为快速参考版(232行)和补充材料版(872行)
5. 拆分 A05_Python代码开发规范.md 为快速参考(265行) + 补充材料(1838行)，保留完整内容
6. Token优化：progress裁剪+4大规范拆分为quick/补充材料+快照分层+模块快照+阅读指南+自动生成快照脚本
7. Token优化第二轮：B05/B06压缩+模板继承索引+update_progress自动归档+清理.bak
8. Token优化第三轮：开发规范压缩+A03/D01 quick版+现有模块精简
9. View refactoring: taxonomy helpers extraction (169→158), customer create/edit dedup + paginator fix (327→294), importexport decorator swap (19→17)
10. 拆分了 ModuleService(921行) 为4个类：ModuleRegistryService(721行)、ModuleDependencyService(86行)、ModuleTaxonomyService(90行)、ModuleService facade(11行)；使用多重继承维持向后兼容；修复循环导入使用惰性导入
11. Service layer refactoring: PermissionService role check simplify, LogService _log_event helper with 7 methods simplified and top-level aliases removed, NodeService inherits BaseService with get_by_id/delete_node removed, NodeTypeService _get_node_type_or_none helper, __import__ replaced with import_module across views and dynamic_import_view utility created
12. 提取 nav_item.html 宏，重构 7 个 frame 模板的侧边导航栏；检查 8 个模板的内联 JS（均含模板变量，不可抽取）
13. 全面代码检查和封装重构：修复7个Bug+常量集中+ModuleService拆分+服务层重构+视图去重+导航宏+URL缓存TTL优化
14. Fix 8 bugs: dynamic_import_view 'modules.' prefix, sample_data_service customer_cn import crash, _load_module_info 'id' validation, dead except handlers, module_dependency public API, importexport login_required_json, users.py exception leak, dead code cleanup
15. Fix 6 real bugs in ruff report: unused import/variables, missing import in get_dependency_chain, unused loop variable
16. 修复：时钟卡片 Invalid Date（JS 访问 data.data.timestamp）; 修复：链接卡片不显示（默认导航卡片回退）
17. 修复：链接卡片不显示 - nav_cards_area.html 中 makeSortable 在 FFE 未加载时立即执行导致 IIFE 中断
18. 修复：链接卡片拖动一次后失效 - onNavCardDrop 改用直接 DOM 交换而非重建
19. 修复：绿岛森林(kajima)主题按钮字体黑色问题 - 修正 --text-inverse 变量名
20. 统一所有8个主题的 btn-secondary 样式，跟随各主题 --text-muted/--text-secondary/--text-primary
21. btn-secondary 改用 color-mix 方案，混合主色60%白作为辅助色
22. btn-secondary 加入 frame.css 的 border: none，尺寸与其它按钮一致
23. 橙红(savawoku)主题：修正 --text-inverse 变量名，btn-primary hover/active 添加白色字体
24. 踊/梵紫/靛蓝/中国红主题：修正 --text-inverse 变量名，补齐 btn-primary color
25. 客户列表查看按钮图标从 bi-eye 改为 bi-search
26. 客户列表查看/编辑/删除三个按钮统一为 btn-primary 风格
27. 客户列表操作按钮放大1.5倍
28. 客户列表操作按钮改为圆角正方形
29. 操作按钮图标改为粗体
30. 默认主题 btn-primary normal 色改为 #f0f0f0
31. 修复 WhatsApp 模块 5 个 bug：slice过滤器、batch未定义、template_ids顺序、url()路径、api分页内存
32. 修复 whatsapp 模板 url() 命名空间为 modules:whatsapp:

# 2026-07-08 修改记录

1. 创建 stage5 文档：01_第三批次修复计划（22项）和 99_暂缓变更记录（7项大规模变更）
2. 执行 stage5/01 计划全部22项：修复API装饰器、数据库配置、模块定义、分页统一、导入优化、代码注释等
3. 执行剩余计划：记录wontfix、修复urls宽泛except+缓存失效、创建syncmodules命令+自动注册
4. 清除git历史为单commit，强制推送到GitHub
5. null→blank 迁移（23字段/7模型）+ marketplace 备份保护 + 暂缓文档更新
6. 导入引擎钩子修复 + backfill_customer_codes 命令
7. 客户数据回填：顺序编码方案（cc格式）覆盖3098条；CustomerService 新增 _generate_unique_code()；服务层创建/导入路径统一使用；回填命令精简为调用服务层；stage5计划文档同步更新
8. 应用 core.0018 （核心模型 null→blank）和 customer.0004 （CustomerFields null→blank）数据迁移
9. 修复 WABridge 连接：清理停滞的菜单进程，重新启动 wabridge 服务（端口3000）
10. 修复号码验证功能3个Bug：(1)含括号/空格/EXT的号码不再被跳过WABridge检测，先清理再判断；(2) check_phone() try/finally保障连接关闭；(3) onWhatsApp空结果确认返回False，节省无效重试
11. 验证日志：新增error结果类型（全失败保持has_whatsapp=None）；check_phone异常返回错误对象；前端渲染异常说明+客户名称截断16字+error badge
12. 号码检测页新增'重置全部验证标记'按钮+确认弹窗+api/reset-check/端点
13. runwabridge启动前自动清理超5天session文件（本次清理47个过期文件）

# 2026-07-09 修改记录

1. 创建 LINE 模块实施计划文档 docs/stage5/02_LINE模块实施计划.md
2. 修复LINE模块实施计划的7个严重+5个中等问题
3. Stage5-第四批次: 修复3个P0+11个P1+10个P2+10个封装重构; 删除core/views.py死代码、抽取IsActiveMixin、修复字典序bug、import_row字段映射、N+1查询优化等
4. R2修复: change_password缺失@login_required+handle_password_decorator崩溃; datetime.now→timezone.now; 修复tools_dashboard.html坏URL; 消除_get_node_type_or_none重复; update()复用FIELD_MAPPING
5. 创建 docs/stage5/05_全面封装重构计划_SML.md：34 项（S10 + M轻16 + M重7 + L1），预估 ~170min
6. S5: settings.py COMMON_ROLES 常量替换 + 修复缩进
7. M轻 批次A: M1-M5 共享函数抽取(csv_response, _read_log_file, _module_to_dict, update_fields, build_filter_summaries)

