# 📐 Formula Proofs — 傳統影像處理數學推導

各 lesson 所用公式的完整推導，供需要深入理解時參考。

---

## 目錄

| # | 主題 | 關聯 Lesson |
|---|------|------------|
| P1 | 2D Convolution 的定義與邊界行為 | L02 |
| P2 | Gaussian Kernel 的 Separability 證明 | L02 |
| P3 | Gaussian Filter 等於頻域低通濾波器 | L02, L05 |
| P4 | Convolution Theorem（空間卷積 = 頻域乘法） | L05 |
| P5 | Ideal LPF 的 Ringing（Gibbs Phenomenon） | L05 |
| P6 | Bilateral Filter 的保邊原理 | L02 |
| P7 | IIR Temporal Filter 的頻率響應 | L06 |
| P8 | Histogram Equalization 的 CDF 映射推導 | L07 |
| P9 | Gamma Correction 的感知模型 | L04 |
| P10 | Laplacian Variance 作為清晰度指標 | L03 |
| P11 | Sobel Gradient Direction 的幾何意義 | L03 |
| P12 | Gray World 白平衡假設 | L04 |

---

## P1 — 2D Convolution 的定義與邊界行為

### 連續形式

$$
(f * g)(x, y) = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} f(\tau_1, \tau_2) \cdot g(x - \tau_1, y - \tau_2) \, d\tau_1 \, d\tau_2
$$

### 離散形式（影像處理使用）

$$
\text{Output}(i, j) = \sum_{m} \sum_{n} K(m, n) \cdot I(i - m, j - n)
$$

但實作上通常寫成 **correlation**（不翻轉 kernel），在 kernel 對稱時兩者等效：

$$
\text{Output}(i, j) = \sum_{m} \sum_{n} K(m, n) \cdot I(i + m, j + n)
$$

### 為什麼要 Replicate Padding？

邊緣 pixel 的鄰域超出圖片邊界，需要填補。

| Padding 方式 | 假設 | 適用場景 |
|------------|------|---------|
| Zero padding | 邊界外全黑 | 常見但會產生邊緣陰影 |
| Replicate | 邊界外 = 最近邊緣 pixel | Camera ISP，自然延伸 |
| Reflect | 邊界外鏡像 | 週期性紋理 |

Replicate padding 在相機 ISP 最常用，因為它假設邊緣像素代表邊界外的顏色，失真最小。

---

## P2 — Gaussian Kernel 的 Separability 證明

### Gaussian 的定義

$$
G(x, y; \sigma) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)
$$

### 可分離性

$$
G(x, y; \sigma) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2}{2\sigma^2}\right) \cdot \exp\left(-\frac{y^2}{2\sigma^2}\right)
$$

$$
= \underbrace{\frac{1}{\sqrt{2\pi}\sigma} e^{-x^2/2\sigma^2}}_{g_1(x)} \cdot \underbrace{\frac{1}{\sqrt{2\pi}\sigma} e^{-y^2/2\sigma^2}}_{g_1(y)}
$$

所以 2D Gaussian = 1D Gaussian（水平）⊗ 1D Gaussian（垂直）。

### 計算量優化

| 方法 | 每 pixel 乘法次數 |
|------|-----------------|
| 直接 2D（k×k kernel） | $k^2$ |
| Separable（兩個 1D） | $2k$ |

對 7×7 kernel：49 次 vs 14 次，**節省 71%**。

這正是 Realtek 硬體 ISP 和 GPU shader 都用 separable filter 的原因。

---

## P3 — Gaussian Filter 等於頻域低通濾波器

### 核心定理

**Gaussian 函數的 Fourier Transform 仍是 Gaussian 函數。**

$$
\mathcal{F}\left\{ e^{-x^2 / 2\sigma^2} \right\} = \sqrt{2\pi}\,\sigma \cdot e^{-2\pi^2 \sigma^2 f^2}
$$

### 意涵

空間域 Gaussian（標準差 $\sigma$）→ 頻域 Gaussian（標準差 $1/\sigma$）

$$
\sigma_{\text{spatial}} \uparrow \quad \Longrightarrow \quad \sigma_{\text{freq}} \downarrow \quad \Longrightarrow \quad \text{更強的低通}
$$

- **大 σ → 強模糊 → 頻域截止頻率低 → 濾掉更多高頻**
- **小 σ → 輕微平滑 → 頻域截止頻率高 → 保留較多高頻**

### 為什麼 Gaussian LPF 沒有 Ringing？

Gaussian 在空間域和頻域都無限延伸，沒有突然截斷，所以不會產生 sinc 函數的旁瓣（見 P5）。

---

## P4 — Convolution Theorem（空間卷積 = 頻域乘法）

### 定理

$$
\mathcal{F}\{f * g\} = \mathcal{F}\{f\} \cdot \mathcal{F}\{g\}
$$

即：**空間域的卷積** 等於 **頻域的逐點乘法**。

### 推導（連續版）

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

### 實際意涵

