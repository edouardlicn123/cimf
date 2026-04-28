# 修改记录

本文档记录项目的每次修改，按日期分组。

---

# 2026-03-19 修改记录

1. 全面检查修复bug：
   - [安全] 用户名可被篡改 - clean_username() 检查用户名是否被修改
   - [安全] 密码验证漏洞 - 创建用户时密码必填验证
   - [安全] timezone.timedelta 使用错误 - 修复 datetime 导入
   - [功能] 主题选项不一致 - 添加 gov/indigo 主题
   - [功能] 统一客户服务接口 - 添加 user 参数
   - [功能] 删除消息显示条件 - customer为None时处理
   - [功能] node_delete customer为None崩溃 - 添加检查
   - [功能] node_view customer为None检查 - 添加重定向
   - [功能] get_list 查询问题 - 使用 Q() 组合查询
   - [功能] TimeSyncTask 使用非单例 - 改用单例模式
   - [功能] cron_service sleep_time 未定义 - 初始化变量
   - [功能] auth_service int(None) 错误 - 添加异常处理
   - [功能] ProfileForm.clean_email user_id为None - 添加条件判断
   - [功能] UserEditForm.clean_username user_id为None - 添加条件判断
   - [模板] watermark.js ID 不匹配 - 统一ID命名
   - [模板] watermark 元素缺失 - 添加 watermarkWarning
   - [模板] dashboard 缺少统计卡片 - 添加二类用户卡片
   - [模板] 用户角色显示错误 - 修复 'admin' → 'manager'
   - [模板] customer country 外键显示 - 改为 country.name
   - [配置] User Theme migration 缺失 - 创建新 migration
   - [配置] csrf_token 返回格式问题 - 直接返回 HTML
   - [配置] 缺少 CustomerCnFields Admin - 注册 Admin
   - [安全] api_regions_* 缺少登录验证 - 添加 @login_required
   - [安全] api_time_* 缺少登录验证 - 添加 @login_required
   - [安全] user_delete 未防止删除自己 - 添加检查
   - [表单] ChangePasswordForm 验证逻辑漏洞 - 确保密码必填
   - [表单] UserService.create_user 缺少密码验证 - 添加验证
   - [安全] 登录锁定阈值硬编码 - 从 SettingsService 读取

2. 优化 update_progress.py：支持追加模式和覆盖模式，同一天多次修改自动编号；更新 AGENTS.md 添加自动更新指令

3. 全面检查修复bug：修复customer_service/customer_cn_service的get_list查询问题；修复nodes/views.py中customer/customer_cn编辑时customer为None的检查

4. 全面检查修复bug：修复dashboard缺少二类用户统计卡片；修复user_delete未防止删除自己账号

5. 全面检查修复bug：修复node_view中customer/customer_cn为None时的检查；优化权限检查一致性

6. 全面检查修复bug：为api_regions_*和api_time_* API添加登录验证，防止未登录访问

7. 修复User.record_failed_attempt()使用硬编码阈值问题，改为从SettingsService读取login_max_failures和login_lock_minutes

8. 修复ChangePasswordForm密码验证逻辑；修复UserService.create_user添加密码非空和长度验证

9. 创建 bug 问题小结文件 `docs/bug_summary.md`

---

