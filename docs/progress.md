# 2026-03-13 修改记录

1. 修复了表单无法完全占满卡片的问题 - 修改了5个主题文件（default.css, dopamine.css, macaron.css, teal.css, uniklo.css）中的 .card-body 样式，移除了 margin: auto 和 max-width 限制
2. 更新了权限管理页面的布局 - 与系统设置页保持一致，添加了表单错误汇总，修复了模板语法错误
3. 修复了词汇表管理页底部内容不可见的问题 - 移除了 frame.css 中的 overflow: hidden，修改了 taxonomies.html 的卡片样式
4. 调整了页脚高度和位置 - base.css 中页脚高度减少到 1rem，base.html 改为 flex 布局让页脚显示在内容下方，移除了"内部使用工具"字样
5. 压缩了仪表盘页面顶部空间 - body padding-top 从 110px 减少到 72px，减少了 welcome-bar 和卡片列表的内边距
6. 将 profile、taxonomy、fields、export 模块移动到 core 下 - 更新了相关的 Python 导入路径
7. 添加了开发模式说明到 README.md - 解释了 Werkzeug 自动重载功能和 "restart with stat" 信息的含义
8. 削减了 navbar 三分之一高度 - 桌面端 80px→53px，移动端 72px→48px，body padding-top 相应调整
9. 稍微增加了 navbar 高度 - 桌面端 53px→60px，移动端 48px→54px
10. 将 templates 目录下的模板移动到 templates/core 目录下 - 更新了所有相关模板的 extends 引用路径
11. 将 models 目录下的模型文件移动到 models/core 目录下 - 更新了 models/__init__.py 和相关服务的导入路径
12. 将 models/__init__.py 移动到 models/core/ 下，并在 models/ 下重新创建 __init__.py 从 core 重新导出，保持原有导入路径不变
13. 将 services 目录下的服务文件移动到 services/core 目录下 - 更新了 core/__init__.py 和所有相关导入路径
14. 将 templates 目录下的模板移动到 templates/core 目录下 - 更新了所有路由中的 render_template 引用路径，添加 core/ 前缀
15. 重写了 05_客户信息范例.md 文档 - 添加了完整的 Node 系统实现指南，包括目录结构规范、模型/服务/路由/表单代码示例
16. 更新了 05_客户信息范例.md - 添加了系统预定义字段类型清单（24种），强调字段类型必须从系统字段类型中选择
17. 更新了 AGENTS.md - 添加了 Node 类型开发规范，包括目录结构要求和字段类型规范
18. 更新了 05_客户信息范例.md - 修改为每个节点类型独立字段表设计，主表+字段表分离
19. 更新了 05_客户信息范例.md - 添加了节点类型配置文件设计，包括相关文件路径、数据库表、字段配置，以及启用/禁用/删除功能
20. 更新了 05_客户信息范例.md - 添加了节点类型管理页面设计，包括管理路由、模板和设置页模板
21. 更新了 05_客户信息范例.md - 添加了节点类型管理页面入口在 frame_structure 框架下的说明
22. 创建了 app/templates/core/frame_node.html 模板 - 参考 frame_structure，用于节点管理页面
23. 更新了 05_客户信息范例.md - 添加节点类型入口链接规范，任何 node 类型的操作主页面的入口链接都挂在 frame_node 框架上
24. 更新了 05_客户信息范例.md - 更新目录结构，明确 core/node 和 modules/nodes 的职责划分，模板位置说明
25. 更新了 04_字段模块.md 文档 - 将目录路径更新为 app/modules/core/fields/，将所有字段状态更新为已完成
26. 在 nav.html 中添加了"事务"链接 - 指向 /nodes dashboard
27. 创建了 app/modules/core/node/ 模块 - 包含 routes.py 和 service.py，用于核心节点管理
28. 修复了 frame_node.html 中的错误 endpoint - node_admin.index 改为 node.node_type_admin
29. 修复了 nav.html 中的高亮条件 - node 改为 node.
30. 修复了 05_客户信息范例.md 文档 - 整理章节编号（1.1-1.6），修正路径为 modules/nodes/、services/、models/
31. 创建了 app/modules/nodes/customer/__init__.py - NODE_TYPE_CONFIG 配置
32. 创建了 app/services/node/customer/customer_service.py - CustomerService 服务类
33. 创建了 app/templates/nodes/customer/list.html - 客户列表模板
34. 创建了 app/templates/nodes/customer/view.html - 客户详情模板
35. 创建了 app/templates/nodes/customer/edit.html - 客户编辑模板
36. 创建了 app/modules/nodes/customer/forms.py - CustomerForm 表单类
37. 在 app/routes/__init__.py 中注册了 customer_bp 蓝图
38. 更新了 customer/routes.py - 添加了客户类型选项的动态加载逻辑
39. 完成了 node_type_admin 路由逻辑 - 包含启用、禁用、删除、设置功能
40. 创建了 app/templates/core/node/node_type_admin.html - 节点类型管理模板
41. 创建了 app/templates/core/node/node_type_settings.html - 节点类型设置模板
42. 更新了 app/templates/core/frame_node.html - 添加了事务总览和客户管理入口
43. 更新了 app/templates/core/node/dashboard.html - 显示已启用的节点类型卡片
44. 扩展了 NodeTypeService - 添加了 enable、disable、get_all_including_inactive、get_node_count、init_default_node_types 方法
45. 在 TaxonomyService 中添加了 customer_type 词汇表 - 包含潜在客户、正式客户、VIP客户
46. 在 app/__init__.py 中添加了节点类型初始化调用
47. 修复了 CustomerService 导入问题 - 在 customer/__init__.py 和 models/node/__init__.py 中添加导出
48. 修复了初始化数据重复问题 - 优化 init_default_taxonomies 和 init_default_node_types 方法
49. 将节点类型管理移动到 frame_structure 框架上 - 更新了 frame_structure.html、node_type_admin.html、node_type_settings.html
50. 创建了 docs/06_node模块建立指引.md - 从 05 文档抽取通用内容，用于指导其他 node 模块的创建
51. 删除了 frame_node 中的"数据管理"分组标题，保留客户管理链接
52. 修改了 content_structure_dashboard 模板 - 将"节点管理"卡片改为"节点类型管理"
53. 在 frame_structure 中添加了"仪表盘"链接
54. 将内容结构相关页面设置为仅管理员可见 - 更新了 frame_structure.html 侧边栏、taxonomy 路由、node 路由
55. 迁移了 routes modules 目录下的 HTML 模板到 app/templates/core/ - 删除了 taxonomy、admin、workspace、auth 下的 templates 目录
56. 更新了 06_node模块建立指引.md - 添加了 NodeType.icon 字段用于图标显示，添加了动态加载机制说明（上下文处理器、frame_node侧边栏、事务总览Dashboard）、权限管理页面CRUD权限自动加载、图标与名称统一方案
57. 执行了06文档的代码修改 - 添加了NodeType.icon字段、初始化默认图标'bi-people'、上下文处理器添加node_types、frame_node.html和dashboard.html改为动态加载
58. 执行了权限管理页面动态加载Node模块CRUD权限 - PermissionService添加get_system_permissions和get_node_permissions方法、路由添加传递变量、模板添加Node权限卡片显示
59. 更新了05_客户信息范例.md文档 - 添加了NodeType.icon字段、动态加载机制说明（上下文处理器、frame_node侧边栏、事务总览Dashboard、权限管理页面）、更新了数据结构示例、更新了版本历史
60. 创建了07_系统权限重构指引.md文档 - 描述了系统权限细化（系统设置/权限管理/人员管理细分为9个权限）、卡片化显示方案、代码修改指引
61. 执行了07文档的代码修改 - 系统权限细化为9个（系统设置2个、权限管理2个、人员管理4个）、系统权限改为卡片样式显示
62. 创建了08_时间管理模块指引.md文档 - 描述了时间服务模块设计（TimeService）、API路由、前端JS改造、水印改造、系统设置页面、时间服务器推荐列表