| 操作 | 等效 |
|------|------|
| 空間域和 Gaussian kernel 做卷積 | 頻域乘以 Gaussian LPF mask |
| 空間域和 Laplacian kernel 做卷積 | 頻域乘以 HPF mask |

這就是為什麼頻域濾波和空間域濾波最終效果相同。

---

## P5 — Ideal LPF 的 Ringing（Gibbs Phenomenon）

### 為什麼 Ideal LPF 會有 Ringing？

Ideal LPF 在頻域是一個矩形函數（rect function）：

$$
H(f) = \text{rect}\left(\frac{f}{2f_0}\right) = \begin{cases} 1 & |f| \leq f_0 \\ 0 & |f| > f_0 \end{cases}
$$

它在空間域對應的 impulse response 是 **sinc 函數**：

$$
h(x) = \mathcal{F}^{-1}\{H\}(x) = 2f_0 \cdot \text{sinc}(2f_0 x)
$$

sinc 函數有無限延伸的旁瓣（side lobes），在邊緣附近造成振盪，即 **ringing artifact**。

### Gibbs Phenomenon

任何有不連續跳躍（discontinuity）的函數用有限頻率還原時，跳躍點附近都會出現約 **±9%** 的過衝（overshoot），這是理論極限，不可避免。

### 解法

用 Gaussian LPF 替代 Ideal LPF：Gaussian 在空間域仍是 Gaussian（無限平滑，無旁瓣），所以完全沒有 ringing。

---

## P6 — Bilateral Filter 的保邊原理

### 定義

普通 Gaussian blur 的權重只考慮空間距離：

$$
W_{\text{Gaussian}}(p, q) = \exp\left(-\frac{\|p - q\|^2}{2\sigma_s^2}\right)
$$

Bilateral filter 額外加入**像素值差異**作為權重：

$$
W_{\text{Bilateral}}(p, q) = \underbrace{\exp\left(-\frac{\|p - q\|^2}{2\sigma_s^2}\right)}_{\text{空間距離}} \cdot \underbrace{\exp\left(-\frac{|I(p) - I(q)|^2}{2\sigma_r^2}\right)}_{\text{像素值差異}}
$$

$$
\text{Output}(p) = \frac{\sum_q W(p, q) \cdot I(q)}{\sum_q W(p, q)}
$$

### 為什麼能保邊？

**邊緣兩側**的像素值差異大（$|I(p) - I(q)|$ 大）：
$$
\exp\left(-\frac{|I(p) - I(q)|^2}{2\sigma_r^2}\right) \approx 0
$$

→ 邊緣對面的像素幾乎不參與加權平均 → 邊緣被保留。

**平坦區域**的像素值差異小（$|I(p) - I(q)|$ 小）：
$$
\exp\left(-\frac{|I(p) - I(q)|^2}{2\sigma_r^2}\right) \approx 1
$$

→ 退化為普通 Gaussian blur → 噪聲被去除。

### 當 $\sigma_r \to \infty$ 時

第二項趨近於 1，Bilateral → Gaussian blur。

---

## P7 — IIR Temporal Filter 的頻率響應

### 時域公式

$$
Y[t] = \alpha \cdot X[t] + (1 - \alpha) \cdot Y[t-1]
$$

### Z-Transform

取 Z-Transform，令 $z^{-1}$ 表示一個 time step 的延遲：

$$
Y(z) = \alpha \cdot X(z) + (1 - \alpha) \cdot z^{-1} \cdot Y(z)
$$

$$
Y(z)\left(1 - (1-\alpha)z^{-1}\right) = \alpha \cdot X(z)
$$

### 轉移函數

$$
H(z) = \frac{Y(z)}{X(z)} = \frac{\alpha}{1 - (1-\alpha)z^{-1}}
$$

### 頻率響應（令 $z = e^{j\omega}$）

$$
|H(e^{j\omega})| = \frac{\alpha}{\sqrt{1 + (1-\alpha)^2 - 2(1-\alpha)\cos\omega}}
$$

- $\omega = 0$（DC，靜態背景）：$|H| = 1$（完全通過）
- $\omega = \pi$（最高頻，快速變化）：$|H| = \frac{\alpha}{2 - \alpha}$（被衰減）

這正是一個 **低通濾波器**，$\alpha$ 小時截止頻率更低，降噪效果更強。

### 穩態響應的展開

$$
Y[t] = \alpha \sum_{k=0}^{\infty} (1-\alpha)^k \cdot X[t-k]
$$

即：輸出是所有歷史輸入的**指數加權移動平均（EMA）**，越舊的 frame 權重越低（指數衰減）。

---

## P8 — Histogram Equalization 的 CDF 映射推導

### 目標

把輸入圖片的灰度分佈（任意分佈）轉換成**均勻分佈**。

### 連續推導

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

### 離散版

$$
s_k = \frac{L - 1}{N} \sum_{j=0}^{k} H(j) = \frac{(L-1) \cdot \text{CDF}(k)}{N}
$$

其中 $H(j)$ 是灰度值 $j$ 的 pixel 數，$N$ 是總 pixel 數。

