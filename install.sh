#!/bin/bash

# OpenClash 节点管理系统一键安装脚本
# 适用于 OpenWrt 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 安装 Python3
install_python3() {
    log_step "安装 Python3..."
    
    if command -v python3 &> /dev/null; then
        log_info "Python3 已安装"
        return 0
    fi
    
    # 更新软件包列表
    opkg update
    
    # 安装 Python3 和相关包
    log_info "正在安装 Python3..."
    opkg install python3 python3-pip python3-requests python3-yaml python3-ruamel-yaml
    
    # 验证安装
    if command -v python3 &> /dev/null; then
        log_info "Python3 安装成功"
        return 0
    else
        log_error "Python3 安装失败"
        return 1
    fi
}

# 安装 pip3
install_pip3() {
    log_step "安装 pip3..."
    
    if command -v pip3 &> /dev/null; then
        log_info "pip3 已安装"
        return 0
    fi
    
    # 尝试安装 pip3
    opkg install python3-pip
    
    # 验证安装
    if command -v pip3 &> /dev/null; then
        log_info "pip3 安装成功"
        return 0
    else
        log_warn "pip3 安装失败，将使用 opkg 安装依赖"
        return 1
    fi
}

# 检查系统
check_system() {
    log_step "检查系统环境..."
    
    # 检查是否为 OpenWrt
    if [ ! -f "/etc/openwrt_release" ]; then
        log_warn "未检测到 OpenWrt 系统，但继续安装..."
    fi
    
    # 检查并安装 Python3
    if ! command -v python3 &> /dev/null; then
        log_warn "Python3 未安装，正在自动安装..."
        if ! install_python3; then
            log_error "无法安装 Python3，请手动安装后重试"
            log_info "手动安装命令：opkg update && opkg install python3 python3-pip"
            exit 1
        fi
    fi
    
    # 检查并安装 pip3
    if ! command -v pip3 &> /dev/null; then
        log_warn "pip3 未安装，正在自动安装..."
        install_pip3
    fi
    
    # 检查 OpenClash
    if [ ! -f "/etc/init.d/openclash" ]; then
        log_warn "未检测到 OpenClash，请确保已安装 OpenClash"
        log_info "OpenClash 安装命令：opkg install luci-app-openclash"
    fi
    
    log_info "系统检查完成"
}

# 创建目录结构
create_directories() {
    log_step "创建目录结构..."
    
    mkdir -p /root/OpenClashManage/wangluo
    mkdir -p /root/OpenClashManage/logs
    
    log_info "目录创建完成"
}

# 下载文件
download_files() {
    log_step "下载项目文件..."
    
    # 设置 GitHub 仓库信息
    GITHUB_USER="kuku0799"
    GITHUB_REPO="5000ceshi"
    GITHUB_BRANCH="main"
    
    # 下载核心文件
    log_info "下载核心系统文件..."
    
    # 下载 jk.sh
    wget -O /root/OpenClashManage/jk.sh \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/jk.sh"
    
    # 下载 Python 文件
    for file in zr.py jx.py zw.py zc.py log.py config.py; do
        wget -O "/root/OpenClashManage/${file}" \
            "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/${file}"
    done
    
    # 下载 Web 编辑器
    log_info "下载 Web 编辑器文件..."
    
    wget -O /root/OpenClashManage/web_editor.py \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/web_editor.py"
    
    mkdir -p /root/OpenClashManage/templates
    wget -O /root/OpenClashManage/templates/index.html \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/templates/index.html"
    
    # 下载依赖文件
    wget -O /root/OpenClashManage/requirements.txt \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/requirements.txt"
    
    # 下载启动脚本
    wget -O /root/OpenClashManage/start_web_editor.sh \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/start_web_editor.sh"
    
    log_info "文件下载完成"
}

# 设置权限
set_permissions() {
    log_step "设置文件权限..."
    
    chmod +x /root/OpenClashManage/jk.sh
    chmod +x /root/OpenClashManage/start_web_editor.sh
    
    log_info "权限设置完成"
}

# 安装依赖
install_dependencies() {
    log_step "安装 Python 依赖..."
    
    if command -v pip3 &> /dev/null; then
        log_info "使用 pip3 安装依赖..."
        pip3 install -r /root/OpenClashManage/requirements.txt
        log_info "Python 依赖安装完成"
    else
        log_warn "pip3 未找到，尝试使用 opkg 安装依赖..."
            # 尝试使用 opkg 安装依赖
    opkg install python3-flask python3-werkzeug python3-ruamel-yaml
    log_info "使用 opkg 安装依赖完成"
    fi

    # 可选：安装 inotify 工具提升监控效率（失败不影响）
    if command -v opkg &> /dev/null; then
        opkg update >/dev/null 2>&1 || true
        opkg install inotify-tools >/dev/null 2>&1 || true
    fi
}

