# P3 — Gaussian Filter 等於頻域低通濾波器

關聯 Lesson：**L02 空間域濾波器、L05 頻域濾波**

---

## 核心定理

**Gaussian 函數的 Fourier Transform 仍是 Gaussian 函數。**

$$
\mathcal{F}\left\{ e^{-x^2 / 2\sigma^2} \right\} = \sqrt{2\pi}\,\sigma \cdot e^{-2\pi^2 \sigma^2 f^2}
$$

## 意涵

空間域 Gaussian（標準差 $\sigma$）→ 頻域 Gaussian（標準差 $1/\sigma$）

$$
\sigma_{\text{spatial}} \uparrow \quad \Longrightarrow \quad \sigma_{\text{freq}} \downarrow \quad \Longrightarrow \quad \text{更強的低通}
$$

- **大 σ → 強模糊 → 頻域截止頻率低 → 濾掉更多高頻**
- **小 σ → 輕微平滑 → 頻域截止頻率高 → 保留較多高頻**

## 為什麼 Gaussian LPF 沒有 Ringing？

Gaussian 在空間域和頻域都無限延伸，沒有突然截斷，所以不會產生 sinc 函數的旁瓣（見 [P5 Ideal LPF Ringing](P05-ideal-lpf-ringing.md)）。

---

← [P2 Gaussian Separability](P02-gaussian-separability.md) ｜ [回目錄](../formula_prove.md) ｜ [P4 Convolution Theorem →](P04-convolution-theorem.md)
