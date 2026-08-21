from django.apps import AppConfig


class NodesConfig(AppConfig):
    name = "modules"
    # 模块自动注册已移至 core/startup.py（延迟到数据库就绪后执行），
    # 避免在 ready() 中访问数据库触发 RuntimeWarning。
