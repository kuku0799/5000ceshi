#!/bin/bash

# 🚀 GitHub 一键部署脚本
# 适用于 OpenWrt 系统的 OpenClash 节点管理系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 一键部署脚本                           ║"
    echo "║              OpenClash 节点管理系统                          ║"
    echo "║                                                              ║"
    echo "║  GitHub: https://github.com/kuku0799/5000ceshi                   ║"
    echo "║  支持协议: SS、Vmess、Vless、Trojan、Socks5                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查系统环境
check_system() {
    log_step "检查系统环境..."
    
    # 检查是否为 OpenWrt
    if [ ! -f "/etc/openwrt_release" ]; then
        log_warn "未检测到 OpenWrt 系统，但继续安装..."
    else
        log_info "检测到 OpenWrt 系统"
    fi
    
    # 检查网络连接
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_info "网络连接正常"
    else
        log_error "网络连接失败，请检查网络设置"
        exit 1
    fi
}

# 安装 Python3
install_python3() {
    log_step "安装 Python3..."
    
    if command -v python3 &> /dev/null; then
        log_info "Python3 已安装: $(python3 --version)"
        return 0
    fi
    
    log_info "正在安装 Python3..."
    
    # 更新软件包列表
    opkg update
    
    # 安装 Python3 和相关包
    opkg install python3 python3-pip python3-requests python3-yaml python3-ruamel-yaml
    
    # 验证安装
    if command -v python3 &> /dev/null; then
        log_success "Python3 安装成功: $(python3 --version)"
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
        log_info "pip3 已安装: $(pip3 --version)"
        return 0
    fi
    
    # 尝试安装 pip3
    opkg install python3-pip
    
    # 验证安装
    if command -v pip3 &> /dev/null; then
        log_success "pip3 安装成功: $(pip3 --version)"
        return 0
    else
        log_warn "pip3 安装失败，将使用 opkg 安装依赖"
        return 1
    fi
}

# 创建目录结构
create_directories() {
    log_step "创建目录结构..."
    
    # 创建主目录
    mkdir -p /root/OpenClashManage
    mkdir -p /root/OpenClashManage/wangluo
    mkdir -p /root/OpenClashManage/templates
    
    log_info "目录创建完成"
}

# 下载文件
download_files() {
    log_step "下载项目文件..."
    
    # 设置 GitHub 仓库信息
    GITHUB_USER="kuku0799"
    GITHUB_REPO="5000ceshi"
    GITHUB_BRANCH="main"
    
    log_info "从 GitHub 仓库下载文件..."
    log_info "仓库: https://github.com/${GITHUB_USER}/${GITHUB_REPO}"
    log_info "分支: ${GITHUB_BRANCH}"
    
    # 下载核心文件
    log_info "下载核心系统文件..."
    
    # 下载 jk.sh
    wget -O /root/OpenClashManage/jk.sh \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/jk.sh"
    
    # 下载 Python 文件
    for file in zr.py jx.py zw.py zc.py log.py; do
        wget -O "/root/OpenClashManage/${file}" \
            "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/${file}"
    done
    
    # 下载 Web 编辑器
    log_info "下载 Web 编辑器文件..."
    
    wget -O /root/OpenClashManage/web_editor.py \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/web_editor.py"
    
    wget -O /root/OpenClashManage/templates/index.html \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/templates/index.html"
    
    # 下载依赖文件
    wget -O /root/OpenClashManage/requirements.txt \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/requirements.txt"
    
    # 下载启动脚本
    wget -O /root/OpenClashManage/start_web_editor.sh \
        "https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}/start_web_editor.sh"
    
    log_success "文件下载完成"
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
        log_success "Python 依赖安装完成"
    else
        log_warn "pip3 未找到，使用 opkg 安装依赖..."
        opkg install python3-flask python3-werkzeug python3-ruamel-yaml
        log_success "使用 opkg 安装依赖完成"
    fi
}

