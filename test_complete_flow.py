#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整测试流程
验证从节点解析到配置注入的整个流程
"""

import sys
import os
import tempfile

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jx import parse_nodes, decode_base64
from zw import inject_proxies
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

def test_complete_flow():
    """测试完整流程"""
    
    print("🧪 测试完整流程：解析 -> 注入")
    print("=" * 60)
    
    # 用户的实际链接
    your_link = "socks://dXNlcmI6cGFzc3dvcmRi@iplc.hulicn.com:52731#ccccc"
    
    print(f"📝 测试链接: {your_link}")
    print()
    
    # 1. 测试 Base64 解码
    print("🔍 步骤1: Base64 解码测试")
    try:
        base64_part = "dXNlcmI6cGFzc3dvcmRi"
        decoded = decode_base64(base64_part)
        print(f"Base64 解码结果: {decoded}")
        
        if ":" in decoded:
            username, password = decoded.split(":", 1)
            print(f"✅ 用户名: {username}")
            print(f"✅ 密码: {password}")
        else:
            print("❌ Base64 解码后格式不正确")
    except Exception as e:
        print(f"❌ Base64 解码失败: {e}")
    
    print()
    
    # 2. 测试节点解析
    print("🔍 步骤2: 节点解析测试")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(your_link + '\n')
        temp_file = f.name
    
    try:
        parsed_nodes = parse_nodes(temp_file)
        print(f"解析结果: {len(parsed_nodes)} 个节点")
        
        for i, node in enumerate(parsed_nodes, 1):
            print(f"\n节点 {i}:")
            print(f"  名称: {node.get('name', 'N/A')}")
            print(f"  类型: {node.get('type', 'N/A')}")
            print(f"  服务器: {node.get('server', 'N/A')}")
            print(f"  端口: {node.get('port', 'N/A')}")
            
            if 'username' in node:
                print(f"  ✅ 用户名: {node.get('username', 'N/A')}")
                print(f"  ✅ 密码: {node.get('password', 'N/A')}")
            else:
                print(f"  ❌ 无认证信息")
        
        # 3. 测试配置注入
        print("\n🔍 步骤3: 配置注入测试")
        
        # 创建模拟的 OpenClash 配置
        mock_config = {
            "proxies": [
                {
                    "name": "existing_proxy",
                    "type": "ss",
                    "server": "existing.com",
                    "port": 8388
                }
            ]
        }
        
        # 注入节点
        updated_config, injected_count, invalid_count, duplicate_count = inject_proxies(mock_config, parsed_nodes)
        
        print(f"注入结果:")
        print(f"  - 注入节点数: {injected_count}")
        print(f"  - 无效节点数: {invalid_count}")
        print(f"  - 重复节点数: {duplicate_count}")
        
        # 显示最终的 proxies 配置
        print(f"\n最终配置中的 proxies:")
        for i, proxy in enumerate(updated_config.get("proxies", []), 1):
            print(f"\n代理 {i}:")
            print(f"  名称: {proxy.get('name', 'N/A')}")
            print(f"  类型: {proxy.get('type', 'N/A')}")
            print(f"  服务器: {proxy.get('server', 'N/A')}")
            print(f"  端口: {proxy.get('port', 'N/A')}")
            
            if 'username' in proxy:
                print(f"  ✅ 用户名: {proxy.get('username', 'N/A')}")
                print(f"  ✅ 密码: {proxy.get('password', 'N/A')}")
            else:
                print(f"  ❌ 无认证信息")
        
        # 验证结果
        if len(parsed_nodes) > 0 and 'username' in parsed_nodes[0]:
            print("\n🎉 完整流程测试成功！")
            return True
        else:
            print("\n❌ 完整流程测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1) 