#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jx import parse_nodes
import tempfile

def test_socks5_parsing():
    """测试socks5协议解析功能"""
    
    # 创建临时测试文件
    test_content = """# 测试socks5协议解析
socks5://user123:pass456@server1.com:1080#Socks5节点1
socks5://server2.com:1080#Socks5节点2（无认证）
socks5://admin:secret@proxy.example.com:1080#Socks5节点3
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # 解析节点
        nodes = parse_nodes(temp_file)
        
        print("🧪 测试socks5协议解析")
        print("=" * 50)
        
        success_count = 0
        for node in nodes:
            if node.get("type") == "socks5":
                print(f"✅ 成功解析socks5节点: {node['name']}")
                print(f"   服务器: {node['server']}:{node['port']}")
                if 'username' in node:
                    print(f"   认证: {node['username']}:{node['password']}")
                else:
                    print(f"   认证: 无")
                print()
                success_count += 1
        
        print(f"📊 测试结果: 成功解析 {success_count} 个socks5节点")
        
        if success_count == 3:
            print("🎉 所有socks5节点解析成功！")
            return True
        else:
            print("❌ 部分socks5节点解析失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_socks5_formats():
    """测试各种socks5格式"""
    
    test_cases = [
        ("socks5://user:pass@server.com:1080#测试节点", "带认证的socks5"),
        ("socks5://server.com:1080#测试节点", "无认证的socks5"),
        ("socks5://admin:secret@proxy.example.com:1080", "无名称的socks5"),
        ("socks5://user:pass@server.com:1080", "无名称带认证"),
    ]
    
    print("🧪 测试各种socks5格式")
    print("=" * 50)
    
    for i, (test_link, description) in enumerate(test_cases, 1):
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_link + "\n")
                temp_file = f.name
            
            # 解析节点
            nodes = parse_nodes(temp_file)
            
            if nodes and nodes[0].get("type") == "socks5":
                node = nodes[0]
                print(f"✅ 测试{i}: {description}")
                print(f"   名称: {node['name']}")
                print(f"   服务器: {node['server']}:{node['port']}")
                if 'username' in node:
                    print(f"   认证: {node['username']}:{node['password']}")
                else:
                    print(f"   认证: 无")
                print()
            else:
                print(f"❌ 测试{i}: {description} - 解析失败")
                print()
                
        except Exception as e:
            print(f"❌ 测试{i}: {description} - 错误: {e}")
            print()
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

if __name__ == "__main__":
    print("🚀 开始测试socks5协议支持")
    print()
    
    # 测试基本解析功能
    test1_result = test_socks5_parsing()
    print()
    
    # 测试各种格式
    test_socks5_formats()
    
    if test1_result:
        print("🎉 socks5协议支持测试完成！")
        sys.exit(0)
    else:
        print("❌ socks5协议支持测试失败！")
        sys.exit(1) 