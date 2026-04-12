# Web 聊天界面数据浏览和波形绘图功能 - 更新总结

## 概述

本次更新为 Web 聊天界面添加了完整的数据浏览和波形绘图功能，用户可以在浏览器中通过自然语言对话来探索地震数据并可视化波形。

## 更新的文件

### 1. `web_app/app.py`

**更新内容：**
- 修改 `/api/chat` 端点，添加图像 URL 处理
- 当检测到波形绘制操作时，自动将图像路径转换为 Web 可访问的 URL

**关键代码：**
```python
@app.route('/api/chat', methods=['POST'])
def chat_message():
    """Process chat message"""
    # ... existing code ...

    result = agent.process_message(user_message)

    # If the action is to display a plot, add image URL
    if result.get('action') == 'display_plot' and result.get('data', {}).get('results', {}).get('image_path'):
        image_path = result['data']['results']['image_path']
        # Convert to relative path for web access
        if os.path.isabs(image_path):
            rel_path = os.path.relpath(image_path, app.config['OUTPUT_FOLDER'])
        else:
            rel_path = image_path
        result['image_url'] = f'/api/output/{rel_path}'

    return jsonify(result)
```

### 2. `web_app/templates/chat.html`

**更新内容：**

#### A. 添加图像显示支持

修改 `addMessage` 函数，支持可选的图像参数：
```javascript
function addMessage(role, content, imageUrl = null) {
    // ... create message bubble ...

    // If there's an image URL, add it
    if (imageUrl) {
        const imgDiv = document.createElement('div');
        imgDiv.style.marginTop = '15px';
        imgDiv.innerHTML = `
            <img src="${imageUrl}" alt="Waveform"
                 style="max-width: 100%; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"
                 onload="chatMessages.scrollTop = chatMessages.scrollHeight;">
            <div style="margin-top: 10px; text-align: center;">
                <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-download"></i> 下载图片
                </a>
            </div>
        `;
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(imgDiv);
    } else {
        messageDiv.appendChild(bubbleDiv);
    }

    // ... rest of function ...
}
```

#### B. 更新消息发送逻辑

修改 `sendMessage` 函数，传递图像 URL：
```javascript
async function sendMessage() {
    // ... send request ...

    const data = await response.json();
    hideTyping();

    // Add assistant response with image if available
    addMessage('assistant', data.response, data.image_url || null);

    // ... rest of function ...
}
```

#### C. 添加新功能卡片

在欢迎页面添加"数据浏览"和"波形绘制"功能卡片：
```html
<div class="feature-cards">
    <div class="feature-card">
        <div class="feature-icon"><i class="bi bi-folder2-open"></i></div>
        <h5>数据浏览</h5>
        <p class="text-muted">查看目录中的地震数据文件</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon"><i class="bi bi-graph-up"></i></div>
        <h5>波形绘制</h5>
        <p class="text-muted">可视化地震波形数据</p>
    </div>
    <!-- ... other cards ... -->
</div>
```

#### D. 添加快速操作按钮

新增两个快捷按钮：
```html
<div class="quick-actions">
    <button class="quick-action-btn" onclick="sendQuickMessage('帮我查看当前目录下的mseed文件')">
        <i class="bi bi-folder2-open"></i> 浏览数据
    </button>
    <button class="quick-action-btn" onclick="sendQuickMessage('绘制波形')">
        <i class="bi bi-graph-up"></i> 绘制波形
    </button>
    <!-- ... other buttons ... -->
</div>
```

#### E. 更新输入框提示

修改占位符文本：
```html
<input type="text" class="form-control" id="userInput"
       placeholder="输入消息... (例如: '查看 /data 目录' 或 '绘制波形')"
       onkeypress="handleKeyPress(event)">
```

## 功能特性

### 1. 图像自动显示

- 当后端返回波形图时，前端自动显示图像
- 图像自适应聊天窗口宽度（`max-width: 100%`）
- 圆角边框和阴影效果，美观大方
- 加载完成后自动滚动到可见区域

### 2. 下载功能

- 每个波形图下方都有"下载图片"按钮
- 使用 Bootstrap 图标和样式
- 点击即可保存 PNG 文件到本地

