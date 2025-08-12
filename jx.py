import os
import re
import json
import base64
from urllib.parse import unquote, urlparse, parse_qs
from typing import List, Dict
from log import write_log  # ✅ 使用统一日志输出

def decode_base64(data: str) -> str:
    try:
        data += '=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(data).decode(errors="ignore")
    except Exception:
        return ""

def clean_name(name: str, existing_names: set) -> str:
    # 统一名称规则：允许中文、字母数字、下划线、短横线、点
    name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_\-\.]', '', name.strip())[:24]
    original = name
    count = 1
    while name in existing_names:
        name = f"{original}_{count}"
        count += 1
    existing_names.add(name)
    return name

def extract_custom_name(link: str) -> str:
    match = re.search(r'#(.+)', link)
    if match:
        name = unquote(match.group(1))
        bracket_match = re.search(r'[（(](.*?)[)）]', name)
        return bracket_match.group(1) if bracket_match else name
    return "Unnamed"

def parse_plugin_params(query: str) -> Dict:
    params = parse_qs(query)
    plugin_opts = {}
    if 'plugin' in params:
        plugin_opts['plugin'] = params['plugin'][0]
    return plugin_opts

def extract_host_port(hostport: str) -> (str, int):
    # 剥离 /、?、# 等尾部干扰字符，仅保留 host:port
    hostport = hostport.strip().split('/')[0].split('?')[0].split('#')[0]
    match = re.match(r"^(.*):(\d+)$", hostport)
    if not match:
        raise ValueError(f"无效 host:port 格式: {hostport}")
    return match.group(1), int(match.group(2))

