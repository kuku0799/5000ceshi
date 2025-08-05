#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试 socks 链接格式
分析为什么用户名和密码没有正确解析
"""

from urllib.parse import urlparse

def debug_socks_link(link):
    """调试 socks 链接格式"""
    print(f"🔍 调试链接: {link}")
    print("=" * 50)
    
    # 检查协议
    if link.startswith("socks://"):
        protocol = "socks://"
    elif link.startswith("socks5://"):
        protocol = "socks5://"
    else:
        print("❌ 不是 socks 协议")
        return
    
    # 提取 body 部分
    body = link[len(protocol):].split("#")[0]
    print(f"Body: {body}")
    
    # 解析 URL
    parsed = urlparse("//" + body)
    print(f"Parsed URL:")
    print(f"  Username: {parsed.username}")
    print(f"  Password: {parsed.password}")
    print(f"  Hostname: {parsed.hostname}")
    print(f"  Port: {parsed.port}")
    print(f"  Path: {parsed.path}")
    print(f"  Query: {parsed.query}")
    
    # 检查是否有认证信息
    if parsed.username and parsed.password:
        print("✅ 找到用户名和密码")
    else:
        print("❌ 未找到用户名和密码")
    
    print()

# 测试你的实际链接
test_links = [
    "socks://dXNlcmI6cGFzc3dvcmRi@i",
    "socks://user:pass@server.com:1080#测试节点",
    "socks5://user:pass@server.com:1080#测试节点",
    "socks://server.com:1080#无认证节点",
]

for link in test_links:
    debug_socks_link(link) 