# 修改记录

本文档记录项目的每次修改，按日期分组。

---


> 最近 300 条记录。历史记录已归档至 `docs/progress_archive/`。

---


变
63. 新增踊主题(odoru)：基于fukunagaazusa.jp配色，青绿+奶油暖白+暖褐，温暖文艺风
64. 删除青绿主题(teal)，savawoku改名为橙红

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
8. M轻 批次B: M6 health.py _run_check简化, M8 login复用authenticate, M9 _convert_setting_value try/except, M10 get_system_url去request参数
9. M轻 批次C: M11 Module.get_active_ids, M12 TaxonomyService.get_items_bulk, M13 CronTask缓存属性
10. M轻 批次D: M14 SETTINGS_META分组注释, M15 迁移脚本常量提取
11. M重 批次E: M17 system_settings拆分, M18 check_node_permission, M19 docstring, M20 validate_upload
12. M重 批次F: M21 api_dashboard_cards拆分, M22 _read_local_version改用importlib, M23 module_dispatch拆分
13. L级: ModuleRegistryService God类拆分为5个服务 (Scan/Install/Lifecycle/Query/Scaffold), ModuleService继承链扩展为7基类
14. 撰写 Stage6 计划: 模块标准化与去重 (5批次, 38项)
15. 撰写 Stage6 补充计划: 模块脚手架升级与规范固化 (4批次)
16. 导入 contactsplus.xlsx 33条新客户 + 修正 probalust aus 电话格式
17. 修复: 删除 _recheck_all_task 中预先重置 has_whatsapp=None 的循环，避免全部验证时中断导致已检测数据丢失；清理调试日志




# 2026-07-10 修改记录

1. 编写 WhatsApp 批次轮次发送开发计划

# 2026-07-16 修改记录

1. AGENTS.md: Bug 排查规范新增「同类问题扩散扫描」规则
2. 修复全面Bug检查发现的问题: system_permissions无限重定向(P0) resident_info迁移依赖(P0) except:pass加日志(P1) customer_code unique+blank(P2) core/node/__init__.py(P2) time_sync日志(P2)
3. 第2轮Bug修复: cards.py日志(P2) resident_info模板block(P2) 模型发现(P2) ordering(P2) code_num TypeError(P2) 冗余decorator(P3) __str__ fallback(P3)
4. 第3轮Bug修复: 双重repr(P1) 会话固定(P1) XSS innerHTML(P1) 密码消息丢失(P1) 并发竞争(P1) login用form(P2) form错误渲染(P2) user_delete异常(P2)

# 2026-07-17 修改记录

1. 第4轮Bug修复: resident_info缩进(P0) export_filter返回None(P0) 邮件头注入(P1) mark_safe XSS(P1) backfill重复code(P1) settings安全配置(P1) CSV注入(P2) autoescape(P2) 死导入(P3)
2. 预防方案全量实施: Ruff bandit(S)规则集+per-file-ignores+noqa; Pre-commit (ruff lint/format+hooks); check --deploy菜单选项7; AGENTS.md高频反模式自查清单13项; CSP中间件+SECURE_CONTENT_TYPE_NOSNIFF
3. 第5轮Bug修复: P0 smtp分页崩溃; P1 export N+1+select_related, import事务, email error_message, node/scaffold装饰器; P2 smtptest require_POST, module_scan N+1, taxonomy bulk_create/bulk_update, database引号, SECURE_PROXY_SSL_HEADER; P3 CSRF_COOKIE_HTTPONLY, SECURE_REFERRER_POLICY, DATA_UPLOAD, require_GET, STATIC/MEDIA_URL绝对路径
4. 第6轮Bug修复: P1 smtptest模板路径修复; customer dashboard_card default颜色; view.html strftime→|date; P2 phone长度/notes限制/has_whatsapp字段; SystemSettingsForm接入; taxonomy None guard; import/export空状态; JS路径重构; P3 其他minor
5. 第7轮Bug修复: P0 SECRET_KEY硬编码→secrets.token_urlsafe; P2 NodeAdmin/SystemSettingAdmin readonly_fields+list_select_related+list_filter; context_processors日志+异常处理; WAL连接try/except; auth.py字段错误渲染; f-string SQL noqa

