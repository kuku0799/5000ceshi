#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查用户的 nodes.txt 文件
查看实际的文件内容
"""

import os

def check_nodes_file():
    """检查 nodes.txt 文件"""
    
    nodes_file = "wangluo/nodes.txt"
    
    print("🔍 检查 nodes.txt 文件")
    print("=" * 50)
    
    if not os.path.exists(nodes_file):
        print(f"❌ 文件不存在: {nodes_file}")
        return
    
    try:
        with open(nodes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"文件大小: {len(content)} 字节")
        print(f"文件内容:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        # 分析内容
        lines = content.split('\n')
        actual_nodes = [line for line in lines if line.strip() and not line.startswith('#')]
        
        print(f"\n📊 分析结果:")
        print(f"  - 总行数: {len(lines)}")
        print(f"  - 实际节点数: {len(actual_nodes)}")
        
        if actual_nodes:
            print(f"  - 节点列表:")
            for i, node in enumerate(actual_nodes, 1):
                print(f"    {i}. {node}")
        else:
            print("  ⚠️  没有找到实际的节点链接")
            print("  💡 请将你的 socks 链接添加到文件中:")
            print("     socks://dXNlcmI6cGFzc3dvcmRi@iplc.hulicn.com:52731#ccccc")
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

if __name__ == "__main__":
    check_nodes_file() 