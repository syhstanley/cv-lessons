# P9 — Gamma Correction 的感知模型

關聯 Lesson：**L04 ISP Pipeline（Task 3）**

---

## Weber-Fechner Law

人眼對亮度的感知是**對數關係**（不是線性）：

$$
\text{Perceived Brightness} \propto \log(\text{Physical Luminance})
$$

即：眼睛對暗部細節更敏感，對亮部變化不敏感。

## Power Law（Stevens' Power Law）

更精確的模型是冪次關係：

$$
\text{Perceived} = \text{Physical}^{\gamma_{\text{eye}}}, \quad \gamma_{\text{eye}} \approx 1/2.2 \approx 0.45
$$

## Gamma Encoding（sRGB）

為了讓數位儲存的位元數對應人眼感知的均勻步階，對線性光 $I_{\text{linear}}$ 做：

$$
I_{\text{encoded}} = I_{\text{linear}}^{1/\gamma}, \quad \gamma = 2.2
$$

這樣 8-bit 的 0–255 才能均勻覆蓋人眼可感知的亮度範圍（否則亮部浪費大量位元，暗部嚴重失真）。

## 顯示器的 Decoding

顯示器內部做逆運算：$I_{\text{linear}} = I_{\text{encoded}}^{\gamma}$，最終打到螢幕的光是線性光。

## ISP 的位置

```
Sensor（線性光）→ ISP gamma encode → 儲存/傳輸 → 顯示器 gamma decode → 眼睛
```

---

← [P8 Histogram Equalization](P08-histogram-equalization.md) ｜ [回目錄](../formula_prove.md) ｜ [P10 Laplacian Variance →](P10-laplacian-variance.md)
