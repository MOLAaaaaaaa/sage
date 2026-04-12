#!/bin/bash

echo "=========================================="
echo "地质解释Agent系统 - 安装脚本"
echo "=========================================="
echo ""

# Check Python version
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: Python3未安装,请先安装Python 3.9+"
    exit 1
fi
echo ""

# Install dependencies
echo "安装Python依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "警告: 部分包安装失败,尝试逐个安装..."
    pip3 install numpy scipy matplotlib pandas
    pip3 install fastapi uvicorn jinja2 python-multipart
    pip3 install click rich loguru
    pip3 install ollama pydantic python-dotenv
    pip3 install Pillow markdown PyYAML tqdm
fi
echo ""

# Create necessary directories
echo "创建必要目录..."
mkdir -p data/uploads
mkdir -p data/input
mkdir -p data/algorithms
mkdir -p output/plots
mkdir -p output/generated_code
mkdir -p output/examples
echo ""

# Check Ollama
echo "检查Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama已安装"
    echo ""
    echo "请运行以下命令拉取模型:"
    echo "  ollama pull qwen3-vl:30b"
else
    echo "⚠ Ollama未安装"
    echo ""
    echo "请访问 https://ollama.ai 下载安装Ollama"
    echo "然后运行: ollama pull qwen3-vl:30b"
fi
echo ""

echo "=========================================="
echo "安装完成!"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 配置环境变量: cp .env.example .env"
echo "2. 启动Ollama并拉取模型"
echo "3. 运行示例: python3 examples/basic_usage.py"
echo "4. 启动Web界面: python3 main.py web"
echo ""
