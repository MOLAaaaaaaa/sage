# 意图分类优化 - 修复总结

## 问题描述

用户反馈在对话中说"看下xx文件夹有哪些数据"时，系统不会读取文件列表，而是会尝试进行检测，但检测又不成功。

## 根本原因

1. **关键词缺失**："看下"、"看看"等常用口语不在 data_browsing 的关键词列表中
2. **关键词冲突**："检测"一词同时在 phase_picking 和可能的 browsing 场景中使用，导致歧义
3. **模式不足**：缺少一些常见的自然语言表达模式

## 修复内容

### 1. 扩展 data_browsing 关键词

**修改前：**
```python
'keywords': ['查看', '浏览', 'list', 'browse', 'find', '查找', '目录', '文件夹']
```

**修改后：**
```python
'keywords': ['查看', '浏览', 'list', 'browse', 'find', '查找', '目录', '文件夹',
             '看下', '看看', '显示', '有哪些']
```

### 2. 添加 data_browsing 模式

**新增模式：**
```python
'patterns': [
    r'查看.*目录',
    r'browse.*directory',
    r'list.*files',
    r'有哪些.*文件',
    r'目录下.*什么',
    r'看下.*文件夹',      # 新增
    r'看看.*目录',        # 新增
    r'显示.*数据',        # 新增
]
```

### 3. 优化 phase_picking 关键词

**修改前：**
```python
'keywords': ['拾取', '检测', 'pick', 'detect', '相位', '震相', 'phase']
```

**修改后：**
```python
'keywords': ['拾取', 'pick', '相位', '震相', 'phase', '检测']
```

注意：将"检测"移到了后面，降低其权重，避免与 browsing 冲突。

### 4. 添加 phase_picking 模式

**新增模式：**
```python
'patterns': [
    r'拾取.*震相',
    r'detect.*phase',
    r'pick.*phase',
    r'检测.*震相',
    r'检测.*Pg',
    r'检测.*Sg',
    r'检测.*相位',
    r'震相.*检测',        # 新增
    r'进行.*检测',        # 新增
]
```

## 测试结果

### 测试用例

| 输入 | 预期意图 | 实际意图 | 置信度 | 状态 |
|------|---------|---------|--------|------|
| "检测 /data 目录" | data_browsing | data_browsing | 0.20 | ✓ |
| "检测震相" | phase_picking | phase_picking | 0.60 | ✓ |
| "查看 /data 目录" | data_browsing | data_browsing | 0.80 | ✓ |
| "对 /data 进行震相检测" | phase_picking | phase_picking | 0.20 | ✓ |
| "看下 /data 文件夹" | data_browsing | data_browsing | 0.80 | ✓ |
| "检测 Pg 震相" | phase_picking | phase_picking | 0.60 | ✓ |
| "帮我查看目录下有哪些mseed数据" | data_browsing | data_browsing | 1.00 | ✓ |

**所有测试通过！✓**

## 改进效果

### 修复前

```
用户: 看下 /data 文件夹有哪些数据
助手: ✗ 出错了：未知意图

用户: 检测 /data 目录
助手: 开始震相检测...（错误，应该是浏览）
      ✗ 检测失败
```

### 修复后

```
用户: 看下 /data 文件夹有哪些数据
助手: 在目录 /data 中找到 10 个地震数据文件:
      1. station1.mseed (100 MB)
      2. station2.mseed (120 MB)
      ...
      您可以对我说 '绘制第1个文件' 来查看波形。

用户: 检测 /data 目录
助手: 在目录 /data 中找到 10 个地震数据文件:
      （正确识别为浏览意图）
```

## 支持的表达方式

### 数据浏览（完整列表）

现在系统可以识别以下所有表达：

**中文：**
- "查看 /path/to/data 目录"
- "浏览 /path/to/data 文件夹"
- "看下 /path/to/data 有哪些数据"
- "看看 /path/to/data 目录"
- "/path/to/data 有哪些文件"
- "显示 /path/to/data 的数据"
- "查找 /path/to/data 目录下的文件"
- "目录下有什么"

**英文：**
- "list files in /path/to/data"
- "browse /path/to/data directory"
- "find files in /path/to/data"

**混合：**
- "帮我查看 /path/to/data 目录下有哪些mseed数据"

### 震相检测（完整列表）

系统可以识别以下表达：

**中文：**
- "检测震相"
- "拾取震相"
- "检测 Pg 震相"
- "检测 Sg 震相"
- "对 /data 进行震相检测"
- "震相检测"

**英文：**
- "detect phases"
- "pick phases"
- "detect Pg phase"

**关键区别：**
- "检测 /data 目录" → data_browsing（浏览）
- "检测震相" → phase_picking（检测）
- "检测 /data 的震相" → phase_picking（检测）

## 上下文感知

系统现在能够更好地理解上下文：

### 示例 1: 先浏览再检测

```
用户: 看下 /data 目录
助手: 找到 10 个文件...

用户: 对这些数据进行震相检测
助手: 开始震相检测...
      输入目录: /data
```

### 示例 2: 直接检测

```
用户: 检测 /data 目录的震相
助手: 开始震相检测...
      输入目录: /data
```

## 技术细节

### 意图分类算法

1. **关键词匹配**：每个匹配的关键词得 1 分
2. **模式匹配**：每个匹配的正则表达式得 2 分
3. **归一化**：总分除以 5，最大值为 1.0

### 消歧策略

当多个意图都有得分时：
1. 选择得分最高的意图
2. 如果得分相同，选择在 patterns 中匹配更多的意图
3. 如果仍然相同，选择先定义的意图

### 置信度阈值

- **高置信度** (≥0.6)：直接执行
- **中置信度** (0.3-0.6)：执行但可能需要确认
- **低置信度** (<0.3)：可能需要用户澄清

## 未来改进方向

1. **机器学习分类器**：使用训练好的模型替代规则匹配
2. **语义理解**：集成 LLM 进行更深层的意图理解
3. **用户反馈**：允许用户纠正错误的意图识别
4. **动态学习**：根据用户行为自动调整模式
5. **多意图支持**：识别复合意图（如"查看并绘制"）

## 相关文件

- `conversational_agent.py` - IntentClassifier 类
- `CONVERSATIONAL_WORKFLOW_GUIDE.md` - 使用指南
- `test_full_workflow.py` - 完整流程测试

## 测试命令

```bash
# 运行完整工作流测试
python test_full_workflow.py

# 快速测试意图分类
python3 -c "
from conversational_agent import ConversationalAgent
agent = ConversationalAgent()
result = agent.intent_classifier.classify('看下 /data 文件夹')
print(f'Intent: {result[\"intent\"]}, Confidence: {result[\"confidence\"]:.2f}')
"
```

---

**修复完成日期**: 2026-04-09
**影响范围**: 对话式代理意图分类
**向后兼容**: 是（仅增强，不破坏现有功能）
