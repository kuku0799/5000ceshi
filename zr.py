#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import hashlib
from ruamel.yaml import YAML
from jx import parse_nodes
from zw import inject_proxies
from zc import inject_groups
from log import write_log
from config import (
    NODES_FILE,
    MD5_RECORD_FILE,
    OPENCLASH_CONFIG_PATH,
    STATUS_FILE,
    BACKUP_DIR,
    BACKUP_COUNT,
)

lock_file = "/tmp/openclash_update.lock"
if os.path.exists(lock_file):
    write_log("⚠️ 已有运行中的更新任务，已退出避免重复执行。")
    exit(0)
open(lock_file, "w").close()

def verify_config(tmp_path: str) -> bool:
    write_log("🔍 正在验证配置可用性 ...")
    result = os.system(f"/etc/init.d/openclash verify_config {tmp_path} > /dev/null 2>&1")
    return result == 0

def write_status(**kwargs):
    """将同步结果写入状态文件"""
    try:
        import json, time
        data = {
            "timestamp": int(time.time()),
            **kwargs,
        }
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        write_log(f"⚠️ 状态写入失败: {e}")

def rotate_backups(config_file: str):
    """将当前配置文件备份到 BACKUP_DIR，保留 BACKUP_COUNT 份"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        base = os.path.basename(config_file)
        backup_path = os.path.join(BACKUP_DIR, f"{base}.{ts}.bak")
        os.system(f"cp {config_file} {backup_path}")
        backups = sorted([
            os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
            if f.startswith(base + ".") and f.endswith(".bak")
        ])
        while len(backups) > BACKUP_COUNT:
            old = backups.pop(0)
            try:
                os.remove(old)
            except Exception:
                pass
    except Exception as e:
        write_log(f"⚠️ 备份轮换失败：{e}")

try:
    nodes_file = NODES_FILE
    md5_record_file = MD5_RECORD_FILE
    config_file = os.popen("uci get openclash.config.config_path").read().strip() or OPENCLASH_CONFIG_PATH

    with open(nodes_file, "r", encoding="utf-8") as f:
        content = f.read()
    current_md5 = hashlib.md5(content.encode()).hexdigest()

    previous_md5 = ""
    if os.path.exists(md5_record_file):
        with open(md5_record_file, "r") as f:
            previous_md5 = f.read().strip()

    yaml = YAML()
    yaml.preserve_quotes = True
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f)
    existing_nodes_count = len(config.get("proxies") or [])

    if current_md5 == previous_md5:
        write_log(f"✅ nodes.txt 内容无变化，无需重启 OpenClash，当前节点数：{existing_nodes_count} 个")
        write_status(changed=False, proxies=existing_nodes_count, message="no changes")
        os.remove(lock_file)
        exit(0)
    else:
        write_log("📝 检测到 nodes.txt 内容发生变更，准备更新配置 ...")
        with open(md5_record_file, "w") as f:
            f.write(current_md5)

    # 清空日志
    with open("/root/OpenClashManage/wangluo/log.txt", "w", encoding="utf-8") as lf:
        lf.truncate(0)

    new_proxies = parse_nodes(nodes_file)
    if not new_proxies:
        write_log("⚠️ 未解析到任何有效节点，终止执行。")
        write_status(changed=True, success=False, message="no valid nodes")
        exit(1)

    updated_config, injected_count, invalid_count, duplicate_count = inject_proxies(config, new_proxies)
    inject_groups(updated_config, [p["name"] for p in new_proxies])

    test_file = "/tmp/clash_verify_test.yaml"
    with open(test_file, "w", encoding="utf-8") as f:
        yaml.dump(updated_config, f)

    if not verify_config(test_file):
        write_log("❌ 配置验证失败，未写入配置，已退出。")
        os.remove(test_file)
        exit(1)
    os.remove(test_file)

    rotate_backups(config_file)
    temp_write = f"{config_file}.tmp"
    with open(temp_write, "w", encoding="utf-8") as f:
        yaml.dump(updated_config, f)
    # 原子覆盖
    os.system(f"mv -f {temp_write} {config_file}")
    write_log("✅ 配置验证通过，已写入配置并完成备份轮换。")

    write_log("✅ 配置写入完成，正在重启 OpenClash ...")
    os.system("/etc/init.d/openclash restart")
    time.sleep(8)

    check_log = os.popen("logread | grep 'Parse config error' | tail -n 5").read()
    if "Parse config error" in check_log:
        write_log("❌ 检测到配置解析错误，已触发回滚 ...")
        try:
            backups = sorted([
                os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
                if f.startswith(os.path.basename(config_file) + ".") and f.endswith(".bak")
            ])
            if backups:
                os.system(f"cp {backups[-1]} {config_file}")
                os.system("/etc/init.d/openclash restart")
        except Exception as e:
            write_log(f"⚠️ 回滚失败：{e}")
        write_status(changed=True, success=False, message="runtime parse error - rolled back")
        exit(1)

    write_log(f"✅ 本次执行完成，已写入新配置并重启，总节点：{len(new_proxies)} 个")
    write_log("✅ OpenClash 已重启运行，节点已同步完成")
    write_status(
        changed=True,
        success=True,
        injected=injected_count,
        invalid=invalid_count,
        duplicate=duplicate_count,
        total=len(new_proxies),
        message="ok",
    )

except Exception as e:
    write_log(f"❌ 脚本执行出错: {e}")
    write_status(changed=True, success=False, message=str(e))

finally:
    if os.path.exists(lock_file):
        os.remove(lock_file)
