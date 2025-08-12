# zc.py
import os
import re
from datetime import datetime

def inject_groups(config, node_names: list) -> tuple:
    # 获取所有策略组，而不是仅限于预设的手机002-手机254
    proxy_groups = config.get("proxy-groups", [])
    target_groups = [g["name"] for g in proxy_groups]

    # 日志路径
    log_path = os.getenv("ZC_LOG_PATH", "/root/OpenClashManage/wangluo/log.txt")
    def write_log(msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

    def is_valid_name(name: str) -> bool:
        # 允许中文、字母数字、下划线、短横线、点
        return bool(re.match(r'^[\w\-\.\u4e00-\u9fa5]+$', name))

    # ✅ 节点名称合法性校验
    valid_names = []
    skipped = 0
    for name in node_names:
        name = name.strip()
        if is_valid_name(name):
            valid_names.append(name)
        else:
            skipped += 1
            write_log(f"⚠️ [zc] 非法节点名已跳过：{name}")

    group_map = {g["name"]: g for g in proxy_groups}

    injected_total = 0
    injected_groups = 0

    for group_name in target_groups:
        group = group_map.get(group_name)
        if not group:
            write_log(f"⚠️ 策略组 [{group_name}] 不存在，跳过注入")
            continue

        original = group.get("proxies", [])
        reserved = [p for p in original if p not in ("REJECT", "DIRECT") and p not in valid_names]
        updated = ["REJECT", "DIRECT"] + valid_names + reserved

        added = len([n for n in valid_names if n not in original])
        group["proxies"] = updated

        injected_total += added
        injected_groups += 1

    config["proxy-groups"] = proxy_groups
    write_log(f"🎯 成功注入 {injected_groups} 个策略组，总计 {injected_total} 个节点，跳过非法节点 {skipped} 个\n")
    return config, injected_total
