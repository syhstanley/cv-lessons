# P1 — 2D Convolution 的定義與邊界行為

關聯 Lesson：**L02 空間域濾波器**

---

## 連續形式

$$
(f * g)(x, y) = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} f(\tau_1, \tau_2) \cdot g(x - \tau_1, y - \tau_2) \, d\tau_1 \, d\tau_2
$$

## 離散形式（影像處理使用）

$$
\text{Output}(i, j) = \sum_{m} \sum_{n} K(m, n) \cdot I(i - m, j - n)
$$

但實作上通常寫成 **correlation**（不翻轉 kernel），在 kernel 對稱時兩者等效：

$$
\text{Output}(i, j) = \sum_{m} \sum_{n} K(m, n) \cdot I(i + m, j + n)
$$

## 為什麼要 Replicate Padding？

邊緣 pixel 的鄰域超出圖片邊界，需要填補。

| Padding 方式 | 假設 | 適用場景 |
|------------|------|---------|
| Zero padding | 邊界外全黑 | 常見但會產生邊緣陰影 |
| Replicate | 邊界外 = 最近邊緣 pixel | Camera ISP，自然延伸 |
| Reflect | 邊界外鏡像 | 週期性紋理 |

Replicate padding 在相機 ISP 最常用，因為它假設邊緣像素代表邊界外的顏色，失真最小。

---

← [回目錄](../formula_prove.md) ｜ 下一篇：[P2 Gaussian Separability →](P02-gaussian-separability.md)
