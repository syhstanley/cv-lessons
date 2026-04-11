# P5 — Ideal LPF 的 Ringing（Gibbs Phenomenon）

關聯 Lesson：**L05 頻域濾波**

---

## 為什麼 Ideal LPF 會有 Ringing？

Ideal LPF 在頻域是一個矩形函數（rect function）：

$$
H(f) = \text{rect}\left(\frac{f}{2f_0}\right) = \begin{cases} 1 & |f| \leq f_0 \\ 0 & |f| > f_0 \end{cases}
$$

它在空間域對應的 impulse response 是 **sinc 函數**：

$$
h(x) = \mathcal{F}^{-1}\{H\}(x) = 2f_0 \cdot \text{sinc}(2f_0 x)
$$

sinc 函數有無限延伸的旁瓣（side lobes），在邊緣附近造成振盪，即 **ringing artifact**。

## Gibbs Phenomenon

任何有不連續跳躍（discontinuity）的函數用有限頻率還原時，跳躍點附近都會出現約 **±9%** 的過衝（overshoot），這是理論極限，不可避免。

## 解法

用 Gaussian LPF 替代 Ideal LPF：Gaussian 在空間域仍是 Gaussian（無限平滑，無旁瓣），所以完全沒有 ringing。

詳見 [P3 — Gaussian Filter 等於頻域低通濾波器](P03-gaussian-lpf.md)。

---

← [P4 Convolution Theorem](P04-convolution-theorem.md) ｜ [回目錄](../formula_prove.md) ｜ [P6 Bilateral Filter →](P06-bilateral-filter.md)
