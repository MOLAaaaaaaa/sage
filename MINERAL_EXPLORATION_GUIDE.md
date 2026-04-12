# 找矿勘探系统使用指南

## 概述

本系统提供针对**金属矿产勘探**的综合分析功能,整合重磁电、测井等多源地球物理数据,进行矿床类型识别、成矿要素分析和资源潜力评价。

## 核心功能

### 1. 多源数据集成
- **重力数据**: 密度结构、构造格架
- **磁法数据**: 磁性体定位、岩体圈定
- **电磁数据**: 导电性分析、硫化物探测
- **测井数据**: 岩性识别、矿层划分
- **地质资料**: 地层、构造、岩性、蚀变

### 2. 矿床类型识别
支持识别的主要矿床类型:
- 斑岩型铜矿
- 矽卡岩型铁矿
- VMS块状硫化物矿床
- 造山型金矿
- 卡林型金矿
- 岩浆铜镍硫化物矿床

### 3. 成矿要素分析
- 构造控矿要素
- 岩性岩相要素
- 岩浆活动要素
- 地层要素
- 蚀变矿化要素
- 地球化学要素
- 地球物理要素

### 4. 综合报告生成
自动生成完整的矿床勘探报告,包括:
- 区域地质背景
- 矿区地质特征
- 地球物理场特征
- 矿床地质特征
- 矿床类型及成矿模式
- 找矿标志
- 资源潜力评价
- 工作建议

## 使用方法

### Python API

```python
from mineral.exploration_agent import MineralExplorationAgent
import numpy as np

# 创建Agent
agent = MineralExplorationAgent(
    enable_rag=True,
    embedding_type="bge-m3"
)

# 1. 加载地球物理数据
gravity_data = {
    'x': np.array([...]),
    'y': np.array([...]),
    'z': np.array([...]),
    'gravity_values': np.array([...])
}
agent.load_gravity_data(gravity_data)

magnetic_data = {
    'x': np.array([...]),
    'y': np.array([...]),
    'magnetic_values': np.array([...])
}
agent.load_magnetic_data(magnetic_data)

# 2. 矿床类型识别
result = agent.identify_deposit_type(
    gravity_anomaly="剩余重力异常显示北东向正异常带,幅值约2mgal",
    magnetic_anomaly="高磁异常,强度500nT,呈等轴状",
    em_response="低阻高极化异常,电阻率<100Ω·m,极化率>5%",
    geological_features="花岗闪长岩与灰岩接触带,石榴子石矽卡岩发育"
)

print(result['analysis'])

# 3. 成矿要素分析
elements_analysis = agent.analyze_mineralization_elements(
    region_description="某地区位于华北克拉通北缘,出露太古宙变质岩系...",
    available_data={
        '重力': '已完成1:5万测量',
        '磁法': '已完成1:1万测量',
        '地质': '发现矽卡岩化'
    }
)

# 4. 综合分析
report = agent.comprehensive_analysis(
    project_name="XX铜矿勘探项目",
    location="XX省XX县,地理坐标...",
    use_rag=True
)

# 5. 生成报告
agent.generate_exploration_report(
    title="XX铜矿勘探综合研究报告",
    analyses=[
        {'title': '区域地质背景', 'content': '...'},
        {'title': '地球物理特征', 'content': '...'},
        {'title': '矿床类型', 'content': result['analysis']}
    ],
    output_path="reports/xx_copper_deposit.md"
)
```

### 典型应用场景

#### 场景1: 斑岩铜矿勘查
```python
# 输入典型的斑岩型铜矿地球物理特征
result = agent.identify_deposit_type(
    gravity_anomaly="环形低重力异常,反映低密度蚀变岩筒",
    magnetic_anomaly="环带状磁异常,中心弱磁外围强磁",
    em_response="核部低阻(泥化带),外带高极化(硫化物矿化)",
    geological_features="花岗闪长斑岩,钾化-绢云母化-青磐岩化分带"
)
# 预期输出: 斑岩型铜矿
```

