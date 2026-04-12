# 地质解释Agent系统 - 使用说明

## 🎯 快速开始 (3步)

### 步骤1: 激活环境
```bash
cd /Users/yuziye/Documents/程序/geo_agent
source venv/bin/activate
```

### 步骤2: 测试系统
```bash
python test_core.py
```

预期输出: `🎉 所有测试通过! 系统已就绪。`

### 步骤3: 运行演示
```bash
python demo.py
```

## 📚 主要功能使用

### 1️⃣ 地质解释 (需要Ollama)

#### CLI方式
```bash
# 分析一个地区
python main.py analyze-region \
  --region "四川盆地" \
  --description "中国南方大型沉积盆地" \
  --output sichuan_report.md

# 分析速度结构(带图片)
python main.py analyze-velocity \
  --image path/to/velocity.png \
  --depth-min 0 \
  --depth-max 50 \
  --output velocity_analysis.md
```

#### Python API方式
```python
from agents.geological_interpreter import GeologicalInterpreterAgent

interpreter = GeologicalInterpreterAgent()

# 区域分析
result = interpreter.analyze_region(
    region_name="塔里木盆地",
    description="中国西部大型含油气盆地"
)
print(result)

# 速度结构分析
result = interpreter.analyze_velocity_structure(
    structure_description="速度随深度增加",
    image_path="velocity.png",  # 可选
    depth_range=(0, 50)
)
```

### 2️⃣ 代码生成 (需要Ollama)

#### 从算法文档生成代码
```bash
python main.py generate-code \
  --doc docs/algorithms/linear_inversion.md \
  --task "实现线性反演,添加可视化" \
  --output my_inversion.py
```

#### Python API
```python
from agents.programming_agent import ProgrammingAgent

prog_agent = ProgrammingAgent()

# 从Markdown文档生成
code = prog_agent.generate_code_from_markdown(
    markdown_path="docs/algorithms/linear_inversion.md",
    task_description="实现反演算法"
)

# 保存代码
with open("inversion.py", "w") as f:
    f.write(code)
```

### 3️⃣ 执行代码
```bash
# CLI方式
python main.py execute-code --code my_inversion.py

# Python API
from agents.programming_agent import ProgrammingAgent

prog_agent = ProgrammingAgent()
result = prog_agent.execute_code(code_file="my_inversion.py")

if result['success']:
    print("输出:", result['output'])
else:
    print("错误:", result['error'])
```

### 4️⃣ 运行反演

#### 完整反演流程
```bash
python main.py run-inversion \
  --algorithm docs/algorithms/linear_inversion.md \
  --data input_data.npy \
  --params '{"regularization_weight": 0.01}'
```

#### Python API
```python
from agents.programming_agent import ProgrammingAgent

prog_agent = ProgrammingAgent()
result = prog_agent.run_inversion(
    algorithm_doc="docs/algorithms/linear_inversion.md",
    input_data_file="data.npy",
    parameters={"regularization_weight": 0.01}
)
```

### 5️⃣ 创建图表

```bash
# 速度剖面图
python main.py create-plot \
  --type velocity-profile \
  --output velocity.png

# 速度断面图
python main.py create-plot \
  --type velocity-section \
  --output section.png

# 反演结果图
python main.py create-plot \
  --type inversion-result \
  --output inversion.png
```

#### Python API绘图
```python
from visualization.plotter import GeologicalPlotter
import numpy as np

plotter = GeologicalPlotter()

# 速度剖面
depths = np.linspace(0, 50, 100)
velocities = 5.0 + 0.1 * depths + np.random.randn(100) * 0.2

plotter.plot_velocity_profile(
    depths=depths,
    velocities=velocities,
    title="My Velocity Profile",
    save_path="output.png"
)

# 速度断面
x = np.linspace(0, 100, 50)
z = np.linspace(0, 30, 40)
X, Z = np.meshgrid(x, z)
V = 5.0 + 0.05 * Z + 0.02 * X

plotter.plot_velocity_section(
    x=x,
    depths=z,
    velocities=V,
    save_path="section.png"
)
```

