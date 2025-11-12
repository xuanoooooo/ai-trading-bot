# 🔒 SSH隧道访问Web界面

## 为什么使用SSH隧道？

✅ **更安全**：
- Web服务只监听 `127.0.0.1`（本地）
- 外网无法直接访问
- 不暴露端口到公网

✅ **加密传输**：
- 所有数据通过SSH加密
- 防止中间人攻击

✅ **简单可靠**：
- 不需要配置防火墙
- 不需要VPN
- 使用SSH的现有认证

---

## 📱 不同系统的使用方法

### 1. Windows系统

**方法1：使用PowerShell或CMD**

```powershell
ssh -L 5000:localhost:5000 root@your-server-ip
```

**方法2：使用PuTTY**

1. 打开PuTTY
2. 在"Session"中输入服务器IP
3. 在左侧菜单找到：Connection → SSH → Tunnels
4. Source port: `5000`
5. Destination: `localhost:5000`
6. 点击"Add"
7. 回到Session，点击"Open"连接

**方法3：使用VSCode**

1. 安装"Remote - SSH"插件
2. 连接到服务器
3. 在终端执行：`cd /root/DS/duobizhong/keshihua && ./start_web.sh`
4. VSCode会自动创建端口转发
5. 浏览器访问 `http://localhost:5000`

---

### 2. macOS / Linux系统

**终端执行**：

```bash
ssh -L 5000:localhost:5000 root@your-server-ip
```

---

## 🚀 完整使用流程

### 步骤1：在服务器上启动Web服务

```bash
cd /root/DS/duobizhong/keshihua
./start_web.sh
```

### 步骤2：在本地电脑建立SSH隧道

**打开新的终端窗口**，执行：

```bash
ssh -L 5000:localhost:5000 root@your-server-ip
```

**保持这个SSH连接打开**！

### 步骤3：访问Web界面

打开浏览器，访问：
```
http://localhost:5000
```

---

## 🔧 高级技巧

### 后台运行SSH隧道

如果想在后台运行SSH隧道（Linux/macOS）：

```bash
ssh -f -N -L 5000:localhost:5000 root@your-server-ip
```

参数说明：
- `-f`: 后台运行
- `-N`: 不执行远程命令
- `-L`: 端口转发

停止后台隧道：
```bash
ps aux | grep "ssh.*5000"
kill <PID>
```

### 使用别名快速连接

在本地电脑的 `~/.bashrc` 或 `~/.zshrc` 添加：

```bash
alias web-tunnel='ssh -L 5000:localhost:5000 root@your-server-ip'
```

然后只需执行：
```bash
web-tunnel
```

### 使用不同端口

如果本地5000端口被占用，可以映射到其他端口：

```bash
# 映射到本地8080端口
ssh -L 8080:localhost:5000 root@your-server-ip
```

然后访问：`http://localhost:8080`

---

## ❓ 常见问题

### Q1: SSH断开后怎么办？

**A**: 重新执行SSH隧道命令即可，Web服务在服务器上持续运行。

### Q2: 能同时有多个人访问吗？

**A**: 每个人都需要建立自己的SSH隧道。每个人在本地访问 `http://localhost:5000` 即可。

### Q3: 端口转发失败？

**可能原因**：
1. 本地5000端口被占用 → 改用其他端口
2. SSH连接断开 → 重新连接
3. Web服务未启动 → 检查服务器上的服务状态

**检查**：
```bash
# 在服务器上检查Web服务
tmux attach -t web

# 在本地检查端口
netstat -an | grep 5000  # Linux/macOS
netstat -an | findstr 5000  # Windows
```

### Q4: 如何在外网访问？

**不推荐直接暴露**！如果必须：

1. 修改 `web_app.py` 中的 `host='0.0.0.0'`
2. 配置防火墙规则
3. 使用Nginx反向代理 + SSL证书

**但强烈建议使用SSH隧道！**

---

## 🔐 安全提示

1. ✅ 使用SSH密钥认证而不是密码
2. ✅ 定期更新服务器系统
3. ✅ 使用强密码
4. ✅ 不要在公共网络使用未加密连接
5. ❌ 不要将Web服务暴露到公网（除非有防护措施）

---

## 📱 移动设备访问

### iOS (使用Termius或Blink Shell)

1. 安装Termius或Blink Shell
2. 配置SSH连接
3. 设置端口转发：Local Port 5000 → Remote localhost:5000
4. 连接后，使用Safari访问 `http://localhost:5000`

### Android (使用JuiceSSH)

1. 安装JuiceSSH
2. 配置SSH连接
3. 在Port Forwarding中添加：5000 → localhost:5000
4. 连接后，使用Chrome访问 `http://localhost:5000`

---

**记住**：保持SSH连接打开，Web界面才能访问！断开SSH连接后，本地浏览器将无法访问（但服务器上的服务仍在运行）。