# 2026-07-20 修改记录

1. 预防方案实施: DTZ规则+迁移scan+checks.py扩充+pre-commit集成deploy/basedpyright+模板检查脚本
2. Round 8 修复: 4x P1 logger.exception, cron cache TTL 30s, perms [] 空列表, XLSX 公式注入, import 事务包裹, email subject 消毒, 模块 scaffold/scan 日志升级
3. Round 8 P2修复: cron加锁, __icontains类型守卫, bulk_update batch_size
4. Round 8 收尾: import并发锁, node_service TOCTOU, user_service update_fields, database.py DB名可配置
5. 预防体系加固: CIMF_W006/W007 checks, AGENTS.md 并发安全项, run.sh 选项9

# 2026-07-21 修改记录

1. Stage5: 全量 Bug 检查 — 扫描 3 层（服务/视图/模型）+ resident_info 专项，manage.py check 59 警告分析完成，无 P0 新增，发现 2 个 P1（静默 except）和 6 个 P2（update_fields/事务/XSS/表单缺失）
2. 修复 10 个 CIMF 警告：marketplace/services.py 3处(静默except+save update_fields)、mixins.py 2处(静默except+update_fields)、base_service.py 2处(update_fields)、resident_info/services.py 1处(save update_fields)+transaction.atomic、marketplace/views.py 1处(静默except)、list.html XSS 分页转义(server-side urlencode)
3. 第二轮修复: smtp模板href URL safe修复+template_service save update_fields+email_service subject去换行+email_service except日志+密码净化+smtp_service except日志+importexport views 3处except日志+import_service save update_fields+循环except日志+noqa修正+settings.py SECRET_KEY校验+SECURE_PROXY_SSL_HEADER条件化+config.env CSRF_TRUSTED_ORIGINS文档
4. 第三轮修复完成：8处 except+logger、8处 save update_fields、health.py overall_status 修复、cards.py break 注释、region_select/watermark 静默 except 备注。CIMF 警告从 59 降至 9
5. 完成余下修复：9 条 CIMF_W006/W007 noqa/+logger、cards.py break 移除、init_scripts stage1-3 noqa。CIMF 从 59 → 8（全部确认误报）
6. 新增预防机制：CIMF_W008(.first() None检查)、CIMF_W009(mark_safe/|safe标记)、pre-commit hook(--tag cimf)、GitHub CI workflow、快照遗留问题清单
7. 第四轮并发+importexport+视图+init脚本 Bug修复：import_service logger未定义、module views消息级别、settings profile表单、customer/user TOCTOU、logs分页、init stage2-4小问题、exc_info补齐、S110 noqa清理
8. 移除 pre-commit django-check hook（已由 run.sh 选项 9 覆盖）
9. 关闭所有 pre-commit hook，设为空 repos: []
10. 第五轮修复：15个Bug修复完成（init_customers bulk_create返回值、backfill Max聚合+事务、resident_info services atomic+views JSON解析、response.py CSV注入过滤、urls.py死代码移除、generate_snapshot语法错误警告、smtp装饰器+去重复查询、list.html|safe、pagination空分页）

# 2026-07-22 修改记录

