---
name: waveform_visualization
category: visualization
keywords: 绘制, 画图, 绘图, 波形图, 可视化, 画波形, 波形绘制, 绘制波形, 粒子运动, 质点运动, plot_stream, plot_spectrogram, plot_psd, plot_particle_motion, savefig
---

# 波形可视化

## 描述

绘制波形时序图、振幅谱图、功率谱密度图和质点运动图，支持震相标注叠加。

---

## ⚠️ 关键说明：工具包函数无需 import，禁止 plt.show()

`plot_stream`、`plot_spectrogram`、`plot_psd`、`plot_particle_motion`、`savefig` 等函数
已通过 `from seismo_code.toolkit import *` **预注入到执行环境**，可以**直接调用**。

服务器运行环境**没有显示器**，使用 `plt.show()` 会导致程序挂起，**必须**改用 `savefig()` 或 `plot_*` 函数保存图像。

```python
# ✅ 正确流程（无需任何 import）
st = read_stream_from_dir("/data/event_001/")
st = detrend_stream(st)
st = filter_stream(st, "bandpass", freqmin=1.0, freqmax=10.0)
plot_stream(st, title="三分量波形")   # 自动保存，自动显示到界面

# ❌ 严禁
# from obspy import plot_stream        # plot_stream 不是 obspy 函数！
# plt.show()                           # 服务器环境无显示器，会挂起！
```

---

## 方案一：使用内置工具包（推荐）

### `plot_stream(st, title="", outfile=None, picks=None)`

绘制多分量波形图（每道一行，纵向排列）。

**参数：**
- `st` : obspy.Stream
- `title` : str — 图标题
- `outfile` : str — 保存路径；为 None 则自动保存到 SAGE_OUTDIR（**推荐不填**）
- `picks` : list[dict] — 震相标注

```python
# ✅ 直接调用（无需 import）
st = read_stream_from_dir("/data/event_001/")
st = detrend_stream(st)
st = filter_stream(st, "bandpass", freqmin=1.0, freqmax=10.0)

# 不传 outfile → 系统自动保存并显示到界面（推荐）
plot_stream(st, title="三分量波形")
```

---

### `plot_spectrogram(tr, outfile=None, wlen=None, per_lap=0.9)`

绘制单道波形的时频谱图。

```python
st = read_stream_from_dir("/data/event_001/")
tr = st.select(channel="*Z")[0]   # 取垂直分量
plot_spectrogram(tr)
```

---

### `plot_psd(tr, outfile=None)`

绘制功率谱密度（PSD）曲线。

```python
tr = st.select(channel="*Z")[0]
plot_psd(tr)
```

---

### `plot_particle_motion(st, outfile=None)`

绘制质点运动图（需要三分量数据）。

```python
st = read_stream_from_dir("/data/event_001/")
st = filter_stream(st, "bandpass", freqmin=1.0, freqmax=10.0)
plot_particle_motion(st)
```

---

## 方案二：使用原生 obspy + matplotlib（手动绘图）

当需要完全自定义图形时，可以用原生 obspy 读取数据，然后用 matplotlib 绘图。
**注意：必须用 `savefig()` 代替 `plt.show()`**

```python
from obspy import read   # obspy.read 是合法的 obspy 内置函数
import matplotlib.pyplot as plt

# 读取单个文件
st = read("/data/event_001/YN.YSW03..HHZ.sac")
tr = st[0]

times = tr.times()   # 相对时间轴（秒）
data = tr.data

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(times, data, linewidth=0.8, color='black')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.set_title(f"{tr.id}")
ax.grid(True, alpha=0.3)
plt.tight_layout()

# ✅ 必须用 savefig() 保存，不能用 plt.show()
savefig("waveform.png")   # savefig 已预注入，自动上报到界面
```

---

## 完整串联示例：一次性完成读取 + 预处理 + 多图可视化

```python
# 一段代码串联多个技能步骤（推荐写法）
st = read_stream_from_dir("/data/event_001/")
stream_info(st)                                          # 打印台站/通道信息

st = detrend_stream(st)
st = taper_stream(st)
st = filter_stream(st, "bandpass", freqmin=1.0, freqmax=10.0)

# 多分量波形图
plot_stream(st, title="事件波形（1-10 Hz）")

# 垂向分量频谱图 + PSD
tr_z = st.select(channel="*Z")[0]
plot_spectrogram(tr_z)
freqs, psd, _ = plot_psd(tr_z)
import numpy as np
print("主频：" + str(round(float(freqs[np.argmax(psd)]), 2)) + " Hz")

# 质点运动
plot_particle_motion(st)
```

---

## 注意事项

- **所有 plot_* 函数和 savefig 均已预注入，无需 import，也不能从 obspy 导入**
- 服务器环境须设 `show=False` 或省略（默认不弹窗），**禁止调用 plt.show()**
- 绘制质点运动图需要三分量数据（Z/N/E 或 Z/1/2），缺分量时跳过对应投影
- `outfile` 不填时自动保存到 `SAGE_OUTDIR` 并输出 `[FIGURE] /path` 供界面捕获
