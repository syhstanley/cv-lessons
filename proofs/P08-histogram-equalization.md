# P8 — Histogram Equalization 的 CDF 映射推導

關聯 Lesson：**L07 影像銳化與畫質增強（Task 3）**

---

## 目標

把輸入圖片的灰度分佈（任意分佈）轉換成**均勻分佈**。

## 連續推導

設輸入灰度值 $r$ 的 PDF 為 $p_r(r)$，目標輸出灰度值 $s$ 的 PDF 為 $p_s(s)$ 是均勻分佈。

對灰度值 mapping $s = T(r)$，PDF 變換公式為：

$$
p_s(s) = p_r(r) \left|\frac{dr}{ds}\right|
$$

若要讓 $p_s(s) = \frac{1}{L}$（均勻分佈，L = 灰度層數）：

$$
\frac{1}{L} = p_r(r) \cdot \frac{dr}{ds} \implies \frac{ds}{dr} = L \cdot p_r(r)
$$

積分得：

$$
s = T(r) = L \int_0^r p_r(t) \, dt = L \cdot \text{CDF}_r(r)
$$

**結論：最佳 mapping = $L$ 倍的累積分佈函數（CDF）。**

## 離散版

$$
s_k = \frac{L - 1}{N} \sum_{j=0}^{k} H(j) = \frac{(L-1) \cdot \text{CDF}(k)}{N}
$$

其中 $H(j)$ 是灰度值 $j$ 的 pixel 數，$N$ 是總 pixel 數。

減去 $\text{CDF}_{\min}$ 是為了讓輸出範圍從 0 開始（防止黑色偏移）：

$$
s_k = \text{round}\left(\frac{\text{CDF}(k) - \text{CDF}_{\min}}{N - \text{CDF}_{\min}} \times 255\right)
$$

---

← [P7 IIR Temporal Filter](P07-iir-temporal-filter.md) ｜ [回目錄](../formula_prove.md) ｜ [P9 Gamma Correction →](P09-gamma-correction.md)
