# 一句话数据浏览和绘图功能指南

## 概述

SeismicX 现在支持通过自然语言对话来浏览地震数据目录和绘制波形图。您可以使用简单的中文或英文命令来查看文件并可视化数据。

## 功能特性

### 1. 数据浏览 (Data Browsing)

扫描指定目录，查找地震数据文件（支持 .mseed, .sac, .seed, .miniseed 格式）。

**示例命令：**
```
- "帮我查看 /path/to/data 目录下有哪些mseed数据"
- "浏览 /data/seismic 目录"
- "list files in /path/to/data"
- "查找 /data 目录下的文件"
```

**输出示例：**
```
在目录 /path/to/data 中找到 15 个地震数据文件:

1. GG.53036.mseed (245.3 MB)
2. GG.53037.mseed (198.7 MB)
3. GG.53038.mseed (312.1 MB)
...

您可以对我说 '绘制第1个文件' 或 '绘制 GG.53036.mseed' 来查看波形。
```

### 2. 波形绘制 (Waveform Plotting)

使用 ObsPy 读取数据并用 matplotlib 创建专业的波形图。

**示例命令：**
```
- "绘制 /path/to/file.mseed 的波形"
- "plot waveform from /data/file.sac"
- "显示 file.mseed 的波形图"
- "画一下这个文件"
```

**输出示例：**
```
✓ 波形图已生成!

文件: GG.53036.mseed
输出: results/waveforms/GG.53036_20260409_143052.png

图片已保存到 results/waveforms 目录。
```

## 使用方式

### 命令行界面 (CLI)

```bash
# 启动对话式代理
python conversational_agent.py

# 然后输入命令，例如：
You: 帮我查看 /Users/yuziye/machinelearning/USTC-Pickers易用性改进和对比/data/0521-0522foryangbi/GG/2021/GG.53036 目录下有哪些mseed数据

Assistant: 在目录 /Users/yuziye/... 中找到 25 个地震数据文件:
1. GG.53036.001.mseed (123.4 MB)
2. GG.53036.002.mseed (145.6 MB)
...

您可以对我说 '绘制第1个文件' 或 '绘制 GG.53036.001.mseed' 来查看波形。

You: 绘制第1个文件

Assistant: ✓ 波形图已生成!
文件: GG.53036.001.mseed
输出: results/waveforms/GG.53036.001_20260409_143052.png
```

### Web 界面

1. 启动 Web 应用：
```bash
cd web_app
python app.py
```

2. 在浏览器中打开 `http://localhost:5000/chat`

3. 在聊天界面中输入命令，例如：
   - "查看 /path/to/data 目录"
   - "绘制波形"

## 多轮对话示例

### 场景 1: 浏览后绘制

```
User: 帮我查看 /data/seismic 目录下有哪些mseed数据

Assistant: 在目录 /data/seismic 中找到 10 个地震数据文件:
1. station1.mseed (100 MB)
2. station2.mseed (120 MB)
...

User: 绘制第1个文件

Assistant: ✓ 波形图已生成!
输出: results/waveforms/station1_20260409_143052.png
```

### 场景 2: 直接绘制指定文件

```
User: 绘制 /data/station1.mseed 的波形

Assistant: ✓ 波形图已生成!
文件: station1.mseed
输出: results/waveforms/station1_20260409_143052.png
```

### 场景 3: 完整工作流程

```
User: 查看 /data/seismic 目录

Assistant: 找到 10 个文件...

User: 绘制第1个文件

Assistant: 波形图已生成...

User: 对这个文件进行震相检测

Assistant: 开始震相检测...
```

## 技术实现

### 依赖库

- **ObsPy**: 用于读取和处理地震数据
- **matplotlib**: 用于创建波形图
- **numpy**: 用于数据处理

安装依赖：
```bash
pip install obspy matplotlib numpy
```

### 支持的文件格式

- MiniSEED (.mseed, .miniseed)
- SAC (.sac)
- SEED (.seed)

### 绘图特性

1. **多道显示**: 自动检测并显示所有数据道
2. **归一化**: 数据自动归一化到 [-1, 1] 范围以便可视化
3. **台站信息**: 显示台站代码、网络代码和通道信息
4. **时间轴**: 以秒为单位的时间轴
5. **高分辨率**: 150 DPI 输出，适合 publication

### 代码结构

```python
# 意图分类
class IntentClassifier:
    - data_browsing: 识别浏览目录的意图
    - waveform_plotting: 识别绘制波形的意图

# 技能执行
class SkillExecutor:
    - _execute_data_browsing(): 扫描目录并返回文件列表
    - _execute_waveform_plotting(): 读取数据并绘制波形

# 内部绘图函数
def _plot_waveform_internal(file_path, output_image, entities):
    - 使用 obspy.read() 读取数据
    - 使用 matplotlib 创建多道波形图
    - 保存为 PNG 图像
```

## 故障排除

### 问题 1: "未安装 ObsPy 库"

**解决方案:**
```bash
pip install obspy
```

### 问题 2: "未安装 matplotlib 库"

**解决方案:**
```bash
pip install matplotlib
```

### 问题 3: "目录不存在"

**检查:**
- 确认路径是否正确
- 确认是否有访问权限
- 使用绝对路径而不是相对路径

### 问题 4: "文件中没有数据道"

**可能原因:**
- 文件格式不正确
- 文件已损坏
- 文件不是有效的地震数据格式

## 高级用法

### 结合其他技能

```
User: 查看 /data/seismic 目录

Assistant: 找到 10 个文件...

User: 绘制第1个文件

Assistant: 波形图已生成...

User: 对第1个文件进行震相检测

Assistant: 开始震相检测...
```

### 批量处理提示

虽然当前版本一次处理一个文件，但您可以通过对话快速连续处理多个文件：

```
User: 绘制第1个文件
User: 绘制第2个文件
User: 绘制第3个文件
```

## 未来改进方向

1. **批量绘图**: 一次绘制多个文件
2. **滤波选项**: 支持带通滤波等预处理
3. **震相标注**: 在波形图上标注拾取的震相
4. **交互式查看**: 支持缩放和平移
5. **频谱分析**: 添加频谱图显示

## 相关文档

- [对话式AI功能说明](CONVERSATIONAL_AGENT_GUIDE.md)
- [波形可视化技能](.lingma/skills/waveform-visualizer/SKILL.md)
- [LLM配置指南](LLM_SETUP_GUIDE.md)
