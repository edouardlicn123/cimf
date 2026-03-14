# 文件路径：app/services/core/time_service.py
# 功能说明：时间服务 - 统一管理系统时间获取

from datetime import datetime
from typing import Optional
from urllib.request import urlopen
from urllib.error import URLError
import json
from app.services.core.settings_service import SettingsService


class TimeService:
    """时间服务 - 统一管理系统时间获取"""
    
    DEFAULT_SERVERS = [
        'https://api.uuni.cn/api/time',
        'http://api.baidu.com/time/get',
        'http://worldtimeapi.org/api/timezone/Asia/Shanghai',
    ]
    
    @staticmethod
    def is_sync_enabled() -> bool:
        """是否启用时间同步"""
        setting = SettingsService.get_setting('enable_time_sync')
        # SettingsService 会将 'true' 转换为 True
        return setting is None or setting is True or setting == 'true'
    
    @staticmethod
    def get_time_server_url() -> str:
        """获取配置的时间服务器URL"""
        url = SettingsService.get_setting('time_server_url')
        if url:
            return url
        return TimeService.DEFAULT_SERVERS[0]
    
    @staticmethod
    def _try_server(url: str) -> bool:
        """测试时间服务器是否可用"""
        try:
            with urlopen(url, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False
    
    @staticmethod
    def fetch_beijing_time() -> Optional[datetime]:
        """从时间服务器获取北京时间"""
        if not TimeService.is_sync_enabled():
            return None
        
        server_url = TimeService.get_time_server_url()
        
        try:
            with urlopen(server_url, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # 解析不同服务器返回格式
                    # api.uuni.cn: {"date": "2026-03-14 12:00:00"}
                    # baidu: {"t": "1699999999"}
                    # worldtimeapi: {"datetime": "2026-03-14T12:00:00+08:00"}
                    
                    date_str = data.get('date') or data.get('datetime', '').split('+')[0]
                    if date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_current_time() -> str:
        """获取当前时间（统一入口）
        
        Returns:
            str: 格式化的当前时间字符串 "YYYY-MM-DD HH:MM:SS"
        """
        server_time = TimeService.fetch_beijing_time()
        if server_time:
            return server_time.strftime('%Y-%m-%d %H:%M:%S')
        
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def get_timezone() -> str:
        """获取配置的时区"""
        return SettingsService.get_setting('time_zone') or 'Asia/Shanghai'
