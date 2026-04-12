# Web 聊天界面 - 数据浏览和波形绘图使用指南

## 概述

Web 聊天界面现在支持通过自然语言对话来浏览地震数据目录和绘制波形图。您可以在浏览器中直接与 AI 助手对话，完成数据探索和可视化任务。

## 访问聊天界面

1. 启动 Web 应用：
```bash
cd web_app
python app.py
```

2. 在浏览器中打开：
```
http://localhost:5010/chat
```

## 功能特性

### 1. 数据浏览

**功能说明：**
- 扫描指定目录查找地震数据文件
- 显示文件列表、大小和数量
- 支持 .mseed, .sac, .seed, .miniseed 格式

**使用方法：**

方法 1：点击快速操作按钮
- 点击 "浏览数据" 按钮

方法 2：输入命令
```
- "帮我查看 /path/to/data 目录下有哪些mseed数据"
- "浏览 /data/seismic 目录"
- "查看 /path/to/data 文件夹"
```

**输出示例：**
```
在目录 /path/to/data 中找到 25 个地震数据文件:

1. GG.53036.mseed (245.3 MB)
2. GG.53037.mseed (198.7 MB)
3. GG.53038.mseed (312.1 MB)
...

您可以对我说 '绘制第1个文件' 或 '绘制 GG.53036.mseed' 来查看波形。
```

### 2. 波形绘制

**功能说明：**
- 使用 ObsPy 读取地震数据
- 使用 matplotlib 创建专业波形图
- 自动在聊天界面中显示图像
- 提供下载按钮保存图像

**使用方法：**

方法 1：点击快速操作按钮
- 点击 "绘制波形" 按钮（需要先浏览过目录）

方法 2：输入命令
```
- "绘制 /path/to/file.mseed 的波形"
- "plot waveform from /data/file.sac"
- "显示 file.mseed 的波形图"
- "绘制第1个文件"  # 需要先浏览目录
- "画一下这个文件"
```

**输出示例：**
```
✓ 波形图已生成!

文件: GG.53036.mseed
输出: results/waveforms/GG.53036_20260409_143052.png

图片已保存到 results/waveforms 目录。
```

聊天界面会显示：
- 波形图像（自动缩放适应聊天窗口）
- 下载按钮（点击可保存 PNG 文件）

## 完整工作流程示例

### 场景 1: 浏览 → 选择 → 绘制

```
步骤 1: 点击 "浏览数据" 按钮或输入
用户: 帮我查看 /data/seismic 目录下有哪些mseed数据

助手: 在目录 /data/seismic 中找到 10 个地震数据文件:
      1. station1.mseed (100 MB)
      2. station2.mseed (120 MB)
      3. station3.mseed (95 MB)
      ...
      您可以对我说 '绘制第1个文件' 来查看波形。

步骤 2: 绘制指定文件
用户: 绘制第1个文件

助手: ✓ 波形图已生成!
      文件: station1.mseed
      输出: results/waveforms/station1_20260409.png

      [显示波形图像]
      [下载图片] 按钮
```

### 场景 2: 直接绘制指定文件

```
用户: 绘制 /data/station1.mseed 的波形

助手: ✓ 波形图已生成!
      文件: station1.mseed
      输出: results/waveforms/station1_20260409.png

      [显示波形图像]
      [下载图片] 按钮
```

### 场景 3: 多轮对话分析

```
用户: 查看 /data/seismic 目录

助手: 找到 10 个文件...

用户: 绘制第1个文件

助手: 波形图已生成... [显示图像]

用户: 对这个文件进行震相检测

助手: 开始震相检测...
```

## 界面元素说明

### 快速操作按钮

聊天界面顶部提供了快捷按钮：

1. **浏览数据** - 快速浏览当前目录
2. **绘制波形** - 绘制上次浏览的文件
3. **拾取震相** - 震相检测功能
4. **关联事件** - 震相关联功能
5. **极性分析** - 初动极性分析
6. **帮助** - 显示功能说明
7. **清空对话** - 清除聊天历史

### 消息显示

**用户消息：**
- 显示在右侧
- 蓝色背景

**助手消息：**
- 显示在左侧
- 白色背景
- 支持富文本格式（粗体、代码、列表）

**图像显示：**
- 自动适应聊天窗口宽度
- 圆角边框和阴影效果
- 加载完成后自动滚动到可见区域
- 附带下载按钮

### 输入框

- 支持回车键发送消息
- 占位符提示常用命令
- 自动清空已发送内容

## 技术实现

### 后端 API

**端点：** `/api/chat`

**请求格式：**
```json
{
  "message": "帮我查看 /data 目录"
}
```

