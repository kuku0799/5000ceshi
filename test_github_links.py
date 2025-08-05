#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 一键部署链接测试脚本
测试所有必要的文件是否可以从 GitHub 正常下载
"""

import requests
import sys
import time
from urllib.parse import urljoin

# GitHub 仓库配置
GITHUB_USER = "kuku0799"
GITHUB_REPO = "5000ceshi"
GITHUB_BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# 需要测试的文件列表
FILES_TO_TEST = [
    "deploy.sh",           # 一键部署脚本
    "jk.sh",              # 守护进程脚本
    "zr.py",              # 主控制器
    "jx.py",              # 节点解析器
    "zw.py",              # 代理注入器
    "zc.py",              # 策略组注入器
    "log.py",             # 日志管理器
    "web_editor.py",      # Web服务器
    "templates/index.html", # 前端界面
    "requirements.txt",    # Python依赖
    "start_web_editor.sh", # 启动脚本
    "README.md",          # 说明文档
    "GITHUB_DEPLOY.md",   # 部署指南
]

def test_url(url, timeout=10):
    """测试URL是否可访问"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, response.status_code, len(response.content)
        else:
            return False, response.status_code, 0
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)

def print_header():
    """打印测试头部信息"""
    print("🚀 GitHub 一键部署链接测试")
    print("=" * 50)
    print(f"仓库: https://github.com/{GITHUB_USER}/{GITHUB_REPO}")
    print(f"分支: {GITHUB_BRANCH}")
    print(f"基础URL: {BASE_URL}")
    print("=" * 50)
    print()

def print_result(filename, success, status_code, content_length):
    """打印测试结果"""
    if success:
        print(f"✅ {filename:<25} | 状态: {status_code} | 大小: {content_length:,} 字节")
    else:
        print(f"❌ {filename:<25} | 状态: {status_code} | 错误: {content_length}")

def test_all_files():
    """测试所有文件"""
    print_header()
    
    total_files = len(FILES_TO_TEST)
    successful_files = 0
    failed_files = []
    
    print("📋 开始测试文件可访问性...")
    print()
    
    for filename in FILES_TO_TEST:
        url = urljoin(BASE_URL + "/", filename)
        success, status_code, content_length = test_url(url)
        
        print_result(filename, success, status_code, content_length)
        
        if success:
            successful_files += 1
        else:
            failed_files.append(filename)
        
        # 避免请求过于频繁
        time.sleep(0.5)
    
    print()
    print("=" * 50)
    print(f"📊 测试结果: {successful_files}/{total_files} 个文件可访问")
    
    if failed_files:
        print(f"❌ 失败的文件: {', '.join(failed_files)}")
    else:
        print("🎉 所有文件都可以正常访问！")
    
    return successful_files == total_files

def generate_deploy_commands():
    """生成部署命令"""
    print()
    print("🚀 一键部署命令:")
    print("-" * 30)
    print("方法1 (wget):")
    print(f"wget -O - {BASE_URL}/deploy.sh | bash")
    print()
    print("方法2 (curl):")
    print(f"curl -sSL {BASE_URL}/deploy.sh | bash")
    print()
    print("方法3 (手动下载):")
    print(f"wget {BASE_URL}/deploy.sh")
    print("bash deploy.sh")

def main():
    """主函数"""
    print("🔍 正在测试 GitHub 一键部署链接...")
    print()
    
    # 测试所有文件
    all_success = test_all_files()
    
    # 生成部署命令
    generate_deploy_commands()
    
    print()
    if all_success:
        print("🎉 GitHub 一键部署配置完成！")
        print("✅ 所有文件都可以正常访问")
        print("✅ 用户可以使用一键部署命令快速安装")
    else:
        print("⚠️  部分文件无法访问，请检查 GitHub 仓库配置")
        print("❌ 需要修复失败的文件链接")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main()) 