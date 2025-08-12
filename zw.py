# zw.py
from ruamel.yaml import YAML
import copy
import os
import re
from jx import parse_nodes
from log import write_log
from config import OPENCLASH_CONFIG_PATH, SYNC_REMOVE_STALE_PROXIES

yaml = YAML()
yaml.preserve_quotes = True

def get_openclash_config_path() -> str:
    try:
        path = os.popen("uci get openclash.config.config_path").read().strip()
        return path or OPENCLASH_CONFIG_PATH
    except Exception:
        return OPENCLASH_CONFIG_PATH

def load_config(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.load(f)
    except:
        return {}

def is_valid_name(name: str) -> bool:
    # 允许中文、字母数字、下划线、短横线、点
    return bool(re.match(r'^[\w\-\.\u4e00-\u9fa5]+$', name))

def inject_proxies(config, nodes: list) -> tuple:
    if "proxies" not in config or not isinstance(config["proxies"], list):
        config["proxies"] = []

    existing_names = {proxy.get("name") for proxy in config["proxies"]}
    new_nodes = []
    injected = 0
    skipped_invalid = 0
    skipped_duplicate = 0

    for node in nodes:
        node = copy.deepcopy(node)
        name = node.get("name", "").strip()

        if not is_valid_name(name):
            skipped_invalid += 1
            write_log(f"⚠️ [zw] 非法节点名已跳过：{name}")
            continue

        if name in existing_names:
            skipped_duplicate += 1
            write_log(f"⏩ [zw] 已存在相同节点名，跳过：{name}")
            continue

        new_nodes.append(node)
        existing_names.add(name)
        injected += 1

    # 同步删除：移除 YAML 中已存在但本次未出现的节点（可配置）
    if SYNC_REMOVE_STALE_PROXIES:
        desired_names = {n.get("name") for n in nodes}
        before = len(config["proxies"])
        config["proxies"] = [p for p in config["proxies"] if p.get("name") in desired_names or p.get("name") is None]
        removed = before - len(config["proxies"])
        if removed > 0:
            write_log(f"🧹 [zw] 移除已删除的代理节点 {removed} 个")

    config["proxies"].extend(new_nodes)
    return config, injected, skipped_invalid, skipped_duplicate

def main():
    write_log("📦 [zw] 开始注入 proxies 网络节点...")

    config_path = get_openclash_config_path()
    if not config_path:
        write_log("❌ [zw] 获取配置路径失败，终止执行。")
        return

    config_data = load_config(config_path)
    if not config_data:
        write_log(f"❌ [zw] 配置文件为空或格式错误，请检查：{config_path}")
        return

    nodes = parse_nodes("/root/OpenClashManage/wangluo/nodes.txt")
    if not nodes:
        write_log("⚠️ [zw] 未获取到有效节点，跳过注入。")
        return

    updated_config, injected_count, invalid_count, duplicate_count = inject_proxies(config_data, nodes)
    total_count = len(nodes)

    if injected_count == 0:
        write_log("🔁 [zw] 无新节点注入。")
        return

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(updated_config, f)
        write_log(f"🎯 成功注入 {injected_count} 个节点（共 {total_count} 个，跳过非法 {invalid_count} 个，重复 {duplicate_count} 个）")
    except Exception as e:
        write_log(f"❌ [zw] 写入配置失败: {e}")

if __name__ == "__main__":
    main()
