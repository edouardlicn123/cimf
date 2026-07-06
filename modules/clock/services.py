"""
时钟模块服务层
"""

from core.services import get_time_sync_service


class ClockService:
    WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MONTHS_CN = ["", "一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    MONTHS_EN = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    @staticmethod
    def get_current_time():
        dt = get_time_sync_service().get_current_time()
        return {
            "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(dt.timestamp()),
            "date": dt.strftime("%Y年%m月%d日"),
            "time": dt.strftime("%H:%M:%S"),
            "weekday": ClockService.WEEKDAYS_CN[dt.weekday()],
            "weekday_en": ClockService.WEEKDAYS_EN[dt.weekday()],
            "month": ClockService.MONTHS_CN[dt.month],
            "month_en": ClockService.MONTHS_EN[dt.month],
        }
