# 🚀 GitHub 一键部署命令

## 📋 项目信息
- **项目**: OpenClash 节点管理系统
- **仓库**: https://github.com/kuku0799/5000ceshi
- **支持协议**: SS、Vmess、Vless、Trojan、Socks5

## 🎯 一键部署命令

### 方法1：使用 wget（推荐）
```bash
wget -O - https://raw.githubusercontent.com/kuku0799/5000ceshi/main/deploy.sh | bash
```

### 方法2：使用 curl
```bash
curl -sSL https://raw.githubusercontent.com/kuku0799/5000ceshi/main/deploy.sh | bash
```

### 方法3：手动下载后执行
```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/kuku0799/5000ceshi/main/deploy.sh

# 执行部署
bash deploy.sh
```

## 🎯 部署后使用

### 1. 启动服务
```bash
cd /root/OpenClashManage
./start_all.sh
```

### 2. 访问 Web 编辑器
打开浏览器访问：`http://你的路由器IP:5000`

### 3. 添加节点
在 Web 编辑器中编辑 `nodes.txt` 文件，添加你的节点链接

## 📋 支持的节点格式

```
# SS 协议
ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@server.com:8388#节点名称

# Vmess 协议
vmess://eyJhZGQiOiJzZXJ2ZXIuY29tIiwicG9ydCI6NDQzLCJpZCI6IjEyMzQ1Njc4LTkwYWItMTFlYy1hYzE1LTAwMTYzYzFhYzE1NSIsImFpZCI6MCwidHlwZSI6Im5vbmUiLCJob3N0IjoiIiwicGF0aCI6IiIsInRscyI6InRscyJ9#节点名称

# Vless 协议
vless://uuid@server.com:443?security=tls#节点名称

# Trojan 协议
trojan://password@server.com:443#节点名称

# Socks/Socks5 协议
socks://username:password@server.com:1080#节点名称
socks://server.com:1080#节点名称（无认证）
socks5://username:password@server.com:1080#节点名称
```

## 🔧 管理命令

```bash
# 启动所有服务
cd /root/OpenClashManage && ./start_all.sh

# 停止所有服务
cd /root/OpenClashManage && ./stop_all.sh

# 查看服务状态
cd /root/OpenClashManage && ./status.sh

# 查看日志
tail -f /root/OpenClashManage/wangluo/log.txt
```

## 📞 技术支持
- **GitHub**: https://github.com/kuku0799/5000ceshi
- **详细文档**: 查看 README.md 和 GITHUB_DEPLOY.md

---

**版本**: v2.0.0 | **许可证**: MIT 