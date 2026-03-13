FFE 项目跟进系统  
基本代码构建计划书

当前日期：2026年2月10日  
阶段：骨架搭建阶段（不包含任何业务功能实现）  
目标：搭建系统最基础的目录结构、运行环境、开发辅助工具、登录认证和启动入口，为后续所有业务模块提供稳定的基座。

1. 构建基本的文件夹和代码文件

项目根目录建议命名为 ffe-followup-system。

根目录下直接创建以下主要文件夹和文件：

一个名为 app 的文件夹，作为主应用包，里面放置所有 Python 模块和模板相关内容。

在 app 文件夹内创建以下 Python 文件：
__init__.py （应用工厂函数 create_app，负责路径处理、扩展初始化、蓝图注册、上下文注入）
config.py （配置类，包含 SECRET_KEY、数据库地址、调试模式等）
extensions.py （全局扩展实例：db、login_manager 等）
models.py （数据库模型，至少包含 User、Role、Permission 基础表）
admin_utils.py （后台通用工具：权限装饰器、文件上传处理等）
context_processors.py （模板全局上下文注入）
error_handlers.py （全局错误处理器）

在 app 文件夹内创建 routes 文件夹，用于存放所有路由蓝图。
routes 文件夹内创建：
__init__.py
main.py （登录、仪表盘、退出等基础路由）
一个 admin 子文件夹，用于后台路由
admin 文件夹内创建：
__init__.py （后台蓝图入口）

在 app 文件夹内创建 services 文件夹，用于业务逻辑层。
services 文件夹内创建：
__init__.py
（初期为空，后续放置计算服务等）

在 app 文件夹内创建 static 文件夹，用于静态资源。
static 文件夹内创建：
css 子文件夹
js 子文件夹
images 子文件夹

在 app 文件夹内创建 templates 文件夹，用于所有 HTML 模板。
templates 文件夹内创建：
base.html （前端基模板，包含导航栏和 footer）
一个 partials 子文件夹，用于公共片段
partials 文件夹内创建：
navbar.html
footer.html
一个 errors 子文件夹，用于错误页面
errors 文件夹内创建：
404.html、403.html、500.html 等

在项目根目录下创建：
instance 文件夹（运行时数据库和配置，加入 gitignore）
uploads 文件夹（持久化上传目录，加入 gitignore）
app/utils 文件夹，用于工具模块
utils 文件夹内创建：
code2ai.py （源码审查脚本）
code2ai_config.toml （code2ai 配置文件）
requirements.txt （依赖清单）
.gitignore （忽略文件）
README.md （项目说明文档）
run.sh （启动与管理脚本）

2. 构建 code2ai 监视系统

保留并直接复用原项目中的 code2ai 功能，作为开发过程中的代码审查与 AI 辅助工具。

具体做法：
在 app/utils 文件夹中直接放置 code2ai.py 文件，保持原有逻辑。
在项目根目录放置 code2ai_config.toml 文件，定义扫描规则（排除 uploads、instance、__pycache__ 等目录）。

功能保持不变：一键扫描项目代码，生成包含文件清单和代码内容的 txt 文件，便于后续交给 AI 进行审查、优化或迭代建议。

使用方式：通过启动脚本 run.sh 提供选项调用，例如运行 ./run.sh code2ai 即可生成审查文件。

初期无需修改代码，仅确保文件位置正确、配置文件能被读取。

3. 构建登录系统

实现最基础的登录认证框架，确保所有页面需登录访问。

核心组成部分：
在 app/models.py 中定义 User 模型，至少包含 id、username、password_hash 字段。
后续扩展时再加入 email、created_at 等字段。

在 app/extensions.py 中初始化 Flask-Login 的 login_manager，并设置 login_view 为 'main.login'，login_message 为“请先登录”。

在 app/routes/main.py 中实现登录相关路由：
GET /login 显示登录表单页面
POST /login 验证用户名和密码，成功后登录并跳转仪表盘
/logout 退出登录并跳转回登录页
/ （根路径）作为仪表盘首页，显示欢迎信息和“我的项目”列表（需登录）

在 templates 文件夹中创建 login.html 模板，包含用户名、密码输入框和提交按钮。
所有页面都继承 base.html，base.html 中判断 current_user.is_authenticated 来显示欢迎信息和退出链接。

在 app/admin_utils.py 中保留或新建 admin_required 装饰器，用于保护后台页面。
后续所有需要登录的路由都使用 login_required 装饰器。

登录流程：
未登录访问任何页面 → 重定向到 /login
输入用户名密码 → 验证成功 → 存入 session → 跳转仪表盘
点击退出 → 清空 session → 返回登录页

4. 构建启动脚本

提供一个名为 run.sh 的启动与管理脚本，仅支持 Linux/macOS 环境（Windows 可后续补充 run.bat）。

脚本放置在项目根目录。

主要功能通过交互菜单或参数调用实现：
检查并创建虚拟环境 venv（如果不存在则自动创建）
激活虚拟环境
使用清华镜像加速安装 pip 和 requirements.txt 中的所有依赖
初始化数据库（运行 init_schema.py，如果存在）
启动 Flask 开发服务器（flask run --host=0.0.0.0）
运行 code2ai 源码审查（生成审查文件）
显示帮助信息

脚本特点：
自动检测虚拟环境是否存在并激活
所有 python / pip 命令都使用 venv 内的解释器
支持直接传参运行，例如 ./run.sh 3 直接启动服务器
提供颜色提示、等待倒计时、默认选项（超时自动运行服务器）
输出关键路径信息（venv 位置、数据库路径等）便于调试

使用示例：
./run.sh → 进入交互菜单
./run.sh 3 → 直接启动开发服务器
./run.sh code2ai → 运行源码审查

脚本不包含任何打包 exe 的逻辑，也不包含 WeasyPrint 安装。