# RAG文献检索功能使用指南

## 概述

RAG (Retrieval-Augmented Generation) 功能允许您上传专业地质文献(PDF格式),建立向量知识库,并在区域地质分析时自动检索相关文献,提供更准确、更有依据的分析结果。

## 核心功能

### 1. PDF文献上传与索引
- 支持上传PDF格式的地质文献
- 自动解析PDF内容并分块
- 使用Ollama生成向量嵌入
- 存储到ChromaDB向量数据库

### 2. 智能文献检索
- 基于语义相似度搜索
- 支持按地区、主题等过滤
- 返回最相关的文献片段

### 3. RAG增强分析
- 区域分析时自动检索相关文献
- 结合文献内容生成专业解释
- 提供文献引用和参考

## 使用方法

### Web界面方式(推荐)

#### 1. 启动Web服务
```bash
cd /Users/yuziye/Documents/程序/geo_agent
source venv/bin/activate
python main.py web
```

访问 http://localhost:8000

#### 2. 上传PDF文献
1. 点击"文献库"标签页
2. 在"上传PDF文献"区域:
   - 选择PDF文件
   - (可选)输入自定义文档ID
   - 点击"上传并索引"
3. 查看上传结果和统计信息

#### 3. 检索文献
1. 在"文献检索"区域:
   - 输入搜索查询(如:"塔里木盆地 构造")
   - 设置返回结果数量
   - 点击"搜索"
2. 查看相关文献片段和相关度评分

#### 4. 管理文献库
- 查看文献库统计(文档数、索引块数)
- 浏览已索引文档列表
- 删除不需要的文档

#### 5. 使用RAG进行区域分析
1. 切换到"区域分析"标签页
2. 输入地区名称和描述
3. 系统会自动使用RAG检索相关文献
4. 查看结合文献的分析结果

### Python API方式

#### 初始化
```python
from agents.geological_interpreter import GeologicalInterpreterAgent

# 创建启用了RAG的Agent
agent = GeologicalInterpreterAgent(enable_rag=True)
```

#### 上传PDF
```python
# 上传单个PDF
result = agent.upload_pdf_to_rag(
    pdf_path="path/to/paper.pdf",
    doc_id="my_paper"  # 可选,默认使用文件名
)

print(f"文档ID: {result['doc_id']}")
print(f"标题: {result['title']}")
print(f"页数: {result['pages']}")
print(f"索引块数: {result['chunks_indexed']}")
```

#### 批量上传
```python
from utils.rag_retriever import RAGRetriever

rag = RAGRetriever()

# 上传目录下的所有PDF
results = rag.batch_upload_pdfs(Path("./my_papers"))

for result in results:
    if result['success']:
        print(f"✓ {result['filename']}")
    else:
        print(f"✗ {result['filename']}: {result['error']}")
```

#### 检索文献
```python
# 搜索相关文献
results = agent.search_literature(
    query="塔里木盆地 奥陶纪 碳酸盐岩",
    n_results=5
)

for i, result in enumerate(results, 1):
    print(f"\n结果 {i}:")
    print(f"文献: {result['metadata']['title']}")
    print(f"作者: {result['metadata']['author']}")
    print(f"页码: {result['metadata']['page_number']}")
    print(f"内容: {result['content'][:200]}...")
    print(f"相关度: {1 - result['distance']:.3f}")
```

#### RAG增强的区域分析
```python
# 使用RAG进行区域分析(默认启用)
analysis = agent.analyze_region(
    region_name="四川盆地",
    description="中国南方大型沉积盆地",
    use_rag=True  # 启用RAG
)

print(analysis)

# 不使用RAG的标准分析
analysis_standard = agent.analyze_region(
    region_name="四川盆地",
    use_rag=False
)
```

#### 管理文献库
```python
# 查看统计
stats = agent.get_rag_stats()
print(f"文档数: {stats['unique_documents']}")
print(f"索引块数: {stats['total_chunks']}")

# 列出所有文档
docs = agent.list_rag_documents()
for doc in docs:
    print(f"- {doc['title']} ({doc['chunks']} chunks)")

# 删除文档
success = agent.delete_rag_document("doc_id")
```

### CLI命令行方式

目前主要通过Web界面操作,未来会添加专用CLI命令。

## 工作流程

```
1. 上传PDF文献
   ↓
2. PDF解析 → 提取文本和元数据
   ↓
3. 文本分块 → 按页面和段落分割
   ↓
4. 向量嵌入 → 使用Ollama生成embedding
   ↓
5. 存入向量数据库 → ChromaDB
   ↓
6. 用户查询 → 生成查询向量
   ↓
7. 相似度搜索 → 检索相关文献片段
   ↓
8. 构建上下文 → 整合物理文献内容
   ↓
9. LLM分析 → 生成专业地质解释
   ↓
10. 返回结果 → 包含文献引用
```

## 最佳实践

### 1. 文献准备
- 选择高质量、权威的地质文献
- 优先上传与研究区域相关的文献
- 确保PDF可复制文本(非扫描版)

### 2. 文献组织
- 使用有意义的文档ID
- 按区域或主题分类上传
- 定期更新和维护文献库

### 3. 查询优化
- 使用专业术语和关键词
- 包含地区名称和地质时代
- 具体而明确的查询效果更好

### 4. 性能考虑
- 单个PDF建议不超过100页
- 大量文献可分批上传
- 定期清理无用文献

## 技术细节

### PDF解析
- 使用PyMuPDF (fitz)库
- 提取每页文本内容
- 保留页面元数据

### 文本分块
- 按页面边界分割
- 每块约1000字符
- 块间重叠200字符
- 保持句子完整性

### 向量嵌入
- 使用Ollama embedding API
- 默认模型: qwen3-vl:30b
- 维度取决于模型

### 向量数据库
- ChromaDB持久化存储
- 位置: `./data/vector_db`
- 支持元数据过滤
- 余弦相似度搜索

## 故障排除

### Q: 上传PDF失败?
A: 检查:
- PDF文件是否损坏
- 是否为加密PDF
- 是否为扫描版(需要OCR)

### Q: 检索结果为空?
A: 可能原因:
- 文献库为空,先上传文献
- 查询词与文献内容不匹配
- 尝试更通用的查询词

### Q: RAG分析很慢?
A: 优化建议:
- 减少n_results参数
- 使用更具体的查询
- 控制文献库规模

### Q: 如何备份文献库?
A: 备份整个vector_db目录:
```bash
cp -r data/vector_db backup/vector_db_backup
```

## 示例场景

### 场景1: 塔里木盆地研究
```python
# 1. 上传相关文献
agent.upload_pdf_to_rag("papers/tarim_structural.pdf")
agent.upload_pdf_to_rag("papers/tarim_stratigraphy.pdf")

# 2. 进行RAG分析
analysis = agent.analyze_region(
    region_name="塔里木盆地",
    description="前寒武纪基底,古生代海相沉积"
)
```

### 场景2: 特定地层研究
```python
# 搜索奥陶纪相关内容
results = agent.search_literature(
    query="奥陶纪 碳酸盐岩 储层",
    n_results=10
)
```

## 扩展开发

### 添加新的文档格式
继承PDFParser类,实现新的解析器:
```python
class WordParser(DocumentParser):
    def parse(self, file_path):
        # 实现Word文档解析
        pass
```

### 自定义分块策略
修改VectorDatabase._chunk_text方法

### 使用不同的Embedding模型
修改OllamaClient.embed方法

---

**RAG功能让地质解释更有依据,更专业!** 📚🌍
