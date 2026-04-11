# P11 — Sobel Gradient Direction 的幾何意義

關聯 Lesson：**L03 邊緣偵測（Task 1）**

---

## 梯度向量

$$
\nabla I = \begin{pmatrix} G_x \\ G_y \end{pmatrix} = \begin{pmatrix} \partial I/\partial x \\ \partial I/\partial y \end{pmatrix}
$$

梯度方向 = 亮度**變化最快**的方向 = **垂直於邊緣**的方向。

## 方向角

$$
\theta = \arctan2(G_y, G_x)
$$

範圍 $-\pi$ 到 $\pi$（或 $-180°$ 到 $180°$）。

## NMS 為什麼用 % 180？

邊緣的方向有 **180° 的對稱性**：從左到右的邊緣和從右到左是同一條邊，只是梯度方向相反（差 180°）。取 `direction % 180` 讓兩者合併為同一條邊緣，避免重複偵測。

## Sobel vs Prewitt

| Kernel 中心行 | 效果 |
|-------------|------|
| Sobel：`[-1, 0, 1]`，中心行 `[-2, 0, 2]` | 對中心行加權，抗噪較強 |
| Prewitt：`[-1, 0, 1]`，中心行 `[-1, 0, 1]` | 各行等權，計算更簡單 |

Sobel 的加權等效於先做一次 1D Gaussian 平滑再求導。

---

← [P10 Laplacian Variance](P10-laplacian-variance.md) ｜ [回目錄](../formula_prove.md) ｜ [P12 Gray World →](P12-gray-world.md)
