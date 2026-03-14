# 文件路径：app/modules/core/time/routes.py
# 功能说明：时间相关 API 路由

from flask import Blueprint, jsonify
from app.services.core.time_service import TimeService


time_bp = Blueprint('time', __name__, url_prefix='/api/time')


@time_bp.route('/current')
def get_current_time():
    """获取当前时间 API
    
    返回当前时间，支持时间服务器同步
    
    Response:
        {
            "time": "2026-03-14 12:00:00",
            "timezone": "Asia/Shanghai",
            "synced": true/false
        }
    """
    synced = TimeService.is_sync_enabled() and TimeService.fetch_beijing_time() is not None
    
    return jsonify({
        'time': TimeService.get_current_time(),
        'timezone': TimeService.get_timezone(),
        'synced': synced,
    })


@time_bp.route('/test')
def test_time_server():
    """测试时间服务器连接
    
    Response:
        {
            "success": true/false,
            "server": "https://api.uuni.cn/api/time",
            "time": "2026-03-14 12:00:00" / null
        }
    """
    server_url = TimeService.get_time_server_url()
    server_time = TimeService.fetch_beijing_time()
    
    return jsonify({
        'success': server_time is not None,
        'server': server_url,
        'time': server_time.strftime('%Y-%m-%d %H:%M:%S') if server_time else None,
    })