#### 场景2: 矽卡岩铁矿评价
```python
result = agent.identify_deposit_type(
    gravity_anomaly="明显正异常,反映高密度磁铁矿体",
    magnetic_anomaly="强高磁异常,>1000nT",
    em_response="低阻异常,磁铁矿导电性好",
    geological_features="岩体与灰岩接触带,石榴子石-透辉石矽卡岩"
)
# 预期输出: 矽卡岩型铁矿
```

## 矿床类型地球物理特征对照表

| 矿床类型 | 重力 | 磁法 | 电磁 | 典型实例 |
|---------|------|------|------|---------|
| 斑岩型铜矿 | 低密度负异常 | 环带状磁性 | 低阻高极化 | 德兴、玉龙 |
| 矽卡岩铁矿 | 高密度正异常 | 强高磁 | 低阻 | 大冶、邯邢 |
| VMS矿床 | 中等差异 | 弱磁 | 极强导电 | 白银厂 |
| 造山型金矿 | 不明显 | 断裂低磁 | 含硫化物时极化 | 焦家、玲珑 |
| 卡林型金矿 | 低密度 | 弱磁 | 含砷黄铁矿时极化 | 烂泥沟 |
| 铜镍硫化物 | 高密度 | 强磁 | 强导电极化 | 金川、黄山 |

## 数据格式要求

### 重力数据
```python
{
    'x': np.array([经度或X坐标]),
    'y': np.array([纬度或Y坐标]),
    'z': np.array([高程]),
    'gravity_values': np.array([布格重力异常, mGal]),
    'station_info': '测站信息描述'
}
```

### 磁法数据
```python
{
    'x': np.array([X坐标]),
    'y': np.array([Y坐标]),
    'magnetic_values': np.array([地磁异常, nT]),
    'survey_info': '测量信息'
}
```

### 电磁数据
```python
{
    'x': np.array([测点X]),
    'y': np.array([测点Y]),
    'resistivity': np.array([视电阻率, Ω·m]),
    'chargeability': np.array([极化率, %]),
    'frequency': np.array([频率, Hz])
}
```

### 测井数据
```python
{
    'depth': np.array([深度, m]),
    'gr': np.array([自然伽马, API]),
    'sp': np.array([自然电位, mV]),
    'resistivity': np.array([电阻率, Ω·m]),
    'density': np.array([密度, g/cm³]),
    'neutron': np.array([中子孔隙度, %])
}
```

## 成矿要素分析框架

系统按照以下框架进行成矿要素分析:

1. **构造控矿**: 大地构造背景、控矿构造样式
2. **岩性控矿**: 容矿岩石、有利岩性组合
3. **岩浆控矿**: 成矿岩体、岩浆演化
4. **地层控矿**: 赋矿层位、时代
5. **蚀变分带**: 蚀变类型、空间分布
6. **地球化学**: 元素组合、原生晕
7. **地球物理**: 重磁电异常模式

## RAG文献检索

系统可自动从上传的地质文献中检索相关信息:

```python
# 上传矿床学文献
agent.rag.upload_pdf("porphyry_copper_deposits.pdf")

# 检索相关文献
results = agent.rag.search_literature("斑岩铜矿 地球物理特征")

# 在分析中自动使用文献
report = agent.comprehensive_analysis(
    project_name="XX铜矿",
    location="...",
    use_rag=True  # 启用文献检索
)
```

## 下一步开发计划

### 已实现
- ✅ 矿床类型识别专家系统
- ✅ 成矿要素分析框架
- ✅ 多源数据管理
- ✅ 综合报告生成
- ✅ RAG文献支持

### 待实现
- [ ] 重力反演模块 (3D密度建模)
- [ ] 磁法反演模块 (磁化率成像)
- [ ] 电磁反演模块 (电阻率层析)
- [ ] 测井解释模块 (岩性识别)
- [ ] 多源数据融合算法
- [ ] 找矿靶区预测
- [ ] 三维可视化

## 技术架构

- **AI模型**: Ollama + Qwen3-VL-30B
- **嵌入模型**: BGE-M3 (中文优化)
- **向量数据库**: ChromaDB
- **科学计算**: NumPy, SciPy
- **数据处理**: 专业地球物理库(待集成)

---

**找矿勘探,智能辅助!** ⛏️🔍
