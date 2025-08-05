#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
诊断自启动问题
检查 OpenClash 节点管理系统的自启动配置
"""

import os
import subprocess
import platform

def check_file_exists(file_path):
    """检查文件是否存在"""
    return os.path.exists(file_path)

def check_file_executable(file_path):
    """检查文件是否有执行权限"""
    if not os.path.exists(file_path):
        return False
    return os.access(file_path, os.X_OK)

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_initd_service():
    """检查 init.d 服务"""
    service_file = "/etc/init.d/openclash-manage"
    if check_file_exists(service_file):
        if check_file_executable(service_file):
            return True, "✅ init.d 服务文件存在且有执行权限"
        else:
            return False, "⚠️  init.d 服务文件存在但无执行权限"
    else:
        return False, "❌ init.d 服务文件不存在"

def check_crontab():
    """检查 crontab 配置"""
    try:
        result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            crontab_content = result.stdout
            if "@reboot" in crontab_content and "OpenClashManage" in crontab_content:
                return True, "✅ crontab 自启动已配置"
            else:
                return False, "❌ crontab 中未找到自启动配置"
        else:
            return False, "⚠️  无法检查 crontab: " + result.stderr.strip()
    except Exception as e:
        return False, f"⚠️  无法检查 crontab: {e}"

def check_start_scripts():
    """检查启动脚本"""
    scripts = [
        "/root/OpenClashManage/start.sh",
        "/root/OpenClashManage/stop.sh", 
        "/root/OpenClashManage/status.sh",
        "/root/OpenClashManage/autostart.sh"
    ]
    
    results = []
    for script in scripts:
        if check_file_exists(script):
            if check_file_executable(script):
                results.append(f"✅ {os.path.basename(script)} 存在且有执行权限")
            else:
                results.append(f"⚠️  {os.path.basename(script)} 存在但无执行权限")
        else:
            results.append(f"❌ {os.path.basename(script)} 不存在")
    
    return results

def check_system_type():
    """检查系统类型"""
    if check_file_exists("/etc/openwrt_release"):
        return "OpenWrt"
    elif platform.system() == "Linux":
        return "Linux"
    else:
        return "Unknown"

def main():
    """主函数"""
    print("🔍 诊断自启动问题")
    print("=" * 60)
    
    # 检查系统类型
    system_type = check_system_type()
    print(f"📋 系统类型: {system_type}")
    print()
    
    # 检查 init.d 服务
    print("📋 1. 检查 init.d 服务")
    initd_ok, initd_msg = check_initd_service()
    print(initd_msg)
    print()
    
    # 检查 crontab
    print("📋 2. 检查 crontab 配置")
    crontab_ok, crontab_msg = check_crontab()
    print(crontab_msg)
    print()
    
    # 检查启动脚本
    print("📋 3. 检查启动脚本")
    script_results = check_start_scripts()
    for result in script_results:
        print(result)
    print()
    
    # 检查系统类型
    print("📋 4. 检查系统类型")
    if system_type == "OpenWrt":
        print("✅ 检测到 OpenWrt 系统")
    elif system_type == "Linux":
        print("⚠️  检测到 Linux 系统（非 OpenWrt）")
    else:
        print("❌ 未知系统类型")
    print()
    
    # 修复建议
    print("📋 5. 修复建议")
    if not initd_ok or not crontab_ok:
        print("如果自启动不可用，请尝试以下步骤：")
        print()
        print("方法1: 重新启用 init.d 服务")
        print("  /etc/init.d/openclash-manage enable")
        print("  /etc/init.d/openclash-manage start")
        print()
        print("方法2: 手动设置 crontab")
        print("  (crontab -l 2>/dev/null; echo '@reboot /root/OpenClashManage/autostart.sh') | crontab -")
        print()
        print("方法3: 重新运行安装脚本")
        print("  wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/install.sh | bash")
        print()
        print("方法4: 手动启用自启动")
        print("  wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/enable_autostart.sh | bash")
        print()
        print("方法5: 快速修复自启动")
        print("  wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/quick_autostart_fix.sh | bash")
    else:
        print("✅ 自启动配置正常")
        print("💡 可以使用以下命令管理服务：")
        print("  /etc/init.d/openclash-manage {start|stop|restart|status}")

if __name__ == "__main__":
    main() 