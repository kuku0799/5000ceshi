#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试用户的 socks 链接解析
验证 Base64 编码的用户名和密码是否正确解析
"""

import sys
import os
import base64

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jx import parse_nodes, decode_base64
import tempfile

def test_your_socks_link():
    """测试用户的 socks 链接"""
    
    # 用户的实际链接
    your_link = "socks://dXNlcmI6cGFzc3dvcmRi@iplc.hulicn.com:52731#ccccc"
    
    print("🧪 测试你的 socks 链接解析")
    print("=" * 50)
    print(f"原始链接: {your_link}")
    print()
    
    # 手动解析 Base64 部分
    try:
        # 提取 Base64 部分
        base64_part = "dXNlcmI6cGFzc3dvcmRi"
        decoded = decode_base64(base64_part)
        print(f"Base64 解码结果: {decoded}")
        
        if ":" in decoded:
            username, password = decoded.split(":", 1)
            print(f"解码后的用户名: {username}")
            print(f"解码后的密码: {password}")
        else:
            print("❌ Base64 解码后格式不正确")
    except Exception as e:
        print(f"❌ Base64 解码失败: {e}")
    
    print()
    
    # 创建临时文件进行完整测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(your_link + '\n')
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
        
        # 验证解析结果
        if len(parsed_nodes) > 0 and 'username' in parsed_nodes[0]:
            print("🎉 你的 socks 链接解析成功！")
            return True
        else:
            print("❌ socks 链接解析失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    success = test_your_socks_link()
    sys.exit(0 if success else 1) 