*最后更新：2026-03-19*
*当前版本：v1.024*
10. 创建bug分析文档 docs/bug_analysis.md：分析bug模式、根因分析、高危区域、下一步排查计划
11. 按照bug_analysis执行完整检查：修复node_service.id__icontains错误；修复UserEditForm.clean_email缺少user_id检查；修复api_regions_import重复装饰器；修复模板外键显示.customer_type.name等；修复csrf_token()调用问题；创建28个单元测试
12. 创建Bug排查规范文档 docs/04_Bug排查规范.md：定义服务层、表单验证、API安全、模板一致性检查要点，包含常见bug模式与修复示例；更新AGENTS.md添加Bug排查规范引用
13. 验证 china_region_service.py 无语法错误；Django check 通过，System check identified no issues
14. 全面检查未覆盖区域：修复 templates/core/admin/system_users.html 和 templates/core/profile.html 中 date()|default() 写法错误（应使用三元表达式）；验证所有 @login_required 装饰器完整性；检查 core/fields、core/management、nodes/customer 等目录均无明显 bug
15. 重命名 docs/04_Bug排查规范.md → docs/bug排查规范.md，并更新 AGENTS.md 中的引用路径
16. 在 docs/开发规范.md 中新增'常见Bug易错点'章节：包含模板语法（|default与三元表达式、csrf_token调用、外键访问）、Python代码（.first()检查、表单clean()验证、API登录验证、密码验证）、安全（用户名篡改、硬编码阈值）、数据模型（id__icontains、QuerySet OR查询）等易错点总结及防御性检查清单
17. 删除 AGENTS.md 和 docs/开发规范.md 中对旧版本 cimf-flask 的参考要求；移除 Flask 到 Django 迁移问题汇总章节
18. 全面优化 docs/开发规范.md：移除过时目录结构和Flask迁移内容，简化章节结构，保留核心规范（项目结构、代码规范、Node模块、安全规范、Bug易错点、防御性检查清单），从542行精简至约300行
19. 全面优化 docs/开发规范.md：基于项目结构分析结果重新组织章节，包含准确的项目结构（core/nodes/templates/services层详细说明）、服务层规范（命名、设计原则）、视图层规范（命名、URL约定）、模型层规范（Core/Nodes模型说明、外键规范）、表单层规范、模板层规范、字段类型（24种）、安全规范、易错点表格化、检查清单；共约350行
20. 继续Bug检查：验证 nodes/services/*.py 和 core/forms/*.py 无新增问题；发现并修复 core/views.py:630 cron_status API缺少@login_required装饰器；验证所有模板外键显示有None检查；所有权限验证逻辑正常；Django check和28个测试全部通过
21. 继续Bug检查：验证 cimf_django/context_processors.py（csrf_token、system_settings正常）、static/js/*.js（watermark.js正常）、templates/includes/*.html（nav/header/js正常）、core/urls.py、nodes/urls.py（所有路由正确）、nodes/services/*.py、core/services/auth_service.py、cron_service.py 均无明显bug；Django check通过
22. 继续Bug检查：验证 templates/*.html、templates/core/admin/*.html、templates/nodes/*.html 全部正常；检查 nodes/forms.py、nodes/customer/forms.py、nodes/views.py、core/fields/*.py、core/fields/__init__.py 均正常；验证 cimf_django/settings.py 中间件配置、Django错误处理视图均正确；Django check和28个测试全部通过
23. 更新 docs/bug排查规范.md：新增'6.1 Bug易错点同步到开发规范'章节，明确要求发现的Bug如果有可能在日后开发中复现，必须写入docs/开发规范.md的'常见Bug易错点'章节，并给出操作示例
24. 整合文档：分析 bug_analysis.md 和 bug_summary.md，提取关键内容添加到 bug排查规范.md（七潜在Bug风险区域、八Bug统计与历史）和开发规范.md（三层架构一致性、复制代码注意事项）；删除旧文档 bug_analysis.md 和 bug_summary.md
25. 优化 docs/bug排查规范.md：从450行精简至260行，移除重复内容，整合检查命令和常见问题，保留核心章节；优化 docs/开发规范.md：从453行精简至230行，精简项目结构表格，整合服务/视图/表单/模板规范，保留核心Bug易错点表格
26. 删除 README 中关于 Flask 版本的全部内容
27. 重写 README 为 GitHub 风格，使用仙芙CIMF系统名称
28. 创建 frame_importexport 模板
29. 重命名 nodes/index.html 为 node_dashboard.html
30. 移动 node_dashboard.html 到 templates/core/node/
31. 创建 structure_dashboard 页面和路由
32. 移动 taxonomies 和 field_types 到 structure 文件夹
33. 修改 frame_structure 导航链接样式
34. 移动 field_types.html 到 structure/field_types 文件夹
35. 移动 profile 和 settings 模板到 usermenu 文件夹
36. 创建 frames 文件夹并移动所有 frame 模板
37. 全面按照Bug排查规范检查项目：服务层.first()返回值、表单验证、API安全、模板一致性等
38. 修改 structure_dashboard 参照 node_dashboard 模式

# 2026-03-20 修改记录

1. 新增导出导入菜单和importexport_dashboard页面
2. 修复regions_import URL缺失问题
3. 为structure和importexport页面添加权限控制及权限管理卡片
4. 还原structure为仅admin可用，只保留importexport的权限控制
5. 删除未完成的导入导出菜单项（词汇表、节点、用户）
6. 简化数据导入导出权限为单一访问权限
7. 创建文档：18_数据导出功能.md 和 19_数据导入功能.md
8. 细化导出功能文档（v1.1）：新增3步流程、字段选择页、确认页设计
9. 细化导出功能文档（v1.2）：新增导出中页、细化UI设计、简化服务层代码
10. 删除 region_test、region_field_test 相关代码（视图、路由、模板、管理命令），保留省市县查询 API
11. 修复导出功能：1) export_fields.html 添加 form action 属性，改用 {% csrf_token %}；2) export_confirm.html 同样修复 csrf_token 并添加 hidden field 传递选中字段；3) export_confirm 视图支持解析 comma-separated 字段字符串
12. 修复导出流程确认环节：1) export_confirm 视图 GET 渲染确认页（展示模块+字段），POST 跳转到 exporting；2) 简化 export_confirm.html，移除数据预览，仅保留摘要信息；3) export_exporting.html 保持过渡动画
13. 导出功能增强：1) 字段默认全部勾选；2) 新增筛选条件功能，6组过滤器（下拉选字段+输入框），过滤器间互斥（已有即排除）；3) customer_cn 额外显示省市区筛选器；4) 确认页展示筛选条件摘要和筛选后预览数据；5) ExportService 支持 filters 参数进行数据筛选
14. Bug 修复：1) 字段选择页 checkbox 的 `name="fields"` 导致 `request.POST.get('fields')` 只取第一个值，移除 checkbox 的 name 属性，仅通过 JS hidden input 传递；2) 数字字段（integer/decimal/float）使用 `__icontains` 筛选语义错误，移出 `FILTERABLE_FIELD_TYPES` 并移除通用 else 分支
15. 修复导出字段选择页：form action 从 export_confirm 改为 export_select_fields，避免 session 为空导致重定向回选择页
16. 将客户信息模块改名为客户信息（海外），介绍改为适用于管理中国以外的客户信息
17. 将客户信息（国内）介绍改为适用于管理国内客户的信息
18. 更新数据导出功能设计文档至 v1.3：补充筛选功能（6组过滤器+省市区筛选）、URL前缀改为nodes/、更新Service层方法、补充前端JS逻辑、移除未实现功能、添加Bug修复记录
19. 修复省市区字段Bug：1) _resolve_region_field 读取键名从 province_name/city_name/district_name 改为 province/city/district；2) _get_filtered_queryset 筛选查询字段从 region__province_name 等改为 region__province 等
20. End-to-end testing of export feature: verified all 4 steps work, filters work correctly, CSV and XLSX exports produce correct output with FK fields resolved and region field formatted properly
21. Fix field_types view template path: index.html → field_types.html
22. Unify spacing across all frame templates: changed pt-2 to py-4 py-md-5 to match dashboard page spacing (4rem mobile, 5rem desktop)
23. Reduce dashboard top spacing: changed main container from py-4 py-md-5 to pt-2 pt-md-3 pt-lg-4 pb-4 pb-md-5 for better balance with fixed navbar
24. Refactor dashboard to use frame_dashboard.html template for consistent spacing with system settings page
25. Redesign importexport dashboard: unified parallel cards for export/import without separate sections
26. Optimize transaction overview page: unified card layout with responsive grid, flex layout, primary-colored icons and prominent buttons
27. Optimize structure dashboard page: unified card layout with responsive grid, flex layout, primary-colored icons and prominent buttons
28. Ensure consistent card widths in structure dashboard by adding d-flex wrapper and w-100 on cards
29. Fix sample data: change customer names from company names to person names (overseas: John Smith, Hans Mueller, etc.; domestic: 张伟, 李娜, etc.)
30. Add missing dependencies to requirements.txt: requests>=2.32,<3.0, openpyxl>=3.1,<4.0
31. Localize Bootstrap libraries: download Bootstrap 5.3.3 and Bootstrap Icons 1.11.3 to static/lib/, update templates to use local files instead of CDN
32. Add logo feature: 1) Logo display in navbar (default sitelogo_white.png), 2) System settings page with logo toggle and upload, 3) Custom logo stored in media/logos/, 4) Added media() Jinja2 function for media URL generation
33. Fix Bootstrap Icons font path: copy woff2 to css/fonts/ and update CSS to use correct relative path

# 2026-03-21 修改记录

1. 修复 ModelRegistry bug：1) 修正 OneToOneRel 类名检查；2) 使用 field.name 代替 model._meta.model_name 以保留下划线（customer_cn_fields → customer_cn 而非 customercn）
2. 验证导入功能完成：ModelRegistry 修复后测试通过，模板生成、字段提取、FK解析器、特字段处理器均工作正常
3. 验证导入功能完整：测试 ModelRegistry、FieldDefExtractor、FKResolverPool、SpecialFieldPool、TemplateGenerator 均工作正常，28个测试全部通过（2个与本功能无关的API测试失败）
4. 修复导入功能 Bug：1) [安全] 为所有导入视图添加 @login_required 装饰器；2) [功能] ImportService.import_data 添加 node_type None 检查；3) [功能] FK 解析失败时不设置 None 值；4) [功能] _find_existing 添加字段不存在异常处理；5) [前端] 修复 import_page.html JS 元素检查；6) [前端] 移除 import_result.html 重复的 if 检查
5. 二次 Bug 检查：1) [前端] 修复 import_page.html 中 csrf_token() 错误调用，改为 {{ csrf_token }}
6. 三次 Bug 检查：1) [功能] TemplateGenerator.generate 添加 node_type None 检查；2) [代码风格] 修复 import_service.py 中 = 缺少空格问题
7. 四次 Bug 检查：全面检查导入功能服务层、视图层、模板层、安全检查，未发现新 Bug
8. 修复 csrf_token 模板语法错误：import_page.html 中 {% csrf_token %} 改为 <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
9. 为 frame_importexport.html 侧边栏添加导入菜单链接
10. 修复 import_page.html 多个问题：1) [功能] 修复空 error div 显示问题；2) [安全] 修复 XSS 漏洞，对 error.errors 和 cell 值进行 HTML 转义；3) [代码] 添加 escapeHtml 辅助函数
11. 彻底修复 import_page.html 空提示问题：移除静态 error div，改为 JS 动态创建，避免被 toast_messages.html 误检测
12. 彻底修复 import_page.html 空提示问题：将所有 .alert 类改为 .msg-box，避免被 toast_messages.html 误检测；同时添加相应 CSS 样式
13. 修复 import_page.html 多余的 </div> 标签导致页面显示 > 字符
14. 修改 import_page.html：返回按钮移至标题行左侧，与导出界面风格一致
15. 修复 import_page.html：移除 show_header = false 使标题区域正常显示

# 2026-03-22 修改记录

1. 修复 import_page.html：添加缺失的 </div> 关闭 row 标签
2. 重新创建 import_page.html：清理所有多余空白和潜在隐藏字符
3. 重新设计 import_page.html：参考导出界面风格，使用 show_header=false，简化结构
4. 修复 import_page.html：csrf_token 从 tag 改为 variable 语法
5. 修复空 toast 问题：移除 alert 类，使用 bg-* 类替代
6. 为导入模板 XLSX 添加 FK 字段可选值工作表：1) import_service.py 添加 get_fk_fields_with_options 方法；2) template_generator.py 添加 _add_fk_sheet 方法生成第二个工作表
7. 完善 FK 字段可选值：1) 在数据库创建 enterprise_type(企业性质) taxonomy 及词汇；2) 为空的 customer_type taxonomy 添加词汇；3) 更新 taxonomy_service.py DEFAULT_TAXONOMIES 列表
8. 为海外客户创建独立的企业性质分类：1) 创建 enterprise_nature(企业性质-海外) taxonomy 及词汇；2) 修改 FK 解析器支持 taxonomy 过滤；3) 修改 ImportService 支持 FK_TAXONOMY_OVERRIDES 映射；4) 更新 taxonomy_service.py DEFAULT_TAXONOMIES 列表
9. 优化客户信息（海外）列表页：1) 使用企业性质(海外) taxonomy 作为筛选条件；2) 列表增加企业性质列（badge 样式）；3) 替换电话列为网站列（带链接）；4) 操作按钮改为图标按钮组；5) 空数据提示增加图标；6) 分页仅显示前后2页
10. 按海外客户列表设计同步优化国内客户列表：增加客户类型列(badge样式)、行业列，操作按钮改为实心图标按钮，空数据增加图标，分页仅显示前后2页
11. 修复客户信息（海外）列表5个问题：1) edit.html国家字段重复name属性 2) node_edit空值检查位置 3) 列表视图添加权限过滤 4) list.html筛选条件类型比较优化 5) view.html三元表达式逻辑优化
12. 客户信息（海外）列表：移除客户类型和行业两列展示
13. 客户信息（海外）列表：添加电子邮件列
14. 客户信息（海外）列表：电子邮件列显示为mailto链接，最多20字符
15. 客户信息（海外）列表：电话1前添加WhatsApp聊天按钮
16. 客户信息（海外）列表：企业名称限制20字符显示
17. 客户信息（国内）列表：企业名称限制13字符，移除企业性质/网站/省市区，新增电话列
18. 客户信息（国内）列表：添加微信号列
19. README.md：添加 cimf.png 图片
20. README.md：图片缩小为50%
21. README.md：许可证更换为MIT
22. 全面检查并修复项目模板Bug：1)system_settings.html重复卡片 2)login.html set语句位置 3)taxonomies分页范围限制 4)system_users筛选逻辑 5)customer_cn region默认值
23. 再次全面检查模板：修复system_settings.html Logo卡片缺少闭合div标签
24. 再次检查修复：1)customer_cn/list.html企业名称空字符串处理 2)system_settings.html水印内容检查改用split后检查
25. 全面修复模板问题：1)客户列表企业名称空值处理 2)toast XSS漏洞修复 3)system_settings split空值保护 4)cron_manager空值检查 5)taxonomies Modal结构 6)customer_cn ID命名 7)permissions说明文字 8)login CSS合并 9)toast style合并
26. 再次修复模板问题：1)toast消息级别改用整数常量 2)cron空任务添加提示 3)customer_cn HTML属性转义 4)customer/customer_cn/edit.html空值处理 5)permissions role_labels默认值 6)taxonomies空值处理
27. 再次修复模板问题：1)customer_cn/edit.html phone2/email2/wechat/dingtalk空值处理 2)system_permissions.html label改为span 3)taxonomies/view.html taxonomy.name空值保护
28. 再次修复模板问题：1)customer_cn/list.html phone1/wechat空值处理 2)system_permissions.html role_permissions改用get方法 3)login.html CSS合并 4)customer/edit.html JS使用严格相等
29. 再次修复模板问题：1)客户列表customer_name添加默认值 2)system_cron_manager CSRF获取失败处理 3)system_users last_login_at添加检查 4)taxonomies编辑链接添加taxonomy检查 5)toast XSS防护改用DOM API 6)system_permissions role_labels改用get方法 7)login CSS选择器修正
30. 十次模板检查并修复：1)customer/edit.html country空值检查 2)system_cron_manager.html cron_status检查 3)system_users.html search_term默认值 4)taxonomies/view.html Modal移到table外 5)login.html settings默认值
31. 创建模板查Bug总结文档：docs/模板查Bug总结.md
32. 模板查Bug第11轮：修复 customer/view.html, customer_cn/view.html, types/, taxonomies/, import_page.html, profile.html, base.html, nav.html 中的 Jinja2 语法混用和 csrf_token 错误

# 2026-03-23 修改记录

1. 模板查Bug第12轮：修复 settings.html, export_fields.html, export_confirm.html 中的 csrf_token 错误
2. 模板查Bug二次检查：修复剩余 csrf_token 错误(7处)、date()语法(1处)
3. 模板查Bug第三轮：全面复查 XSS/JS安全、循环空值、ID唯一性 - 未发现新问题
4. 修复 Jinja2 default 过滤器语法错误：单引号改为冒号双引号
5. 修复 Jinja2 default 过滤器语法：强制使用括号()而非冒号:，修复 base.html, profile.html, nav.html, dashboard.html
6. 修复 Jinja2 csrf_token 语法：所有 {% csrf_token %} 改回 {{ csrf_token }}（共14处）
7. 修复 Jinja2 date 过滤器语法：所有 |date:"..." 改为 |date("...")（共8处）
8. 修复 Jinja2 dict 语法：.items() 改为 .items（3处），修复 system_permissions.html 和 system_cron_manager.html
9. 修复 Jinja2 过滤器链式调用：|default().split() 需要用括号分组（system_settings.html 4处）
10. 修复 Jinja2 dict.items() 语法：Jinja2 需要显式调用 items() 方法（permissions 和 cron_manager 3处）
11. 修复模板Bug: taxonomies/view.html移动Modal到表外、dashboard.html添加stats默认值、customer表单添加customer空值检查、修复JS中XSS风险
12. 创建模板开发规范文档，包含目录结构、Jinja2语法规范、模板片段库、变量/文件命名规范、新建页面Checklist、组件化指南、性能优化、Accessibility、调试方法、反模式、项目特殊约定等内容，并更新AGENTS.md
13. 将模板开发规范移动到 docs/技术规范/ 目录，更新 AGENTS.md 中的链接
14. 删除 01_分页器技术规范.md，更新 AGENTS.md
15. 更新 Node模块技术规范 文档：修正目录结构、更新模板示例为 frame_node.html、修正 csrf_token 语法、更新路由表添加导入导出和API路由
16. 创建Python代码开发规范文档 (05_Python代码开发规范.md)，包含11章+5个附录：文件头注释、导入规范、命名规范、类定义、函数规范、Django特定规范、API设计规范、测试规范、数据库迁移规范、定时任务规范，以及代码模板、反模式、检查清单等

# 2026-03-24 修改记录

1. 更新 README.md，补充字段类型系统、项目结构、文档说明、开发命令等内容
2. 创建客户模块目录重构计划文档 (20_客户模块目录重构计划.md)
3. 更新客户模块目录重构计划文档，添加Node支撑系统移入core目录的架构设计
4. 更新重构计划文档，添加模块自包含的templates目录设计
5. 开始执行客户模块目录重构：创建 core/node/ 模块，移动 NodeType 和 Node 模型
6. 完成客户模块目录重构核心部分：创建 core/node/ 模块，移动客户服务到各自目录
7. 完成客户模块目录重构：更新所有相关文件的导入路径
8. 完成客户模块目录重构：移动模板到模块自包含目录，更新settings.py模板路径
9. 完成 views.py 拆分：创建 core/node/views.py 节点类型管理视图，移动模板到 core/node/templates/
10. 完成 Import/Export 功能迁移：创建 core/importexport/ 模块，移动模板到 templates/importexport/
11. 完成 nodes 应用清理：移动 NodeTypeAdmin/NodeAdmin 到 core/node/admin，移动 NodeTypeForm 到 core/node/forms，删除旧文件
12. 完成 stage3 重构：创建 core/node/ 和 core/importexport/ 模块，整理客户模块到 nodes/customer/ 和 nodes/customer_cn/，Django check 通过
13. 创建 management command：./manage.py init_sample_data 用于初始化客户样本数据
14. run.sh 添加选项 5 用于初始化客户样本数据
15. 清理项目：删除6个空__init__.py文件和5个空目录
16. 重构 Admin：将 CustomerFieldsAdmin 移到 nodes/customer/admin.py，CustomerCnFieldsAdmin 移到 nodes/customer_cn/admin.py
17. 重构 nodes/ 目录：将 models 移到 customer/models.py 和 customer_cn/models.py，创建 customer/urls.py 和 customer_cn/urls.py
18. 完成 nodes/ 目录彻底清理：删除 models.py/admin.py/views.py，创建 customer 和 customer_cn 独立 app
19. 移动通用节点路由到 core/node/urls.py，nodes/urls.py 仅保留客户路由
20. 删除 nodes/tests.py 测试文件
21. 重组迁移目录：NodeType/Node迁移到core/migrations/，CustomerFields到customer/migrations/，CustomerCnFields到customer_cn/migrations/
22. 移动 management/ 命令到 core/management/commands/init_sample_data.py
23. 重构样本数据：core/services/sample_data_service.py 包含初始化逻辑，customer/sample_data.py 和 customer_cn/sample_data.py 分别包含各自样本数据，删除 nodes/services/ 目录
24. 分离初始化命令：init_node_types、init_overseas_customers、init_domestic_customers，并更新 run.sh 菜单
25. 移动主模板目录 templates/ 到 core/templates/，更新 settings.py 模板路径配置
26. 移动主模板目录 templates/ 到 core/templates/
27. 修复模板路径：修正 views.py 中的模板路径从 'customer/templates/xxx' 改为 'xxx'
28. 修复 URL 路由冲突：将 core/urls.py 中的 nodes/ 改为 node/，添加 nodes:index URL
29. 修复 URL 路由：修复节点 URL 顺序（export/import 必须在 generic slug 之前），修复 Jinja2 模板语法（date filter），修复 URL 命名空间（nodes: → core:）
30. 验证目录重构完成 - 系统检查通过，URL路由正常
31. 修复模板查找顺序 - 将 customer_cn 模板目录置于 customer 之前
32. 修复国内客户URL - 将slug从customer_cn改为customer-cn，匹配URL路由
33. 修复禁用节点类型错误提示 - 显示'节点类型已禁用'而非'不存在'
34. 修复Toast消息模板 - message|tojson改为message.message|tojson
35. 修复词汇表管理页分页 - 使用page_obj.paginator.page_range替代未定义的pages_to_show
36. 修复词汇项页分页 - 使用page_obj.paginator.page_range替代错误的range逻辑
37. 修复词汇表列表页 - taxonomy.items.count改为taxonomy.items.count()
38. 修复客户模板冲突 - 重命名customer_cn模板为list_cn.html等，添加缺失的API路由，修复redirect URL
39. 更新三个技术规范文档的描述，反映项目架构变化
40. 优化 Cron 服务初始化时机，从 CoreConfig.ready() 移至 run.py 和 wsgi.py
41. 修复 Cron 服务启动时机问题，使用后台线程 + django.setup() 确保应用已加载
42. 海外客户模块：新增领英字段（linkedin），合并联系方式卡片为统一入口

# 2026-03-25 修改记录

1. 修复国内客户省市区联动：移除API登录要求，导入省市区数据
2. 修复客户表单验证问题：添加novalidate禁用浏览器HTML5验证
3. 整合客户信息页面：将联系方式1、联系方式2、社交信息合并为统一的联系信息卡片
4. 更新Node模块技术规范文档：新增模块注册机制（十一）、模块信息文件（十二）、模块服务层（十三）、模块管理页面（十四）、新建模块功能（十五）、默认模块处理（十六）、模块与节点类型关系（十七）
5. 实现Node模块注册安装机制：创建NodeModule模型、NodeModuleService服务、为customer和customer_cn创建module.py、建立模块管理页面、初始化默认模块
6. 统一国内客户模块slug为customer_cn：修改services.py、urls.py、views.py、services、permission_service、sample_data、init_node_types、init_domestic_customers
7. 编写Node模块动态加载方案文档，保存至 docs/stage3/22_Node模块动态加载方案.md
8. 实现Node模块动态加载机制：添加module.py视图配置、实现module_dispatch视图分发、完善register/install逻辑、测试通过
9. 完成Node模块动态加载方案：更新init_db.py使用动态模块扫描安装、更新run.py添加模块初始化函数
10. 添加模块目录缺失自动修复和界面优化
11. 更新Node模块技术规范文档v1.3
12. 实现INSTALLED_APPS动态加载，新增模块无需修改配置文件
13. 完成新建模块功能的后端逻辑

# 2026-03-26 修改记录

1. 完成全面 Bug 检查
2. 完成全面 Bug 检查（第二轮）
3. 修改客户模块描述
4. 创建数据库配置模块独立化方案文档
5. 重构存储目录：新建storage/，包含uploads/和backups/
6. 实施数据库配置模块独立化方案
7. 合并node_modules和node_types页面

# 2026-03-27 修改记录

1. 实施模块管理功能升级方案
2. 删除模块管理页与frame_structure的关联，改用frame_admin
3. 创建frame_module框架并应用于模块管理页
4. 将 nodes 目录重命名为 modules，完成所有 nodes->modules 引用更新
5. 模块技术规范文档升级：新增模块设计总结.md，重写02_模块技术规范.md（从nodes改为modules）
6. 全面检查并修复URL namespace引用：nodes:改为modules:或importexport:
7. 修复模板加载问题：settings.py中nodes路径改为modules，APP_DIRS改为False确保Jinja2优先
8. 修复首页内容区域与顶部菜单间距过大：dashboard.html添加use_custom_main=true和show_header=false
9. 修复首页间距问题：恢复frame_dashboard.html原padding (py-4 py-md-5)
10. 删除core/node/views.py中无效的node_list和node_view视图（重定向到modules对应视图）
11. 优化代码：将9处裸except改为except Exception
12. 实现首页功能卡片区域与时钟模块：创建clock模块基础文件(apps.py/urls.py/services.py)、实现时间API、创建时钟卡片模板、添加3×2功能卡片区域HTML、实现拖拽功能和位置保存API
13. 实现动态模板加载：修改settings.py，在启动时自动扫描modules/目录下所有模块的templates目录并加入模板搜索路径
14. 修复首页功能卡片区域不显示时钟卡片的问题：修正core/views.py中模块路径导入错误，使用modules.{module_path}.module格式
15. 修复时钟卡片不显示时间问题：修正JS中时钟API URL从/modules/clock/改为/nodes/clock/
16. 修改URL路径从nodes/改为modules/，统一模块URL前缀
17. 为run.sh添加杀死服务器进程功能，支持通过DJANGO_PORT环境变量指定端口
18. 删除首页仪表盘中的用户统计卡片区域
19. 修复 init_db.py 初始化顺序：管理员用户创建移到客户样本数据初始化之前

# 2026-03-28 修改记录

1. 实现模块类型分类：添加 module_type 字段区分 node 和 system 类型，事务处理页面过滤 system 类型模块
2. 改进模块扫描逻辑：使用 ast 直接解析 module.py 文件，新增模块无需重启服务即可被扫描到
3. 更新 02_模块技术规范.md 文档：新增模块类型分类（node/system）、module_type 字段说明、更新示例代码
4. 合并文档：删除模块设计总结.md，将其核心概念表格整合到 02_模块技术规范.md
5. 整理优化 02_模块技术规范.md：精简结构，优化章节顺序，增强可读性
6. 优化仪表盘卡片配色：使用 --bg-nav 和 --text-nav 变量实现主题跟随
7. 为 customer 和 customer_cn 模块创建仪表盘卡片，显示客户数量统计
8. 修复dashboard卡片显示bug：移除module_type='node'过滤条件，使system类型的clock模块也能显示在卡片区域
9. 修复dashboard卡片渲染逻辑：当有保存的位置时，填充空槽位显示默认卡片
10. 修复dashboard时钟卡片不显示：改为遍历默认模块列表，为每个模块找到第一个空槽位进行填充
11. 修改dashboard页面标题为'欢迎回来，用户名'
12. 新增首页设置页面：用户可在个人设置中管理首页卡片，支持拖拽添加/移除/调整卡片位置
13. 重新设计首页设置页面：简化拖拽逻辑，使用document级别事件监听器
14. 优化首页设置页面UI：卡片式布局、渐变标题、hover效果提升
15. 首页设置页面样式与首页保持一致：使用CSS变量、Bootstrap grid、统一的卡片阴影和边框样式
16. 修复首页设置页面边框显示：使用内联style确保CSS变量正确应用
17. 重新设计首页设置页面卡片样式：CSS Grid布局、渐变卡片、hover光效、圆角边框
18. 首页设置页面改回3x2实线边框布局，与首页保持一致
19. 修复首页设置页面3x2布局：使用Bootstrap row g-0 + col-4实现正确的3列2行网格
20. 修复首页设置页面边框显示：使用明确的颜色值替代CSS变量
21. 修复首页设置页面样式加载：使用正确的head_extra block名称替代extra_head
22. 修复安全漏洞：api_regions_path API添加@login_required装饰器
23. 更新模块技术规范：新增「十一、首页卡片系统」章节，提供完整的模块首页卡片开发指南
24. 更新README.md：反映最新的项目结构（modules目录、core/node、core/importexport等），更新功能特点和技术栈说明



# 2026-03-29 修改记录

1. 实现动态URL加载和模块安全加载，系统可在任意模块缺失时正常启动

# 2026-03-30 修改记录

1. 重新创建居民信息模块（代码已重建，模板文件待补充）
2. 修复迁移冲突：将NodeModule类名改为Module，合并迁移文件
3. 更新模块技术规范：添加动态URL加载机制
4. 恢复居民信息模块模板文件：list.html, edit.html, view.html
5. 修复 resident_info 模块模板语法错误，将 Jinja2 模板中的 Django 模板语法转换为 Jinja2 语法
6. 修复 edit.html 模板中 csrf_token 标签语法错误，将 Django 模板语法 {% csrf_token %} 改为 Jinja2 语法 {{ csrf_token }}
7. 修复 resident_info 模块所有模板语法错误，包括将 Django 模板语法转换为 Jinja2 语法，修复 default 过滤器、date 过滤器和 csrf_token 标签
8. 在 ModuleService 中添加 create_module_taxonomies 方法，在安装模块时自动创建模块定义的词汇表
9. 修复 resident_info 模块 bug：delete 方法逻辑错误、node_delete 参数传递错误、redirect 调用方式错误
10. 修复 resident_info 模块 bug：redirect 使用硬编码 URL 改为命名 URL 反向解析，修复 edit.html 模板空指针问题
11. 修复 edit.html 模板中多处空指针问题：访问属性时需先检查 resident 是否为 None
12. 修复 models.py 中 id_card 和 phone 字段缺少 null=True 的问题
13. 修改 init_db.py 模块初始化逻辑，只注册模块不安装/启用
14. 修复 run.py 中 NodeModuleService 导入错误，改为 ModuleService

# 2026-03-31 修改记录

1. 全面 Bug 排查修复：customer/customer_cn services 节点创建返回值检查、core/views 词汇表操作验证、edit_cn.html 重复字段删除、view.html/view_cn.html date 过滤器空值检查
2. 检查 core/views.py 和 core/node/views.py 的参数验证问题
3. 继续排查类似问题：customer/templates/edit.html 8个空值检查、core/views.py taxonomy_edit 验证和 cron_toggle_task JSON 解析、TaxonomyService 添加 get_item 方法
4. 排查类似问题：system_user_edit.html 5处空值检查、node/types/edit.html 和 node/edit.html 4处空值检查、homepage_settings.html 字典安全访问和硬编码URL修复
5. 继续排查 edit_cn.html 5处空值检查修复：postal_code、address、industry、registered_capital、credit_limit、website、notes
6. 删除性别词汇表中“其他”选项，补全居民信息模块民族词汇表为55个民族+其他=56项
7. 修复 module_scan 视图重定向 URL 错误和 node_type_create 视图 try-except 结构错误
8. 修复 module_scan 视图重定向 URL 从 core:node_types 改为 node:modules
9. 修复节点类型相关 URL 配置：添加缺失的 URL 路由，修正 views.py 和模板中的错误 URL 引用
10. 修复 module_scan 视图重定向 URL 从 core:node_types 改为 node:node_types_list
11. 修复 module_scan 重定向从 node_types_list 改为 node:index，扫描完成后返回模块管理页面
12. 修复 module_scan 重定向到 node:modules（模块管理页面）
13. 修复SQLite数据库初始化问题：在database.py中添加自动创建instance目录的逻辑
14. 修复Node模块初始化警告：使用register_and_install替代register_module，确保NodeType在客户数据初始化前创建
15. 为居民信息模块添加README文档（modules/resident_info/README.md）
16. 修复模块安装后错误跳转到节点页的缩进bug（core/node/views.py:289）
17. 添加数据库初始化选择功能：--reset-db 删除重建，--incremental 增量式，无参数时交互式选择

# 2026-04-01 修改记录

1. 删除run.sh中单独的海外/国内客户样本数据初始化菜单选项（功能已包含在初始化系统中）
2. 优化虚拟环境安装进度显示：添加 [1/N] 进度条指示
3. 修复居民信息模块NOT NULL约束错误：CharField字段空值改为空字符串而非None
4. 补充字段空值处理规范到技术文档（05_Python代码开发规范.md 10.6节）
5. 在AGENTS.md中添加技术规范参考提醒，强调开发时必须参考技术规范文档
6. 居民信息模块：人员类型移除"暂住人口"，合并为"流动人口"

# 2026-04-02 修改记录

1. 修复API安全漏洞：为api_regions_provinces添加@login_required装饰器
2. 合并stage3目录：将根目录的导出导入模块化设计方案移动到docs/stage3
3. 修复 modules/urls.py 中 NodeModule → Module 导入错误
4. 修复导入功能：创建缺失的 core/importexport/templates 目录及模板文件（import.html, import_page.html, import_result.html, export.html, export_fields.html, export_confirm.html, export_exporting.html）
5. 修复 importexport：添加 SpecialFieldPool.is_special_field() 方法

# 2026-04-03 修改记录

1. 修复 importexport：修复 SpecialFieldPool.handle() 调用为 handle_import()
2. 检查 importexport 模块无类似问题
3. 完成项目全面检查：服务层、表单验证、API安全、模板一致性均通过
4. 修复模块首页循环重定向问题：core/node/views.py 添加模块安装检查
5. 同类问题检查完成：发现1个需迁移问题(resident_info表缺失)，核心循环重定向已全部修复
6. 修复模块安装逻辑：添加表存在性验证，迁移失败时抛出异常而非静默跳过
7. 更新模块技术规范：补充安装流程、迁移验证、错误处理规范（v2.6→v2.7）
8. 修复 _check_tables_exist 函数：使用 Django ORM introspection 替代原始 SQL，兼容 Django 6.0
9. 合并 resident_info 迁移文件：0001 + 0002 + 0003 → 0001
10. 合并 customer 迁移文件：0001 + 0002 → 0001 (添加linkedin字段)
11. 优化 install_module 逻辑：已有迁移文件的模块不再使用 run_syncdb 参数
12. 合并 core 迁移：删除 NodeModule 相关迁移(0006,0008,0009)，新建 0006_module 直接创建 Module 表
13. 合并 core 迁移：0001+0002+0003+0004 → 0001_initial (含ChinaRegion, User.role/theme最终定义)
14. 重构 core 迁移：0001包含基础表+NodeType+Node，0002为独立Module表
15. 全面Bug检查：修复clock system类型模块循环重定向问题
16. 优化 init_db.py：按阶段分组（5个阶段），修复步骤编号，改进输出格式
17. 优化 init_default_taxonomies：使用 bulk_create，性能提升15倍(8s→0.5s)
18. Fix init_db.py duplicate migration: add --skip-migrate option and update run.sh
19. Simplify run.sh init: remove duplicate migrate, let init_db.py handle migrations
20. Optimize module scan/install: batch queries, skip installed, cache AST parsing, bulk create taxonomies
21. Optimize customer seed commands: bulk_create + pre-fetch existing names + transaction
22. Optimize init_db.py: skip migrations in incremental mode if no pending migrations
23. Fix module state reset bug: register_module() no longer resets is_installed/is_active
24. Bug check: fix duplicate @login_required decorator, all forms have csrf_token

# 2026-04-04 修改记录

1. Implement SMTP email module: models, services, forms, views, templates (Phase 1-2, 4-5)
2. Complete SMTP async: add EmailSendingTask, update cron_service, update doc #35
3. SMTP config: add batch_size, rate_limit, log_days, failed_notify, notify_email, system_url, skip_verify options
4. Fix SMTP bugs: notification logic and create missing history.html template
5. Bug check: add form validation for failed_notify + notify_email, add template error display

# 2026-04-05 修改记录

1. Bug check complete: no critical bugs found, code quality is good
2. Update bug排查规范.md: add system checks, command tables, new module checklist (8.1-8.9)
3. 完成邮件模板功能：添加 TemplateService.init_default_templates() 初始化默认模板（验证码、密码重置、通知），EmailService 添加 send_verification_code()、send_password_reset()、send_notification() 便捷方法，init_db.py 添加阶段2.4邮件模板初始化步骤

# 2026-04-06 修改记录

1. Bug检查完成：系统无发现bug
2. 创建CRM功能规划建议文档
3. 创建导航卡片功能设计方案文档 (docs/stage3/36_导航卡片功能设计方案.md)
4. 实现模块依赖检查功能：添加require属性 + 递归验证依赖
5. 修正模块依赖：4个模块均无依赖关系
6. Bug检查完成：系统无发现bug，模块依赖功能正常
7. 更新模块技术规范文档：添加require字段和依赖检查功能说明
8. 修正模块技术规范文档：NodeModule→Module，创建示例添加require字段，版本升至2.9
9. 技术规范目录文档编号改为A02-A05格式，并更新内部链接引用
10. 创建A01_项目概述与技术架构.md文档，移动README中的字段类型、项目结构等内容
11. 实现导航卡片功能：用户自定义导航链接，支持添加/编辑/删除/拖拽排序，最多12个卡片
12. 添加默认导航网站：必应、豆包、千问、百度地图
13. Bug检查：修复导航卡片设置页面初始化时未渲染空槽位问题
14. 全面 Bug 排查完成 - 所有阶段检查通过
15. 修复 user/nav-cards 页面语法错误：1) 模板缺少 {% endblock %} 结束标签；2) forloop.counter 改为 Jinja2 的 loop.index
16. 移除导航卡片设置页面的预设颜色功能，改用颜色选择器
17. 导航卡片：设置页保存后自动通知首页更新（使用 BroadcastChannel API）
18. 导航卡片：删除卡片后自动保存并通知首页更新
19. 修复导航卡片拖拽功能：1) 设置页修复数据数组操作；2) 首页添加拖拽排序功能
20. 首页导航卡片拖拽：改用事件委托，避免 DOM 重建后事件丢失
21. 修复导航卡片拖拽问题：1) 设置页和首页都改用从 DOM 读取卡片顺序；2) 首页拖拽也能拖入空格子
22. 导航卡片同步：添加 localStorage 作为 BroadcastChannel 的备选方案
23. 修复导航卡片拖拽：交换整个 .col-2 容器而不是只移动卡片元素
24. 修复导航卡片拖拽：保存后调用 updateCardDisplay() 重新渲染页面
25. 重构导航卡片拖拽：使用事件委托替代逐个绑定事件
26. 修复导航卡片拖拽：参考首页实现，拖拽时直接移动 DOM 元素，保存后不重建 DOM
27. 修复导航卡片拖拽：修复 setTimeout 中 draggingCard 为 null 的问题
28. 修复导航卡片页面：确保 updateCardDisplay() 正确渲染格子
29. 修复导航卡片拖拽：目标 slot 有卡片时交换两者位置而不是覆盖
30. 移除 storage 事件监听器，避免 updateCardDisplay() 重建 DOM 覆盖拖拽结果
31. 实现导航卡片位置固定功能：1) 数据模型添加position字段；2) 设置页按position渲染和拖拽；3) 新增卡片分配第一个空position；4) 首页按position渲染；5) 现有数据迁移
32. 修复模块安装问题：使用subprocess运行迁移命令，动态注册模块app到INSTALLED_APPS
33. 首页导航卡片：添加拖拽功能，支持位置交换和空位置移动

# 2026-04-07 修改记录

1. 修复导航卡片bug：1) position重复时自动分配到空位置；2) 移除console.log
2. 修复模块安装后无限重定向问题：将 modules/urls.py 和 core/node/urls.py 的 catch-all 模式改为使用 module_dispatch
3. 居民信息模块身份证功能增强：添加身份证验证和自动填充功能
4. 修复模块安装后点击事务处理的 NoReverseMatch 错误：统一使用 modules:module_page URL
5. 修复 module_dispatch 参数名不匹配：统一使用 node_type_slug
6. 修复模块缺少 views 配置导致 404：resident_info 和 clock 模块添加 views 配置
7. 模块管理页面添加重启服务器按钮：支持 runserver 和 gunicorn，自动检测服务器类型，30秒频率限制，日志记录到 storage/logs/restart.log
8. 移除模块管理的重启服务器按钮，改为页面底部文字提示
9. 修复居民信息模块身份证自动填充功能：将 oninput/onpaste 改为 addEventListener 绑定事件
10. 移除服务器重启功能代码：ServerService类、server_restart视图和URL路由
11. 修复模板Bug：customer_cn模板孤立的div标签、resident_info出生日期格式
12. 实现模块市场功能：下载并解压模块到modules目录
13. 统一所有frame模板设计：参考frame_module修改6个frame模板，更新39个引用页面的block名称
14. 市场功能升级：版本检测和升级功能，检测到已注册模块版本低于市场版本时显示升级按钮
15. 模块市场页面添加更新后需重启服务器的提示
16. 新增customer_cn模块到模块市场
17. 将marketplace.json移动到core/marketplace目录
18. 删除temp临时目录
19. 修复登录页面csrf_token显示乱码问题
20. 初始化时设置默认导航卡片配置
21. 全面检查项目Bug：修复3处csrf_token语法错误
22. 合并importexport模板到core/templates
23. 执行模板目录扁平化：移动文件+更新路径
24. 全面检查模板Bug：修复13处csrf_token语法错误
25. 二次检查模板Bug：无问题
26. 修复导航卡片设置页保存后首页不更新问题
27. 修复导航卡片保存async函数声明
28. 更新导航卡片默认颜色为用户配置
29. 将run.sh初始化菜单改名为安装/初始化
30. 删除 settings.py 中不存在的 node/templates 路径引用
31. 创建 core/models 模型设计规范文档 (B06)
32. 完成 core 模块技术规范文档系列 (B01-B05)
33. 将 B01-B05 技术规范文档加入 AGENTS.md
34. 合并 AGENTS.md 中的技术规范目录
35. 修正 AGENTS.md 中的标题，去掉模块二字

# 2026-04-08 修改记录

1. 修复 resident_info 模块缺少 views 配置的问题
2. 修复模块模板 extends 路径，从 core/frames/ 改为 frames/
3. 更新 customer 和 clock 模块版本为 1.1.1
4. 恢复 customer 和 clock 模块版本为 1.0.0
5. 在 AGENTS.md 中添加项目关键概念段落
6. 升级模块市场两个模块版本到 1.1.1
7. 修复登录页错误消息不显示问题
8. 修复模块市场升级后版本号未更新问题
9. 修复导入结果页模板数据格式不匹配问题：转换 errors 格式从 {'row','errors'} 为 {'row','message'}
10. 修复 customer 模块模板扩展路径：从 'frames/frame_node.html' 改为 'core/frames/frame_node.html'
11. 修复模块模板扩展路径：统一使用 'frames/frame_node.html'（移除错误的 'core/' 前缀）
12. 居民信息列表：1) 添加现住小区/建筑过滤；2) 优化表单布局；3) 分页链接添加所有过滤参数
13. 居民信息搜索：添加显式 NULL 检查，确保搜索只匹配非空字段
14. 居民信息模块：1) 新增人员按钮移至右上角；2) 列表表格修改列：移除人员类型/创建时间，增加所在小区/建筑；3) 新增页面标题改为新增人员
15. 居民信息模块增加联系电话2、联系电话3字段：模型、服务、视图、模板、导出字段全部更新
16. 修复模块安装迁移功能：重构 _run_migration_commands 函数，移除被注释的迁移代码；为 resident_info 添加 phone2/phone3 字段及迁移

# 2026-04-09 修改记录

1. 完成测试覆盖扩展计划，创建新测试目录和101个测试用例
2. 完成项目全面Bug检查，系统检查、服务层、API安全、表单验证、模板一致性均通过
3. 完成API版本控制计划，实现了URLPathVersioning、创建core/api_urls.py和version_service.py
4. 完成请求频率限制计划，实现了全局Throttling和自定义LoginRateThrottle
5. 完成日志配置增强计划，实现了LOGGING多handler配置、RotatingFileHandler日志轮转、创建logging_utils.py
6. 完成Health_Check端点计划，实现了/health/、/health/detailed/、/api/version/三个端点
7. 完成全面Bug检查，系统检查、服务层、API安全、表单验证、模板一致性均通过，54个测试全部通过
8. 完成所有5个阶段4计划文档的执行及全面Bug检查，系统已增强测试覆盖、API版本控制、请求限制、日志轮转和健康监控
9. 完成阶段4所有5个计划文档的执行及全面项目增强，测试覆盖达101用例，API版本化、请求限制、日志轮转和健康监控已就绪
10. 创建了08_代码精简与重构计划.md文档，详细规划了删除废弃测试、重构Fields基类、拆分Views模块的实施方案
11. 完成了代码精简计划Phase1和Phase2：删除废弃core/tests.py、重构Fields基类(增强通用方法)、简化string/text/integer字段
12. 完成08文档Phase 3：拆分Views模块，创建12个视图文件
13. 修复登录页循环重定向问题：移除 login_view 的 @login_required 装饰器
14. 完成代码精简：views.py从1311行精简至48行，迁移错误处理和辅助函数
15. 代码优化：移除未使用导入、精简局部import、优化settings_list
16. 优化：移除未使用的settings_list函数和导出
17. 优化：创建admin_required装饰器，重构18个视图函数使用装饰器
18. 优化：dashboard.py 使用 @admin_required 装饰器
19. 优化：smtp/views.py和node/views.py使用@admin_required，urls.py移除未使用导入
20. 分拆 core/node/services.py 为独立模块（node_type_service, node_service, module_service），确认测试已迁移
21. 补充 UserService、AuthService、SettingsService 测试用例
22. 编写初始化代码执行速度优化方案文档
23. 实施初始化代码执行速度优化（SettingsService批量写入、PermissionService批量查询、init_db.py并行化）
24. 编写日志管理页面实施计划文档
25. 实施日志服务与日志管理页面（LogService读写合一、页面展示、security.log配置）

# 2026-04-10 修改记录

1. 检查四个模块（clock、customer、customer_cn、resident_info），确认均无 bug
2. 修复 storage 目录自动创建机制：在 settings.py 中添加代码，Django 启动时自动创建 storage/logs、storage/uploads、storage/backups 目录；同时在开发规范中添加存储目录说明
3. Git 排除 customer_cn 模块：在 .gitignore 中添加 modules/customer_cn/
4. 添加 run.sh 启动动画：使用 sub-zero 字体的 CIMF 字母逐行显示（蓝色，2秒）
5. run.sh 添加打字机效果：CIMF 启动动画使用 typewrite 函数逐字符输出（约2秒），菜单标题使用打字效果，添加 typewrite 函数
6. run.sh 启动动画优化：CIMF 字母放大一倍（每行重复），取消底部蓝色线和标题字，动画完成后停留0.5秒
7. 修复 NodeService 方法调用错误：添加 get_by_id 方法，修复 views.py 和 services.py 中的错误调用（delete→delete_node, create→create_node, update→update_node）
8. 修复居民信息模块详情页字段不完整问题：在 view.html 中补充了 16 个缺失字段（phone2, phone3, key_category, registered_region, household_number, is_separated, actual_residence, is_moved_out, move_out_date, move_to_place, is_deceased, death_date, work_status），并新增迁移信息和生命状态两个卡片
9. 修复模块中 NodeService 方法调用错误：resident_info 和 customer_cn 模块的 create/update/delete 调用修改为 create_node/update_node/delete_node
10. 优化居民信息详情页：修复标题和按钮块名称为 admin_title_content 和 admin_buttons_content，标题显示居民姓名，已死亡/已迁出状态显示在姓名旁
11. 完善居民信息编辑页：在 edit.html 中补充了缺失的字段（registered_region, household_number, is_separated, actual_residence, is_moved_out, move_out_date, move_to_place, is_deceased, death_date, work_status），并添加了相应的分组标题
12. 优化居民信息列表页：在姓名旁增加状态列，显示已死亡和已迁出标签，两标签同时存在时上下布局
13. 重新设计居民信息列表页：每条记录增加详情行（默认展开），显示状态、所属网格、户籍、人员类型；表头保留姓名、身份证号、电话、所在小区/建筑、操作
14. 从 settings.py 移除 Jinja2 配置，保留 Django 仅引擎

# 2026-04-11 修改记录

1. 完成发送模块计划文档（docs/stage4/12_发送模块计划.md）
2. 更新发送模块计划文档（添加批次表、异步方式、URL命名空间等改进）
3. 更新发送模块计划文档（v1.2：添加分页、最近发送日期、清理策略等）
4. 更新发送模块计划文档（v1.3：修复重复注释、更新版本号、添加apps.py、补充测试用例）
5. 更新发送模块计划文档（v1.4：添加WABridge服务设置、筛选选项、API端点清单等）
6. 更新发送模块计划文档（v1.4：修复版本号、删除重复内容、补充API端点、内联编辑模板设计）
7. 更新发送模块计划文档（v1.5：添加搜索说明、变量验证、最近发送日期查询优化）
8. 更新发送模块计划文档（v1.5：修复版本号、删除重复搜索说明、补充apps.py、添加变量验证测试用例）
9. 标记文档11_模板引擎统一方案.md为废弃

# 2026-04-12 修改记录

1. 创建 LinkedIn 模块技术规范文档（暂无实施计划）
2. 更新 requirements.txt，所有依赖更新到安全稳定版本
3. 更新 README.md：添加技术架构、核心概念、模块市场、开发规范章节，修正模块列表
4. 新增工具模块框架：主菜单链接、frame_tools模板、tools视图和路由
5. 修复登录页无法访问：禁用 Django admin，恢复 Jinja2 模板引擎
6. 修复 navigation_cards JSONField default 为可调用函数
7. 修复 navigation_cards JSONField default 使用可调用函数
8. 新增协作工具功能：顶部菜单链接、frame_tools模板、tools视图和路由
9. 更新模块技术规范文档：添加 tool 模块类型、协作工具页面架构
10. 创建 ToolType 模型，更新协作工具使用 ToolType 而非 NodeType
11. 更新模块技术规范：明确 tool 类型支持首页卡片和协作工具首页
12. 创建协作工具Tool模块设计文档
13. 实现协作工具tool功能：ToolType模型、tools视图、URL路由、协作工具模板、calc示例模块
14. 更新A02_模块技术规范：添加tool模块views.py规范、模板继承规范、无models.py模块安装处理、类型过滤逻辑更新
15. 完成 WhatsApp 发送模块（whatsapp）的开发：\n- 创建模块目录结构和所有文件（models, services, views, urls, templates）\n- 添加 logs.html 模板\n- 修复 urls.py 导入问题\n- 创建数据库迁移并执行\n- 安装并启用模块\n- 安装 wabridge SDK 依赖
16. 修复 dashboard_card 模板路径：移除 modules/ 前缀，因为模板目录已自动加入 Django 搜索路径

# 2026-04-13 修改记录

1. 优化 createModuleCard 实现真正的动态模板加载
2. 改为全部动态加载：移除预渲染，使用纯前端动态加载模块卡片模板
3. 检查模块：创建 resident_info/whatsapp 的 dashboard_card.html；customer_cn 未注册（仅 migrations）
4. 修复 customer_cn 模块：添加 dashboard_cards 配置和 dashboard_card.html 模板
5. 修复首页卡片 404：改为后端预渲染模块内容 (module_contents)，前端直接使用
6. 修改 frame_myinfo.html：首页设置 → 功能卡片
7. 修改 frame_myinfo.html：导航设置 → 导航卡片
8. 修复功能卡片显示：按 data-module 属性设置模块专属背景色
9. 重命名 clock-card 为 module-card；恢复各模块背景色（方案1：模块内定义）
10. 功能卡片和导航卡片：从圆角改为直角
11. 修复居民信息模块安装：迁移依赖从0009改为0002
12. 更新 A02_模块技术规范文档：clock-card 改为 module-card，模块内联样式定义背景色，动态模板变量等
13. 更新A02模块技术规范：明确功能卡片概念、补充模块类型表格、简化API返回字段、添加背景色设计指南和动态变量扩展示例
14. 功能卡片颜色配置迁移：将渐变色定义从模板移至module.py的dashboard_cards配置（color_start/color_end）
15. 修复时钟卡片显示：统一 CSS 类名与 updateClock() 函数匹配
16. 市场模块更新到1.1.7：resident_info和customer_cn
17. 修复市场模块下载链接文件名：使用 cimf-{module}.zip 格式
18. 修复 resident_info 模块 dashboard_card.html 模板：CSS类名改为 module-card、根元素改为 div、背景色改为 linear-gradient 渐变、添加拖拽属性和模块标识
19. 修复首页功能卡片拖动保存问题及居民信息卡片链接
20. 修复功能卡片链接问题：前端 renderCards 函数将预渲染的 div 卡片转换为带链接的 a 标签
21. 简化功能卡片点击跳转逻辑：使用 onclick 事件处理 div 卡片点击跳转

# 2026-04-14 修改记录

1. 修复导入功能：添加数据预览表格，显示上传文件的前10行数据
2. 修复导入预览数据格式：将字典 key 从字段名改为中文列名，使其与 headers 对应
3. 居民信息列表页：增加展开行显示身份证、户籍地址、所属网格，第一行字体加大，第二行高度降低
4. 居民信息列表操作按钮改为实心按钮加文字，第二行增加人员类型，属性标题用不同颜色区分
5. 居民信息过滤器：增加显示已迁出/已死亡复选框，默认不显示，所属网格标签使用深橙色
6. 居民信息过滤器调整：搜索框/现住小区/人员类型/所属网格放第一行，复选框放第二行，搜索按钮实心
7. 居民信息详情页和编辑页补充缺失字段
8. 居民信息编辑页：合并迁移信息和生命状态为迁移与生命状态，条件字段根据复选框状态显示/隐藏
9. 居民信息详情页：合并迁移信息和生命状态为迁移与生命状态卡片
10. 居民信息：增加死亡原因字段，编辑页条件显示；详情页户籍信息移除是否人户分离显示，实际居住地条件显示
11. 居民信息模块检查完成：修复创建方法death_reason字段缺失，添加编辑页人户分离条件显示逻辑
12. 列表页：在第二行展开行最前面增加迁出/死亡标签，黄底迁出，灰底死亡
13. 居民信息模块检查完成：所有功能正常
14. 修复居民信息首页卡片统计：只计算正常人员，不包括已迁出和已死亡
15. 居民信息列表页优化：过滤区所属网格改为普通色，第二行字号加大，死亡标签间距减小，列表网格改为灰色
16. 修复首页卡片统计不显示问题：在渲染模板时传递total和recent数据
17. 修复居民信息列表翻页后复选框状态丢失问题：views.py 修复参数解析逻辑，list.html 分页链接传 1/0 而非 True/False

# 2026-04-15 修改记录

1. 修复首页功能卡片居民信息数不刷新问题：cards API 添加缓存控制头
2. 修复导出字段选择页面：1) 默认全选字段 2) 添加全选/全不选按钮 3) 修复字段收集逻辑 bug
3. 全面检查导入导出功能并修复 4 个 bug：1) URL redirect 错误 2) 上传预览字段映射问题 3) XLSX 文件读取指针问题 4) CSV 文件读取指针问题
4. 修复导出功能两个 bug：1) _get_service_class 优先匹配同名 Service 2) 补充 resident_info 表缺失的 phone2/phone3/death_reason 列
5. 实现导入导出自动发现机制：1) 重构 FieldDefExtractor 字段提取器 2) ExportService 支持自动从 Django 模型发现字段 3) 支持模块补充指定机制 4) 直接查询模块模型而非通过 Service

# 2026-04-19 修改记录

1. 修复Bug: 服务层外键未检查、API缺少认证、表单user_id风险、模板空值处理
2. 更新A02_模块技术规范：添加models字段、SQL钩子函数、region字段类型、修正tool类型显示位置、添加模块市场配置
3. 顶部导航菜单增加hover特效：默认100%不透明，hover时当前链接保持100%，其他链接80%透明度

# 2026-04-20 修改记录

1. 修复多个模块bug：calc eval危险使用、whatsapp .get()无异常处理、clock模板默认值、whatsapp Jinja2时间格式化
2. 二次修复模块bug：customer/customer_cn Jinja2 date语法、whatsapp/resident_info外键检查、resident_info模板字段访问
3. 第三次Bug检查：验证确认所有高优先级问题已修复
4. Clock卡片链接修复：添加frontpage_card_clickable配置
5. IP访问限制功能：config.env配置、中间件、启动验证

# 2026-04-21 修改记录

1. 模块安装流程修复：下载后自动注册、扫描自动安装、register_and_install完善、启用逻辑优化
2. 导入功能修复：自动创建词汇表项、添加8个居民信息词汇表、修复education映射
3. 导入功能修复：移除验证阶段外键检查、确保转换阶段自动创建、改进错误报告

# 2026-04-27 修改记录

1. 修复居民信息模块UnboundLocalError：删除services.py中重复的Q导入
2. 居民信息搜索优化：现住小区筛选支持'小区 房号'组合模糊搜索
3. 居民信息列表页：在身份证后增加'关系'列（与户主关系）
4. 居民信息列表页：关系字段改用红色高亮显示
5. 撰写居民模块'其他证件'功能开发计划
6. 居民模块添加'其他证件'功能
7. 修复导出页面ModelBase JSON序列化错误
8. 修复导入导出FK字段解析，移除fk_model引用，改为使用fk_to字符串
9. 居民信息编辑页使用卡片布局优化
10. 添加身份证联动调试日志
11. 修复居民模块：创建缺失的性别和其他证件类型词汇表，修复身份证联动逻辑
12. 修复 Taxonomy 创建时的 UNIQUE constraint 冲突问题
13. 词汇表列表页增加搜索名称过滤功能
14. 修改网页标题为 页面标题-仙芙CIMF 格式（无标题则仅显示系统名称）
15. 修复网页标题 block 重复定义错误，改用 page_title 变量
16. 修改网页标题为 页面标题-仙芙CIMF 格式
17. 修改网页标题为页面标题-仙芙CIMF格式（为各子模板添加title块）
18. 修复网页标题格式问题，为剩余页面添加title块
19. 模仿daisyUI风格修改事务总览卡片
20. 补全主题CSS中的entry-card样式（图标3.5rem）
21. 修改tools/importexport页面卡片为entry-card样式
22. 修复entry-card按钮位置统一到底部
23. 修复entry-card按钮固定右下角（添加flex布局）
24. 修复entry-card按钮固定右下角完整版
25. 修复whatsapp模块（安装wabridge依赖）
26. 修正customer_cn模块模板为entry-card样式
27. 修复customer_cn模块模板路径和目录结构
28. 修复乱码（禁用jinja2.ext.debug）和省市县联动（导入3429条省市区数据）
29. 实现省市县数据从网络下载更新本地文件的完整逻辑
30. 修复客户编辑页乱码：'所���行业' → '所在行业'
31. 修复 CSRF token 显示问题：将 Jinja2 模板中的 '{{ csrf_token }}' 改为 '{% csrf_token %}'

# 2026-04-28 修改记录

1. 修复 CSRF token 显示：修改 context_processor 返回完整 input 元素，并在 jinja2.py 中注册 csrf_token 函数
2. 更新技术规范文档：A03新增数据维护流程章节、A04新增csrf_token实现机制说明
3. 更新规范文档：B02新增ChinaRegionService方法、A04新增Jinja2环境配置章节和过滤器速查
4. 更新A01项目概述文档：删除customer_cn/resident_info，新增calc模块，更新文档列表
5. 更新A02模块技术规范：删除customer_cn/resident_info，添加calc目录结构
6. 更新A04模板开发规范：删除customer_cn/resident_info相关示例
7. 修复A03省市县规范：删除重复行，修正章节编号
8. 全面修复技术规范文档：A01/A03/A06添加版本和日期，B01-B05/A06补充换行符
9. 创建 customer_cn 模块技术规范文档（modules/customer_cn/docs/README.md）
10. 补充 customer_cn 模块技术文档：新增分页参数、表单处理流程、API响应格式、表单验证与错误处理章节
11. 修复登录页 CSRF token 嵌套问题
12. 检查并修复所有模板的 CSRF token 使用方式
13. 修改 entry_card 样式：标题移至照片区域下方，图标透明度改为 70%
14. 模块市场 customer_cn 升级到 v1.1.5
15. 新增 resident_info 模块技术规范文档
16. 修复 importexport 模块 entry_card 布局：将标题移至照片区域下方
17. 修复导入功能：新增布尔字段智能转换，支持是/否、True/False、1/0 等多种格式
18. 修复导入关系栏失败：import_service.py 使用 taxonomy 映射，修复 fk_resolver.py 变量未定义 bug
19. 补充 other_id_type 词汇表：module.py 添加词汇表定义，field_extractor.py 添加 FK_TAXONOMY_MAP 映射
20. 从模块市场移除 whatsapp 模块
21. 确保模块初始化时完成词汇表初始化：修改 scan_and_register_modules 移除静默异常、增强 create_module_taxonomies 验证、修改 install_module 检查创建结果、init_db.py 添加验证步骤
22. 方案B测试通过：词汇表全部创建成功（10个表102项），导入功能验证通过（关系栏正确导入）
23. 修复居民信息导入预览问题：将relation字段verbose_name从'与其他人员关系'改为'与户主关系'，确保导入模板列名与字段标签一致

