# Lesson 05 — 頻域濾波（Frequency Domain Filtering）

## 為什麼要去頻域？

空間域的卷積 ↔ 頻域的乘法（Convolution Theorem）

```
f * g  ←→  F · G
```

大 kernel 的卷積在頻域乘法更快（FFT O(N log N) vs 卷積 O(N²)）

---

## 1. Fourier Transform 複習

**2D DFT**：
```
F(u,v) = Σ Σ f(x,y) · exp(-j2π(ux/M + vy/N))
```

- F(u,v)：頻域表示（複數）
- u,v：頻率座標
- 中心 (0,0)：DC 分量（平均亮度）
- 距離中心越遠：頻率越高（細節、邊緣、噪聲）

**Magnitude Spectrum**：`|F(u,v)|`，取 log 可視化

---

## 2. 頻域濾波步驟

```
1. 計算 DFT：F = fft2(image)
2. Shift：fftshift(F) 把 DC 移到中心
3. 設計 Filter mask H(u,v)
4. 相乘：G = H · F
5. Shift back：ifftshift(G)
6. 逆 DFT：g = ifft2(G)，取實部
7. Clip 到 [0, 255]
```

---

## 3. 常用 Filter

### Low-pass Filter（低通）= 保留低頻 = 模糊

**Ideal LPF**：
```
H(u,v) = 1 if D(u,v) ≤ D0
         0 if D(u,v) > D0
```
- D(u,v) = 距中心的距離
- 問題：Ideal LPF 有 ringing artifact（Gibbs phenomenon）

**Gaussian LPF**（無 ringing）：
```
H(u,v) = exp(-D²(u,v) / 2D0²)
```

### High-pass Filter（高通）= 保留高頻 = 邊緣

```
H_HPF = 1 - H_LPF
```

### Band-pass Filter：保留特定頻率範圍

---

## 4. 頻域與空間域的對應

| 頻域 | 空間域等效 | 視覺效果 |
|------|-----------|----------|
| 低通 | Gaussian blur | 模糊 |
| 高通 | Sobel/Laplacian | 邊緣 |
| Band-pass | 帶通濾波器 | 特定紋理 |

---

## 5. 週期性噪聲消除（Realtek 相關）

TV 信號或 LCD 可能有**摩爾紋（Moiré pattern）**，在頻域是**特定頻率的亮點**。

做法：在頻譜上把那個亮點蓋掉（notch filter），再逆回空間域。

---

## 重點整理

- Convolution Theorem：空間卷積 = 頻域乘法
- Low-pass：去噪/模糊；High-pass：邊緣/銳化
- Ideal filter 有 ringing，Gaussian filter 無
- 週期性噪聲在頻域容易消除

---

## 延伸思考

1. 為什麼 Gaussian blur 在頻域是 Gaussian LPF？
2. Canny edge detection 的 Gaussian blur 在頻域的意義是什麼？
3. JPEG 壓縮用的 DCT 和 DFT 有什麼關係？