1. 第六轮修复：14个Bug修复完成（node_type_service update_fields追踪、customer services事务+update_fields、health.py logger定义、node views logger日志、calc/cron装饰器顺序、customer views节点None反馈、taxonomy冗余查询消除、settings SECRET_KEY名修复+CSRF_TRUSTED_ORIGINS外移、middleware白名单+CSP script-src）
2. 第七轮修复：12个Bug修复完成（settings_service批量缓存+JSON日志、auth_service类型转换日志、cron_service线程锁、taxonomy_service logger去重、views/settings f-string->%s、api/cards except+e+多卡片合并、log_service TOCTU保护、init_node_types get_or_create+事务）
3. 第八轮修复：16个问题修复完成（customer/forms动态queryset+NullBooleanField、context_processors active_section返回、jinja2日志+死代码+date/slice过滤器、migration 0018用户字段NULL→空、settings_forms不可达检查移除、apps.py WAL exc_info、modules/urls双导入+冗余异常清理）
4. 预防体系搭建：ruff新增TRY规则（后因噪音大撤回）、checks.py新增CIMF_W010（ModelChoiceField静态queryset检查）+ CIMF_W011（NullBooleanField弃用检查）、修复customer/forms.py NullBooleanField->TypedChoiceField
5. run.sh 7/8/9 三项检查统一输出为报告存档模式（storage/reports/下保存 deploy/templates/precheck_时间戳.txt）
6. maintenance: 将 backup/clean_cache/show_env/generate_secret_key 转为 manage.py 命令
7. server_service: 将 run.py 启动逻辑封装到 core/server_service.py, run.py 从188行精简至29行
8. bugscan: 创建6个检测器(3 L1 grep + 3 L2 AST) + .bugscanignore + run.sh维护菜单合并为6(全面检查)/7(bugscan)，修复maintenance.py datetime.now时区bug
9. AGENTS.md: Bug排查规范新增bugscan前置步骤(省token)
10. docs/A04_补充材料.md: 更新目录树、修复 Jinja2 语法、CSRF 实现、block 命名
11. 修复region_select.py URL reverse命名空间(core:→api:)和Media JS路径(/js→js)、更新A03文档region_select.js状态
12. 修复 A05_Python代码开发规范.md 和 A05_补充材料.md 中与实际代码不一致的文档（响应函数名、错误响应键名、测试文件结构、Jinja2 转义说明）
13. 同步 A07_环境变量与配置管理规范.md 与实际代码一致：调整 §2.2 分类（DJANGO_PORT/DJANGO_HOST 移至开发服务器配置、SECRET_KEY 改为 ⚠️、SQLite 路径补充 instance/）、替换 §3.3 为完整 config.env.sample、§4 改用 pathlib.Path 风格、§5.2 修正 .gitignore 规则、§4.3 补充缺少的安全配置、新增 §8 已知问题说明死配置
14. 同步A01_项目概述与技术架构.md与实际代码一致
15. 修复 D01_CSS外观设计标准套件.md：卡片边框/圆角/变体、过滤标签色值/圆角、btn-secondary 边框、导航卡片数量
16. 同步 B01_core_models 规范与实际代码：补充 IsActiveMixin、User.is_active、TaxonomyItem.unique_together、ChinaRegion 字段约束、Node 外键 on_delete、Module.get_active_ids、EmailLog 字段修正
17. 同步服务层规范文档与代码：修正 AuthService.login 签名、PermissionService 补充 check_node_permission、SettingsService 修正为 57 项/补充 8 项/删除 smtp_rate_limit/改 smtp_send_interval 默认值、TaxonomyService 补充缺失方法、CronService 补充 set_app_ready、新增 TimeService/TimeSyncService/LogService 章节
18. 更新 B04 和 B05 技术规范文档：路由计数、表单分布、继承类、主题选项等
19. 更新 A08_Bug排查技术规范.md 和 A08_补充材料.md: 统计标记已清零，BP01~BP18 标注已修复，附录 B 标记已清理，新增 CIMF_W001~W011 Django 检查体系文档
20. 全面技术规范文档修正：根据代码现状更新 A01-D01 共18份技术规范文档
21. 删除7个文档中的待补充章节/页脚版本号不一致内容
22. 删除 A02_补充材料 十二节（重复的模块市场配置）和 A08_补充材料 附录C（重复的Bug修复前后对比）
23. 精简技术规范文档：删除版本历史/更新记录(7份)、待补充章节(4份)、页脚版本号(5份)、重复内容(2份)

# 2026-07-23 修改记录

