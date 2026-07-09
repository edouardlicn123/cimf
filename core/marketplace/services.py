"""
模块市场服务
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile
from importlib import import_module as _import_module
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from django.utils.timezone import now

BASE_DIR = Path(__file__).resolve().parent.parent
MARKETPLACE_CONFIG = BASE_DIR / "marketplace" / "marketplace.json"
MODULES_DIR = BASE_DIR.parent / "modules"
BACKUP_DIR = BASE_DIR.parent / "storage" / "backups" / "modules"

# 安全限制
MAX_DOWNLOAD_SIZE = 200 * 1024 * 1024  # 200MB
MAX_EXTRACT_SIZE = 1024 * 1024 * 1024  # 1GB
ALLOWED_DOWNLOAD_DOMAINS = [
    "github.com",
    "raw.githubusercontent.com",
    "gitlab.com",
    "gitee.com",
]


class MarketService:
    @classmethod
    def _compare_version_parts(cls, v1: str, v2: str) -> int:
        """比较两个版本字符串的部分，返回 -1, 0, 1"""
        parts1 = [int(x) for x in v1.split(".") if x.isdigit()]
        parts2 = [int(x) for x in v2.split(".") if x.isdigit()]

        max_len = max(len(parts1), len(parts2))

        for i in range(max_len):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0

            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1

        return 0

    @classmethod
    def compare_versions(cls, local: str, remote: str) -> int:
        """比较版本号，返回 -1(本地更低), 0(相同), 1(本地更高)"""
        if local == remote:
            return 0

        local_clean = local.strip().lstrip("vV")
        remote_clean = remote.strip().lstrip("vV")

        return cls._compare_version_parts(local_clean, remote_clean)

    @classmethod
    def get_modules(cls) -> list[dict[str, Any]]:
        """获取所有可用模块"""
        if not MARKETPLACE_CONFIG.exists():
            return []

        try:
            with MARKETPLACE_CONFIG.open(encoding="utf-8") as f:
                config = json.load(f)
            return config.get("modules", [])
        except (OSError, json.JSONDecodeError):
            return []

    @classmethod
    def get_module(cls, module_id: str) -> dict[str, Any] | None:
        """获取指定模块"""
        modules = cls.get_modules()
        for module in modules:
            if module.get("id") == module_id:
                return module
        return None

    @classmethod
    def get_installed_module_version(cls, module_id: str) -> str | None:
        """从数据库获取已注册模块的版本"""
        try:
            from core.module.models import Module  # noqa: PLC0415

            module = Module.objects.filter(module_id=module_id).first()
            if module:
                return module.version
        except Exception:
            pass
        return None

    @classmethod
    def is_installed(cls, module_id: str) -> bool:
        """检查模块是否已安装（目录存在）"""
        safe_id = Path(module_id).name
        module_dir = MODULES_DIR / safe_id
        module_py = module_dir / "module.py"
        return module_dir.exists() and module_py.exists()

    @classmethod
    def get_module_status(cls, module_id: str) -> dict[str, Any]:
        """获取模块状态"""
        safe_id = Path(module_id).name
        market_module = cls.get_module(safe_id)

        if not market_module:
            return {
                "exists": False,
                "installed": False,
                "has_update": False,
                "market_version": None,
                "installed_version": None,
            }

        market_version = market_module.get("version", "1.0")
        installed_version = cls.get_installed_module_version(module_id)
        is_installed = cls.is_installed(module_id)

        has_update = False
        if installed_version:
            has_update = cls.compare_versions(installed_version, market_version) < 0

        return {
            "exists": True,
            "installed": is_installed,
            "has_update": has_update,
            "market_version": market_version,
            "installed_version": installed_version,
        }

    @classmethod
    def _validate_download_url(cls, url: str) -> bool:
        """验证下载 URL 是否在允许域名内（SSRF 防护）"""
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            return any(domain == allowed or domain.endswith("." + allowed) for allowed in ALLOWED_DOWNLOAD_DOMAINS)
        except Exception:
            return False

    @classmethod
    def _backup_existing(cls, module_id: str) -> str | None:
        """备份已有的模块目录，返回备份路径；无备份时返回 None"""
        safe_id = Path(module_id).name
        module_dir = MODULES_DIR / safe_id
        if not module_dir.exists():
            return None

        timestamp = now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"{safe_id}_{timestamp}"
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(module_dir), str(backup_path))
        return str(backup_path)

    @classmethod
    def _read_local_version(cls, module_id: str) -> str | None:
        """从本地 module.py 读取版本号（动态导入）"""
        safe_id = Path(module_id).name
        module_py = MODULES_DIR / safe_id / "module.py"
        if not module_py.exists():
            return None

        module_path = f"modules.{safe_id}.module"
        try:
            if module_path in sys.modules:
                del sys.modules[module_path]
            mod = _import_module(module_path)
            if hasattr(mod, "MODULE_INFO") and isinstance(mod.MODULE_INFO, dict):
                return mod.MODULE_INFO.get("version")
        except Exception:
            pass
        finally:
            sys.modules.pop(module_path, None)
        return None

    @classmethod
    def check_conflict(cls, module_id: str) -> dict[str, Any]:
        """检查模块是否已存在且是否可覆盖"""
        safe_id = Path(module_id).name
        module_dir = MODULES_DIR / safe_id
        if not module_dir.exists():
            return {"blocked": False}

        local_version = cls._read_local_version(module_id)
        market_module = cls.get_module(module_id)
        market_version = market_module.get("version", "") if market_module else ""

        warning_parts = []
        if local_version and market_version:
            cmp = cls.compare_versions(local_version, market_version)
            if cmp < 0:
                warning_parts.append(f"本地版本 v{local_version} < 市场 v{market_version}，将升级覆盖")
            elif cmp > 0:
                warning_parts.append(f"本地版本 v{local_version} > 市场 v{market_version}，将降级覆盖")
            else:
                warning_parts.append(f"版本相同 v{local_version}，将重新安装")

        return {
            "blocked": False,
            "exists": True,
            "local_version": local_version,
            "market_version": market_version,
            "warning": "；".join(warning_parts) if warning_parts else None,
        }

    @classmethod
    def download_and_extract(cls, module_id: str) -> dict[str, Any]:
        """下载并解压模块，含安全限制和备份保护"""
        module = cls.get_module(module_id)
        if not module:
            return {"success": False, "error": "模块不存在"}

        download_url = module.get("download_url")
        if not download_url:
            return {"success": False, "error": "模块下载地址不存在"}

        if not cls._validate_download_url(download_url):
            return {"success": False, "error": f"下载地址不被允许: {download_url}"}

        safe_id = Path(module_id).name
        module_dir = MODULES_DIR / safe_id

        # 检查模块冲突
        conflict = cls.check_conflict(module_id)
        if conflict.get("blocked"):
            return {
                "success": False,
                "error": conflict["reason"],
                "conflict": True,
            }

        # 备份已存在的模块
        backup_path = cls._backup_existing(module_id)

        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{module_id}.zip"

        try:
            response = requests.get(download_url, timeout=60, stream=True)
            if response.status_code != 200:
                return {"success": False, "error": f"下载失败: HTTP {response.status_code}"}

            downloaded = 0
            with Path(zip_path).open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded += len(chunk)
                    if downloaded > MAX_DOWNLOAD_SIZE:
                        return {
                            "success": False,
                            "error": f"下载文件过大（超过 {MAX_DOWNLOAD_SIZE // 1024 // 1024}MB 限制）",
                        }
                    f.write(chunk)

            total_extracted = 0
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    member_path = os.path.normpath(Path(temp_dir) / member)
                    if not member_path.startswith(os.path.normpath(temp_dir) + os.sep):
                        continue
                    if Path(member_path).exists() and Path(member_path).is_dir():
                        continue
                    info = zip_ref.getinfo(member)
                    total_extracted += info.file_size
                    if total_extracted > MAX_EXTRACT_SIZE:
                        return {
                            "success": False,
                            "error": f"解压文件过大（超过 {MAX_EXTRACT_SIZE // 1024 // 1024}GB 限制）",
                        }
                    zip_ref.extract(member, temp_dir)

            items = list(Path(temp_dir).iterdir())
            extracted_dir = None
            for item in items:
                if item.name != f"{module_id}.zip" and item.is_dir():
                    extracted_dir = item
                    break

            if extracted_dir:
                if module_dir.exists():
                    shutil.rmtree(module_dir)
                shutil.move(str(extracted_dir), str(module_dir))

            # 更新数据库中的模块版本号
            market_version = module.get("version", "1.0.0")
            try:
                from core.module.models import Module  # noqa: PLC0415

                existing = Module.objects.filter(module_id=module_id).first()
                if existing:
                    existing.version = market_version
                    existing.save()
            except Exception as e:
                return {"success": False, "error": f"解压成功但更新版本失败: {e!s}"}

            result = {"success": True, "message": "下载成功"}
            if backup_path:
                result["backup_path"] = backup_path
            return result

        except requests.RequestException as e:
            return {"success": False, "error": f"下载失败: {e!s}"}
        except zipfile.BadZipFile:
            return {"success": False, "error": "文件格式错误，不是有效的zip文件"}
        except Exception as e:
            return {"success": False, "error": f"解压失败: {e!s}"}
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
