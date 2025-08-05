#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 socks 协议解析功能
验证用户名和密码是否正确解析
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jx import parse_nodes
import tempfile

def test_socks_parsing():
    """测试 socks 协议解析"""
    
    # 测试用例 - 包含用户名和密码的 socks 链接
    test_cases = [
        # 带认证的 socks 链接
        "socks://user123:pass456@server1.com:1080#Socks节点1",
        "socks5://user123:pass456@server1.com:1080#Socks5节点1",
        "socks://admin:secret@proxy.example.com:1080#管理节点",
        "socks5://testuser:testpass@testserver.com:1080#测试节点",
        
        # 无认证的 socks 链接
        "socks://server2.com:1080#Socks节点2",
        "socks5://server2.com:1080#Socks5节点2",
        
        # 其他协议作为对比
        "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@server.com:8388#SS节点",
    ]
    
    print("🧪 测试 socks 协议解析")
    print("=" * 50)
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        for test_case in test_cases:
            f.write(test_case + '\n')
        temp_file = f.name
    
    try:
        # 解析节点
        parsed_nodes = parse_nodes(temp_file)
        
        print(f"📊 解析结果: 成功解析 {len(parsed_nodes)} 个节点")
        print()
        
        # 显示解析结果
        for i, node in enumerate(parsed_nodes, 1):
            print(f"节点 {i}:")
            print(f"  名称: {node.get('name', 'N/A')}")
            print(f"  类型: {node.get('type', 'N/A')}")
            print(f"  服务器: {node.get('server', 'N/A')}")
            print(f"  端口: {node.get('port', 'N/A')}")
            
            # 显示认证信息（如果有）
            if 'username' in node:
                print(f"  用户名: {node.get('username', 'N/A')}")
                print(f"  密码: {node.get('password', 'N/A')}")
                print(f"  ✅ 认证信息已解析")
            else:
                print(f"  ⚠️  无认证信息")
            
            print()
        
        # 统计 socks 节点
        socks_nodes = [node for node in parsed_nodes if node.get('type') == 'socks5']
        socks_with_auth = [node for node in socks_nodes if 'username' in node]
        socks_without_auth = [node for node in socks_nodes if 'username' not in node]
        
        print("📈 统计结果:")
        print(f"  - 总节点数: {len(parsed_nodes)}")
        print(f"  - Socks5节点: {len(socks_nodes)}")
        print(f"  - 带认证的Socks: {len(socks_with_auth)}")
        print(f"  - 无认证的Socks: {len(socks_without_auth)}")
        
        # 验证解析结果
        if len(socks_with_auth) > 0:
            print("🎉 socks 协议用户名密码解析正常！")
            return True
        else:
            print("❌ 未找到带认证的 socks 节点")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    success = test_socks_parsing()
    sys.exit(0 if success else 1) 