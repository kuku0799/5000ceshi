"""
全局配置中心

优先使用 OpenWrt 目录 /root/OpenClashManage；如果不存在，则回落到项目目录，方便本地开发与测试。
可通过环境变量覆盖同名配置，例如：
  export WEB_PORT=5800
  export BASIC_AUTH_ENABLED=true
"""

import os
from pathlib import Path


def _bool_env(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "yes", "on"}


# 基础目录：OpenWrt 目录优先；本地无该路径时使用仓库目录
OPENCLASH_HOME = "/root/OpenClashManage"
REPO_DIR = Path(__file__).resolve().parent
BASE_DIR = OPENCLASH_HOME if os.path.isdir(OPENCLASH_HOME) else str(REPO_DIR)

# 关键路径
WANGLUO_DIR = os.getenv("WANGLUO_DIR", os.path.join(BASE_DIR, "wangluo"))
LOG_FILE = os.getenv("LOG_FILE", os.path.join(WANGLUO_DIR, "log.txt"))

NODES_FILE = os.getenv("NODES_FILE", os.path.join(WANGLUO_DIR, "nodes.txt"))
MD5_RECORD_FILE = os.getenv(
    "MD5_RECORD_FILE", os.path.join(WANGLUO_DIR, "nodes_content.md5")
)

# 状态文件（供 Web 或外部查看最近一次同步结果）
STATUS_FILE = os.getenv("STATUS_FILE", os.path.join(WANGLUO_DIR, "status.json"))

# OpenClash 配置路径：允许外部明确指定，否则默认配置文件路径
OPENCLASH_CONFIG_PATH = os.getenv("OPENCLASH_CONFIG_PATH", "/etc/openclash/config.yaml")

# Web 服务
WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "please-change-me")

# Web 基本认证（可选）
BASIC_AUTH_ENABLED = _bool_env("BASIC_AUTH_ENABLED", False)
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER", "admin")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS", "admin")

# 日志轮转
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(512 * 1024)))  # 512KB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "3"))

# 配置备份
BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(BASE_DIR, "backups"))
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", "5"))


