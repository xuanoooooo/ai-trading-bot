# ⚙️ 配置指南

## 🔑 API密钥配置

### 1. DeepSeek API密钥

#### 获取步骤
1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 注册/登录账户
3. 进入API管理页面
4. 创建新的API密钥
5. 复制API密钥

#### 配置方法
```env
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```

### 2. 币安API密钥

#### 获取步骤
1. 访问 [币安官网](https://www.binance.com/)
2. 登录您的账户
3. 进入 "账户" → "API管理"
4. 创建新的API密钥
5. **重要**: 确保勾选"期货交易"权限
6. 复制API密钥和密钥

#### 配置方法
```env
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET=your-binance-secret
```

#### 安全设置
- ✅ 启用IP白名单（推荐）
- ✅ 仅启用期货交易权限
- ❌ 不要启用提现权限
- ❌ 不要启用现货交易权限

## 📊 交易配置

### 基本配置
在 `src/deepseekBNB.py` 中修改 `TRADE_CONFIG`：

```python
TRADE_CONFIG = {
    'symbol': 'BNB/USDT',        # 交易对
    'leverage': 3,                # 杠杆倍数
    'timeframe': '15m',           # K线周期
    'test_mode': False,           # 实盘/测试模式
    'data_points': 96,            # 历史数据点数
}
```

### 支持的交易对
- `BNB/USDT` - 币安币
- `DOGE/USDT` - 狗狗币
- `BTC/USDT` - 比特币
- `ETH/USDT` - 以太坊
- 其他币安期货支持的交易对

### 时间周期选项
- `1m` - 1分钟
- `5m` - 5分钟
- `15m` - 15分钟（推荐）
- `1h` - 1小时
- `4h` - 4小时
- `1d` - 1天

## 🛡️ 风险管理配置

### 仓位管理
```python
'position_management': {
    'max_position_percent': 80,    # 最大仓位百分比
    'min_position_percent': 5,     # 最小仓位百分比
    'force_reserve_percent': 20,   # 强制预留资金
    'allow_zero': True            # 允许AI返回0（不交易）
}
```

### 风险参数说明
- **max_position_percent**: AI最多使用80%可用资金
- **min_position_percent**: AI最少使用5%可用资金
- **force_reserve_percent**: 系统强制预留20%缓冲资金
- **allow_zero**: 允许AI决定不交易

### 杠杆设置
```python
'leverage': 3  # 固定3倍杠杆
```
- 杠杆倍数固定为3倍
- 实际仓位 = 保证金 × 3
- 风险可控，适合大多数用户

## 📈 技术分析配置

### 指标参数
```python
'analysis_periods': {
    'short_term': 20,    # 短期均线周期
    'medium_term': 50,   # 中期均线周期
    'long_term': 96      # 长期趋势周期
}
```

### 数据点设置
```python
'data_points': 96  # 24小时数据（96根15分钟K线）
```

## 🔧 高级配置

### 日志配置
```python
# 日志文件设置
log_handler = RotatingFileHandler(
    'trading_bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3,         # 保留3个备份
    encoding='utf-8'
)
```

### 重试机制
```python
# 最大重试次数
max_retries = 3

# 请求超时时间
request_timeout = 30
```

### 精度设置
```python
# 不同币种的精度要求
precision_config = {
    'BNB/USDT': {'decimals': 3, 'min_amount': 0.01},
    'DOGE/USDT': {'decimals': 1, 'min_amount': 10},
    'BTC/USDT': {'decimals': 3, 'min_amount': 0.001}
}
```

## 🖥️ 服务器配置

### 系统要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 10GB以上可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Ubuntu 20.04 LTS
- **Python**: 3.11+
- **内存**: 8GB+
- **存储**: SSD 50GB+

### 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化网络参数
echo "net.core.rmem_max = 16777216" >> /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" >> /etc/sysctl.conf
sysctl -p
```

## 🔒 安全配置

### API密钥安全
1. **环境变量**: 使用 `.env` 文件存储密钥
2. **文件权限**: 设置适当的文件权限
```bash
chmod 600 .env
```

3. **IP白名单**: 在币安设置IP白名单
4. **权限最小化**: 仅启用必要的API权限

### 网络安全
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from your_ip_address

# 使用VPN（可选）
# 建议使用稳定的VPN服务
```

### 数据备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "backup_${DATE}.tar.gz" \
    logs/ \
    .env \
    config/ \
    src/
EOF

chmod +x backup.sh
```

## 📊 监控配置

### 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs -y

# 监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== 系统状态 ==="
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "内存使用: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "磁盘使用: $(df -h / | awk 'NR==2{print $5}')"
echo "网络连接: $(netstat -an | grep ESTABLISHED | wc -l)"
EOF

chmod +x monitor.sh
```

### 日志监控
```bash
# 实时查看日志
tail -f trading_bot.log

# 错误日志过滤
grep -i error trading_bot.log

# 交易记录查看
grep -i "交易" trading_bot.log
```

## ✅ 配置验证

### 检查清单
- [ ] API密钥已正确配置
- [ ] 交易对设置正确
- [ ] 杠杆倍数设置合理
- [ ] 风险参数配置适当
- [ ] 日志配置正确
- [ ] 安全设置已启用
- [ ] 监控工具已安装
- [ ] 备份策略已制定

### 测试配置
```bash
# 运行配置测试
python -c "
from src.utils import load_env_vars, validate_api_keys
from src.deepseekBNB import TRADE_CONFIG

# 检查API密钥
env_vars = load_env_vars()
if validate_api_keys(env_vars):
    print('✅ API密钥配置正确')
else:
    print('❌ API密钥配置有误')

# 检查交易配置
print(f'交易对: {TRADE_CONFIG[\"symbol\"]}')
print(f'杠杆: {TRADE_CONFIG[\"leverage\"]}x')
print(f'周期: {TRADE_CONFIG[\"timeframe\"]}')
print(f'模式: {\"测试\" if TRADE_CONFIG[\"test_mode\"] else \"实盘\"}')
"
```

配置完成后，请参考 [交易指南](trading_guide.md) 开始使用交易机器人。
