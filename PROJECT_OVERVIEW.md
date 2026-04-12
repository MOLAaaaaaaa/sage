# SeismicX Skills - 项目结构

## 📁 目录结构

```
SeismicX-Skills/
├── .lingma/skills/                    # AI Skills定义
│   ├── seismic-phase-picker/         # 震相检测技能
│   │   └── SKILL.md                  # 技能文档和使用指南
│   ├── seismic-phase-associator/     # 震相关联技能
│   │   └── SKILL.md                  # 技能文档和使用指南
│   └── seismic-polarity-analyzer/    # 初动极性分析技能
│       └── SKILL.md                  # 技能文档和使用指南
│
├── pnsn/                             # PNSN原始项目(地震监测流程)
│   ├── pickers/                      # 预训练模型
│   │   ├── pnsn.v3.jit              # PNSN v3模型(TorchScript)
│   │   ├── pnsn.diff.v3.jit         # PNSN v3差分模型
│   │   ├── polar.jit                # 初动极性模型
│   │   ├── eqt.jit                  # EQTransformer模型
│   │   ├── phasenet.jit             # PhaseNet模型
│   │   └── ...                       # 其他模型
│   ├── ckpt/                         # 模型检查点
│   ├── config/                       # 配置文件
│   │   ├── picker.py                # 拾取器配置
│   │   ├── fastlink.py              # FastLink配置
│   │   └── gamma.py                 # GaMMA配置
│   ├── models/                       # 模型定义
│   ├── picker.py                     # 震相拾取主程序
│   ├── fastlinker.py                 # FastLink关联程序
│   ├── reallinker.py                 # REAL关联程序
│   ├── gammalink.py                  # GaMMA关联程序
│   └── data/                         # 示例数据
│
├── web_app/                          # Web界面应用
│   ├── app.py                        # Flask主应用
│   ├── requirements.txt              # Python依赖
│   ├── templates/                    # HTML模板
│   │   ├── index.html               # 主页
│   │   ├── picker.html              # 震相检测页面
│   │   ├── associator.html          # 震相关联页面
│   │   └── polarity.html            # 极性分析页面
│   ├── static/                       # 静态资源
│   │   ├── css/                     # 样式文件
│   │   └── js/                      # JavaScript文件
│   ├── uploads/                      # 上传文件目录
│   └── outputs/                      # 输出文件目录
│
├── seismic_cli.py                    # 统一CLI命令行工具
├── SKILLS_README.md                  # Skills使用文档
├── PROJECT_OVERVIEW.md               # 本文件
└── examples/                         # 使用示例
    └── quickstart.sh                 # 快速启动脚本
```

## 🔧 核心组件

### 1. Skills层 (.lingma/skills/)

三个独立的AI技能,每个包含完整的SKILL.md文档:

**seismic-phase-picker**
- 功能: 震相自动检测
- 输入: 波形文件目录
- 输出: 震相拾取文件(.txt)
- 支持: CLI + Web

**seismic-phase-associator**
- 功能: 地震事件关联
- 输入: 震相文件 + 台站文件
- 输出: 地震事件目录
- 算法: REAL / FastLink / GaMMA

**seismic-polarity-analyzer**
- 功能: 初动极性分类
- 输入: 震相文件 + 波形文件
- 输出: 极性标注结果
- 应用: 震源机制解

### 2. PNSN核心层 (pnsn/)

原始地震监测流程代码:

**模型文件**
- TorchScript格式(.jit): 直接PyTorch加载
- ONNX格式(.onnx): 跨平台部署

**处理脚本**
- `picker.py`: 多进程震相拾取
- `fastlinker.py`: LPPN关联算法
- `reallinker.py`: REAL关联算法
- `gammalink.py`: GaMMA关联算法

**配置系统**
- `config/picker.py`: 拾取参数
- `config/fastlink.py`: FastLink参数
- `config/gamma.py`: GaMMA参数

### 3. 接口层

**CLI接口 (seismic_cli.py)**
```bash
python seismic_cli.py <command> [options]

Commands:
  pick        - 震相检测
  associate   - 震相关联
  polarity    - 极性分析
```

**Web接口 (web_app/)**
```bash
cd web_app && python app.py

Endpoints:
  GET  /              - 主页
  GET  /picker        - 震相检测界面
  GET  /associator    - 震相关联界面
  GET  /polarity      - 极性分析界面
  POST /api/pick      - 提交拾取任务
  POST /api/associate - 提交关联任务
  POST /api/polarity  - 提交极性任务
```

