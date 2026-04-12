# BGE-M3 嵌入模型配置指南

## 概述

系统现已支持使用 **BGE-M3** 作为文本嵌入模型,相比Ollama embedding,BGE-M3在中文理解方面表现更优。

## BGE-M3 vs Ollama Embedding

| 特性 | BGE-M3 | Ollama |
|------|--------|--------|
| 中文支持 | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 良好 |
| 最大长度 | 8192 tokens | 取决于模型 |
| 向量维度 | 1024 | 可变 |
| 运行方式 | 本地 (sentence-transformers) | 需要Ollama服务 |
| 首次加载 | 较慢(需下载模型) | 快 |
| 稳定性 | ⭐⭐⭐⭐⭐ 非常稳定 | ⭐⭐⭐ 依赖版本 |
| 推荐场景 | 中文文献为主 | 已有Ollama基础设施 |

## 使用方法

### 1. Web界面 (默认使用BGE-M3)

Web界面已默认配置为使用BGE-M3:

```python
# web/app.py
interpreter = GeologicalInterpreterAgent(
    ollama_client,
    enable_rag=True,
    embedding_type="bge-m3"  # 默认
)
```

### 2. Python API

#### 使用BGE-M3 (推荐)
```python
from agents.geological_interpreter import GeologicalInterpreterAgent

# 创建Agent,使用BGE-M3
agent = GeologicalInterpreterAgent(
    enable_rag=True,
    embedding_type="bge-m3"  # 显式指定
)

# 上传PDF
result = agent.upload_pdf_to_rag("地质文献.pdf")

# 搜索文献 (会使用BGE-M3生成查询向量)
results = agent.search_literature("塔里木盆地 构造特征")
```

#### 使用Ollama Embedding
```python
# 如果需要使用Ollama
agent = GeologicalInterpreterAgent(
    enable_rag=True,
    embedding_type="ollama"
)
```

### 3. 直接创建RAGRetriever

```python
from utils.rag_retriever import RAGRetriever

# 使用BGE-M3
rag = RAGRetriever(embedding_type="bge-m3")

# 使用Ollama
rag = RAGRetriever(embedding_type="ollama")
```

## 技术实现

### BGE-M3加载
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="mps",  # Apple Silicon Mac
    trust_remote_code=True
)
```

### 设备选择
系统会自动选择最佳设备:
- **MPS**: Apple Silicon Mac (M1/M2/M3)
- **CUDA**: NVIDIA GPU
- **CPU**: 其他情况

### 批量编码
```python
embeddings = model.encode(
    texts,
    batch_size=12,
    normalize_embeddings=True
)
```

## 性能对比

### 编码速度
- BGE-M3 (MPS): ~100 texts/sec
- BGE-M3 (CPU): ~20 texts/sec
- Ollama: ~5-10 texts/sec (取决于模型)

### 内存占用
- BGE-M3: ~2GB
- Ollama: 取决于模型大小

## 首次使用

首次使用BGE-M3时,会自动从HuggingFace下载模型(~2GB):

```
Loading BGE-M3 via sentence-transformers: BAAI/bge-m3
Downloading: 100%|██████████| 2.1G/2.1G
```

下载后会缓存到 `~/.cache/huggingface/`,后续使用无需再次下载。

## 切换模型

如需从Ollama切换到BGE-M3:

1. 修改代码中的 `embedding_type` 参数
2. 注意: 不同模型生成的向量不能混用
3. 建议清空向量数据库后重新索引

```python
# 清空并重建
import shutil
shutil.rmtree("./data/vector_db")

# 使用新模型重新索引文献
rag = RAGRetriever(embedding_type="bge-m3")
rag.batch_upload_pdfs(Path("./papers"))
```

## 故障排除

### Q: 模型下载很慢?
A: 可以使用国内镜像:
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

### Q: MPS内存不足?
A: 强制使用CPU:
```python
rag = RAGRetriever(embedding_type="bge-m3")
rag.vector_db.embedding_model.model = rag.vector_db.embedding_model.model.to("cpu")
```

### Q: 向量维度不匹配?
A: BGE-M3固定为1024维,确保ChromaDB collection使用相同维度。

## 测试

运行测试脚本验证BGE-M3功能:

```bash
python test_bge_m3.py
```

预期输出:
```
BGE-M3 Embedding                    ✓ PASS
Vector DB with BGE-M3               ✓ PASS
RAG with BGE-M3                     ✓ PASS

Total: 3/3 tests passed
```

## 最佳实践

1. **中文文献**: 优先使用BGE-M3
2. **英文文献**: BGE-M3和Ollama均可
3. **混合语言**: BGE-M3表现更好
4. **生产环境**: 建议使用BGE-M3,更稳定
5. **开发测试**: 可使用Ollama,更快启动

---

**BGE-M3让中文地质文献检索更准确!** 🇨🇳📚