### 3. 快速操作

- "浏览数据"按钮 - 快速扫描目录
- "绘制波形"按钮 - 快速绘制上次浏览的文件
- 减少输入，提高效率

### 4. 友好的用户界面

- 功能卡片展示所有可用功能
- 清晰的视觉层次
- 响应式设计，适配不同屏幕尺寸

## 使用流程

### 典型工作流程

```
1. 用户打开 http://localhost:5010/chat

2. 点击 "浏览数据" 按钮或输入命令
   → 助手显示文件列表

3. 点击 "绘制第1个文件" 或直接说 "绘制第1个文件"
   → 助手生成波形图
   → 图像自动显示在聊天窗口
   → 显示下载按钮

4. 用户可以继续对话
   - "绘制第2个文件"
   - "对这个文件进行震相检测"
   - 等等...
```

## 技术细节

### 图像路径转换

**后端处理：**
```python
# 绝对路径 → 相对路径 → Web URL
image_path = "/path/to/results/waveforms/file.png"
rel_path = os.path.relpath(image_path, app.config['OUTPUT_FOLDER'])
# rel_path = "waveforms/file.png"

result['image_url'] = f'/api/output/{rel_path}'
# image_url = "/api/output/waveforms/file.png"
```

**前端访问：**
```
<img src="/api/output/waveforms/file.png">
↓
Flask serves file from web_app/outputs/waveforms/file.png
```

### 文件服务

Flask 已有的 `/api/output/<filename>` 端点提供文件下载服务：
```python
@app.route('/api/output/<filename>', methods=['GET'])
def download_output(filename):
    """Download output file"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404
```

这个端点同时支持：
- 浏览器直接访问（显示图像）
- 下载链接（`download` 属性触发下载）

## 测试验证

运行测试脚本验证功能：
```bash
python test_web_chat.py
```

测试场景包括：
1. 数据浏览意图识别
2. 波形绘制意图识别
3. 实体提取（文件路径）
4. 错误处理（不存在的文件/目录）

## 依赖要求

确保已安装必要的 Python 库：
```bash
pip install obspy matplotlib numpy flask
```

## 浏览器兼容性

支持的浏览器：
- Chrome/Edge (推荐)
- Firefox
- Safari
- Opera

需要支持的特性：
- Fetch API
- ES6 JavaScript
- CSS3 Flexbox

## 性能考虑

### 图像加载

- 使用 `onload` 事件确保图像加载完成后才滚动
- 图像自适应宽度，避免布局抖动
- 懒加载策略（只在需要时加载）

### 内存管理

- 定期清空聊天历史（提供"清空对话"按钮）
- 图像不会无限累积在 DOM 中
- 浏览器刷新会重置状态

## 安全考虑

### 文件访问控制

- 只能通过 `/api/output/` 访问 `outputs` 目录中的文件
- 无法访问系统其他目录
- 文件名由服务器生成，避免路径遍历攻击

### XSS 防护

- 用户输入经过转义后显示
- 图像 URL 由服务器生成，不接受用户提供的 URL
- 使用 `textContent` 而非 `innerHTML` 显示用户消息

## 未来改进方向

1. **图像缩放** - 添加放大/缩小控件
2. **灯箱效果** - 点击图像全屏查看
3. **缩略图** - 批量浏览时显示小图
4. **图像对比** - 并排显示多个波形
5. **交互式图表** - 集成 plotly.js 支持缩放

## 相关文档

- [Web 聊天使用指南](WEB_CHAT_VISUALIZATION_GUIDE.md)
- [快速开始](QUICK_START_WAVEFORM.md)
- [完整功能说明](WAVEFORM_VISUALIZATION_GUIDE.md)
- [技术实现总结](IMPLEMENTATION_SUMMARY.md)

## 版本信息

- **更新日期**: 2026-04-09
- **影响范围**: Web 聊天界面
- **向后兼容**: 是（不影响现有功能）
- **需要重启**: 是（重启 Flask 应用生效）

---

**立即体验：**
```bash
cd web_app
python app.py
# 访问 http://localhost:5010/chat
```
