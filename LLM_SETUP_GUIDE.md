# LLM 配置指南

SeismicX 支持多种大语言模型(LLM)提供商,让您可以根据需求选择合适的AI助手。

## 📋 目录

- [支持的提供商](#支持的提供商)
- [首次使用设置](#首次使用设置)
- [CLI配置方法](#cli配置方法)
- [Web界面配置](#web界面配置)
- [Ollama本地模型](#ollama本地模型)
- [在线API模型](#在线api模型)
- [常见问题](#常见问题)

## 支持的提供商

### 1. Ollama (推荐)
- ✅ **优点**: 本地运行、隐私保护、离线可用
- ⚠️ **缺点**: 需要安装Ollama、占用磁盘空间
- 💾 **存储**: 模型大小2-8GB不等
- 🔗 **官网**: https://ollama.ai

### 2. OpenAI
- ✅ **优点**: 高质量模型(GPT-4)、稳定可靠
- ⚠️ **缺点**: 需要付费、需要网络连接
- 💰 **费用**: 按token计费
- 🔗 **官网**: https://platform.openai.com

### 3. Anthropic (Claude)
- ✅ **优点**: 强大的推理能力、长上下文
- ⚠️ **缺点**: 需要付费、需要网络连接
- 💰 **费用**: 按token计费
- 🔗 **官网**: https://console.anthropic.com

### 4. Azure OpenAI
- ✅ **优点**: 企业级服务、合规性好
- ⚠️ **缺点**: 需要Azure账户、设置复杂
- 💰 **费用**: 按token计费
- 🔗 **官网**: https://azure.microsoft.com

### 5. Custom API
- ✅ **优点**: 灵活定制、可连接任何兼容API
- ⚠️ **缺点**: 需要自行搭建或订阅服务
- 🔗 **兼容**: OpenAI API格式

## 首次使用设置

当您第一次运行SeismicX时,会自动启动设置向导:

### CLI首次设置

```bash
python seismic_cli.py
```

系统会提示:
```
Welcome to SeismicX!
This appears to be your first time using SeismicX.
Let's configure your LLM (Large Language Model) settings.

Would you like to set up LLM configuration now? (y/n) [y]:
```

输入 `y` 开始交互式设置:

1. **选择提供商**: 输入数字选择(1-5)
2. **选择模型**: 从列表中选择或手动输入
3. **配置API**: 如选择在线提供商,需输入API密钥
4. **完成设置**: 配置保存到 `~/.seismicx/config.json`

### Web首次设置

访问 http://localhost:5000 时,如果未配置LLM,会自动跳转到设置页面。

## CLI配置方法

### 查看当前配置

```bash
python seismic_cli.py llm show
```

输出示例:
```
Current LLM Configuration:
----------------------------------------
provider: ollama
model: qwen2.5:7b
api_base: http://localhost:11434
api_key: ******** (hidden)
temperature: 0.7
max_tokens: 2000
```

### 交互式设置

```bash
python seismic_cli.py llm setup
```

这会启动完整的交互式设置向导。

### 快速切换提供商

```bash
# 切换到OpenAI
python seismic_cli.py llm set-provider openai

# 切换到Ollama
python seismic_cli.py llm set-provider ollama
```

### 设置模型

```bash
# 设置Ollama模型
python seismic_cli.py llm set-model qwen2.5:14b

# 设置OpenAI模型
python seismic_cli.py llm set-model gpt-4o
```

### 查看可用模型

```bash
python seismic_cli.py llm list-models
```

这会列出所有已安装的Ollama模型。

## Web界面配置

1. **访问设置页面**
   - 点击导航栏的 "LLM Settings"
   - 或直接访问: http://localhost:5000/llm-settings

2. **选择提供商**
   - 点击对应的提供商卡片
   - 系统会自动显示相关配置选项

3. **配置模型**
   - **Ollama**: 从列表中选择或输入模型名
   - **在线API**: 输入模型名称和API密钥

4. **高级设置**
   - Temperature: 控制回答随机性 (0-2)
   - Max Tokens: 最大响应长度

5. **保存配置**
   - 点击 "Save Configuration"
   - 系统会验证并保存设置

6. **测试连接**
   - 点击 "Test Connection" 验证配置是否正确

## Ollama本地模型

### 安装Ollama

**macOS:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**Windows:**
- 下载 installer: https://ollama.ai
- 运行安装程序
- 启动Ollama应用

### 推荐模型

| 模型 | 大小 | 特点 | 适用场景 |
|------|------|------|---------|
| `qwen2.5:7b` | ~4GB | 平衡性能与速度 | 通用任务 (推荐) |
| `qwen2.5:14b` | ~8GB | 更高质量 | 复杂分析 |
| `llama3.2:3b` | ~2GB | 快速轻量 | 简单任务 |
| `llama3.1:8b` | ~4.7GB | 通用性好 | 日常使用 |
| `mistral:7b` | ~4.1GB | 高效能 | 代码生成 |
| `deepseek-coder:6.7b` | ~3.8GB | 代码专用 | 编程辅助 |

### 安装模型

**方法1: 通过CLI**
```bash
ollama pull qwen2.5:7b
```

**方法2: 通过Web界面**
1. 访问 LLM Settings
2. 在 "Recommended Models" 区域
3. 点击模型旁边的 "Install" 按钮

**方法3: 通过CLI工具**
```bash
python seismic_cli.py llm list-models  # 查看已安装
# 然后在Web界面或手动安装新模型
```

### 管理模型

```bash
# 查看所有模型
ollama list

# 删除模型
ollama rm model_name

# 更新模型
ollama pull model_name
```

## 在线API模型

### OpenAI

1. **获取API密钥**
   - 访问: https://platform.openai.com/api-keys
   - 创建新账户或登录
   - 生成API密钥

2. **配置**
   ```bash
   python seismic_cli.py llm set-provider openai
   python seismic_cli.py llm set-model gpt-4o
   # 然后在提示中输入API密钥
   ```

3. **推荐模型**
   - `gpt-4o`: 最佳质量
   - `gpt-4o-mini`: 性价比高
   - `gpt-3.5-turbo`: 经济实惠

### Anthropic (Claude)

1. **获取API密钥**
   - 访问: https://console.anthropic.com
   - 创建账户
   - 生成API密钥

2. **配置**
   ```bash
   python seismic_cli.py llm set-provider anthropic
   python seismic_cli.py llm set-model claude-3-sonnet-20240229
   ```

3. **推荐模型**
   - `claude-3-sonnet-20240229`: 平衡选择
   - `claude-3-haiku-20240307`: 快速响应
   - `claude-3-opus-20240229`: 最高质量

### Azure OpenAI

1. **设置Azure资源**
   - 创建Azure账户
   - 部署OpenAI模型
   - 获取Endpoint和API密钥

2. **配置**
   ```bash
   python seismic_cli.py llm set-provider azure
   python seismic_cli.py llm set-model gpt-4o
   # 输入API密钥和Endpoint URL
   ```

## 配置文件说明

配置保存在 `~/.seismicx/config.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "model": "qwen2.5:7b",
    "api_base": "http://localhost:11434",
    "api_key": "",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "first_run": false
}
```

**参数说明:**
- `provider`: LLM提供商 (ollama/openai/anthropic/azure/custom)
- `model`: 模型名称
- `api_base`: API基础URL
- `api_key`: API密钥 (在线提供商需要)
- `temperature`: 温度参数 (0-2, 越高越随机)
- `max_tokens`: 最大生成长度

## 常见问题

### Q1: Ollama检测不到怎么办?

**A:** 检查Ollama是否运行:
```bash
# 检查服务状态
ollama list

# 如果没有运行,启动服务
ollama serve
```

### Q2: 如何切换模型?

**A:**
```bash
# CLI方式
python seismic_cli.py llm set-model 新模型名

# Web方式
访问 LLM Settings → 选择新模型 → Save
```

### Q3: API密钥安全吗?

**A:** 是的。API密钥仅保存在本地配置文件 `~/.seismicx/config.json` 中,不会上传到任何服务器。Web界面显示时会隐藏大部分字符。

### Q4: 哪个模型最好?

**A:** 取决于您的需求:
- **隐私优先**: Ollama + qwen2.5:7b
- **质量优先**: OpenAI GPT-4o
- **性价比**: Ollama + llama3.2:3b 或 OpenAI GPT-4o-mini
- **代码任务**: deepseek-coder:6.7b 或 GPT-4o

### Q5: 如何重置配置?

**A:** 删除配置文件即可:
```bash
rm ~/.seismicx/config.json
# 下次运行时会自动重新配置
```

### Q6: Ollama模型占用太多空间怎么办?

**A:** 删除不用的模型:
```bash
# 查看所有模型及大小
ollama list

# 删除不需要的模型
ollama rm 模型名
```

### Q7: 可以在多个设备间同步配置吗?

**A:** 可以。复制 `~/.seismicx/config.json` 到其他设备的相同位置即可。注意API密钥的安全性。

## 最佳实践

### 1. 选择合适的模型
- 日常使用: 中等大小模型 (7B参数)
- 简单任务: 小模型 (3B参数)
- 复杂分析: 大模型 (14B+参数)或GPT-4

### 2. 调整Temperature
- 事实性问题: 低温度 (0.2-0.5)
- 创意性任务: 高温度 (0.7-1.0)
- 代码生成: 中等温度 (0.5-0.7)

### 3. 监控API费用
- 设置预算提醒
- 定期检查使用情况
- 优先使用本地模型降低成本

### 4. 备份配置
```bash
# 备份配置
cp ~/.seismicx/config.json ~/.seismicx/config.json.backup

# 恢复配置
cp ~/.seismicx/config.json.backup ~/.seismicx/config.json
```

## 技术支持

如遇到问题:
1. 查看本文档的常见问题部分
2. 检查配置文件格式是否正确
3. 确认网络连接正常
4. 联系技术支持: yuziye@cea-igp.ac.cn

---

**最后更新**: 2026-04-09
**版本**: v1.0.0
