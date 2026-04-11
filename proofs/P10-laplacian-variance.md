# P10 — Laplacian Variance 作為清晰度指標

關聯 Lesson：**L03 邊緣偵測（Task 4）**

---

## Laplacian 的定義

$$
\nabla^2 I(x, y) = \frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}
$$

離散近似（3×3 kernel）：

$$
\nabla^2 I(i,j) \approx I(i-1,j) + I(i+1,j) + I(i,j-1) + I(i,j+1) - 4I(i,j)
$$

## 為什麼 Variance 代表清晰度？

- **清晰圖片**：邊緣多，Laplacian 在邊緣有大數值（正負均有），variance 大。
- **模糊圖片**：邊緣被平滑，Laplacian 各處接近 0，variance 小。

## 數學關係

Laplacian 在頻域相當於乘以 $-(u^2 + v^2)$（Parseval 定理）：

$$
\text{Var}(\nabla^2 I) \propto \sum_{u,v} (u^2 + v^2)^2 |F(u,v)|^2
$$

模糊後高頻分量 $|F(u,v)|$ 在高 $u,v$ 處被衰減，所以 Laplacian variance 直接反映高頻能量。

---

← [P9 Gamma Correction](P09-gamma-correction.md) ｜ [回目錄](../formula_prove.md) ｜ [P11 Sobel Gradient →](P11-sobel-gradient.md)
