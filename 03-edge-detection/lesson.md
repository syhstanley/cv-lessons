# Lesson 03 — 邊緣偵測（Edge Detection）

## 什麼是邊緣？

邊緣 = 像素值**急劇變化**的地方 = 一階導數的極值 = 二階導數的零交叉

---

## 1. 一階導數：Gradient-based

### Sobel Operator

水平方向（偵測垂直邊緣）：
```
-1  0  +1
-2  0  +2
-1  0  +1
```

垂直方向（偵測水平邊緣）：
```
-1  -2  -1
 0   0   0
+1  +2  +1
```

Gradient magnitude：
```
G = sqrt(Gx² + Gy²)  （或近似為 |Gx| + |Gy|）
```

Gradient direction：
```
θ = arctan(Gy / Gx)
```

### Prewitt Operator
與 Sobel 類似，但係數不同（無加權中心）：
```
-1  0  +1      -1  -1  -1
-1  0  +1  ,    0   0   0
-1  0  +1      +1  +1  +1
```

---

## 2. 二階導數：Laplacian

```
 0  -1   0
-1  +4  -1
 0  -1   0
```

- 對噪聲更敏感
- 各向同性（無方向性）
- 輸出正負兩側的響應，零交叉處是邊緣

**LoG（Laplacian of Gaussian）**：先用 Gaussian 平滑再做 Laplacian，抑制噪聲

---

## 3. Canny Edge Detector

**業界最常用的邊緣偵測器**，是 multi-step pipeline：

```
1. Gaussian Blur      → 去噪
2. Sobel Gradient     → 計算方向與強度
3. Non-Maximum Suppression (NMS) → 細化邊緣（只保留局部最大值）
4. Double Threshold   → 強邊緣 / 弱邊緣 分類
5. Edge Tracking (Hysteresis) → 弱邊緣若連接強邊緣就保留
```

Canny 的優勢：
- 邊緣細（1 pixel 寬）
- 抗噪
- 可控參數少（只有 low_threshold, high_threshold）

---

## Realtek 相關應用

| 技術 | 應用場景 |
|------|----------|
| Sobel | Monitor 畫質增強（邊緣銳化基礎） |
| Canny | Camera Auto Focus 評估（對焦度 = 邊緣強度） |
| LoG | 影像品質評估（模糊偵測） |
| Gradient direction | Deinterlacing（判斷邊緣方向做內插） |

---

## 重點整理

- Sobel：有方向性，計算 Gradient
- Laplacian：各向同性，對噪聲敏感
- Canny：最實用，multi-step pipeline
- 記住 NMS 和 Hysteresis 是 Canny 的精髓
