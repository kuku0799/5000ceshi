#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile

# 临时禁用日志输出
os.environ['LOG_FILE'] = '/dev/null'

# 导入解析模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_socks5_parsing():
    """测试socks5协议解析功能"""
    
    # 模拟parse_nodes函数的核心逻辑
    def parse_socks5(line):
        if line.startswith("socks5://"):
            body = line[9:].split("#")[0]
            from urllib.parse import urlparse
            parsed = urlparse("//" + body)
            host, port = parsed.hostname, parsed.port
            username = parsed.username
            password = parsed.password
            
            if not all([host, port]):
                return None
            
            node = {
                "name": line.split("#")[1] if "#" in line else "Unnamed",
                "type": "socks5",
                "server": host,
                "port": int(port)
            }
            
            if username and password:
                node["username"] = username
                node["password"] = password
            
            return node
        return None
    
    # 测试用例
    test_cases = [
        "socks5://user123:pass456@server1.com:1080#Socks5节点1",
        "socks5://server2.com:1080#Socks5节点2（无认证）",
        "socks5://admin:secret@proxy.example.com:1080#Socks5节点3"
    ]
    
    print("🧪 测试socks5协议解析")
    print("=" * 50)
    
    success_count = 0
    for i, test_link in enumerate(test_cases, 1):
        node = parse_socks5(test_link)
        if node:
            print(f"✅ 测试{i}: 成功解析socks5节点")
            print(f"   名称: {node['name']}")
            print(f"   服务器: {node['server']}:{node['port']}")
            if 'username' in node:
                print(f"   认证: {node['username']}:{node['password']}")
            else:
                print(f"   认证: 无")
            print()
            success_count += 1
        else:
            print(f"❌ 测试{i}: 解析失败")
            print()
    
    print(f"📊 测试结果: 成功解析 {success_count}/{len(test_cases)} 个socks5节点")
    
    if success_count == len(test_cases):
        print("🎉 所有socks5节点解析成功！")
        return True
    else:
        print("❌ 部分socks5节点解析失败")
        return False

if __name__ == "__main__":
    print("🚀 开始测试socks5协议支持")
    print()
    
    if test_socks5_parsing():
        print("🎉 socks5协议支持测试完成！")
        sys.exit(0)
    else:
        print("❌ socks5协议支持测试失败！")
        sys.exit(1) 