def parse_nodes(file_path: str) -> List[Dict]:
    parsed_nodes = []
    existing_names = set()
    success_count = 0
    error_count = 0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        write_log(f"❌ [parse] 无法读取节点文件: {e}")
        return []

    for idx, line in enumerate(lines, 1):
        try:
            if line.startswith("ss://"):
                raw = line[5:]
                name = clean_name(extract_custom_name(line), existing_names)

                if '@' in raw:
                    # 兼容两种 userinfo：明文 method:password 或 base64(method:password)
                    info, server = raw.split("@", 1)
                    info = unquote(info)

                    if ":" in info:
                        method, password = info.split(":", 1)
                    else:
                        decoded_info = decode_base64(info)
                        if decoded_info and ":" in decoded_info:
                            method, password = decoded_info.split(":", 1)
                        else:
                            raise ValueError("SS 用户信息既非明文也非可解的Base64")

                    hostport = server.split("#")[0].split("?")[0]
                    host, port = extract_host_port(hostport)

                    # 从整行中解析 plugin 参数（若存在）
                    query = urlparse(line).query
                    plugin_opts = parse_plugin_params(query)

                    if not all([host, port, method, password]):
                        raise ValueError("字段缺失")

                    node = {
                        "name": name,
                        "type": "ss",
                        "server": host,
                        "port": port,
                        "cipher": method,
                        "password": password
                    }
                    if plugin_opts:
                        node.update(plugin_opts)
                    parsed_nodes.append(node)
                else:
                    # 整段Base64：base64(method:password@host:port?plugin=...)
                    b64 = unquote(raw.split("#")[0].split("?", 1)[0])
                    decoded = decode_base64(b64)
                    if not decoded:
                        raise ValueError("Base64解码失败")

                    # 去掉可能的多余片段
                    decoded_main = decoded.strip().split("#")[0]
                    method_password, server = decoded_main.split("@", 1)
                    method, password = method_password.split(":", 1)
                    host, port = extract_host_port(server)
                    if not all([host, port, method, password]):
                        raise ValueError("字段缺失")
                    parsed_nodes.append({
                        "name": name,
                        "type": "ss",
                        "server": host,
                        "port": port,
                        "cipher": method,
                        "password": password
                    })
                success_count += 1

            elif line.startswith("vmess://"):
                payload = unquote(line[8:].split("#")[0])
                decoded = decode_base64(payload)
                if not decoded:
                    raise ValueError("Base64解码失败")
                node = json.loads(decoded)
                name = clean_name(extract_custom_name(line), existing_names)
                if not all([node.get("add"), node.get("port"), node.get("id")]):
                    raise ValueError("字段缺失")
                parsed_nodes.append({
                    "name": name,
                    "type": "vmess",
                    "server": node["add"],
                    "port": int(node["port"]),
                    "uuid": node["id"],
                    "alterId": int(node.get("aid", 0)),
                    "cipher": node.get("type", "auto"),
                    "tls": node.get("tls", "").lower() == "tls",
                    "network": node.get("net"),
                    "ws-opts": {
                        "path": node.get("path", ""),
                        "headers": {"Host": node.get("host", "")}
                    } if node.get("net") == "ws" else {}
                })
                success_count += 1

            elif line.startswith("vless://"):
                info = line[8:].split("#")[0]
                name = clean_name(extract_custom_name(line), existing_names)
                parts = info.split("@")
                if len(parts) != 2:
                    raise ValueError("字段格式不正确")
                uuid = parts[0]
                parsed = urlparse("//" + parts[1])
                host, port = parsed.hostname, parsed.port
                query = parse_qs(parsed.query)
                if not all([host, port, uuid]):
                    raise ValueError("字段缺失")
                parsed_nodes.append({
                    "name": name,
                    "type": "vless",
                    "server": host,
                    "port": int(port),
                    "uuid": uuid,
                    "encryption": query.get("encryption", ["none"])[0],
                    "flow": query.get("flow", [None])[0],
                    "tls": query.get("security", ["none"])[0] == "tls"
                })
                success_count += 1

            elif line.startswith("trojan://"):
                body = line[9:].split("#")[0]
                parsed = urlparse("//" + body)
                password = parsed.username
                host, port = parsed.hostname, parsed.port
                query = parse_qs(parsed.query)
                name = clean_name(extract_custom_name(line), existing_names)
                if not all([host, port, password]):
                    raise ValueError("字段缺失")
                parsed_nodes.append({
                    "name": name,
                    "type": "trojan",
                    "server": host,
                    "port": int(port),
                    "password": password,
                    "sni": query.get("sni", [""])[0],
                    "alpn": query.get("alpn", []),
                    "skip-cert-verify": query.get("allowInsecure", ["false"])[0].lower() == "true"
                })
                success_count += 1

            elif line.startswith("socks5://") or line.startswith("socks://"):
                # 解析 socks5:// 或 socks:// 格式
                protocol = "socks5://" if line.startswith("socks5://") else "socks://"
                body = line[len(protocol):].split("#")[0]
                name = clean_name(extract_custom_name(line), existing_names)
                
                # 检查是否是新的完全 Base64 编码格式（包含查询参数）
                if "?" in body:
                    # 新格式：socks://base64(username:password@host:port)?remarks=xxx
                    base64_part = body.split("?", 1)[0]
                    base64_part = unquote(base64_part)
                    query_part = body.split("?", 1)[1] if "?" in body else ""
                    
                    # 从查询参数中提取节点名
                    if "remarks=" in query_part:
                        remarks_match = re.search(r'remarks=([^&]+)', query_part)
                        if remarks_match:
                            remarks_name = unquote(remarks_match.group(1))
                            # 使用 remarks 作为节点名，如果没有 # 节点名的话
                            if name == "Unnamed":
                                name = clean_name(remarks_name, existing_names)
                    
                    try:
                        # 修复 Base64 填充
                        padding = 4 - (len(base64_part) % 4)
                        if padding != 4:
                            base64_part += "=" * padding
                        
                        # 解码 Base64
                        decoded = decode_base64(base64_part)
                        if "@" in decoded:
                            auth_part, server_part = decoded.split("@", 1)
                            
                            # 解析认证信息
                            if ":" in auth_part:
                                username, password = auth_part.split(":", 1)
                            else:
                                username, password = auth_part, None
                            
                            # 解析服务器信息
                            if ":" in server_part:
                                host, port = server_part.split(":", 1)
                                port = int(port)
                            else:
                                host, port = server_part, None
                            
                            if not all([host, port]):
                                raise ValueError("字段缺失")
                            
                            node = {
                                "name": name,
                                "type": "socks5",
                                "server": host,
                                "port": port
                            }
                            
                            if username:
                                node["username"] = username
                            if password:
                                node["password"] = password
                            
                            parsed_nodes.append(node)
                            success_count += 1
                        else:
                            raise ValueError("Base64 解码后格式不正确")
                    except Exception as e:
                        raise ValueError(f"新格式解析失败: {e}")
                else:
                    # 原格式：socks://username:password@host:port 或 socks://base64(username:password)@host:port
                    parsed = urlparse("//" + body)
                    host, port = parsed.hostname, parsed.port
                    username = parsed.username
                    password = parsed.password
                    
                    if not all([host, port]):
                        raise ValueError("字段缺失")
                    
                    node = {
                        "name": name,
                        "type": "socks5",
                        "server": host,
                        "port": int(port)
                    }
                    
                    # 处理认证信息
                    if username:
                        # 检查用户名是否是 Base64 编码的
                        try:
                            # 尝试解码 Base64
                            decoded_auth = decode_base64(username)
                            if ":" in decoded_auth:
                                # 解码成功，包含用户名和密码
                                decoded_username, decoded_password = decoded_auth.split(":", 1)
                                node["username"] = decoded_username
                                node["password"] = decoded_password
                            else:
                                # 解码失败或格式不正确，使用原始值
                                node["username"] = username
                                if password:
                                    node["password"] = password
                        except Exception:
                            # 解码失败，使用原始值
                            node["username"] = username
                            if password:
                                node["password"] = password
                    
                    parsed_nodes.append(node)
                    success_count += 1

            else:
                write_log(f"⚠️ [parse] 不支持的协议: {line[:30]}")
                error_count += 1

        except Exception as e:
            proto = line.split("://", 1)[0] if "://" in line else "unknown"
            write_log(f"❌ [parse] 第{idx}行 协议={proto} 解析失败: {e} | 片段={line[:60]}")
            error_count += 1

    write_log(f"✅ [parse] 成功解析 {success_count} 条，失败 {error_count} 条")
    write_log("------------------------------------------------------------")
    return parsed_nodes