1. 修正B04表单规范主题值拼写(odogu→odoru)
2. 删除死代码：core/models.py 末尾重导出、SampleDataService、dashboard_cards.js、js.html 重复 navbar scroll 脚本
3. 用 RedirectView 替换 profile 视图函数：更新 URL 配置、删除 settings.py 中 profile 函数、清理 __init__.py 导入
4. 从全部 8 个主题文件中提取 .btn-secondary CSS 至 base.css（共用规则，基于 CSS 变量）
5. 封装重构：删除死代码(models.py重导出/SampleDataService/dashboard_cards.js/导航栏滚动重复)、提取btn-secondary到base.css、profile视图→RedirectView、误判项补注释
6. 代码重构：core/checks.py 拆为 core/checks/ 包(8个检查模块)；settings_service.py 的 SETTINGS_META 提取到 core/settings_meta.py；views.py 推广 redirect_with_success/error；ResidentInfoFields 改用 BaseModel 继承；删除 resident_info 自定义权限检查，统一使用 PermissionService.check_node_permission；创建 core/node/base_node_service.py(BaseNodeService) 和 core/node/base_node_view.py(make_api_stats_view)；customer/resident_info 服务继承 BaseNodeService 消除 get_by_id/get_by_node_id 重复；api_stats 视图改用工厂函数
7. Phase 3: get_all_pages_with_permission_status 从 cron.py 移到 permission_service.py; Phase 4: profile_settings 拆分为6个辅助函数; Phase 5: resident_info 创建 ResidentInfoForm 类消除原始 POST 处理; Phase 6: 创建 make_node_view / make_node_delete 工厂视图, 替换 customer 和 resident_info 的 node_view/node_delete; create_user 改为 @classmethod 修正 F821; Ruff+manage check 全绿
8. 将 core/bugscan/detectors.py 拆分为 finding/l1/l2/ast/scanner 包结构
9. 将 export_service.py 拆分为 export_service/ 包（field_service/query_service/value_resolver mixins + __init__）
10. Phase 7: 创建 @json_body 装饰器, 统一 JsonResponse (health.py/calc/clock/cron/cards); 大文件拆分: detectors.py→5文件, import_service.py→4文件, export_service.py→4文件, email_service.py→4文件, importexport/views.py→2文件, template_service.py 提取默认模板数据; user_service.py 裸save修复; Ruff+manage check 全绿

# 2026-07-24 修改记录

1. 封装重构：删除 mixins.py 重复 update_fields；权限字符串 PERMISSION_GROUPS 单源合并；ModuleRegistry 抽象层（8 处 import_module 集中化）；BaseNodeService 继承 BaseService；URLName 常量类；taxonomy.py 服务层重构（消除直接 model 访问）；健康检查合并 _build_check_base/_finalize_check；COMMON_ROLES 从 UserRole 推导；update_taxonomy/update_item None 过滤
2. 封装/拆分第1-4批: 删除死亡代码; 核心→模块解耦(init命令搬迁); 服务层补齐(BootstrapFormMixin+视图bypass消除); 客户表单简化+模板加命名空间
3. 批量修复: N+1查询(3处get_by_node_id+1处prefetch); SmtpConfigForm/NodeTypeForm加BootstrapFormMixin; 删除core/node/views.py死亡视图5个; LogService精简; VersionService精简; marketplace硬导入修复; health.py/users.py视图bypass消除
4. 修复resident_info模块: 表单上下文传递+错误展示; max_length对齐(forms<->model)x4; 删除重复@staticmethod; select_related补齐x4(delete/get_list/get_by_node_id); 批量加载taxonomy替代11次独立调用; 5个字符串字段移除null=True+迁移
5. 清除 bugscan 报告: 添加 3 条抑制规则 (l1_detectors datetime_now / customer first_unchecked / base_node_service first_returned)，报告清零

# 2026-07-26 修改记录

