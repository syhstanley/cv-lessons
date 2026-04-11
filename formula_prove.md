# 📐 Formula Proofs — 傳統影像處理數學推導

各 lesson 所用公式的完整推導，每個章節獨立一份檔案，放在 `proofs/` 資料夾。

---

## 目錄

| # | 主題 | 關聯 Lesson | 連結 |
|---|------|------------|------|
| P1 | 2D Convolution 的定義與邊界行為 | L02 | [→ proofs/P01](proofs/P01-2d-convolution.md) |
| P2 | Gaussian Kernel 的 Separability 證明 | L02 | [→ proofs/P02](proofs/P02-gaussian-separability.md) |
| P3 | Gaussian Filter 等於頻域低通濾波器 | L02, L05 | [→ proofs/P03](proofs/P03-gaussian-lpf.md) |
| P4 | Convolution Theorem（空間卷積 = 頻域乘法） | L05 | [→ proofs/P04](proofs/P04-convolution-theorem.md) |
| P5 | Ideal LPF 的 Ringing（Gibbs Phenomenon） | L05 | [→ proofs/P05](proofs/P05-ideal-lpf-ringing.md) |
| P6 | Bilateral Filter 的保邊原理 | L02 | [→ proofs/P06](proofs/P06-bilateral-filter.md) |
| P7 | IIR Temporal Filter 的頻率響應 | L06 | [→ proofs/P07](proofs/P07-iir-temporal-filter.md) |
| P8 | Histogram Equalization 的 CDF 映射推導 | L07 | [→ proofs/P08](proofs/P08-histogram-equalization.md) |
| P9 | Gamma Correction 的感知模型 | L04 | [→ proofs/P09](proofs/P09-gamma-correction.md) |
| P10 | Laplacian Variance 作為清晰度指標 | L03 | [→ proofs/P10](proofs/P10-laplacian-variance.md) |
| P11 | Sobel Gradient Direction 的幾何意義 | L03 | [→ proofs/P11](proofs/P11-sobel-gradient.md) |
| P12 | Gray World 白平衡假設 | L04 | [→ proofs/P12](proofs/P12-gray-world.md) |

---

## 各 Lesson 對應的 Proofs

| Lesson | 主題 | 相關 Proofs |
|--------|------|------------|
| L02 空間域濾波器 | Gaussian / Median / Bilateral | P1, P2, P3, P6 |
| L03 邊緣偵測 | Sobel / Canny / 模糊偵測 | P10, P11 |
| L04 ISP Pipeline | Demosaic / AWB / Gamma | P9, P12 |
| L05 頻域濾波 | FFT / LPF / HPF | P3, P4, P5 |
| L06 Noise Reduction | Temporal NR / Motion-Adaptive | P7 |
| L07 影像銳化 | USM / Hist EQ / CLAHE | P8 |
