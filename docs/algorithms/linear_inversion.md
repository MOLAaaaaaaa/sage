# 线性反演算法

## 概述

线性反演是地球物理中最基础的反演方法之一,适用于正演关系为线性的问题。通过最小二乘法求解模型参数,使预测数据与观测数据的残差最小。

## 数学原理

### 正演方程

对于线性问题,正演关系可以表示为:

$$d = Gm$$

其中:
- $d$ 是观测数据向量 (n×1)
- $G$ 是灵敏度矩阵或核矩阵 (n×m)
- $m$ 是模型参数向量 (m×1)

### 反演公式

使用阻尼最小二乘法(Tikhonov正则化),反演解为:

$$m = (G^T G + \lambda I)^{-1} G^T d$$

其中:
- $\lambda$ 是正则化参数,控制解的平滑程度
- $I$ 是单位矩阵

### 目标函数

最小化的目标函数为:

$$\phi(m) = ||Gm - d||^2_2 + \lambda ||m||^2_2$$

第一项为数据拟合项,第二项为模型正则化项。

## 算法步骤

**步骤1**: 构建灵敏度矩阵G

根据正演问题的物理模型,构建数据与模型之间的线性关系矩阵G。

**步骤2**: 选择正则化参数

通过L曲线法、交叉验证或经验值选择合适的正则化参数λ。

**步骤3**: 计算反演解

使用公式 $m = (G^T G + \lambda I)^{-1} G^T d$ 计算模型参数。

**步骤4**: 评估结果

- 计算预测数据: $d_{pred} = Gm$
- 计算残差: $r = d_{obs} - d_{pred}$
- 计算RMS误差: $RMS = \sqrt{\frac{1}{n}\sum r_i^2}$

**步骤5**: 不确定性分析(可选)

计算模型协方差矩阵:

$$C_m = \sigma^2 (G^T G + \lambda I)^{-1}$$

## 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| regularization_weight | float | 0.01 | 正则化权重λ |
| max_iterations | int | 100 | 最大迭代次数 |
| tolerance | float | 1e-6 | 收敛容差 |

## Python实现要点

### 输入数据格式

```python
# 观测数据
data = np.array([...])  # shape: (n_data,)

# 灵敏度矩阵
G = np.array([...])  # shape: (n_data, n_model)
```

### 核心代码结构

```python
import numpy as np

def linear_inversion(G, data, reg_weight=0.01):
    """
    执行线性反演

    参数:
        G: 灵敏度矩阵 (n_data x n_model)
        data: 观测数据 (n_data,)
        reg_weight: 正则化参数

    返回:
        model: 反演得到的模型参数
        predicted: 预测数据
        misfit: RMS残差
    """
    n_model = G.shape[1]

    # 构建正规方程
    GtG = G.T @ G
    Gtd = G.T @ data

    # 添加正则化
    A = GtG + reg_weight * np.eye(n_model)

    # 求解
    model = np.linalg.solve(A, Gtd)

    # 计算预测数据和残差
    predicted = G @ model
    misfit = np.sqrt(np.mean((data - predicted)**2))

    return model, predicted, misfit
```

## 应用实例

### 速度结构反演

在地震层析成像中,走时数据与慢度扰动之间近似为线性关系:

$$\delta t = \int_L \delta s(x) dx$$

离散化后可写为矩阵形式,使用线性反演求解速度结构。

### 重力反演

对于密度界面的小幅扰动,重力异常与界面深度变化近似线性相关,可使用线性反演方法。

## 注意事项

1. **线性假设**: 仅适用于正演关系为线性或可线性化的问题
2. **正则化选择**: λ过大导致过度平滑,λ过小导致解不稳定
3. **矩阵条件数**: G的条件数过大会导致数值不稳定
4. **计算效率**: 对于大规模问题,建议使用迭代求解器而非直接求逆

## 参考文献

1. Tarantola, A. (2005). Inverse Problem Theory and Methods for Model Parameter Estimation. SIAM.
2. Aster, R. C., Borchers, B., & Thurber, C. H. (2018). Parameter Estimation and Inverse Problems. Elsevier.
3. Menke, W. (2018). Geophysical Data Analysis: Discrete Inverse Theory. Academic Press.
