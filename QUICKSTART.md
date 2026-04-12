# 快速开始指南

## 5分钟快速上手

### 1. 安装依赖

```bash
cd geo_agent
pip install -r requirements.txt
```

### 2. 配置Ollama

```bash
# 启动Ollama (如果尚未运行)
ollama serve

# 在另一个终端拉取模型
ollama pull qwen3-vl:30b
```

### 3. 运行示例

```bash
# 运行所有示例
python examples/basic_usage.py

# 或使用CLI
python main.py check
```

### 4. 启动Web界面

```bash
python main.py web
```

然后在浏览器打开: http://localhost:8000

## 常用命令

### CLI命令

```bash
# 区域分析
python main.py analyze-region --region "四川盆地" --output result.md

# 速度结构分析
python main.py analyze-velocity --image velocity.png --depth-min 0 --depth-max 50

# 生成代码
python main.py generate-code --doc docs/algorithms/linear_inversion.md --output code.py

# 执行代码
python main.py execute-code --code code.py

# 创建图表
python main.py create-plot --type velocity-profile
```

### Python API

```python
from agents.geological_interpreter import GeologicalInterpreterAgent
from visualization.plotter import GeologicalPlotter
import numpy as np

# 地质解释
interpreter = GeologicalInterpreterAgent()
result = interpreter.analyze_region("塔里木盆地")
print(result)

# 绘图
plotter = GeologicalPlotter()
depths = np.linspace(0, 50, 100)
velocities = 5.0 + 0.1 * depths
plotter.plot_velocity_profile(depths, velocities)
```

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 `examples/` 目录中的示例代码
- 编写自己的算法文档并生成代码
- 探索 Web 界面的所有功能

## 故障排除

### 问题: ImportError: No module named 'xxx'
解决: `pip install -r requirements.txt`

### 问题: Ollama连接失败
解决:
1. 确认Ollama已安装: `which ollama`
2. 启动服务: `ollama serve`
3. 检查模型: `ollama list`
4. 拉取模型: `ollama pull qwen3-vl:30b`

### 问题: Web界面无法访问
解决:
1. 检查端口是否被占用: `lsof -i :8000`
2. 更换端口: 修改 `web/app.py` 中的端口号
3. 检查防火墙设置