## 🚀 使用流程

### 典型工作流

```
1. 准备数据
   ↓
   波形文件(mseed/sac) + 台站文件(txt)

2. 震相检测 (Phase Picker)
   ↓
   python seismic_cli.py pick -i waveforms -o picks -m model

3. 震相关联 (Phase Associator)
   ↓
   python seismic_cli.py associate -i picks.txt -s stations.txt -o events.txt

4. 极性分析 (Polarity Analyzer) [可选]
   ↓
   python seismic_cli.py polarity -i picks.txt -w waveforms -o polarity.txt

5. 结果分析
   ↓
   地震目录 + 震相报告 + 极性数据
```

### Web界面工作流

```
1. 启动Web服务
   ↓
   cd web_app && python app.py

2. 浏览器访问 http://localhost:5000

3. 在图形界面中:
   - 选择技能
   - 填写参数
   - 提交任务
   - 查看状态
   - 下载结果
```

## 📊 数据流

```
波形数据 (Input)
    ↓
[Phase Picker]
    ↓
震相拾取文件 (.txt)
    ├─ 相对时间
    ├─ 绝对时间
    ├─ 置信度
    ├─ 信噪比
    └─ 台站信息
    ↓
[Phase Associator]
    ↓
地震事件文件 (.txt)
    ├─ 发震时刻
    ├─ 经纬度
    ├─ 深度
    └─ 关联震相
    ↓
[Polarity Analyzer] (Optional)
    ↓
极性标注结果 (.txt)
    ├─ 极性方向 (U/D)
    └─ 置信度
```

## 🔑 关键特性

### 多模型支持
- **PNSN v3**: 最佳综合性能
- **PhaseNet**: 快速推理
- **EQTransformer**: 全球适用
- **RNN**: 高召回率
- **LPPN**: 轻量级

### 多算法关联
- **FastLink**: 快速2D关联
- **REAL**: 高精度3D定位
- **GaMMA**: 概率框架

### 双接口设计
- **CLI**: 适合批处理和自动化
- **Web**: 适合交互式探索

### 并行处理
- 多进程数据加载
- 多模型并行推理
- GPU加速支持

## 📝 配置文件说明

### picker.py 配置

```python
class Parameter:
    nchannel = 3              # 通道数
    samplerate = 100          # 采样率(Hz)
    prob = 0.3                # 置信度阈值
    nmslen = 1000             # NMS窗口(采样点)
    npicker = 1               # 并行模型数
    npre = 2                  # 数据加载进程数
    polar = False             # 初动极性开关
    ifplot = False            # 绘图开关
```

### fastlink.py 配置

```python
class Parameter:
    ngrid = 20                # 网格大小
    win_length = 30.0         # 时间窗口长度(秒)
    win_stirde = 5.0          # 窗口步长(秒)
    nps = 6                   # 最小总震相数
    np = 3                    # 最小P震相数
    ns = 2                    # 最小S震相数
```

## 🎯 应用场景

### 1. 实时地震监测
- 连续波形流处理
- 自动震相拾取
- 快速事件关联
- 实时目录生成

### 2. 离线数据分析
- 历史数据重处理
- 模型对比测试
- 参数优化研究

### 3. 震源机制研究
- 初动极性提取
- 断层面解约束
- 应力场分析

### 4. 台网质量评估
- 拾取一致性检查
- 台站性能监控
- 速度模型验证

## 🔍 故障排查

### 常见问题

**问题1: 模型加载失败**
```
解决: 确认模型文件路径正确
检查: ls -lh pnsn/pickers/*.jit
```

**问题2: CUDA out of memory**
```
解决: 减小batch size或使用CPU
命令: -d cpu
```

**问题3: 无震相输出**
```
解决: 降低置信度阈值
配置: prob = 0.1
```

**问题4: 关联不出事件**
```
解决: 检查台站坐标
验证: cat stations.txt
```

## 📚 相关文档

- **Skills文档**: `.lingma/skills/*/SKILL.md`
- **使用指南**: `SKILLS_README.md`
- **PNSN原文档**: `pnsn/README.md`
- **快速开始**: `examples/quickstart.sh`

## 🤝 贡献指南

欢迎贡献:
1. Fork本项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📧 联系方式

- **原作者**: Yuqi Cai, Ziye Yu
- **邮箱**: yuziye@cea-igp.ac.cn
- **论文**: https://doi.org/10.1029/2025JH000944

---

**版本**: v1.0.0
**更新日期**: 2026-04-09
