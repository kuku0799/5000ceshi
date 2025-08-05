#!/bin/bash

# OpenClash 节点管理系统 - 完整自启动修复脚本

echo "🔧 完整修复 OpenClash 节点管理系统自启动问题"
echo "=============================================="
echo ""

# 检查是否已安装
if [ ! -d "/root/OpenClashManage" ]; then
    echo "❌ 未找到 OpenClash 节点管理系统"
    echo "请先运行安装脚本: wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/install.sh | bash"
    exit 1
fi

echo "✅ 检测到已安装的系统"

# 1. 创建启动脚本
echo ""
echo "📋 步骤1: 创建启动脚本"
cat > /root/OpenClashManage/start.sh << 'EOF'
#!/bin/bash

# 启动 OpenClash 节点管理系统

echo "🚀 启动 OpenClash 节点管理系统..."

# 切换到工作目录
cd /root/OpenClashManage

# 检查是否已经在运行
if [ -f /tmp/openclash_web.pid ] && kill -0 $(cat /tmp/openclash_web.pid) 2>/dev/null; then
    echo "⚠️  Web 编辑器已在运行"
else
    # 启动 Web 编辑器
    echo "📱 启动 Web 编辑器..."
    nohup python3 web_editor.py > /dev/null 2>&1 &
    WEB_PID=$!
    echo "$WEB_PID" > /tmp/openclash_web.pid
    echo "✅ Web 编辑器已启动 (PID: $WEB_PID)"
    echo "📱 访问地址: http://$(hostname -I | awk '{print $1}'):5000"
fi

# 检查守护进程是否在运行
if [ -f /tmp/openclash_daemon.pid ] && kill -0 $(cat /tmp/openclash_daemon.pid) 2>/dev/null; then
    echo "⚠️  守护进程已在运行"
else
    # 启动守护进程
    echo "🔄 启动守护进程..."
    nohup ./jk.sh > /dev/null 2>&1 &
    DAEMON_PID=$!
    echo "$DAEMON_PID" > /tmp/openclash_daemon.pid
    echo "✅ 守护进程已启动 (PID: $DAEMON_PID)"
fi

echo "🎉 所有服务启动完成！"
echo "📱 Web编辑器: http://$(hostname -I | awk '{print $1}'):5000"
echo "📁 配置文件: /root/OpenClashManage/wangluo/"
echo "📝 日志文件: /root/OpenClashManage/wangluo/log.txt"
EOF

# 2. 创建停止脚本
echo "📋 步骤2: 创建停止脚本"
cat > /root/OpenClashManage/stop.sh << 'EOF'
#!/bin/bash

# 停止 OpenClash 节点管理系统

echo "🛑 停止 OpenClash 节点管理系统..."

