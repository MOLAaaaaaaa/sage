# 地质解释Agent系统

SAGE (Seismological Agent for Guided Exploration) 是一个旨在将先进的大语言模型（LLM）能力与地震学专业物理知识深度融合的智能体系统。

## 功能特性

### 1. 地质解释Agent
- **区域地质分析**: 输入地区名称和描述,自动生成专业地质解释
- **速度结构分析**: 分析速度剖面图和数据结构,识别地质层位和构造特征
- **地震剖面解释**: 支持上传地震剖面图像进行自动解释
- **多区域对比**: 对比不同地区的地质特征

### 2. 编程Agent
- **算法文档解析**: 读取Markdown格式的算法说明文档
- **自动代码生成**: 根据算法文档自动生成Python实现代码
- **代码执行**: 安全执行生成的代码
- **反演/正演**: 支持地球物理反演和正演模拟

### 3. 可视化模块
- 速度剖面图绘制
- 二维速度断面图
- 反演结果可视化
- 残差分布分析

### 4. 双界面支持
- **命令行界面(CLI)**: 适合脚本化处理和自动化
- **Web界面**: 友好的图形界面,支持文件上传和交互式分析

## 技术架构

- **AI模型**: Ollama + Qwen3-VL-30B (支持视觉理解)
- **后端**: Python + FastAPI
- **科学计算**: NumPy, SciPy
- **可视化**: Matplotlib, Plotly
- **前端**: HTML5 + CSS3 + JavaScript

## 安装

### 前置要求

1. Python 3.9+
2. Ollama (用于运行LLM)

### 安装步骤

```bash
# 克隆或下载项目
cd geo_agent

# 安装依赖
pip install -r requirements.txt

# 或者使用setup.py
pip install -e .
```

### 配置Ollama

```bash
# 启动Ollama服务
ollama serve

# 拉取所需模型
ollama pull qwen3-vl:30b

# 验证模型
ollama list
```

### 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件,配置Ollama地址等参数
```

## 使用方法

### CLI命令行工具

```bash
# 检查系统状态
python main.py check

# 区域地质分析
python main.py analyze-region --region "塔里木盆地" --description "中国西部大型含油气盆地" --output report.md

# 速度结构分析(带图片)
python main.py analyze-velocity --image velocity.png --description "某地区速度剖面" --depth-min 0 --depth-max 50

# 从算法文档生成代码
python main.py generate-code --doc docs/algorithms/linear_inversion.md --output inversion_code.py

# 执行生成的代码
python main.py execute-code --code inversion_code.py

# 运行反演
python main.py run-inversion --algorithm algo.md --data data.npy --params '{"reg_weight": 0.01}'

# 创建示例图表
python main.py create-plot --type velocity-profile --output plot.png

# 启动Web界面
python main.py web
```

### Web界面

```bash
# 启动Web服务
python main.py web

# 或使用uvicorn直接启动
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

然后在浏览器访问: http://localhost:8000

Web界面提供以下功能:
- 区域地质分析表单
- 速度结构图上传和分析
- 算法文档上传和代码生成
- 反演任务提交和执行

## 项目结构

```
geo_agent/
├── agents/                  # Agent模块
│   ├── geological_interpreter.py  # 地质解释Agent
│   └── programming_agent.py       # 编程Agent
├── core/                    # 核心模块
│   └── ollama_client.py    # Ollama客户端
├── inversion/               # 反演算法
│   └── base.py             # 基础反演类
├── visualization/           # 可视化模块
│   └── plotter.py          # 绘图工具
├── utils/                   # 工具函数
│   └── document_parser.py  # 文档解析器
├── web/                     # Web应用
│   ├── app.py              # FastAPI应用
│   ├── templates/          # HTML模板
│   └── static/             # 静态文件
├── cli/                     # 命令行工具
│   └── main.py             # CLI入口
├── docs/                    # 文档
│   └── algorithms/         # 算法文档
├── data/                    # 数据目录
├── output/                  # 输出目录
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

## 算法文档格式

编程Agent可以读取Markdown格式的算法文档并自动生成代码。文档应包含:

```markdown
# 算法名称

## 概述
算法的简要说明

## 数学原理
关键公式和推导过程

## 算法步骤
1. 步骤一
2. 步骤二
...

## 参数说明
- 参数1: 说明
- 参数2: 说明

## Python实现要点
代码示例和注意事项
```

参考示例: `docs/algorithms/linear_inversion.md`

## API接口

### REST API

```
POST /api/analyze-region          # 区域分析
POST /api/analyze-velocity        # 速度结构分析
POST /api/upload-velocity-image   # 上传速度图
POST /api/generate-code           # 生成代码
POST /api/execute-code            # 执行代码
POST /api/run-inversion           # 运行反演
GET  /api/plot/velocity-profile   # 获取示例图
GET  /health                      # 健康检查
```

## 示例工作流

### 示例1: 区域地质分析

```python
from agents.geological_interpreter import GeologicalInterpreterAgent

interpreter = GeologicalInterpreterAgent()
result = interpreter.analyze_region(
    region_name="四川盆地",
    description="中国南方大型沉积盆地"
)
print(result)
```

### 示例2: 速度结构分析

```python
result = interpreter.analyze_velocity_structure(
    structure_description="某地区速度随深度增加而增大",
    image_path="velocity_section.png",
    depth_range=(0, 50)
)
```

### 示例3: 自动生成反演代码

```python
from agents.programming_agent import ProgrammingAgent

prog_agent = ProgrammingAgent()
code = prog_agent.generate_code_from_markdown(
    markdown_path="docs/algorithms/linear_inversion.md",
    task_description="实现线性反演,处理地震走时数据"
)

# 保存并执行
with open("my_inversion.py", "w") as f:
    f.write(code)

result = prog_agent.execute_code(code)
```

## 开发指南

### 添加新的反演算法

1. 在 `inversion/` 目录下创建新模块
2. 继承 `InversionAlgorithm` 基类
3. 实现 `forward()` 和 `invert()` 方法
4. 编写算法文档放到 `docs/algorithms/`

### 扩展Agent功能

1. 在 `agents/` 目录下创建新Agent
2. 使用 `OllamaClient` 进行AI交互
3. 在CLI和Web中添加对应接口

## 常见问题

### Q: Ollama连接失败?
A: 确保Ollama服务已启动 (`ollama serve`),并且模型已下载 (`ollama pull qwen3-vl:30b`)

### Q: 生成的代码执行出错?
A: 检查算法文档是否清晰完整,可以在任务描述中提供更多细节

### Q: 如何更换AI模型?
A: 修改 `.env` 文件中的 `OLLAMA_MODEL` 参数,或使用其他支持vision的模型

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request!

## 联系方式

如有问题或建议,请提交Issue。
