#!/bin/bash

# 创建缺失的启动脚本

echo "🔧 创建缺失的启动脚本"
echo "======================"

# 检查是否已安装
if [ ! -d "/root/OpenClashManage" ]; then
    echo "❌ 未找到 OpenClash 节点管理系统"
    echo "请先运行安装脚本: wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/install.sh | bash"
    exit 1
fi

echo "✅ 检测到已安装的系统"

# 创建启动脚本
echo ""
echo "📋 创建启动脚本 (start.sh)"
cat > /root/OpenClashManage/start.sh << 'EOF'
#!/bin/bash

# 启动 OpenClash 节点管理系统

echo "🚀 启动 OpenClash 节点管理系统..."

# 切换到工作目录
cd /root/OpenClashManage

# 启动 Web 编辑器
echo "📱 启动 Web 编辑器..."
nohup python3 web_editor.py > /dev/null 2>&1 &
WEB_PID=$!
echo "✅ Web 编辑器已启动 (PID: $WEB_PID)"
echo "📱 访问地址: http://$(hostname -I | awk '{print $1}'):5000"

# 启动守护进程
echo "🔄 启动守护进程..."
nohup ./jk.sh > /dev/null 2>&1 &
DAEMON_PID=$!
echo "✅ 守护进程已启动 (PID: $DAEMON_PID)"

# 保存 PID 到文件
echo "$WEB_PID" > /tmp/openclash_web.pid
echo "$DAEMON_PID" > /tmp/openclash_daemon.pid

echo "🎉 所有服务启动完成！"
echo "📱 Web编辑器: http://$(hostname -I | awk '{print $1}'):5000"
echo "📁 配置文件: /root/OpenClashManage/wangluo/"
echo "📝 日志文件: /root/OpenClashManage/wangluo/log.txt"
EOF

# 创建停止脚本
echo "📋 创建停止脚本 (stop.sh)"
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

# 创建状态检查脚本
echo "📋 创建状态检查脚本 (status.sh)"
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

# 创建开机自启动脚本
echo "📋 创建开机自启动脚本 (autostart.sh)"
cat > /root/OpenClashManage/autostart.sh << 'EOF'
#!/bin/bash
cd /root/OpenClashManage
./start.sh
EOF

# 设置执行权限
echo ""
echo "📋 设置脚本权限"
chmod +x /root/OpenClashManage/start.sh
chmod +x /root/OpenClashManage/stop.sh
chmod +x /root/OpenClashManage/status.sh
chmod +x /root/OpenClashManage/autostart.sh

echo "✅ 所有脚本权限已设置"

# 验证文件创建
echo ""
echo "📋 验证文件创建"
scripts=("start.sh" "stop.sh" "status.sh" "autostart.sh")

for script in "${scripts[@]}"; do
    if [ -f "/root/OpenClashManage/$script" ]; then
        echo "✅ $script 已创建"
        if [ -x "/root/OpenClashManage/$script" ]; then
            echo "✅ $script 有执行权限"
        else
            echo "❌ $script 没有执行权限"
        fi
    else
        echo "❌ $script 创建失败"
    fi
done

echo ""
echo "🎉 脚本创建完成！"
echo ""
echo "💡 使用方法:"
echo "  启动服务: cd /root/OpenClashManage && ./start.sh"
echo "  停止服务: cd /root/OpenClashManage && ./stop.sh"
echo "  查看状态: cd /root/OpenClashManage && ./status.sh"
echo ""
echo "🔍 测试启动:"
echo "  cd /root/OpenClashManage && ./start.sh" 