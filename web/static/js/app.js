// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all tabs
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Add active class to clicked tab
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Helper function to show loading state
function showLoading(panelId) {
    const panel = document.getElementById(panelId);
    panel.innerHTML = '<div class="loading">处理中</div>';
    panel.classList.add('show');
}

// Helper function to show error
function showError(panelId, message) {
    const panel = document.getElementById(panelId);
    panel.innerHTML = `<div class="error">错误: ${message}</div>`;
    panel.classList.add('show');
}

// Helper function to format markdown-like text
function formatMarkdown(text) {
    // Convert headings
    text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Convert bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert lists
    text = text.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    text = text.replace(/^- (.+)$/gm, '<li>$1</li>');

    // Wrap consecutive list items
    text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Convert paragraphs
    text = text.replace(/\n\n/g, '</p><p>');
    text = '<p>' + text + '</p>';

    // Clean up empty paragraphs
    text = text.replace(/<p><\/p>/g, '');

    return text;
}

// Region Analysis Form
document.getElementById('region-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const regionName = document.getElementById('region-name').value;
    const description = document.getElementById('region-description').value;

    showLoading('region-result');

    try {
        const response = await fetch('/api/analyze-region', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                region_name: regionName,
                description: description || null
            })
        });

        const data = await response.json();

        if (data.success) {
            const panel = document.getElementById('region-result');
            panel.innerHTML = `
                <h3>分析结果</h3>
                <div class="markdown-content">${formatMarkdown(data.analysis)}</div>
            `;
        } else {
            showError('region-result', '分析失败');
        }
    } catch (error) {
        showError('region-result', error.message);
    }
});

// Velocity Analysis Form
document.getElementById('velocity-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('velocity-image');
    const description = document.getElementById('velocity-description').value;
    const depthMin = document.getElementById('depth-min').value;
    const depthMax = document.getElementById('depth-max').value;

    showLoading('velocity-result');

    try {
        const formData = new FormData();

        if (fileInput.files[0]) {
            formData.append('file', fileInput.files[0]);
        }
        formData.append('description', description);
        if (depthMin) formData.append('depth_min', depthMin);
        if (depthMax) formData.append('depth_max', depthMax);

        const response = await fetch('/api/upload-velocity-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const panel = document.getElementById('velocity-result');
            panel.innerHTML = `
                <h3>速度结构分析结果</h3>
                <div class="markdown-content">${formatMarkdown(data.analysis)}</div>
            `;
        } else {
            showError('velocity-result', '分析失败');
        }
    } catch (error) {
        showError('velocity-result', error.message);
    }
});

// Code Generation Form
document.getElementById('code-gen-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const docFile = document.getElementById('algorithm-doc').files[0];
    const taskDesc = document.getElementById('task-desc').value;

    showLoading('code-result');

    try {
        const formData = new FormData();
        formData.append('algorithm_doc', docFile);
        formData.append('task_description', taskDesc);

        const response = await fetch('/api/generate-code', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const panel = document.getElementById('code-result');
            document.getElementById('generated-code').textContent = data.code;
            panel.classList.add('show');
        } else {
            showError('code-result', '代码生成失败');
        }
    } catch (error) {
        showError('code-result', error.message);
    }
});

