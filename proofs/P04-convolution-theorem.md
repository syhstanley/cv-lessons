# P4 — Convolution Theorem（空間卷積 = 頻域乘法）

關聯 Lesson：**L05 頻域濾波**

---

## 定理

$$
\mathcal{F}\{f * g\} = \mathcal{F}\{f\} \cdot \mathcal{F}\{g\}
$$

即：**空間域的卷積** 等於 **頻域的逐點乘法**。

## 推導（連續版）

$$
\mathcal{F}\{f * g\}(u) = \int_{-\infty}^{\infty} \left[\int_{-\infty}^{\infty} f(\tau) g(x - \tau) d\tau \right] e^{-j2\pi ux} dx
$$

交換積分順序：

$$
= \int_{-\infty}^{\infty} f(\tau) \left[\int_{-\infty}^{\infty} g(x - \tau) e^{-j2\pi ux} dx \right] d\tau
$$

令 $x' = x - \tau$：

$$
= \int_{-\infty}^{\infty} f(\tau) e^{-j2\pi u\tau} d\tau \cdot \int_{-\infty}^{\infty} g(x') e^{-j2\pi ux'} dx'
$$

$$
= \mathcal{F}\{f\}(u) \cdot \mathcal{F}\{g\}(u) \quad \blacksquare
$$

## 實際意涵

| 操作 | 等效 |
|------|------|
| 空間域和 Gaussian kernel 做卷積 | 頻域乘以 Gaussian LPF mask |
| 空間域和 Laplacian kernel 做卷積 | 頻域乘以 HPF mask |

這就是為什麼頻域濾波和空間域濾波最終效果相同。

---

← [P3 Gaussian LPF](P03-gaussian-lpf.md) ｜ [回目錄](../formula_prove.md) ｜ [P5 Ideal LPF Ringing →](P05-ideal-lpf-ringing.md)
