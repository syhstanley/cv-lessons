# Lesson 07 — 影像銳化與畫質增強

## Realtek 的應用場景

- **Monitor**：顯示卡輸出需要銳化讓字體/細節更清晰
- **TV**：廣播訊號壓縮後模糊，需要銳化補償
- **Camera**：照片/影片的最後一道銳化處理

---

## 1. Unsharp Masking（USM）

**最常用的銳化方法**，名字聽起來很反直覺。

原理：
```
Sharpened = Original + amount × (Original - Blurred)
```

`(Original - Blurred)` = **高頻部分（細節）**

步驟：
1. 對原圖做 Gaussian blur
2. 計算差值（High Frequency）
3. 加回原圖（放大高頻）

可調參數：
- **Radius**：Gaussian blur 的 σ（影響什麼尺度的細節被銳化）
- **Amount**：高頻放大倍數（過大會產生 halo）
- **Threshold**：差值低於此值不做銳化（保留平坦區域）

---

## 2. Laplacian Sharpening

```
Sharpened = Original - k × Laplacian(Original)
```

- Laplacian 是二階導數，在邊緣有強響應
- 減去 Laplacian → 放大邊緣

Laplacian kernel：
```
 0  -1   0
-1   5  -1
 0  -1   0
```
（這個 kernel 一步完成 "Original - Laplacian"）

---

## 3. Histogram Equalization（對比度增強）

把灰度直方圖「拉平」，讓暗部細節更清楚。

步驟：
1. 計算 CDF（累積分佈函數）
2. 用 CDF 做灰度映射

```
output(x) = round(CDF(input(x)) × (L-1))
```
L = 灰度層數（通常 256）

### CLAHE（Contrast Limited AHE）

- 針對局部區域（tile）做 Histogram EQ
- 限制對比度放大倍率（避免過度增強噪聲）
- **Realtek Monitor 的 CABC（Content Adaptive Brightness Control）類似原理**

---

## 4. 銳化的陷阱：Ringing / Halo

過度銳化會在邊緣產生亮/暗的光暈（halo artifact），常見於：
- USM amount 太大
- Laplacian sharpening 係數太大
- JPEG 過度壓縮後的邊緣

解法：
- 限制銳化強度
- 只在邊緣區域銳化（edge-adaptive sharpening）
- 加 threshold，平坦區域不銳化

---

## 重點整理

| 方法 | 公式 | 特點 |
|------|------|------|
| USM | I + a×(I - blur(I)) | 最常用，可調參數多 |
| Laplacian | I - k×L(I) | 簡單快速 |
| Hist EQ | CDF 映射 | 對比度增強 |
| CLAHE | 局部 Hist EQ | 抑制噪聲放大 |