減去 $\text{CDF}_{\min}$ 是為了讓輸出範圍從 0 開始（防止黑色偏移）：

$$
s_k = \text{round}\left(\frac{\text{CDF}(k) - \text{CDF}_{\min}}{N - \text{CDF}_{\min}} \times 255\right)
$$

---

## P9 — Gamma Correction 的感知模型

### Weber-Fechner Law

人眼對亮度的感知是**對數關係**（不是線性）：

$$
\text{Perceived Brightness} \propto \log(\text{Physical Luminance})
$$

即：眼睛對暗部細節更敏感，對亮部變化不敏感。

### Power Law（Stevens' Power Law）

更精確的模型是冪次關係：

$$
\text{Perceived} = \text{Physical}^{\gamma_{\text{eye}}}, \quad \gamma_{\text{eye}} \approx 1/2.2 \approx 0.45
$$

### Gamma Encoding（sRGB）

為了讓數位儲存的位元數對應人眼感知的均勻步階，對線性光 $I_{\text{linear}}$ 做：

$$
I_{\text{encoded}} = I_{\text{linear}}^{1/\gamma}, \quad \gamma = 2.2
$$

這樣 8-bit 的 0–255 才能均勻覆蓋人眼可感知的亮度範圍（否則亮部浪費大量位元，暗部嚴重失真）。

### 顯示器的 Decoding

顯示器內部做逆運算：$I_{\text{linear}} = I_{\text{encoded}}^{\gamma}$，最終打到螢幕的光是線性光。

### ISP 的位置

```
Sensor（線性光）→ ISP gamma encode → 儲存/傳輸 → 顯示器 gamma decode → 眼睛
```

---

## P10 — Laplacian Variance 作為清晰度指標

### Laplacian 的定義

$$
\nabla^2 I(x, y) = \frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}
$$

離散近似（3×3 kernel）：

$$
\nabla^2 I(i,j) \approx I(i-1,j) + I(i+1,j) + I(i,j-1) + I(i,j+1) - 4I(i,j)
$$

### 為什麼 Variance 代表清晰度？

- **清晰圖片**：邊緣多，Laplacian 在邊緣有大數值（正負均有），variance 大。
- **模糊圖片**：邊緣被平滑，Laplacian 各處接近 0，variance 小。

### 數學關係

Laplacian 在頻域相當於乘以 $-(u^2 + v^2)$（Parseval 定理）：

$$
\text{Var}(\nabla^2 I) \propto \sum_{u,v} (u^2 + v^2)^2 |F(u,v)|^2
$$

模糊後高頻分量 $|F(u,v)|$ 在高 $u,v$ 處被衰減，所以 Laplacian variance 直接反映高頻能量。

---

## P11 — Sobel Gradient Direction 的幾何意義

### 梯度向量

$$
\nabla I = \begin{pmatrix} G_x \\ G_y \end{pmatrix} = \begin{pmatrix} \partial I/\partial x \\ \partial I/\partial y \end{pmatrix}
$$

梯度方向 = 亮度**變化最快**的方向 = **垂直於邊緣**的方向。

### 方向角

$$
\theta = \arctan2(G_y, G_x)
$$

範圍 $-\pi$ 到 $\pi$（或 $-180°$ 到 $180°$）。

### NMS 為什麼用 % 180？

邊緣的方向有 **180° 的對稱性**：從左到右的邊緣和從右到左是同一條邊，只是梯度方向相反（差 180°）。取 `direction % 180` 讓兩者合併為同一條邊緣，避免重複偵測。

### Sobel vs Prewitt

| Kernel 中心行 | 效果 |
|-------------|------|
| Sobel：`[-1, 0, 1]`，中心行 `[-2, 0, 2]` | 對中心行加權，抗噪較強 |
| Prewitt：`[-1, 0, 1]`，中心行 `[-1, 0, 1]` | 各行等權，計算更簡單 |

Sobel 的加權等效於先做一次 1D Gaussian 平滑再求導。

---

## P12 — Gray World 白平衡假設

### 假設

一張自然場景的圖片，所有像素在 R、G、B 三個 channel 的平均值應該相等（即整體偏灰）：

$$
\bar{R} = \bar{G} = \bar{B}
$$

### 現實情況

在偏黃光源下（如室內燈）：$\bar{R} > \bar{G} > \bar{B}$

### 校正

讓各 channel 的平均值等於三者平均：

$$
\bar{\mu} = \frac{\bar{R} + \bar{G} + \bar{B}}{3}
$$

$$
\text{gain}_R = \frac{\bar{\mu}}{\bar{R}}, \quad \text{gain}_G = 1.0, \quad \text{gain}_B = \frac{\bar{\mu}}{\bar{B}}
$$

$$
R'(x,y) = \text{clip}(R(x,y) \cdot \text{gain}_R, \; 0, 255)
$$

### 限制

Gray World 假設在以下情況失效：
- 圖片以單一顏色為主（例如一整片草地）
- 人造場景（展覽、廣告牌）
- 日落/日出等極端光源

實際相機的 AWB 算法通常結合 Gray World、白點偵測和機器學習模型。