// Inversion Form
document.getElementById('inversion-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const algoFile = document.getElementById('inv-algorithm').files[0];
    const dataFile = document.getElementById('inv-data').files[0];
    const params = document.getElementById('inv-params').value;

    showLoading('inversion-result');

    try {
        const formData = new FormData();
        formData.append('algorithm_doc', algoFile);
        formData.append('input_data', dataFile);
        if (params) formData.append('parameters', params);

        const response = await fetch('/api/run-inversion', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const panel = document.getElementById('inversion-result');
            panel.innerHTML = `
                <h3>反演结果</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
            panel.classList.add('show');
        } else {
            showError('inversion-result', data.error || '反演失败');
        }
    } catch (error) {
        showError('inversion-result', error.message);
    }
});

// RAG: Upload PDF Form
document.getElementById('upload-pdf-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('pdf-file');
    const docId = document.getElementById('doc-id').value;

    showLoading('upload-result');

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        if (docId) formData.append('doc_id', docId);

        const response = await fetch('/api/upload-pdf', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const panel = document.getElementById('upload-result');
            panel.innerHTML = `
                <div class="success">
                    <h4>✓ 上传成功</h4>
                    <p>文档ID: ${data.doc_id}</p>
                    <p>标题: ${data.title}</p>
                    <p>页数: ${data.pages}</p>
                    <p>索引块数: ${data.chunks_indexed}</p>
                </div>
            `;
            panel.classList.add('show');

            // Refresh stats
            loadRagStats();
        } else {
            showError('upload-result', data.error || '上传失败');
        }
    } catch (error) {
        showError('upload-result', error.message);
    }
});

// RAG: Search Form
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const query = document.getElementById('search-query').value;
    const nResults = document.getElementById('n-results').value;

    showLoading('search-result');

    try {
        const formData = new FormData();
        formData.append('query', query);
        formData.append('n_results', nResults);

        const response = await fetch('/api/rag/search', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            const panel = document.getElementById('search-result');
            let html = '<h3>搜索结果</h3>';

            data.results.forEach((result, index) => {
                html += `
                    <div class="search-result-item">
                        <div class="result-header">${index + 1}. ${result.metadata.title || '未知文献'}</div>
                        <div class="result-content">${result.content.substring(0, 500)}...</div>
                        <div class="result-meta">
                            作者: ${result.metadata.author || '未知'} |
                            页码: ${result.metadata.page_number || 'N/A'} |
                            相关度: ${(1 - result.distance).toFixed(3)}
                        </div>
                    </div>
                `;
            });

            panel.innerHTML = html;
            panel.classList.add('show');
        } else {
            const panel = document.getElementById('search-result');
            panel.innerHTML = '<div class="error">未找到相关文献</div>';
            panel.classList.add('show');
        }
    } catch (error) {
        showError('search-result', error.message);
    }
});

// RAG: Load Statistics
async function loadRagStats() {
    try {
        const response = await fetch('/api/rag/stats');
        const stats = await response.json();

        const statsPanel = document.getElementById('rag-stats');
        statsPanel.innerHTML = `
            <div class="stat-item">
                <span>总文档数:</span>
                <strong>${stats.unique_documents || 0}</strong>
            </div>
            <div class="stat-item">
                <span>总索引块数:</span>
                <strong>${stats.total_chunks || 0}</strong>
            </div>
            <div class="stat-item">
                <span>数据库路径:</span>
                <strong>${stats.db_path || 'N/A'}</strong>
            </div>
        `;
        statsPanel.classList.add('show');

        // Load document list
        loadDocumentList();
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// RAG: Load Document List
async function loadDocumentList() {
    try {
        const response = await fetch('/api/rag/documents');
        const data = await response.json();

        const docList = document.getElementById('document-list');

        if (data.documents && data.documents.length > 0) {
            let html = '<h4>已索引文档</h4>';

            data.documents.forEach(doc => {
                html += `
                    <div class="document-item">
                        <div class="doc-info">
                            <div class="doc-title">${doc.title}</div>
                            <div class="doc-meta">
                                作者: ${doc.author || '未知'} |
                                文件: ${doc.filename} |
                                块数: ${doc.chunks}
                            </div>
                        </div>
                        <div class="doc-actions">
                            <button class="btn btn-danger" onclick="deleteDocument('${doc.doc_id}')">删除</button>
                        </div>
                    </div>
                `;
            });

            docList.innerHTML = html;
        } else {
            docList.innerHTML = '<p style="color: #6c757d;">暂无文献</p>';
        }
    } catch (error) {
        console.error('Failed to load documents:', error);
    }
}

// RAG: Delete Document
async function deleteDocument(docId) {
    if (!confirm(`确定要删除文档 ${docId} 吗?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/rag/document/${docId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert('删除成功');
            loadRagStats();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

// Refresh stats button
document.getElementById('refresh-stats').addEventListener('click', loadRagStats);

// Load stats when RAG tab is activated
document.querySelector('[data-tab="rag-literature"]').addEventListener('click', () => {
    loadRagStats();
});

// Check system health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        const status = await response.json();

        if (!status.ollama_connected) {
            console.warn('Ollama server is not connected');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
});
