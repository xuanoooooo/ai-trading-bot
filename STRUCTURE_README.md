# AI多币种交易系统 - 项目结构说明

## 📁 新的项目结构（整理后）

```
duobizhong/
├── .env                          # 环境变量配置（API密钥等）
├── .gitignore                    # Git忽略文件
├── README.md                     # 详细项目说明（原有）
├── STRUCTURE_README.md          # 本项目结构说明（当前文件）
│
├── src/                          # 源代码目录
│   ├── core/                     # 核心交易模块
│   │   ├── portfolio_manager.py   # 交易主程序（AI决策引擎）
│   │   ├── market_scanner.py      # 市场数据扫描器
│   │   └── portfolio_statistics.py # 统计和盈亏计算模块
│   ├── ai/                       # AI相关模块（预留）
│   └── api/                      # API接口模块（预留）
│
├── web/                          # 可视化看板
│   ├── web_app.py                # Flask Web应用
│   ├── start_web.sh              # Web服务启动脚本
│   ├── static/                   # 静态资源
│   │   ├── app.js                # 前端JavaScript
│   │   └── style.css             # 样式文件
│   ├── templates/                # HTML模板
│   │   └── index.html            # 主页面
│   └── *.md                      # Web相关文档
│
├── config/                       # 配置文件
│   ├── coins_config.json         # 币种配置（精度、最小金额等）
│   └── 配置说明.md               # 配置说明文档
│
├── prompts/                      # AI提示词策略
│   └── default.txt               # 默认交易策略（可外部修改）
│
├── scripts/                      # 脚本文件
│   ├── start_portfolio.sh        # 交易程序启动脚本
│   └── 清理历史记录.sh            # 历史数据清理脚本
│
├── data/                         # 数据文件
│   ├── portfolio_stats.json      # 交易统计数据
│   ├── ai_decisions.json         # AI决策记录
│   ├── current_runtime.json      # 运行时状态
│   └── backups/                  # 备份目录（自动生成）
│
├── docs/                         # 文档
│   ├── 持仓同步说明.md           # 持仓同步机制说明
│   ├── 快速开始交易程序.md       # 交易程序使用指南
│   └── 终端连接.md               # 终端连接说明
│
├── tests/                       # 测试文件
│   └── test_stop_loss_record.py  # 止损记录测试
│
└── backups/                     # 备份目录（由系统自动生成）
```

## 🔄 整理前后的变化

### 整理前（松散的目录结构）
- 所有核心文件都在根目录
- 脚本、文档、配置文件混杂在一起
- `web` 目录包含所有web相关文件
- 不易维护和扩展

### 整理后（模块化结构）
- **src/**: 源代码按功能模块分离
- **web/**: 所有Web相关文件集中管理
- **config/**: 配置文件统一管理
- **scripts/**: 启动和管理脚本集中
- **data/**: 运行时数据文件统一存储
- **docs/**: 文档文件分类整理
- **tests/**: 测试文件独立目录

## 🚀 如何使用新的结构

### 启动交易程序
```bash
# 使用更新后的脚本
./scripts/start_portfolio.sh

# 主程序位置：src/core/portfolio_manager.py
```

### 启动Web看板
```bash
# 进入web目录执行
cd web
./start_web.sh

# 或者直接运行
python3 web/web_app.py
```

### 修改配置
- 币种配置：`/root/ziyong/duobizhong/config/coins_config.json`
- 交易策略：`/root/ziyong/duobizhong/prompts/default.txt`
- 环境变量：`.env`

### 查看数据
- 交易统计：`/root/ziyong/duobizhong/data/portfolio_stats.json`
- AI决策记录：`/root/ziyong/duobizhong/data/ai_decisions.json`
- 程序日志：自动生成在根目录

## 📝 重要文件说明

| 文件 | 作用 | 位置 |
|------|------|------|
| 交易主程序 | AI决策引擎，5分钟调用一次 | `/root/ziyong/duobizhong/src/core/portfolio_manager.py` |
| 市场扫描器 | 获取K线数据和技术指标 | `/root/ziyong/duobizhong/src/core/market_scanner.py` |
| Web应用 | 可视化监控看板 | `/root/ziyong/duobizhong/web/web_app.py` |
| 币种配置 | 精度、最小金额、杠杆等 | `/root/ziyong/duobizhong/config/coins_config.json` |
| 交易策略 | AI提示词，可外部修改 | `/root/ziyong/duobizhong/prompts/default.txt` |
| 启动脚本 | 后台运行交易程序 | `/root/ziyong/duobizhong/scripts/start_portfolio.sh` |

## ✅ 更新完成的功能

1. **文件移动完成**：所有文件已按模块分类
2. **导入路径更新**：Python模块导入路径已适配新结构
3. **脚本路径更新**：启动脚本已更新执行路径
4. **空目录清理**：移除了不必要的空目录
5. **结构文档**：创建了本说明文件

## 🔧 注意事项

- 原有功能完全保留，只是文件组织方式改变
- 需要从新的脚本路径启动程序
- 数据文件现在统一存储在 `data/` 目录
- 配置文件位置保持不变，便于维护

## 📊 项目特色

- **AI驱动**：基于多周期K线数据的AI决策
- **多币种支持**：BTC、ETH、SOL、BNB、XRP、ADA、DOGE
- **自动止损**：开仓即下止损单
- **可视化监控**：实时Web看板
- **模块化架构**：便于维护和扩展

这个新的项目结构更加清晰、易于维护，为后续的功能扩展提供了良好的基础。