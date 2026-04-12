# 快速开始 - 一句话数据浏览和绘图

## 安装依赖

```bash
pip install obspy matplotlib numpy
```

## 使用方式

### 方式 1: 命令行对话 (CLI)

```bash
python conversational_agent.py
```

**示例对话：**

```
Assistant: 您好！我是SeismicX智能助手...

You: 帮我查看 /path/to/data 目录下有哪些mseed数据
Assistant: 在目录 /path/to/data 中找到 25 个地震数据文件:
           1. GG.53036.mseed (245.3 MB)
           2. GG.53037.mseed (198.7 MB)
           ...

You: 绘制第1个文件
Assistant: ✓ 波形图已生成!
           文件: GG.53036.mseed
           输出: results/waveforms/GG.53036_20260409_143052.png

You: 退出
Assistant: 再见！祝您工作顺利！
```

### 方式 2: Web 聊天界面

```bash
cd web_app
python app.py
```

然后在浏览器中访问 `http://localhost:5000/chat`

### 方式 3: 直接运行演示

```bash
python demo_waveform_visualization.py
```

## 常用命令

### 数据浏览

```
"查看 /path/to/data 目录"
"浏览 /data/seismic 文件夹"
"list files in /path/to/data"
"查找目录下的mseed文件"
```

### 波形绘制

```
"绘制 /path/to/file.mseed 的波形"
"plot waveform from /data/file.sac"
"显示 file.mseed 的波形图"
"画一下这个文件"
"绘制第1个文件"  # 需要先浏览过目录
```

### 其他功能

```
"能做什么"                    # 显示帮助信息
"帮我拾取震相"                # 震相检测
"关联地震事件"                # 震相关联
"分析极性"                    # 初动极性分析
```

## 工作流程示例

### 场景 1: 浏览 → 选择 → 绘制

```
You: 查看 /data/seismic 目录
Assistant: 找到 10 个文件...

You: 绘制第3个文件
Assistant: 波形图已生成...
```

### 场景 2: 直接绘制指定文件

```
You: 绘制 /data/station1.mseed 的波形
Assistant: 波形图已生成!
           输出: results/waveforms/station1_20260409.png
```

### 场景 3: 完整分析流程

```
You: 查看 /data/seismic 目录
Assistant: 找到 10 个文件...

You: 绘制第1个文件
Assistant: 波形图已生成...

You: 对第1个文件进行震相检测
Assistant: 开始震相检测...
```

## 输出说明

### 浏览结果

- 文件名列表（最多显示20个）
- 每个文件的大小（MB）
- 总文件数量
- 后续操作提示

### 绘图结果

- 成功消息
- 源文件名
- 输出文件路径
- 保存目录位置

## 支持的文件格式

- **MiniSEED**: `.mseed`, `.miniseed`
- **SAC**: `.sac`
- **SEED**: `.seed`

## 常见问题

**Q: 为什么找不到我的文件？**
A: 确保路径正确，使用绝对路径更可靠。检查文件扩展名是否为支持的格式。

**Q: 绘图失败怎么办？**
A: 检查是否安装了 ObsPy 和 matplotlib：
```bash
pip install obspy matplotlib
```

**Q: 可以一次绘制多个文件吗？**
A: 当前版本一次绘制一个文件，但可以通过连续对话快速处理多个文件。

**Q: 波形图保存在哪里？**
A: 默认保存在 `results/waveforms/` 目录下。

## 下一步

- 阅读 [完整使用指南](WAVEFORM_VISUALIZATION_GUIDE.md)
- 查看 [实现细节](IMPLEMENTATION_SUMMARY.md)
- 了解 [对话式AI功能](CONVERSATIONAL_AGENT_GUIDE.md)
