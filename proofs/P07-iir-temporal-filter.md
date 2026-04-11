# P7 — IIR Temporal Filter 的頻率響應

關聯 Lesson：**L06 Noise Reduction（Task 1, Task 3）**

---

## 時域公式

$$
Y[t] = \alpha \cdot X[t] + (1 - \alpha) \cdot Y[t-1]
$$

## Z-Transform

取 Z-Transform，令 $z^{-1}$ 表示一個 time step 的延遲：

$$
Y(z) = \alpha \cdot X(z) + (1 - \alpha) \cdot z^{-1} \cdot Y(z)
$$

$$
Y(z)\left(1 - (1-\alpha)z^{-1}\right) = \alpha \cdot X(z)
$$

## 轉移函數

$$
H(z) = \frac{Y(z)}{X(z)} = \frac{\alpha}{1 - (1-\alpha)z^{-1}}
$$

## 頻率響應（令 $z = e^{j\omega}$）

$$
|H(e^{j\omega})| = \frac{\alpha}{\sqrt{1 + (1-\alpha)^2 - 2(1-\alpha)\cos\omega}}
$$

- $\omega = 0$（DC，靜態背景）：$|H| = 1$（完全通過）
- $\omega = \pi$（最高頻，快速變化）：$|H| = \frac{\alpha}{2 - \alpha}$（被衰減）

這正是一個 **低通濾波器**，$\alpha$ 小時截止頻率更低，降噪效果更強。

## 穩態響應的展開

$$
Y[t] = \alpha \sum_{k=0}^{\infty} (1-\alpha)^k \cdot X[t-k]
$$

即：輸出是所有歷史輸入的**指數加權移動平均（EMA）**，越舊的 frame 權重越低（指數衰減）。

---

← [P6 Bilateral Filter](P06-bilateral-filter.md) ｜ [回目錄](../formula_prove.md) ｜ [P8 Histogram Equalization →](P08-histogram-equalization.md)
