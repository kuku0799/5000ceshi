from datetime import datetime
import os
from logging.handlers import RotatingFileHandler
import logging
from config import LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT

DEFAULT_LOG_FILE = LOG_FILE

# 可选控制是否在控制台打印日志（True = 打印）
ENABLE_CONSOLE_OUTPUT = True

def write_log(msg: str, log_path: str = DEFAULT_LOG_FILE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now} {msg}"

    if ENABLE_CONSOLE_OUTPUT:
        print(line)

    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        # 轮转文件写入
        logger = logging.getLogger("openclash-manage-file")
        if not logger.handlers:
            handler = RotatingFileHandler(log_path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        logger.info(line)
    except Exception as e:
        if ENABLE_CONSOLE_OUTPUT:
            print(f"[log.py] Failed to write log: {e}")
