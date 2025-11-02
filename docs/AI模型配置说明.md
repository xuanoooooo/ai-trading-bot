# AI模型配置说明

本系统支持多种AI模型提供商，包括 OpenRouter、DeepSeek、OpenAI、Qwen等。

## 配置方式

### 1. API Key配置（`.env` 文件）

在项目根目录的 `.env` 文件中配置API密钥：

```bash
# DeepSeek（默认）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# OpenRouter（可选）
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# OpenAI（可选）
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Qwen（可选）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx

# 币安API（必需）
BINANCE_API_KEY=xxxxxxxxxxxxx
BINANCE_SECRET=xxxxxxxxxxxxx
```

### 2. 模型配置（`config/coins_config.json`）

在 `ai_config` 部分配置要使用的AI模型：

```json
{
  "ai_config": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_base": "https://api.deepseek.com",
    "api_key_env": "DEEPSEEK_API_KEY",
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

## 支持的AI提供商

### 1. DeepSeek（默认，推荐）

```json
{
  "provider": "deepseek",
  "model": "deepseek-chat",
  "api_base": "https://api.deepseek.com",
  "api_key_env": "DEEPSEEK_API_KEY",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**优势**：
- 性价比高（0.14¥/百万tokens）
- 推理能力强
- 响应速度快

### 2. OpenRouter（灵活选择）

```json
{
  "provider": "openrouter",
  "model": "deepseek/deepseek-chat",
  "api_base": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**可用模型**：
- `deepseek/deepseek-chat` - DeepSeek V3
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4o` - GPT-4o
- `google/gemini-pro-1.5` - Gemini 1.5 Pro
- `qwen/qwen-2.5-72b-instruct` - Qwen 2.5 72B

**优势**：
- 一个API访问多个模型
- 统一的接口规范
- 方便模型对比测试

### 3. OpenAI

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "api_base": "https://api.openai.com/v1",
  "api_key_env": "OPENAI_API_KEY",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

### 4. Qwen（通义千问）

```json
{
  "provider": "qwen",
  "model": "qwen-max",
  "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "api_key_env": "DASHSCOPE_API_KEY",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

## 智能检测机制（v2.4.9+）

系统支持智能API Key检测，使配置更加简单：

### 工作原理

1. **优先使用配置的API Key**：
   - 系统首先读取 `config/coins_config.json` 中的 `api_key_env`
   - 如果对应的环境变量存在，直接使用

2. **自动Fallback**：
   - 如果配置的Key不存在，系统会自动检测其他可用的API Key
   - 检测顺序：DEEPSEEK_API_KEY → OPENROUTER_API_KEY → OPENAI_API_KEY → DASHSCOPE_API_KEY
   - 找到可用的Key后自动切换并给出提示

3. **友好提示**：
   - 明确显示正在使用哪个API Key
   - 如果没有任何可用Key，给出清晰的错误提示

### 使用场景

**场景1：只配置一个API Key**
```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxx
```
✅ 系统自动使用 DEEPSEEK_API_KEY，无需修改配置文件

**场景2：配置多个API Key**
```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx
```
- 默认使用 `config/coins_config.json` 中配置的
- 如果想切换，修改json中的 `api_key_env` 即可

**场景3：配置错误时的自动恢复**
```bash
# coins_config.json 配置了OPENROUTER_API_KEY
# 但 .env 中只有 DEEPSEEK_API_KEY
```
✅ 系统自动使用 DEEPSEEK_API_KEY 并给出提示

## 快速切换模型

### 方式1：修改配置文件（推荐）

1. **编辑配置文件**：
   ```bash
   vi config/coins_config.json
   ```

2. **修改 `ai_config` 部分**（参考上面的示例）

3. **重启程序**：
   ```bash
   pkill -f portfolio_manager.py
   ./start_portfolio.sh
   ```

### 方式2：只配置.env（最简单）

1. **在 `.env` 中只配置你要用的API Key**
2. **直接启动程序**（系统会自动检测并使用）

## 参数说明

- **provider**: AI提供商标识（仅用于日志显示）
- **model**: 模型名称（必须与API提供商的模型名称一致）
- **api_base**: API地址
- **api_key_env**: `.env` 文件中的环境变量名
- **temperature**: 温度参数（0-1，越高越随机，建议0.7）
- **max_tokens**: 最大输出token数（建议4000）

## 注意事项

1. **API Key安全**：
   - `.env` 文件不要提交到Git
   - 不要在代码中硬编码API Key

2. **模型成本**：
   - DeepSeek最便宜（0.14¥/百万tokens）
   - OpenRouter价格取决于所选模型
   - OpenAI和Claude相对较贵

3. **模型性能**：
   - 推荐使用DeepSeek V3（推理能力强且便宜）
   - Claude 3.5 Sonnet也很优秀但价格较高
   - 可以通过OpenRouter轻松对比测试

4. **重启生效**：
   - 修改配置后必须重启程序才能生效

## 推荐配置

**日常使用**（性价比）：
```json
{
  "provider": "deepseek",
  "model": "deepseek-chat",
  "api_base": "https://api.deepseek.com",
  "api_key_env": "DEEPSEEK_API_KEY"
}
```

**高要求场景**（性能优先）：
```json
{
  "provider": "openrouter",
  "model": "anthropic/claude-3.5-sonnet",
  "api_base": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY"
}
```

**国内网络**（阿里云）：
```json
{
  "provider": "qwen",
  "model": "qwen-max",
  "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "api_key_env": "DASHSCOPE_API_KEY"
}
```

