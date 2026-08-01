import httpx

_SERVICE_ERROR_MAP = [
    (httpx.ConnectError, "无法连接到 {} 服务"),
    (httpx.TimeoutException, "{} 服务连接超时"),
]


def service_connect_error(e: Exception, service_name: str = "远程服务") -> str:
    """将外部 HTTP 服务异常映射为用户友好的中文提示"""
    for exc_type, template in _SERVICE_ERROR_MAP:
        if isinstance(e, exc_type):
            return template.format(service_name)
    return f"{service_name} 服务异常"
