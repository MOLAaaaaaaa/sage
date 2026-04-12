# 自然语言对话功能使用指南

## 概述

现在您可以通过自然语言与系统对话,执行文件管理、绘图、地质分析等操作,无需记住复杂的命令。

## 核心功能

### 1. 智能意图识别
系统能自动识别您的意图并路由到相应功能:
- 文件列表和浏览
- 数据可视化绘图
- 区域地质分析
- 文献检索
- 矿床类型识别
- 一般对话

### 2. 文件系统操作

#### CLI方式
```bash
# 列出当前目录文件
python main.py chat "列出当前目录的文件"

# 列出指定目录
python main.py chat "列出docs目录下的文件"

# 列出特定类型文件
python main.py chat "列出markdown文件"
python main.py chat "列出PDF文件"
```

#### Web API
```bash
curl -X POST http://localhost:8000/api/chat \
  -d "message=列出当前目录的文件"
```

#### Python API
```python
from core.chat_agent import ChatAgent

agent = ChatAgent()
result = agent.process_command("列出docs目录下的markdown文件")
print(result['response'])
```

### 3. 自然语言绘图

#### 示例命令
```bash
# 绘制速度剖面图
python main.py chat "绘制速度剖面图 data.npy"

# 绘制重力异常图
python main.py chat "绘制重力异常图 gravity.csv"

# 绘制磁异常图
python main.py chat "绘制磁异常图 magnetic_data.txt"
```

#### 支持的数据格式
- `.npy` / `.npz`: NumPy数组
- `.csv`: CSV表格
- `.json`: JSON数据
- `.txt`: 文本表格

#### 数据格式要求

**速度剖面数据**:
```python
{
    'depth': [0, 1, 2, 3, ...],      # 深度
    'velocity': [5.0, 5.2, 5.5, ...]  # 速度
}
```

**重力数据**:
```python
{
    'x': [0, 1, 2, 3, ...],           # 距离
    'gravity': [0.5, 0.8, 1.2, ...]   # 重力异常(mGal)
}
```

**磁法数据**:
```python
{
    'x': [0, 1, 2, 3, ...],            # 距离
    'magnetic': [100, 150, 200, ...]   # 磁异常(nT)
}
```

### 4. 地质分析

#### 区域分析
```bash
python main.py chat "分析塔里木盆地的地质特征"
python main.py chat "分析四川盆地"
```

#### 文献检索
```bash
python main.py chat "搜索斑岩铜矿相关文献"
python main.py chat "查找矽卡岩铁矿资料"
```

#### 矿床识别
```bash
python main.py chat "识别矿床类型: 高磁异常,高密度,接触带矽卡岩"
```

## 使用示例

### 示例1: 文件管理
```
用户: 列出当前目录的文件
系统: 📁 目录 /path/to/project 下的文件:

1. 📄 README.md
   大小: 5.2 KB | 修改: 2026-04-10 09:30
2. 📄 main.py
   大小: 1.2 KB | 修改: 2026-04-10 09:25
...

总计: 19 个文件
```

### 示例2: 绘图
```
用户: 绘制速度剖面图 velocity_data.npy
系统: ✅ 速度剖面图已保存到: output/plots/velocity_profile.png
```

### 示例3: 地质分析
```
用户: 分析塔里木盆地
系统: (AI生成的详细地质分析报告...)
```

## 支持的命令模式

### 文件操作
- "列出[目录]的文件"
- "查看[目录]有哪些文件"
- "显示[类型]文件"
- "list files in [directory]"

### 绘图
- "绘制[数据类型]图 [文件]"
- "画图 [文件]"
- "plot [file]"
- "可视化[数据]"

### 地质分析
- "分析[地区]"
- "地质解释[地区]"
- "搜索[主题]文献"
- "识别矿床类型"

## 技术架构

### 组件
1. **ChatRouter**: 意图识别和参数提取
2. **FileSystemTool**: 文件系统操作
3. **NaturalLanguagePlotter**: 自然语言绘图
4. **ChatAgent**: 统一对话处理器

### 工作流程
```
用户输入
  ↓
意图识别 (ChatRouter)
  ↓
参数提取
  ↓
路由到处理器
  ↓
执行操作
  ↓
返回结果
```

## Web界面集成

在Web界面中添加聊天框(待实现):
```html
<div class="chat-container">
    <input type="text" id="chat-input" placeholder="输入命令...">
    <button onclick="sendChat()">发送</button>
    <div id="chat-response"></div>
</div>

<script>
async function sendChat() {
    const message = document.getElementById('chat-input').value;
    const response = await fetch('/api/chat', {
        method: 'POST',
        body: new FormData().append('message', message)
    });
    const result = await response.json();
    document.getElementById('chat-response').innerText = result.response;
}
</script>
```

## 扩展开发

### 添加新的意图类型

1. 在 `ChatRouter.command_patterns` 中添加新模式
2. 在 `ChatAgent` 中实现对应的处理方法
3. 更新路由逻辑

```python
# 在 chat_router.py 中添加
self.command_patterns['new_intent'] = [
    r'模式1',
    r'pattern2',
]

# 在 chat_agent.py 中添加
def _handle_new_intent(self, user_input, params):
    # 实现处理逻辑
    pass
```

## 故障排除

### Q: 意图识别不准确?
A: 尝试更明确的表达,或添加关键词如"列出"、"绘制"、"分析"等

### Q: 文件找不到?
A: 使用相对路径或绝对路径,确保路径正确

### Q: 绘图失败?
A: 检查数据文件格式,确保包含必需的字段

## 最佳实践

1. **明确表达**: 使用清晰的动词如"列出"、"绘制"、"分析"
2. **提供路径**: 操作文件时指定明确的路径
3. **数据格式**: 确保数据文件符合要求的格式
4. **渐进式**: 先列出文件,再选择具体文件操作

---

**让地质工作更智能,从自然语言对话开始!** 💬🌍
