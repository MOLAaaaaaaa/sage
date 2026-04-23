---
name: gmt_plotting
category: visualization
keywords: GMT, 地图, 震中分布, 台站分布, 断层, 地形, 震源机制, 海岸线, 等值线, 剖面, 走时, 地震目录, basemap, coast, pscoast, meca, coupe, grdimage, gmt begin, gmt end, run_gmt
---

# GMT 地图绘制

## 描述

使用 GMT (Generic Mapping Tools) 绘制地震学专业地图：震中分布图、台站位置图、地形图、震源机制球、剖面图等。

---

## ⚠️ 关键说明

- `run_gmt(script, outname, title)` 已预注入，**直接调用，无需 import**
- `script` 参数是**完整的 GMT6 bash 脚本字符串**（多行字符串）
- 脚本中必须使用 `gmt begin <name> PNG` ... `gmt end` 结构（GMT6 modern mode）
- 执行后自动生成 **PNG 图像** 和 **.sh 脚本文件**，均可在界面下载
- 需要系统安装 GMT >= 6.0

---

## 核心函数

### `run_gmt(script, outname="gmt_map", title="GMT Map")`

**参数：**
- `script` : str — 完整 GMT6 bash 脚本（多行字符串）
- `outname` : str — 输出文件基名，如 `"seismicity_map"`
- `title` : str — 脚本注释标题

**返回：** str（PNG 图像路径）

---

## 示例集

### 1. 震中分布图（最常用）

```python
gmt_script = """
gmt begin seismicity PNG
  # 底图：中国及周边区域
  gmt basemap -R70/140/15/55 -JM15c -Baf -BWSne+t"Seismicity Map"

  # 海岸线 + 国家边界
  gmt coast -Gtan -Slightblue -W0.5p,gray40 -N1/0.8p,gray60

  # 从 CSV 读取地震目录并绘制震中（lon, lat, depth, mag）
  # CSV 格式: lon lat depth mag
  gmt plot catalog.csv -i0,1 -Sc0.2c -Cjet -W0.3p,black -t30

  # 图例
  gmt legend -DjBL+w4c+o0.2c -F+g255/255/255@30 << 'EOF'
G 0.1c
H 9p,Helvetica-Bold 震中分布
D 0.1c 1p
S 0.2c c 0.3c red 0.5p,black 0.4c M<=4
S 0.2c c 0.4c orange 0.5p,black 0.4c 4<M<=5
S 0.2c c 0.5c blue 0.5p,black 0.4c M>5
EOF

gmt end
"""

run_gmt(gmt_script, outname="seismicity_map", title="震中分布图")
```

---

### 2. 台站位置图

```python
gmt_script = """
gmt begin station_map PNG
  gmt basemap -R100/115/25/42 -JM14c -Baf -BWSne+t"Station Map"
  gmt coast -Gwheat -Slightblue -W0.5p -N1/0.8p,gray

  # 绘制台站（三角形），数据文件：lon lat sta_name
  gmt plot stations.txt -i0,1 -St0.5c -Gred -W1p,black

  # 台站名标注
  gmt text stations.txt -i0,1,2 -F+f7p,Helvetica,black+jBL -D0.1c/0.1c

gmt end
"""

run_gmt(gmt_script, outname="station_map", title="台站分布图")
```

---

### 3. 震源机制球（beachball）

```python
gmt_script = """
gmt begin focal_map PNG
  gmt basemap -R95/105/28/38 -JM12c -Baf -BWSne+t"Focal Mechanisms"
  gmt coast -Gtan -Slightblue -W0.5p -N1/0.5p

  # 震源机制数据：lon lat depth strike dip rake mag [event_name]
  # 使用 meca 绘制（需要 GMT 的 seismology 模块）
  cat << 'EOF' | gmt meca -Sa1c -Gred -W0.5p,black
  100.5 33.2 15 120 60 -90 5.8 1 1
  102.1 30.5 20  45 75  30 4.9 1 1
  103.4 31.8 10  90 45 180 5.2 1 1
EOF

gmt end
"""

run_gmt(gmt_script, outname="focal_map", title="震源机制图")
```

---

### 4. 地形图（ETOPO / SRTM）

