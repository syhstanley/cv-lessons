# P2 — Gaussian Kernel 的 Separability 證明

關聯 Lesson：**L02 空間域濾波器（Task 2, Task 5）**

---

## Gaussian 的定義

$$
G(x, y; \sigma) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)
$$

## 可分離性

$$
G(x, y; \sigma) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2}{2\sigma^2}\right) \cdot \exp\left(-\frac{y^2}{2\sigma^2}\right)
$$

$$
= \underbrace{\frac{1}{\sqrt{2\pi}\sigma} e^{-x^2/2\sigma^2}}_{g_1(x)} \cdot \underbrace{\frac{1}{\sqrt{2\pi}\sigma} e^{-y^2/2\sigma^2}}_{g_1(y)}
$$

所以 2D Gaussian = 1D Gaussian（水平）⊗ 1D Gaussian（垂直）。

## 計算量優化

| 方法 | 每 pixel 乘法次數 |
|------|-----------------|
| 直接 2D（k×k kernel） | $k^2$ |
| Separable（兩個 1D） | $2k$ |

對 7×7 kernel：49 次 vs 14 次，**節省 71%**。

這正是 Realtek 硬體 ISP 和 GPU shader 都用 separable filter 的原因。

---

← [P1 2D Convolution](P01-2d-convolution.md) ｜ [回目錄](../formula_prove.md) ｜ [P3 Gaussian LPF →](P03-gaussian-lpf.md)
