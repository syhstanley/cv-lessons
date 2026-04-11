# P6 — Bilateral Filter 的保邊原理

關聯 Lesson：**L02 空間域濾波器（Task 4）**

---

## 定義

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

## 為什麼能保邊？

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

## 當 $\sigma_r \to \infty$ 時

第二項趨近於 1，Bilateral → Gaussian blur。

---

← [P5 Ideal LPF Ringing](P05-ideal-lpf-ringing.md) ｜ [回目錄](../formula_prove.md) ｜ [P7 IIR Temporal Filter →](P07-iir-temporal-filter.md)
