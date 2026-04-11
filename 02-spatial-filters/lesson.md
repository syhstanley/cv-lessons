# Lesson 02 — 空間域濾波器（Spatial Filters）

## 核心概念：Convolution（卷積）

所有空間域濾波器的本質都是 **2D 卷積**：

```
Output(x,y) = Σ Σ Kernel(i,j) × Input(x+i, y+j)
```

Kernel（又叫 filter / mask）決定濾波效果。
這也是 CNN 的基礎——你已經知道反向傳播，但先搞懂手工 kernel 很重要。

---

## 1. Gaussian Blur（高斯模糊）

**用途**：降噪、pre-processing 前的平滑、邊緣偵測前置

Kernel 來自 2D Gaussian 函數：

```
G(x,y) = (1/2πσ²) * exp(-(x²+y²) / 2σ²)
```

3x3 Gaussian kernel（σ≈1）：

```
1  2  1
2  4  2  × (1/16)
1  2  1
```

- σ 越大 → 模糊越強
- **Separable filter**：可以拆成水平 × 垂直，加速運算（Realtek 硬體實作常這樣做）

---

## 2. Median Filter（中值濾波）

**用途**：去除 salt-and-pepper noise（Camera sensor 常見的隨機壞點）

做法：取 neighborhood 內所有 pixel 的中值

```
[10, 20, 255, 15, 12, 8, 200, 11, 9]
排序後 → 中值 = 12  （255 和 200 被排除）
```

- **非線性**濾波器（無法用卷積表示）
- 保邊效果比 Gaussian 好
- 對 impulse noise 特別有效

---

## 3. Bilateral Filter（雙邊濾波）

**Realtek TV/Monitor 畫質增強最愛用的濾波器**

問題：Gaussian blur 在去噪的同時也模糊了邊緣。

解法：Bilateral = Gaussian（空間距離）× Gaussian（像素值差異）

```
W(i,j) = exp(-‖p-q‖² / 2σ_s²) × exp(-|I(p)-I(q)|² / 2σ_r²)
```

| 參數 | 意義 |
|------|------|
| σ_s | 空間域 sigma（控制影響範圍） |
| σ_r | 值域 sigma（控制顏色差異敏感度） |

- 邊緣兩側 pixel 差異大 → 權重小 → **邊緣保留**
- 平坦區域 pixel 差異小 → 正常平滑

**缺點**：計算量大，硬體要做近似（Realtek 用 guided filter 等近似版本）

---

## 4. 邊界處理（Padding）

做卷積時，邊緣 pixel 怎麼處理？

| 方式 | 說明 |
|------|------|
| Zero padding | 補 0，最簡單 |
| Replicate | 複製邊緣 pixel |
| Reflect | 鏡像翻轉 |
| Wrap | 循環（圖塊拼接） |

Camera ISP 通常用 **Replicate**。

---

## 重點整理

| Filter | 特性 | Realtek 應用 |
|--------|------|-------------|
| Gaussian | 線性、平滑 | Pre-processing |
| Median | 非線性、保邊 | Camera 去壞點 |
| Bilateral | 保邊去噪 | TV 畫質增強 |

---

## 延伸思考

1. Gaussian kernel 的 σ 怎麼影響 frequency response？（想想低通濾波器）
2. 為什麼 Median filter 對 Gaussian noise 效果差？
3. Bilateral filter 為什麼在 HDR 場景會有 halo artifact？
