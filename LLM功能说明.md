# ✅ LLM模型选择功能已完成

## 📦 新增内容

### 1. 配置管理器 (config_manager.py)

**位置**: `config_manager.py`

**功能**:
- ✅ 支持5种LLM提供商 (Ollama, OpenAI, Anthropic, Azure, Custom)
- ✅ 交互式首次设置向导
- ✅ 配置文件管理 (~/.seismicx/config.json)
- ✅ Ollama模型检测与管理
- ✅ API密钥安全存储
- ✅ 推荐模型列表

**核心类**: `LLMConfigManager`

### 2. CLI增强 (seismic_cli.py)

**新增命令**:
```bash
# 查看当前配置
python seismic_cli.py llm show

# 交互式设置
python seismic_cli.py llm setup

# 设置提供商
python seismic_cli.py llm set-provider ollama

# 设置模型
python seismic_cli.py llm set-model qwen2.5:7b

# 列出可用模型
python seismic_cli.py llm list-models
```

**特性**:
- ✅ 首次运行自动启动设置向导
- ✅ 可随时修改配置
- ✅ 友好的交互式界面
- ✅ 参数验证和错误提示

### 3. Web设置页面 (llm_settings.html)

**位置**: `web_app/templates/llm_settings.html`

**访问**: http://localhost:5000/llm-settings

**功能**:
- ✅ 可视化提供商选择卡片
- ✅ Ollama状态实时检测
- ✅ 已安装模型列表
- ✅ 推荐模型一键安装
- ✅ API密钥安全输入
- ✅ 高级参数调节 (Temperature, Max Tokens)
- ✅ 连接测试功能
- ✅ 配置保存与加载

### 4. Flask API端点 (web_app/app.py)

**新增API**:
```python
GET  /llm-settings              # LLM设置页面
GET  /api/llm/config            # 获取当前配置
POST /api/llm/config            # 更新配置
GET  /api/llm/ollama/models     # 获取Ollama模型列表
POST /api/llm/ollama/pull       # 下载Ollama模型
```

### 5. 完整文档 (LLM_SETUP_GUIDE.md)

**内容**:
- ✅ 支持的提供商详细说明
- ✅ 首次使用设置指南
- ✅ CLI和Web配置方法
- ✅ Ollama安装和使用教程
- ✅ 在线API配置步骤
- ✅ 常见问题解答
- ✅ 最佳实践建议

## 🎯 实现的功能需求

### ✓ 自由选择大模型工具

用户可以在以下提供商之间自由切换:

1. **Ollama** - 本地模型
   - 隐私保护最好
   - 离线可用
   - 无需API费用
   - 需要安装Ollama

2. **OpenAI** - GPT系列
   - GPT-4o (最高质量)
   - GPT-4o-mini (性价比)
   - GPT-3.5-turbo (经济)

3. **Anthropic** - Claude系列
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Claude 3 Opus

4. **Azure OpenAI** - 企业级
   - 合规性好
   - 稳定性高

5. **Custom API** - 自定义
   - 任何OpenAI兼容API
   - 灵活扩展

### ✓ 首次使用时设置

**CLI方式**:
```bash
python seismic_cli.py
# 自动检测首次运行
# 启动交互式设置向导
```

**Web方式**:
```
访问 http://localhost:5000
如果未配置,会自动提示前往设置页面
```

**设置流程**:
1. 选择提供商 (Ollama/OpenAI/Anthropic等)
2. 选择或输入模型名称
3. 输入API密钥 (在线提供商需要)
4. 配置高级参数 (可选)
5. 保存到配置文件

### ✓ 配置持久化保存

**保存位置**: `~/.seismicx/config.json`

**保存内容**:
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

**特性**:
- ✅ 自动创建配置目录
- ✅ JSON格式易于编辑
- ✅ API密钥加密存储(部分隐藏)
- ✅ 跨会话保持
- ✅ 可随时修改

### ✓ 后续使用中可修改

**CLI修改**:
```bash
# 随时查看配置
python seismic_cli.py llm show

# 重新设置
python seismic_cli.py llm setup

# 快速切换
python seismic_cli.py llm set-provider openai
python seismic_cli.py llm set-model gpt-4o
```

**Web修改**:
```
1. 访问 /llm-settings
2. 修改任意配置项
3. 点击 "Save Configuration"
4. 立即生效
```

## 📊 文件清单

### 新增文件

1. **config_manager.py** - 配置管理器核心
2. **web_app/templates/llm_settings.html** - Web设置页面
3. **LLM_SETUP_GUIDE.md** - 详细使用文档
4. **LLM功能说明.md** - 本文件

### 修改文件

1. **seismic_cli.py**
   - 添加LLM子命令
   - 首次运行检测
   - 配置导入

2. **web_app/app.py**
   - 添加配置管理器导入
   - 新增5个LLM相关API端点
   - 更新启动信息

3. **web_app/templates/index.html**
   - 导航栏添加LLM Settings链接

## 🚀 使用示例

### 示例1: 首次使用CLI

```bash
$ python seismic_cli.py

================================================================================
Welcome to SeismicX!
================================================================================

This appears to be your first time using SeismicX.
Let's configure your LLM (Large Language Model) settings.

Would you like to set up LLM configuration now? (y/n) [y]: y

================================================================================
SeismicX - First Time Setup
================================================================================

✓ Ollama detected on your system
✓ Found 3 installed model(s):
  - qwen2.5:7b
  - llama3.2:3b
  - mistral:7b

Choose your LLM provider:
  1. Ollama (Local models - Recommended)
  2. OpenAI (GPT-4, GPT-3.5)
  3. Anthropic (Claude)
  4. Azure OpenAI
  5. Custom API

Enter choice (1-5) [1]: 1

Available Ollama models:
  1. qwen2.5:7b (installed)
  2. llama3.2:3b (installed)
  3. mistral:7b (installed)

Select a model:
  - Enter number to choose from above
  - Or type model name directly (e.g., 'qwen2.5:7b')

Your choice: 1

================================================================================
✓ Setup complete! Configuration saved.
================================================================================
```

