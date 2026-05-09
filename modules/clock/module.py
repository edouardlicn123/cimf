# -*- coding: utf-8 -*-
"""
模块信息
"""

MODULE_INFO = {
    'id': 'clock',
    'name': '时钟',
    'type': 'system',
    'version': '1.1.0',
    'author': 'edouardlicn',
    'description': '提供时钟、日历的展现功能。',
    'icon': 'bi-clock',
    'require': [],
    'install_on_init': True,
    'frontpage_card_clickable': False,
    'frontpage_card': True,
    'dashboard_cards': [
        {
            'id': 'clock_card',
            'name': '时钟卡片',
            'template': 'clock/dashboard_card.html',
            'color_start': '#0d6efd',
            'color_end': '#0a58ca',
        }
    ],
}
