# SeismicX Skills - 地震学分析技能集合

基于PNSN (Pg/Sg/Pn/Sn Phase Picking) 项目创建的地震学方向AI Skills,提供震相检测、震相关联和初动极性分析的完整解决方案。

## 📋 目录

- [概述](#概述)
- [Skills列表](#skills列表)
- [快速开始](#快速开始)
- [CLI使用指南](#cli使用指南)
- [Web界面使用](#web界面使用)
- [技能详解](#技能详解)

## 概述

SeismicX Skills将复杂的地震监测流程封装为三个核心技能:

1. **震相检测** - 使用深度学习模型自动检测地震波震相
2. **震相关联** - 将多台站震相拾取关联为地震事件
3. **初动极性分析** - 分析P波初动方向用于震源机制研究

每个技能都支持CLI命令行和Web图形界面两种控制方式。

## Skills列表

### 1. seismic-phase-picker (震相检测器)

**功能:**
- 检测Pg, Sg, Pn, Sn等多种震相
- 支持多种深度学习模型(PNSN, PhaseNet, EQTransformer等)
- 自动生成震相拾取图
- 批量处理波形文件

**位置:** `.lingma/skills/seismic-phase-picker/SKILL.md`

### 2. seismic-phase-associator (震相关联器)

**功能:**
- 三种关联算法(REAL, FastLink, GaMMA)
- 地震事件定位(经纬度、深度、发震时刻)
- 震相-事件分配与残差计算
- 质量控制指标

**位置:** `.lingma/skills/seismic-phase-associator/SKILL.md`

### 3. seismic-polarity-analyzer (初动极性分析器)

**功能:**
- P波初动方向分类(向上/向下)
- 置信度评分
- 波形可视化标注
- 适用于震源机制解研究

**位置:** `.lingma/skills/seismic-polarity-analyzer/SKILL.md`

## 快速开始

### 环境要求

```bash
Python >= 3.8
PyTorch >= 2.0
ObsPy >= 1.4
NumPy >= 1.24
SciPy >= 1.11
```

### 安装依赖

```bash
pip install numpy scipy obspy torch onnxruntime matplotlib tqdm
pip install flask  # Web界面需要
```

### 验证安装

```bash
python -c "import torch; import obspy; print('Dependencies OK')"
```

## CLI使用指南

### 统一CLI工具

```bash
# 查看帮助
python seismic_cli.py --help

# 震相检测
python seismic_cli.py pick \
    -i data/waveforms \
    -o results/picks \
    -m pnsn/pickers/pnsn.v3.jit \
    -d cpu

# 震相关联
python seismic_cli.py associate \
    -i results/picks.txt \
    -o results/events.txt \
    -s data/stations.txt \
    -m fastlink

# 初动极性分析
python seismic_cli.py polarity \
    -i results/picks.txt \
    -w data/waveforms \
    -o results/polarity.txt
```

### 直接使用原始脚本

```bash
# 震相检测
python pnsn/picker.py -i <输入目录> -o <输出名> -m <模型> -d <设备>

# FastLink关联
python pnsn/fastlinker.py -i <拾取文件> -o <输出文件> -s <台站文件> -d <设备>

# REAL关联
python pnsn/reallinker.py -i <拾取文件> -o <输出文件> -s <台站文件>

# GaMMA关联
python pnsn/gammalink.py -i <拾取文件> -o <输出文件> -s <台站文件>
```

## Web界面使用

### 启动Web服务

```bash
cd web_app
python app.py --port 5000 --host 0.0.0.0
```

### 访问界面

浏览器打开: `http://localhost:5000`

**主要页面:**
- **主页** (`/`) - Dashboard和技能概览
- **震相检测** (`/picker`) - 配置和运行震相拾取
- **震相关联** (`/associator`) - 选择算法并关联事件
- **初动极性** (`/polarity`) - 分析P波初动方向

### API端点

```bash
# 查看任务列表
GET /api/tasks

# 查看任务详情
GET /api/task/<task_id>

# 提交震相检测任务
POST /api/pick
{
    "input_dir": "/path/to/waveforms",
    "model": "pnsn/pickers/pnsn.v3.jit",
    "device": "cpu"
}

# 提交关联任务
POST /api/associate
{
    "input_file": "picks.txt",
    "station_file": "stations.txt",
    "method": "fastlink"
}

# 提交极性分析任务
POST /api/polarity
{
    "input_file": "picks.txt",
    "waveform_dir": "/path/to/waveforms",
    "phase": "Pg"
}
```

## 技能详解

### Skill 1: 震相检测 (Phase Picker)

#### 工作流程

```
波形数据 → 预处理 → 深度学习模型 → 后处理 → 震相输出
            ↓                        ↓
        带通滤波                 阈值+NMS
```

#### 支持的模型

| 模型 | 震相类型 | 大小 | 适用场景 |
|------|---------|------|---------|
| PNSN v3 | Pg,Sg,Pn,Sn | 1.9MB | 综合性能最佳 |
| PNSN v3 Diff | Pg,Sg,Pn,Sn | 1.9MB | 高通滤波输入 |
| PhaseNet | Pg,Sg | 1.2MB | 快速推理 |
| EQTransformer | Pg,Sg | 2.0MB | 全球宽频带 |
| RNN | Pg,Sg | 1.9MB | 高召回率 |

#### 配置参数

编辑 `pnsn/config/picker.py`:

```python
# 数据设置
nchannel = 3              # 通道数
samplerate = 100          # 采样率(Hz)

# 拾取设置
prob = 0.3                # 置信度阈值
nmslen = 1000             # NMS窗口(采样点)
npicker = 1               # 并行模型数

# 文件组织
namekeyindex = [0, 1]     # 文件名中台站标识位置
channelindex = 3          # 文件名中分量标识位置

# 输出设置
polar = False             # 是否输出初动极性
ifplot = False            # 是否绘制波形图
```

#### 输出格式

```text
#数据路径
震相名,相对时间(s),置信度,绝对时间,信噪比,振幅,台站,初动,初动概率
Pg,32640.160,0.936,2021-05-21 09:04:00.165000,8.5,0.0234,SC.A0801,U,0.89
Sg,32655.420,0.872,2021-05-21 09:04:15.425000,6.2,0.0189,SC.A0801,N,0.00
```

### Skill 2: 震相关联 (Phase Associator)

#### 三种算法对比

**FastLink (LPPN-based)**
- ✅ 速度快,适合区域台网
- ✅ 神经网络评分
- ⚠️ 仅2D定位(经纬度)
- 适用: 实时监测、密集台阵

**REAL**
- ✅ 高精度3D定位
- ✅ 网格搜索全面
- ⚠️ 计算量大
- 适用: 精确定位、离线分析

**GaMMA**
- ✅ 概率框架
- ✅ 不确定性量化
- ⚠️ 参数调优复杂
- 适用: 研究级分析

#### 台站文件格式

```text
NETWORK STATION LOCATION LONGITUDE LATITUDE ELEVATION(m)
SC AXX 00 110.00 38.00 1000.00
YN YSW03 00 102.345 24.567 1850.0
```

#### 输出格式

```text
#EVENT,TIME,LAT,LON,DEP
PHASE,TIME,LAT,LON,TYPE,PROB,STATION,DIST,DELTA,ERROR#
EVENT,2022-04-09 02:28:38.021000,100.6492,25.3660,10.0
PHASE,2022-04-09 02:28:40.123000,100.6492,25.3660,Pg,0.936,SC.AXX,12.5,0.15,0.02#
```

### Skill 3: 初动极性分析 (Polarity Analyzer)

#### 工作原理

```
P波拾取点 → 截取±512采样点 → 深度学习分类 → 向上/向下
                                    ↓
                              置信度评分
```

#### 分类结果

- **U (Upward)**: 压缩初动,正极性
  - 表示震源球压缩象限的台站
  - 模型输出类别0

- **D (Downward)**: 膨胀初动,负极性
  - 表示震源球膨胀象限的台站
  - 模型输出类别1

#### 应用

1. **震源机制解** - 约束断层面解
2. **应力场分析** - 推断区域应力状态
3. **破裂方向性** - 研究地震破裂过程

## 常见问题

### Q1: 检测不到震相怎么办?

**A:** 降低置信度阈值:
```python
# config/picker.py
prob = 0.1  # 更敏感
```

### Q2: 误触发太多?

**A:** 提高阈值或增大NMS窗口:
```python
prob = 0.5      # 更高阈值
nmslen = 2000   # 更宽抑制窗口
```

### Q3: 关联不出事件?

**A:** 检查:
- 台站文件坐标是否正确
- 拾取文件是否有足够空间覆盖
- 降低最小震相数要求

### Q4: 处理速度慢?

**A:** 
- 使用GPU: `-d cuda:0`
- 选择轻量模型: `lppnt.jit`
- 减少并行模型数: `npicker = 1`

## 完整工作流示例

```bash
# 步骤1: 震相检测
python seismic_cli.py pick \
    -i /data/waveforms/2024 \
    -o output/picks_2024 \
    -m pnsn/pickers/pnsn.v3.jit \
    -d cuda:0 \
    --enable-polarity

# 步骤2: 震相关联
python seismic_cli.py associate \
    -i output/picks_2024.txt \
    -o output/events_2024.txt \
    -s data/stations.txt \
    -m real

# 步骤3: (可选)单独极性分析
python seismic_cli.py polarity \
    -i output/picks_2024.txt \
    -w /data/waveforms/2024 \
    -o output/polarity_2024.txt \
    --min-confidence 0.7
```

## 参考文献

- **论文**: "A Deep Learning Framework for Pg/Sg/Pn/Sn Phase Picking and Its Nationwide Implementation in Mainland China"
- **DOI**: https://doi.org/10.1029/2025JH000944
- **作者**: Yuqi Cai, Ziye Yu, et al.
- **联系**: yuziye@cea-igp.ac.cn

## 许可证

本项目遵循GPL-3.0许可证(非商业学术和研究用途)。

商业用途请联系作者获取许可。

## 更新日志

### v1.0.0 (2026-04-09)
- ✨ 初始版本发布
- ✨ 三个核心Skills完成
- ✨ CLI统一接口
- ✨ Web图形界面
- ✨ 完整文档

---

**开发团队**: SeismicX
**最后更新**: 2026-04-09