# 创建示例文件
create_sample_files() {
    log_step "创建示例文件..."
    
    # 创建示例 nodes.txt
    cat > /root/OpenClashManage/wangluo/nodes.txt << 'EOF'
# 在此粘贴你的节点链接，一行一个，支持 ss:// vmess:// vless:// trojan:// socks:// socks5:// 协议

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
    cat > /root/OpenClashManage/start_all.sh << 'EOF'
#!/bin/bash

# 启动所有服务

echo "🚀 启动 OpenClash 节点管理系统..."

# 启动 Web 编辑器
cd /root/OpenClashManage
./start_web_editor.sh

# 启动守护进程
./jk.sh &

echo "✅ 服务启动完成"
echo "🌐 Web 编辑器地址: http://$(hostname -I | awk '{print $1}'):5000"
echo "📝 编辑节点文件: /root/OpenClashManage/wangluo/nodes.txt"
EOF

    # 创建停止脚本
    cat > /root/OpenClashManage/stop_all.sh << 'EOF'
#!/bin/bash

# 停止所有服务

echo "🛑 停止 OpenClash 节点管理系统..."

# 停止 Web 编辑器
pkill -f web_editor.py

# 停止守护进程
pkill -f jk.sh

echo "✅ 服务停止完成"
EOF

    # 创建状态检查脚本
    cat > /root/OpenClashManage/status.sh << 'EOF'
#!/bin/bash

# 检查服务状态

echo "📊 服务状态检查..."

echo "🔍 Web 编辑器状态:"
if pgrep -f web_editor.py > /dev/null; then
    echo "   ✅ 运行中 (PID: $(pgrep -f web_editor.py))"
else
    echo "   ❌ 未运行"
fi

echo "🔍 守护进程状态:"
if pgrep -f jk.sh > /dev/null; then
    echo "   ✅ 运行中 (PID: $(pgrep -f jk.sh))"
else
    echo "   ❌ 未运行"
fi

echo "🔍 OpenClash 状态:"
if [ -f "/etc/init.d/openclash" ]; then
    /etc/init.d/openclash status
else
    echo "   ⚠️  OpenClash 未安装"
fi

echo "🌐 Web 编辑器地址: http://$(hostname -I | awk '{print $1}'):5000"
EOF

    # 设置执行权限
    chmod +x /root/OpenClashManage/start_all.sh
    chmod +x /root/OpenClashManage/stop_all.sh
    chmod +x /root/OpenClashManage/status.sh
    
    log_info "服务脚本创建完成"
}

# 显示安装完成信息
show_completion() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 安装完成！                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_success "OpenClash 节点管理系统安装完成！"
    echo ""
    echo "📁 安装目录: /root/OpenClashManage"
    echo "📝 节点文件: /root/OpenClashManage/wangluo/nodes.txt"
    echo "🌐 Web 编辑器: http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "🚀 启动服务:"
    echo "   cd /root/OpenClashManage && ./start_all.sh"
    echo ""
    echo "🛑 停止服务:"
    echo "   cd /root/OpenClashManage && ./stop_all.sh"
    echo ""
    echo "📊 查看状态:"
    echo "   cd /root/OpenClashManage && ./status.sh"
    echo ""
    echo "📖 详细文档:"
    echo "   https://github.com/kuku0799/5000ceshi"
    echo ""
}

# 主函数
main() {
    show_welcome
    
    # 检查系统环境
    check_system
    
    # 安装 Python3
    if ! install_python3; then
        log_error "Python3 安装失败，请手动安装后重试"
        exit 1
    fi
    
    # 安装 pip3
    install_pip3
    
    # 创建目录结构
    create_directories
    
    # 下载文件
    download_files
    
    # 设置权限
    set_permissions
    
    # 安装依赖
    install_dependencies
    
    # 创建示例文件
    create_sample_files
    
    # 创建服务脚本
    create_service_scripts
    
    # 显示完成信息
    show_completion
}

# 执行主函数
main "$@" 