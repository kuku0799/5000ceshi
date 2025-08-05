#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的启动脚本
验证 start.sh, stop.sh, status.sh 脚本
"""

import os
import tempfile

def test_start_scripts():
    """测试启动脚本"""
    
    print("🧪 测试新的启动脚本")
    print("=" * 50)
    
    # 检查脚本文件是否存在
    scripts = ['start.sh', 'stop.sh', 'status.sh', 'autostart.sh']
    
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script} 存在")
        else:
            print(f"❌ {script} 不存在")
    
    print()
    print("📋 脚本功能说明:")
    print("  - start.sh: 启动 Web 编辑器和守护进程")
    print("  - stop.sh: 停止所有服务")
    print("  - status.sh: 检查服务状态")
    print("  - autostart.sh: 开机自启动脚本")
    
    print()
    print("🔧 使用方法:")
    print("  1. 安装时自动设置开机自启动")
    print("  2. 手动启动: cd /root/OpenClashManage && ./start.sh")
    print("  3. 手动停止: cd /root/OpenClashManage && ./stop.sh")
    print("  4. 状态检查: cd /root/OpenClashManage && ./status.sh")
    print("  5. 服务管理: /etc/init.d/openclash-manage {start|stop|restart|status}")

if __name__ == "__main__":
    test_start_scripts() 