```python
gmt_script = """
gmt begin topo_map PNG
  # 下载并使用 ETOPO 地形数据（需联网）
  gmt grdcut @earth_relief_01m -R100/115/25/40 -Gtopo.grd

  # 地形渲染
  gmt grdimage topo.grd -JM14c -Cetopo1 -I+d

  # 叠加海岸线和边界
  gmt coast -W0.5p,gray40 -N1/0.8p,gray60 -Baf -BWSne+t"Topography"

  # 色标
  gmt colorbar -DJBC+w8c/0.4c+e -Baf+l"Elevation (m)"

gmt end
"""

run_gmt(gmt_script, outname="topo_map", title="地形图")
```

---

### 5. 剖面图（Cross-section）

```python
gmt_script = """
gmt begin cross_section PNG
  # 剖面参数: A点(lon1,lat1) → B点(lon2,lat2)，深度 0-100km，宽度 ±50km
  # 先提取投影范围内的地震
  # gmt project catalog.csv -C100/30 -E110/35 -W-50/50 -Fxyzpqrs > proj.txt

  gmt basemap -R0/1200/0/100 -JX15c/-8c -Bxaf+l"Distance (km)" -Byaf+l"Depth (km)" -BWSne+t"Cross Section A-B"

  # 绘制投影后的震中（距离, 深度）
  # gmt plot proj.txt -i4,2 -Sc0.15c -Cjet -W0.2p

  # 参考线
  gmt plot -W1p,red,- << 'EOF'
0 35
1200 35
EOF

gmt end
"""

run_gmt(gmt_script, outname="cross_section", title="地震剖面图")
```

---

## 完整串联示例：从 CSV 目录到震中图

```python
import os

# 假设已有地震目录 CSV：lon,lat,depth,mag
catalog_file = "/data/catalog/eq_catalog.csv"

gmt_script = """
gmt begin seismicity_final PNG
  gmt basemap -R70/140/15/55 -JM16c -Baf+g245/245/240 -BWSne+t"2020-2024 Seismicity"
  gmt coast -Gtan -Slightblue -W0.5p,gray50 -N1/0.8p,gray70 -A500

  # 小地震（M<4）：小灰点
  awk -F',' '$4<4 {print $1,$2}' """ + catalog_file + """ | gmt plot -Sc0.08c -Ggray60 -t50

  # 中等地震（4≤M<5）：橙点
  awk -F',' '$4>=4 && $4<5 {print $1,$2}' """ + catalog_file + """ | gmt plot -Sc0.18c -Gorange -W0.3p,black

  # 大地震（M≥5）：红点
  awk -F',' '$4>=5 {print $1,$2,($4*0.15)"c"}' """ + catalog_file + """ | gmt plot -Sc -Gred -W0.5p,black

  gmt colorbar -DJBC+w6c/0.35c -Baf+l"Depth (km)"

gmt end
"""

run_gmt(gmt_script, outname="seismicity_final", title="震中分布图")
print("地震数量：" + str(sum(1 for _ in open(catalog_file)) - 1))
```

---

## 常用 GMT6 命令速查

| 命令 | 用途 |
|------|------|
| `gmt basemap` | 绘制底图框架、坐标轴 |
| `gmt coast` | 海岸线、国界、地形填色 |
| `gmt plot` | 绘制点、线、多边形 |
| `gmt text` | 文字标注 |
| `gmt grdimage` | 栅格数据渲染（地形、速度模型）|
| `gmt colorbar` | 色标 |
| `gmt meca` | 震源机制球 |
| `gmt coupe` | 震源机制剖面 |
| `gmt project` | 坐标投影（做剖面）|
| `gmt surface` | 数据插值为网格 |
| `gmt contour` | 等值线 |

---

## 注意事项

- GMT6 modern mode：`gmt begin <name> PNG` ... `gmt end`（**推荐**）
- 脚本执行目录为 `SAGE_OUTDIR`（临时目录），数据文件需使用**绝对路径**
- `run_gmt` 会自动将 `gmt begin` 后的文件名替换为 `outname`
- 输出的 `.sh` 脚本可直接在终端重新运行，完全可重现