**响应格式：**
```json
{
  "response": "在目录 /data 中找到 10 个文件...",
  "action": "display_files",
  "data": {
    "results": {
      "files": [...],
      "count": 10
    }
  },
  "image_url": null  // 如果有图像，会包含 URL
}
```

### 前端处理

**图像显示流程：**

1. 接收 API 响应
2. 检查 `image_url` 字段
3. 如果存在，创建 `<img>` 元素
4. 添加下载按钮
5. 自动滚动到最新消息

**关键代码：**
```javascript
// Add assistant response with image if available
addMessage('assistant', data.response, data.image_url || null);

// In addMessage function
if (imageUrl) {
    const imgDiv = document.createElement('div');
    imgDiv.innerHTML = `
        <img src="${imageUrl}" alt="Waveform"
             style="max-width: 100%; border-radius: 10px;">
        <div>
            <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                <i class="bi bi-download"></i> 下载图片
            </a>
        </div>
    `;
}
```

### 文件路径处理

**后端（app.py）：**
```python
# If the action is to display a plot, add image URL
if result.get('action') == 'display_plot':
    image_path = result['data']['results']['image_path']
    # Convert to relative path for web access
    rel_path = os.path.relpath(image_path, app.config['OUTPUT_FOLDER'])
    result['image_url'] = f'/api/output/{rel_path}'
```

**前端访问：**
- 图像 URL 格式：`/api/output/waveforms/filename.png`
- Flask 的 `/api/output/<filename>` 端点提供文件服务

## 常见问题

### Q1: 图像不显示怎么办？

**可能原因：**
1. 文件路径不正确
2. 输出目录权限问题
3. 浏览器缓存

**解决方案：**
```bash
# 检查输出目录是否存在
ls -la web_app/outputs/

# 检查文件权限
chmod -R 755 web_app/outputs/

# 清除浏览器缓存
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (Mac)
```

### Q2: 点击下载按钮没有反应？

**解决方案：**
1. 检查浏览器是否阻止了下载
2. 右键点击图像，选择"另存为"
3. 直接在浏览器中打开图像 URL

### Q3: 如何查看原始大小的图像？

**方法：**
1. 点击图像在新标签页中打开
2. 或者点击下载按钮保存后查看

### Q4: 可以同时绘制多个文件吗？

**当前限制：**
- 一次只能绘制一个文件
- 可以通过连续对话快速处理多个文件

** workaround：**
```
用户: 绘制第1个文件
[等待图像显示]
用户: 绘制第2个文件
[等待图像显示]
用户: 绘制第3个文件
```

## 性能优化建议

### 1. 图像大小

系统自动生成 150 DPI 的 PNG 图像，平衡质量和文件大小。

**如果需要更小的文件：**
修改 `conversational_agent.py` 中的 `dpi` 参数：
```python
plt.savefig(output_image, dpi=100, bbox_inches='tight')  # 降低 DPI
```

### 2. 浏览器性能

如果聊天历史很长，建议定期清空对话：
- 点击 "清空对话" 按钮
- 或刷新页面

### 3. 服务器资源

大文件绘图可能需要较长时间：
- 系统会显示 "正在输入..." 指示器
- 后台使用 matplotlib 的 Agg 后端（非交互式）
- 不会阻塞其他请求

## 集成到其他页面

如果您想在其他页面也显示波形图，可以复用以下组件：

**HTML：**
```html
<div id="waveformContainer">
    <img id="waveformImage" src="" alt="Waveform" style="max-width: 100%;">
    <a id="downloadLink" href="" download class="btn btn-primary">下载图片</a>
</div>
```

**JavaScript：**
```javascript
function displayWaveform(imageUrl) {
    document.getElementById('waveformImage').src = imageUrl;
    document.getElementById('downloadLink').href = imageUrl;
    document.getElementById('waveformContainer').style.display = 'block';
}
```

## 未来改进方向

1. **图像缩放** - 添加放大/缩小功能
2. **交互式查看** - 集成 plotly.js 支持缩放和平移
3. **批量绘图** - 一次生成多个文件的缩略图
4. **图像对比** - 并排显示多个波形图
5. **标注功能** - 在图像上添加注释和标记

## 相关文档

- [快速开始指南](QUICK_START_WAVEFORM.md)
- [完整使用指南](WAVEFORM_VISUALIZATION_GUIDE.md)
- [技术实现总结](IMPLEMENTATION_SUMMARY.md)
- [对话式AI功能](CONVERSATIONAL_AGENT_GUIDE.md)

---

**提示：** 充分利用快速操作按钮可以提高工作效率！
