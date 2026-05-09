# -*- coding: utf-8 -*-
"""
数据库配置模块

根据 config.env 配置返回 Django DATABASES 格式的数据库配置
支持 SQLite 和 MySQL 两种数据库
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_database_config():
    """
    根据配置获取数据库配置
    
    读取 config.env 中的 DB_TYPE、DB_NAME、DB_USER 等配置
    返回 Django DATABASES 格式的配置字典
    
    Returns:
        dict: Django DATABASES 配置
    """
    
    config_path = BASE_DIR / 'config.env'
    db_config = _load_config(config_path)
    
    db_type = db_config.get('DB_TYPE', 'sqlite').lower().strip()
    
    if db_type == 'mysql':
        return _get_mysql_config(db_config)
    else:
        return _get_sqlite_config()


def _load_config(config_path: Path) -> dict:
    """
    读取配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        dict: 配置字典
    """
    config = {}
    
    if not config_path.exists():
        return config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def _get_sqlite_config() -> dict:
    """获取 SQLite 配置"""
    db_path = BASE_DIR / 'instance' / 'django.db'
    # 确保 instance 目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 确保数据库文件使用WAL模式
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
    except Exception:
        pass  # 如果失败，继续
    
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_path,
        'OPTIONS': {
            'timeout': 30,
        },
    }


def _get_mysql_config(config: dict) -> dict:
    """获取 MySQL 配置"""
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('DB_NAME', 'cimf'),
        'USER': config.get('DB_USER', 'root'),
        'PASSWORD': config.get('DB_PASSWORD', ''),
        'HOST': config.get('DB_HOST', 'localhost'),
        'PORT': config.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }


def drop_database():
    """
    删除数据库
    
    SQLite: 删除数据库文件
    MySQL: DROP DATABASE + CREATE DATABASE
    """
    db_config = get_database_config()
    engine = db_config.get('ENGINE', '')
    
    if 'sqlite3' in engine:
        # SQLite: 删除文件
        db_path = Path(db_config['NAME'])
        if db_path.exists():
            db_path.unlink()
            print(f"已删除 SQLite 数据库文件: {db_path}")
    elif 'mysql' in engine:
        # MySQL: DROP + CREATE DATABASE
        try:
            import pymysql
        except ImportError:
            raise ImportError("使用 MySQL 需要安装 pymysql: pip install pymysql")
        
        db_name = db_config.get('NAME', 'cimf')
        conn = pymysql.connect(
            host=db_config.get('HOST', 'localhost'),
            port=int(db_config.get('PORT', 3306)),
            user=db_config.get('USER', 'root'),
            password=db_config.get('PASSWORD', ''),
        )
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        conn.close()
        print(f"已重建 MySQL 数据库: {db_name}")


def database_exists() -> bool:
    """
    检查数据库是否存在
    
    Returns:
        bool: 数据库是否存在
    """
    db_config = get_database_config()
    engine = db_config.get('ENGINE', '')
    
    if 'sqlite3' in engine:
        db_path = Path(db_config['NAME'])
        return db_path.exists()
    elif 'mysql' in engine:
        try:
            import pymysql
            conn = pymysql.connect(
                host=db_config.get('HOST', 'localhost'),
                port=int(db_config.get('PORT', 3306)),
                user=db_config.get('USER', 'root'),
                password=db_config.get('PASSWORD', ''),
            )
            db_name = db_config.get('NAME', 'cimf')
            with conn.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
                result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception:
            return False
    
    return False