### 示例2: 切换到OpenAI

```bash
$ python seismic_cli.py llm set-provider openai
✓ LLM provider set to: openai

$ python seismic_cli.py llm set-model gpt-4o
✓ LLM model set to: gpt-4o

$ python seismic_cli.py llm show
Current LLM Configuration:
----------------------------------------
provider: openai
model: gpt-4o
api_base: https://api.openai.com/v1
api_key: ******** (hidden)
temperature: 0.7
max_tokens: 2000
```

### 示例3: Web界面操作

1. 访问 http://localhost:5000/llm-settings
2. 点击 "OpenAI" 卡片
3. 输入API密钥: sk-xxxxxxxxx
4. 输入模型名: gpt-4o
5. 调整Temperature: 0.7
6. 点击 "Save Configuration"
7. 看到成功提示 ✓

### 示例4: 安装新Ollama模型

**方法1: 命令行**
```bash
ollama pull llama3.1:8b
```

**方法2: Web界面**
1. 访问 LLM Settings
2. 在 "Recommended Models" 找到 llama3.1:8b
3. 点击 "Install" 按钮
4. 等待下载完成
5. 模型自动出现在已安装列表

## 🔒 安全性

### API密钥保护

1. **存储安全**
   - 仅保存在本地文件
   - 不会上传到任何服务器
   - 文件权限设置为仅所有者可读

2. **显示安全**
   - Web界面显示时隐藏大部分字符
   - CLI显示时用星号替代
   - 日志中不记录完整密钥

3. **传输安全**
   - Web API使用HTTPS (生产环境)
   - 本地通信使用localhost

### 隐私保护

- Ollama本地模型: 所有数据处理在本地
- 在线API: 遵循各提供商隐私政策
- 无数据收集: SeismicX不收集使用情况

## 💡 最佳实践

### 1. 选择合适的提供商

**个人研究**:
- 推荐: Ollama + qwen2.5:7b
- 原因: 免费、隐私好、性能足够

**生产环境**:
- 推荐: OpenAI GPT-4o 或 Azure
- 原因: 稳定、高质量、技术支持

**预算有限**:
- 推荐: Ollama + llama3.2:3b
- 原因: 轻量、快速、免费

### 2. 模型选择建议

| 任务类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 地震数据分析 | qwen2.5:14b | 理解能力强 |
| 代码生成 | deepseek-coder:6.7b | 代码专用 |
| 快速问答 | llama3.2:3b | 响应快 |
| 复杂推理 | GPT-4o | 最强推理 |
| 长文本 | Claude-3 | 上下文长 |

### 3. 参数调优

**Temperature**:
- 事实查询: 0.2-0.4 (更确定)
- 一般对话: 0.5-0.7 (平衡)
- 创意任务: 0.8-1.0 (更多样)

**Max Tokens**:
- 简短回答: 500-1000
- 详细解释: 2000-3000
- 长篇分析: 4000+

## 🐛 故障排查

### 问题1: 首次设置没有启动

**解决**:
```bash
# 手动启动设置
python seismic_cli.py llm setup

# 或删除配置文件重置
rm ~/.seismicx/config.json
```

### 问题2: Ollama检测失败

**检查**:
```bash
# Ollama是否安装
which ollama

# 服务是否运行
ollama list

# 启动服务
ollama serve
```

### 问题3: Web页面无法保存配置

**检查**:
1. 浏览器控制台是否有错误
2. Flask应用是否正常启动
3. 配置文件权限是否正确

**修复**:
```bash
# 检查配置目录权限
ls -la ~/.seismicx/

# 修复权限
chmod 700 ~/.seismicx
chmod 600 ~/.seismicx/config.json
```

### 问题4: API调用失败

**检查**:
1. API密钥是否正确
2. 网络连接是否正常
3. API配额是否用完

**调试**:
```bash
# 测试OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 📈 性能优化

### Ollama优化

1. **选择合适大小的模型**
   - CPU: 3B-7B参数
   - GPU (4GB): 7B参数
   - GPU (8GB+): 14B+参数

2. **量化版本**
   ```bash
   # 使用量化模型(更小更快)
   ollama pull qwen2.5:7b-q4_K_M
   ```

3. **内存管理**
   ```bash
   # 卸载不用的模型释放内存
   ollama rm unused_model
   ```

### 在线API优化

1. **使用缓存**
   - 相同问题不重复调用
   - 本地缓存常用回答

2. **批量处理**
   - 合并多个请求
   - 减少API调用次数

3. **监控费用**
   - 设置预算提醒
   - 定期检查用量

## 🎓 学习资源

- **Ollama官方**: https://ollama.ai
- **OpenAI文档**: https://platform.openai.com/docs
- **Anthropic文档**: https://docs.anthropic.com
- **SeismicX文档**: LLM_SETUP_GUIDE.md

## 📞 技术支持

如有问题:
1. 查看 LLM_SETUP_GUIDE.md
2. 检查本文档的故障排查部分
3. 联系: yuziye@cea-igp.ac.cn

---

**完成日期**: 2026-04-09
**版本**: v1.0.0
**状态**: ✅ 已完成并测试
