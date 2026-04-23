---
name: waveform_io
category: waveform
keywords: 读取波形, 加载波形, mseed, sac, miniseed, seed, 波形文件, read_stream, stream_info, picks_to_dict
---

# 波形读取与信息查询

## 描述

读取本地波形文件（SAC / MiniSEED / SEED 等），获取流信息，加载震相拾取结果。

---

## ⚠️ 关键说明：工具包函数无需 import

`read_stream`、`read_stream_from_dir`、`stream_info`、`picks_to_dict` 等函数已通过
`from seismo_code.toolkit import *` **预注入到执行环境**，可以**直接调用**：

```python
# ✅ 正确：直接调用，无需任何 import
st = read_stream_from_dir("/data/event_001/")
```

**❌ 严禁以下写法（会报 ImportError）：**
```python
# 错误：read_stream_from_dir 不是 obspy 的函数！
from obspy import read_stream_from_dir

# 错误：已预注入，不需要再 import
from seismo_code.toolkit import read_stream_from_dir
```

---

## 主要函数

### `read_stream(path)`

读取单个波形文件，返回 `obspy.Stream`。

**参数：**
- `path` : str — 波形文件路径（支持 .mseed / .sac / .seed / .msd 等）

**返回：** `obspy.Stream`

```python
# ✅ 直接调用（无需 import）
st = read_stream("/data/station/HHZ.mseed")
print(st)
# 输出: 1 Trace(s) in Stream: NET.STA.LOC.HHZ ...
```

---

### `read_stream_from_dir(directory, pattern="**/*")`

递归读取目录下所有波形文件（SAC / MiniSEED / SEED 均可），合并为一个 Stream。

**参数：**
- `directory` : str — 目录路径
- `pattern` : str — glob 模式，默认 `**/*`（**读取所有格式**，推荐使用默认值）

**返回：** `obspy.Stream`

> ⚠️ **重要**：`read_stream` 只能读取**单个文件**，不支持 glob（`*`）路径。
> 读取整个目录时，**必须**使用 `read_stream_from_dir(directory)`。

```python
# ✅ 正确：读取目录下全部波形（直接调用，无需 import）
st = read_stream_from_dir("/data/event_001/")
print(f"共加载 {len(st)} 条 Trace")

# ✅ 也可以只读 .sac 文件
st = read_stream_from_dir("/data/event_001/", pattern="**/*.sac")

# ❌ 错误：不能给 read_stream 传 glob 路径
# st = read_stream("/data/event_001/*.mseed")  # 会报错！

# ❌ 错误：不能从 obspy 导入此函数
# from obspy import read_stream_from_dir  # ImportError！
```

---

### 原生 obspy 替代写法（读取单个 SAC 文件）

如果只需要读取单个文件，也可以使用原生 obspy：

```python
from obspy import read   # obspy.read 是合法的 obspy 函数

# 读取单个文件
st = read("/data/event_001/YN.YSW03..HHZ.sac")
tr = st[0]
print(f"台站: {tr.id}, 采样率: {tr.stats.sampling_rate} Hz")
print(f"时长: {tr.stats.npts / tr.stats.sampling_rate:.1f} 秒")
```

---

### `stream_info(st)`

打印 Stream 的详细统计信息（台站、通道、时间范围、采样率）。

```python
# ✅ 直接调用（无需 import）
st = read_stream_from_dir("/data/event_001/")
info = stream_info(st)
print(info)
```

---

### `picks_to_dict(picks_file)`

读取震相拾取结果文件（CSV 格式）。

```python
# ✅ 直接调用（无需 import）
picks = picks_to_dict("results/picks.csv")
for p in picks:
    print(f"{p['phase']}  t={p['rel_time']:.2f}s  conf={p['confidence']:.2f}")
```

---

## 注意事项

- 所有工具包函数已预注入，**不需要也不能用 `from obspy import ...` 导入它们**
- 需要原生 obspy 功能时用 `from obspy import read`（这是 obspy 自己的函数）
- 三分量文件（HHZ/HHN/HHE）建议放在同一目录并用 `read_stream_from_dir` 一次性加载
- 若文件路径不存在会抛出 `FileNotFoundError`，建议用 `try/except` 保护
