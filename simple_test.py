#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jx import parse_nodes
import tempfile
import os

def test_socks5():
    """简单测试socks5协议解析"""
    
    # 创建测试内容
    test_content = """# 测试socks5协议
socks5://user123:pass456@server1.com:1080#Socks5节点1
socks5://server2.com:1080#Socks5节点2（无认证）
"""
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # 解析节点
        nodes = parse_nodes(temp_file)
        
        print("🧪 测试socks5协议解析")
        print("=" * 40)
        
        for i, node in enumerate(nodes, 1):
            if node.get("type") == "socks5":
                print(f"✅ 节点{i}: {node['name']}")
                print(f"   服务器: {node['server']}:{node['port']}")
                if 'username' in node:
                    print(f"   认证: {node['username']}:{node['password']}")
                else:
                    print(f"   认证: 无")
                print()
        
        print(f"📊 成功解析 {len([n for n in nodes if n.get('type') == 'socks5'])} 个socks5节点")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    print("🚀 开始测试socks5协议支持")
    print()
    
    if test_socks5():
        print("🎉 socks5协议支持测试成功！")
    else:
        print("❌ socks5协议支持测试失败！") 