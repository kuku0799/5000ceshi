#!/bin/bash

# OpenClash 节点管理系统 - 快速启用开机自启动

echo "🔧 快速启用 OpenClash 节点管理系统开机自启动..."
echo ""

# 检查是否已安装
if [ ! -d "/root/OpenClashManage" ]; then
    echo "❌ 未找到 OpenClash 节点管理系统"
    echo "请先运行安装脚本: wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/install.sh | bash"
    exit 1
fi

echo "✅ 检测到已安装的系统"

# 检查是否为 OpenWrt 系统
if [ -f /etc/openwrt_release ]; then
    echo "📋 使用 init.d 服务方案"
    
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
    
    echo "✅ init.d 服务已启用"
    echo ""
    echo "💡 服务管理命令:"
    echo "  启动: /etc/init.d/openclash-manage start"
    echo "  停止: /etc/init.d/openclash-manage stop"
    echo "  重启: /etc/init.d/openclash-manage restart"
    echo "  状态: /etc/init.d/openclash-manage status"
    
else
    echo "📋 使用 crontab 方案"
    
    # 创建开机自启动脚本
    cat > /root/OpenClashManage/autostart.sh << 'EOF'
#!/bin/bash
cd /root/OpenClashManage
./start.sh
EOF

    chmod +x /root/OpenClashManage/autostart.sh
    
    # 添加到 crontab
    (crontab -l 2>/dev/null | grep -v "@reboot.*OpenClashManage"; echo "@reboot /root/OpenClashManage/autostart.sh") | crontab -
    
    echo "✅ crontab 自启动已设置"
    echo ""
    echo "💡 查看 crontab: crontab -l"
fi

echo ""
echo "🎉 开机自启动设置完成！"
echo "📝 重启设备后，系统将自动启动 OpenClash 节点管理系统"
echo ""
echo "🔍 当前服务状态:"
if [ -f /etc/init.d/openclash-manage ]; then
    /etc/init.d/openclash-manage status 2>/dev/null || echo "服务未运行"
else
    echo "使用 crontab 方案，重启后生效"
fi 