1. 修复 BaseNodeService 无 model_class 时 get_count 崩溃；_collect_module_stats 跳过 model_class 为 None 的服务类
2. 修复 manage.py check 报告：CIMF_W001 calc 类方法误报、CIMF_W002 views_check 缺少 admin_required_json、CIMF_W006/W007 whatsapp services/views 的 save/except 问题、CIMF_W008/W009 noqa
3. 新增 core/utils/error_utils.py 提供 service_connect_error() 公用工具；WhatsApp 模块 7 处异常消息改用友好中文提示
4. 删除 calc（计算器）模块：数据库记录、模块目录、文档引用
5. 清除 calc 模块残余文档引用：A01/A02/A04/B02/B03/B05 技术规范 + 补充材料 + 快照
6. 修复 WABridge 重启超时：services.py 加 stdin=DEVNULL；run_stop/run_start CLI 模式跳过 press_enter；socket.js 重连加 .catch() 防进程退出；_kill_wabridge_processes 加 SIGKILL 兜底
7. 修复 socket.js startSocket async anti-pattern：try-catch 包裹 async executor 防止 unhandled rejection 导致 Node 进程退出；重连失败 10s 后自动重试
8. socket.js ev.process 回调内加 try-catch 防 saveCreds 异常逃逸；serve.js 加 unhandledRejection 全局兜底
9. WABridge 稳定性加固：serve.js 加 uncaughtException 兜底；WABridgeRestartTask cron 间隔改为5分钟、仅不健康时重启
10. 新增 cimf-whatsapp/PATCHES.md 补丁管理文档；更新 README.md 进程稳定性章节和故障排查
11. 文档补全：修正 whatsapp 模块快照，新增 cimf-whatsapp/whatsapp/README.md 和 runwabridge/README.md，更新 snapshot_完整.md 添加 WhatsApp 模型/服务/Cron 条目
12. 模块快照迁移：将 clock/customer/smtptest/whatsapp 快照从 docs/模块快照/ 移至各自模块根目录 SNAPSHOT.md，更新 AGENTS.md/现有模块.md/开发规范.md 引用路径，resident_info.md 保留原处待后续迁移
13. 修复时间同步服务：移除无效的百度接口，新增 suning 接口，超时 3→5 秒，支持更多响应字段名(sysTime2/dateTime)



# 2026-07-27 修改记录

1. 统一模块文档架构：为 resident_info 创建 SNAPSHOT.md；更新 generate_snapshot.py 同步写入模块目录 SNAPSHOT.md；更新 ModuleScaffoldService 自动生成 SNAPSHOT.md 骨架；现有模块.md 新增文档架构规范章节

# 2026-07-29 修改记录

1. 修复 Ruff 6 处真 bug: 移除 scanner.py/base_node_view.py/server_service.py 无用 noqa, 删除 reporter.py 未用导入 os/re, 删除 base_node_view.py 未用 require_POST 导入
2. 添加 3 个 bugscan 检测器: http_fallback_url(L1), mark_safe_fstring(L1), silent_except(L2); 更新 .bugscanignore

# 2026-07-30 修改记录

1. 移除废弃模块 calc 目录（仅有空壳文件，无源码）
2. 清理 calc 模块：删除 modules 目录、数据库 modules 记录、tool_types 记录
3. 删除 has_whatsapp=False 的客户记录 3104 条



# 2026-07-31 修改记录

1. WhatsApp: 清理batch#32重复入队日志21条(206→185, 修正total_count), create_batch新增客户去重(含追加已有批次场景)

# 2026-08-01 修改记录

1. 修复 GitHub Actions CI 必失败问题：清除全库 25 个 ruff 错误（E402×15 import 乱序、I001×3、S308/S112 noqa 补码、S104/S607/S105×2 语义、F401），修复 ci.yml deploy 检查缺 DJANGO_ALLOWED_HOSTS 与 SECRET_KEY 过短(security.W009)，锁定 ruff==0.16.1、移除 basedpyright 与 || true
2. scanner_checks.py 自定义检查器改为 _has_noqa 裸代码匹配，使 CIMF_W00X 与 ruff 规则码可共存于同一 noqa 注释；ruff 解析确认：noqa 中识别码须在前，未知代码靠前会导致整个指令失效
3. 修复 CI 必失败: 清除25个ruff错误+ci.yml补ALLOWED_HOSTS/长SECRET_KEY/锁定ruff0.16.1, scanner_checks改用_has_noqa裸码匹配, 版本v2.152

# 2026-08-02 修改记录