### 6️⃣ Web界面

```bash
# 启动Web服务
python main.py web

# 或使用uvicorn
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

然后在浏览器访问: **http://localhost:8000**

Web界面功能:
- 📊 区域地质分析表单
- 🖼️ 上传速度结构图并分析
- 💻 上传算法文档生成代码
- 🔬 提交反演任务
- 📈 查看实时结果

## 🔧 高级用法

### 自定义Ollama配置

编辑 `.env` 文件:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3-vl:30b  # 可改为其他模型
```

### 扩展反演算法

```python
from inversion.base import InversionAlgorithm
import numpy as np

class MyInversion(InversionAlgorithm):
    def forward(self, model):
        # 实现正演
        return predicted_data

    def invert(self, data, initial_model=None):
        # 实现反演
        return inverted_model

# 使用
inv = MyInversion(param1=value1, param2=value2)
model = inv.invert(data)
```

### 批量处理

```python
from agents.geological_interpreter import GeologicalInterpreterAgent

interpreter = GeologicalInterpreterAgent()

regions = ["塔里木盆地", "四川盆地", "鄂尔多斯盆地"]
results = {}

for region in regions:
    results[region] = interpreter.analyze_region(region)
    # 保存结果
    with open(f"{region}_report.md", "w") as f:
        f.write(results[region])
```

### 解析算法文档

```python
from utils.document_parser import AlgorithmDocumentParser

parser = AlgorithmDocumentParser()
parsed = parser.parse_markdown("algo.md")

# 访问解析结果
print("标题:", parsed['title'])
print("章节:", [s['title'] for s in parsed['sections']])
print("参数:", [p['name'] for p in parsed['parameters']])
print("公式数量:", len(parsed['equations']))
```

## 📖 编写算法文档

为了让编程Agent更好地生成代码,算法文档应包含:

```markdown
# 算法名称

## 概述
简要说明算法用途

## 数学原理
$$关键公式$$

## 算法步骤
**步骤1**: 描述
**步骤2**: 描述
...

## 参数说明
- **参数1**: 类型,默认值,说明
- **参数2**: 类型,默认值,说明

## Python实现要点
```python
# 示例代码片段
```

## 应用实例
实际应用场景
```

参考: `docs/algorithms/linear_inversion.md`

## ❓ 常见问题

### Q: Ollama连接失败?
```bash
# 检查Ollama是否运行
ollama list

# 如果没有运行,启动服务
ollama serve

# 拉取模型
ollama pull qwen3-vl:30b
```

### Q: 内存不足?
qwen3-vl:30b需要约60GB显存。可以使用较小模型:
```bash
ollama pull qwen2.5:7b
# 修改 .env: OLLAMA_MODEL=qwen2.5:7b
```

### Q: 生成的代码有错误?
1. 检查算法文档是否清晰完整
2. 在task_description中提供更多细节
3. 手动修正后重新运行

### Q: Web界面无法访问?
```bash
# 检查端口占用
lsof -i :8000

# 更换端口
uvicorn web.app:app --port 8080
```

### Q: 如何查看日志?
日志会自动输出到控制台。要保存到文件:
```python
from loguru import logger
logger.add("app.log")
```

## 🎓 学习资源

- **项目文档**: README.md
- **快速开始**: QUICKSTART.md
- **项目总结**: PROJECT_SUMMARY.md
- **示例代码**: examples/basic_usage.py
- **演示脚本**: demo.py
- **测试脚本**: test_core.py

## 🚀 下一步

1. ✅ 完成快速开始
2. ✅ 运行所有示例
3. ✅ 尝试Web界面
4. ✅ 编写自己的算法文档
5. ✅ 处理实际地质数据
6. ✅ 扩展新功能

---

**技术支持**: 如有问题,请查看文档或提交Issue

**祝使用愉快!** 🎉