# 创建示例文件
create_sample_files() {
    log_step "创建示例文件..."
    
    # 创建示例 nodes.txt
    cat > /root/OpenClashManage/wangluo/nodes.txt << 'EOF'
# 在此粘贴你的节点链接，一行一个，支持 ss:// vmess:// vless:// trojan:// socks:// socks5://协议

# 示例节点格式：
# ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@server.com:8388#节点名称
# vmess://eyJhZGQiOiJzZXJ2ZXIuY29tIiwicG9ydCI6NDQzLCJpZCI6IjEyMzQ1Njc4LTkwYWItMTFlYy1hYzE1LTAwMTYzYzFhYzE1NSIsImFpZCI6MCwidHlwZSI6Im5vbmUiLCJob3N0IjoiIiwicGF0aCI6IiIsInRscyI6InRscyJ9#节点名称
# vless://uuid@server.com:443?security=tls#节点名称
# trojan://password@server.com:443#节点名称
# socks://username:password@server.com:1080#节点名称
# socks://server.com:1080#节点名称（无认证）
# socks5://username:password@server.com:1080#节点名称
EOF

    # 创建日志文件
    touch /root/OpenClashManage/wangluo/log.txt
    
    log_info "示例文件创建完成"
}

# 创建服务脚本
create_service_scripts() {
    log_step "创建服务脚本..."
    
    # 创建启动脚本
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

    chmod +x /root/OpenClashManage/start.sh
    chmod +x /root/OpenClashManage/stop.sh
    chmod +x /root/OpenClashManage/status.sh
    
    log_info "服务脚本创建完成"
}

# 设置开机自启动
setup_autostart() {
    log_step "设置开机自启动..."
    
    # 创建开机自启动脚本
    cat > /root/OpenClashManage/autostart.sh << 'EOF'
#!/bin/bash
cd /root/OpenClashManage
./start.sh
EOF

    chmod +x /root/OpenClashManage/autostart.sh
    
    # 检查是否为 OpenWrt 系统
    if [ -f /etc/openwrt_release ]; then
        log_info "检测到 OpenWrt 系统，使用 init.d 服务"
        
        # 创建 init.d 服务脚本
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
        
        # 启用服务
        /etc/init.d/openclash-manage enable
        
        log_info "init.d 服务已启用"
        log_info "管理命令: /etc/init.d/openclash-manage {start|stop|restart|status}"
        
    else
        log_info "使用 crontab 设置开机自启动"
        
        # 添加到 crontab
        (crontab -l 2>/dev/null | grep -v "@reboot.*OpenClashManage"; echo "@reboot /root/OpenClashManage/autostart.sh") | crontab -
        
        log_info "crontab 自启动已设置"
    fi
    
    log_info "开机自启动设置完成"
}

# 显示安装信息
show_install_info() {
    log_step "安装完成！"
    
    echo ""
    echo "🎉 OpenClash 节点管理系统安装完成！"
    echo ""
    echo "📁 安装目录: /root/OpenClashManage/"
    echo "📱 Web编辑器: http://$(hostname -I | awk '{print $1}'):5000"
    echo "📝 配置文件: /root/OpenClashManage/wangluo/nodes.txt"
    echo ""
    echo "🚀 启动服务:"
    echo "   cd /root/OpenClashManage && ./start.sh"
    echo ""
    echo "🛑 停止服务:"
    echo "   cd /root/OpenClashManage && ./stop.sh"
    echo ""
    echo "🔍 查看状态:"
    echo "   cd /root/OpenClashManage && ./status.sh"
    echo ""
    echo "🔄 服务管理:"
    if [ -f /etc/init.d/openclash-manage ]; then
        echo "   启动: /etc/init.d/openclash-manage start"
        echo "   停止: /etc/init.d/openclash-manage stop"
        echo "   重启: /etc/init.d/openclash-manage restart"
        echo "   状态: /etc/init.d/openclash-manage status"
        echo "   直接启动: cd /root/OpenClashManage && ./start.sh"
        echo "   直接停止: cd /root/OpenClashManage && ./stop.sh"
        echo "   状态检查: cd /root/OpenClashManage && ./status.sh"
    else
        echo "   使用 crontab 自启动，重启后生效"
        echo "   直接启动: cd /root/OpenClashManage && ./start.sh"
        echo "   直接停止: cd /root/OpenClashManage && ./stop.sh"
        echo "   状态检查: cd /root/OpenClashManage && ./status.sh"
    fi
    echo ""
    echo "📖 使用说明:"
    echo "   1. 访问 Web 编辑器添加节点"
    echo "   2. 系统自动监控文件变化"
    echo "   3. 自动同步到 OpenClash"
    echo "   4. 系统重启后自动启动"
    echo ""
    echo "⚠️  注意：请确保已安装 OpenClash 插件"
    echo ""
}

# 主安装流程
main() {
    echo "🌐 OpenClash 节点管理系统一键安装脚本"
    echo "=========================================="
    echo ""
    
    check_system
    create_directories
    download_files
    set_permissions
    install_dependencies
    create_sample_files
    create_service_scripts
    setup_autostart
    show_install_info
}

# 执行安装
main "$@" 