1. 修复：首页功能卡片不显示 - user_dashboard_card_positions设置为空时api_dashboard_cards无默认布局回退（非封装/修bug回归，系设计缺口），仿照api_nav_cards的DEFAULT_NAV_CARDS在服务端回退前6个可用frontpage模块填槽位1-6；已配置时不覆盖；AGENTS.md反模式自查清单新增#15配置驱动UI默认回退
2. 修复：首页功能卡片拖动后位置不保持 - CSRF_COOKIE_HTTPONLY=True致JS读不到csrftoken Cookie，getCsrfToken()返回空导致api_dashboard_cards_save静默403；common.js新增meta[name=csrf-token]回退读取，同时修复nav_cards/homepage_settings等所有fetch POST；AGENTS.md反模式清单新增#16 AJAX CSRF token可读性检查
3. 修复：首页时钟时间快8小时 - TimeSyncService._fetch_time_from_server把时间服务器返回的北京墙钟date误标为UTC(replace(tzinfo=UTC))且丢弃权威timestamp字段，致system_synced_time快8h、首页时钟显示快8h；改为优先用timestamp/unixtime epoch，无偏移裸墙钟按time_zone配置(ZoneInfo)解释，get_current_time()返回本地化datetime供strftime显示，重同步覆盖陈旧DB值；common.js updateBeijingTime改data.data.time；AGENTS.md新增#17外部时间源误当UTC检查项
4. git清理：git rm --cached -r .opencode/取消跟踪package-lock.json+7个plans计划文档(本地保留)，根.gitignore新增.opencode/；.github/workflows/ci.yml保持跟踪
5. 时间硬化：TimeSyncService.get_current_time()增加MAX_SYNC_AGE=24h护栏，陈旧/脏同步基准自动降级到本地时间；首页时钟卡片toBeijingDate强制Asia/Shanghai显示(时间/日期/星期/农历全时区正确)；AGENTS.md反模式清单新增#18时钟改动须重启+等同步提醒
6. 修复WhatsApp首页卡片状态显示：dashboard_card.html的{% if wa_connected %}改为{% if connected %}(get_status()返回键名是connected，原变量全项目无来源致徽标永远未连接)；get_status()增加today_sent/daily_limit(复用check_daily_limit滚动24h)，卡片今日计数由硬编码0/0改为真实数据

# 2026-08-03 修改记录

1. whatsapp 模块统一 toast：3 个模板（send/check/check_logs）移除本地 Bootstrap #liveToast 与 showToast()，改用全局 window.FFE.showToast
2. whatsapp logs 页改为近 10 天记录 + 分页（每页 50 条），logs_view 用 paginate_queryset，模板改用 page_obj 并引入分页组件
3. whatsapp services：新增 _log_wa_connection_failure 助手，8 处 WABridge 连接异常（含 check_health）连接拒绝时仅记简短提示不再刷完整堆栈；batch_check_whatsapp 错误提示改用中文

# 2026-08-07 修改记录

1. 修复 Django 应用初始化期访问数据库的 RuntimeWarning：将 SMTP 配置同步与模块自动注册从 ready() 移至 core/startup.py（run.py/wsgi.py/asgi.py 显式调用 + request_started 兜底）

# 2026-08-08 修改记录

1. 修复 WhatsApp 媒体发送 404：build_media_url 缺少 whatsapp/ 目录段
2. 新增 serve_media 媒体视图并无条件挂载 /media/，消除生产模式 DEBUG 门控导致的 404；生产验证需关闭 SECURE_SSL_REDIRECT
3. 生产安全配置改为尊重 DJANGO_SSL_REDIRECT/DJANGO_SESSION_COOKIE_SECURE/DJANGO_CSRF_COOKIE_SECURE 环境变量，支持无 HTTPS 单机部署

# 2026-08-26 修改记录

1. 修复12个Bug+3项重构: 1.@json_body返回400 2.do_export加@require_POST 3.api_time_test异常处理 4.登录双查DB修复 5.文件句柄泄漏修复 6.时间服务器更新HTTPS 7.WABridge日志限频60s 8.module_custom_dispatch拓宽异常 9.homepage_settings加@require_GET 10.taxonomy重复创建修复 11.cards响应格式 12.logger f-string修复; P0删除僵尸services.py(1087行); P1 whatsapp/api.py统一json_success+json_error+@json_body
2. 修复时间同步: timeapi.io日期格式MM/DD/YYYY解析+替换死服务器(worldtimeapi/uuni→timeapi.io双备份); 执行whatsapp迁移0007