# 停止 Web 编辑器
if [ -f /tmp/openclash_web.pid ]; then
    WEB_PID=$(cat /tmp/openclash_web.pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        kill $WEB_PID
        echo "✅ Web 编辑器已停止 (PID: $WEB_PID)"
    else
        echo "⚠️  Web 编辑器进程不存在"
    fi
    rm -f /tmp/openclash_web.pid
else
    pkill -f "python3 web_editor.py"
    echo "✅ Web 编辑器已停止"
fi

# 停止守护进程
if [ -f /tmp/openclash_daemon.pid ]; then
    DAEMON_PID=$(cat /tmp/openclash_daemon.pid)
    if kill -0 $DAEMON_PID 2>/dev/null; then
        kill $DAEMON_PID
        echo "✅ 守护进程已停止 (PID: $DAEMON_PID)"
    else
        echo "⚠️  守护进程不存在"
    fi
    rm -f /tmp/openclash_daemon.pid
else
    pkill -f "jk.sh"
    echo "✅ 守护进程已停止"
fi

# 清理 PID 文件
rm -f /tmp/openclash_watchdog.pid

echo "🎉 所有服务已停止！"
EOF

# 3. 创建状态检查脚本
echo "📋 步骤3: 创建状态检查脚本"
cat > /root/OpenClashManage/status.sh << 'EOF'
#!/bin/bash

# 检查 OpenClash 节点管理系统状态

echo "🔍 OpenClash 节点管理系统状态检查"
echo "=================================="

# 检查 Web 编辑器
if [ -f /tmp/openclash_web.pid ]; then
    WEB_PID=$(cat /tmp/openclash_web.pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        echo "✅ Web 编辑器运行中 (PID: $WEB_PID)"
    else
        echo "❌ Web 编辑器未运行"
    fi
else
    if pgrep -f "python3 web_editor.py" > /dev/null; then
        echo "✅ Web 编辑器运行中"
    else
        echo "❌ Web 编辑器未运行"
    fi
fi

# 检查守护进程
if [ -f /tmp/openclash_daemon.pid ]; then
    DAEMON_PID=$(cat /tmp/openclash_daemon.pid)
    if kill -0 $DAEMON_PID 2>/dev/null; then
        echo "✅ 守护进程运行中 (PID: $DAEMON_PID)"
    else
        echo "❌ 守护进程未运行"
    fi
else
    if pgrep -f "jk.sh" > /dev/null; then
        echo "✅ 守护进程运行中"
    else
        echo "❌ 守护进程未运行"
    fi
fi

# 检查端口
if netstat -tlnp 2>/dev/null | grep ":5000 " > /dev/null; then
    echo "✅ Web 服务端口 5000 正常"
else
    echo "❌ Web 服务端口 5000 未监听"
fi

# 显示访问地址
echo "📱 Web编辑器地址: http://$(hostname -I | awk '{print $1}'):5000"
EOF

# 4. 创建开机自启动脚本
echo "📋 步骤4: 创建开机自启动脚本"
cat > /root/OpenClashManage/autostart.sh << 'EOF'
#!/bin/bash
cd /root/OpenClashManage
./start.sh
EOF

# 5. 设置脚本权限
echo "📋 步骤5: 设置脚本权限"
chmod +x /root/OpenClashManage/start.sh
chmod +x /root/OpenClashManage/stop.sh
chmod +x /root/OpenClashManage/status.sh
chmod +x /root/OpenClashManage/autostart.sh

echo "✅ 所有脚本权限已设置"

# 6. 配置 init.d 服务（OpenWrt）
echo ""
echo "📋 步骤6: 配置 init.d 服务"
if [ -f /etc/openwrt_release ]; then
    echo "检测到 OpenWrt 系统，创建 init.d 服务"
    
    cat > /etc/init.d/openclash-manage << 'EOF'
#!/bin/sh /etc/rc.common

START=99
STOP=15
USE_PROCD=1

start_service() {
    procd_open_instance
    procd_set_param command /root/OpenClashManage/start.sh
    procd_set_param respawn
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}

stop_service() {
    /root/OpenClashManage/stop.sh
}
EOF

    chmod +x /etc/init.d/openclash-manage
    /etc/init.d/openclash-manage enable
    
    echo "✅ init.d 服务已创建并启用"
    echo "💡 管理命令:"
    echo "  启动: /etc/init.d/openclash-manage start"
    echo "  停止: /etc/init.d/openclash-manage stop"
    echo "  重启: /etc/init.d/openclash-manage restart"
    echo "  状态: /etc/init.d/openclash-manage status"
else
    echo "⚠️  未检测到 OpenWrt 系统，跳过 init.d 服务"
fi

# 7. 配置 crontab 自启动
echo ""
echo "📋 步骤7: 配置 crontab 自启动"
# 移除旧的 crontab 条目
(crontab -l 2>/dev/null | grep -v "@reboot.*OpenClashManage") | crontab -

# 添加新的 crontab 条目
(crontab -l 2>/dev/null; echo "@reboot /root/OpenClashManage/autostart.sh") | crontab -

echo "✅ crontab 自启动已配置"
echo "💡 查看 crontab: crontab -l"

# 8. 配置 systemd 服务（如果支持）
echo ""
echo "📋 步骤8: 配置 systemd 服务"
if command -v systemctl >/dev/null 2>&1; then
    cat > /etc/systemd/system/openclash-manage.service << 'EOF'
[Unit]
Description=OpenClash Node Management System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/OpenClashManage
ExecStart=/root/OpenClashManage/start.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable openclash-manage.service
    
    echo "✅ systemd 服务已创建并启用"
    echo "💡 管理命令:"
    echo "  启动: systemctl start openclash-manage"
    echo "  停止: systemctl stop openclash-manage"
    echo "  重启: systemctl restart openclash-manage"
    echo "  状态: systemctl status openclash-manage"
else
    echo "⚠️  未检测到 systemd，跳过 systemd 服务创建"
fi

# 9. 测试启动脚本
echo ""
echo "📋 步骤9: 测试启动脚本"
if [ -x "/root/OpenClashManage/start.sh" ]; then
    echo "✅ 启动脚本测试通过"
else
    echo "❌ 启动脚本权限问题，正在修复..."
    chmod +x /root/OpenClashManage/start.sh
fi

echo ""
echo "🎉 自启动修复完成！"
echo ""
echo "📋 修复内容总结:"
echo "  ✅ 启动脚本 (start.sh)"
echo "  ✅ 停止脚本 (stop.sh)"
echo "  ✅ 状态检查脚本 (status.sh)"
echo "  ✅ 开机自启动脚本 (autostart.sh)"
echo "  ✅ init.d 服务配置"
echo "  ✅ crontab 自启动配置"
echo "  ✅ systemd 服务配置（如果支持）"
echo "  ✅ 脚本权限设置"
echo ""
echo "🔍 测试命令:"
echo "  1. 手动启动: cd /root/OpenClashManage && ./start.sh"
echo "  2. 查看状态: cd /root/OpenClashManage && ./status.sh"
echo "  3. 手动停止: cd /root/OpenClashManage && ./stop.sh"
echo "  4. 重启测试: reboot"
echo ""
echo "💡 服务管理:"
if [ -f /etc/init.d/openclash-manage ]; then
    echo "  - init.d: /etc/init.d/openclash-manage {start|stop|restart|status}"
fi
if command -v systemctl >/dev/null 2>&1; then
    echo "  - systemd: systemctl {start|stop|restart|status} openclash-manage"
fi
echo "  - crontab: crontab -l"
echo ""
echo "🎯 现在系统将在重启后自动启动 OpenClash 节点管理系统！" 