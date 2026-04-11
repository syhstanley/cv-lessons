# Lesson 04 — ISP Pipeline（Image Signal Processing）

## 什麼是 ISP？

Camera sensor 拍出來的 raw data 不能直接顯示，要經過一連串的處理才能變成人眼能看的彩色圖片。這個處理流程就是 **ISP Pipeline**。

Realtek 的 Camera SoC 裡有硬體 ISP，這是 Camera 部門的核心技術。

---

## 完整 ISP Pipeline

```
Sensor Raw (Bayer)
    │
    ▼
① Black Level Correction (BLC)
    │
    ▼
② Lens Shading Correction (LSC)
    │
    ▼
③ Bad Pixel Correction (BPC)
    │
    ▼
④ Demosaicing (Bayer → RGB)        ← 最關鍵
    │
    ▼
⑤ White Balance (AWB)
    │
    ▼
⑥ Color Correction Matrix (CCM)
    │
    ▼
⑦ Gamma Correction
    │
    ▼
⑧ Color Space Conversion (RGB → YUV)
    │
    ▼
⑨ Noise Reduction（見 Lesson 06）
    │
    ▼
⑩ Edge Enhancement / Sharpening（見 Lesson 07）
    │
    ▼
Output（YUV / JPEG / H.264）
```

---

## 各步驟詳解

### ① Black Level Correction（BLC）

Sensor 在完全黑暗時仍有輸出（dark current），需要減掉：
```
corrected = raw - black_level
```
black_level 通常是 sensor 規格表的固定值（例：64 for 10-bit sensor）

---

### ② Lens Shading Correction（LSC）

鏡頭邊緣比中心暗（Vignetting），需要補償：
- 中心增益 = 1.0
- 邊緣增益 = 1.x（根據校正表）

---

### ③ Bad Pixel Correction（BPC）

Camera sensor 有壞點（stuck pixel / hot pixel），用周圍像素插值取代。
- 類似 Lesson 02 的 Median Filter，但只針對確定的壞點座標

---

### ④ Demosaicing（最重要）

Camera sensor 的 Bayer Pattern：
```
R G R G
G B G B
R G R G
```

每個 pixel 只有 1 個顏色，需要**插值**出其他 2 個顏色。

**Bilinear Demosaicing**（最簡單）：
- 用周圍同色 pixel 的平均值補全
- 例：G pixel 位置的 R 值 = 上下左右 R 的平均

**問題**：Bilinear 在邊緣會產生顏色偽影（color fringing）

**改進方法**：
- **AAAHD**（Adaptive Homogeneity-Directed）
- **Edge-based interpolation**：沿邊緣方向插值
- 現代方法：CNN demosaicing（你就懂了）

---

### ⑤ White Balance（AWB）

不同光源的色溫不同（陽光 5500K、室內燈 2700K），需要校正讓白色看起來是白的。

**Gray World 假設**：圖片中所有像素平均應該是灰色
```
R_gain = mean(all) / mean(R)
G_gain = 1.0  （G 作為基準）
B_gain = mean(all) / mean(B)
```

---

### ⑥ Color Correction Matrix（CCM）

補償 sensor 的色彩偏差，用 3×3 矩陣：
```
[R']     [a11 a12 a13] [R]
[G']  =  [a21 a22 a23] [G]
[B']     [a31 a32 a33] [B]
```
係數由 sensor 廠商標定（ColorChecker 測試卡校正）

---

### ⑦ Gamma Correction

人眼對亮度的感知是非線性的（對暗部更敏感）。

```
output = input^(1/gamma)    （通常 gamma = 2.2）
```

- **Encoding gamma**（sRGB / BT.709）：線性光 → 非線性編碼
- **Decoding gamma**：非線性編碼 → 線性光（顯示器做這個）

---

## 重點整理

| 步驟 | 關鍵技術 |
|------|----------|
| Demosaicing | Bilinear / Edge-based 插值 |
| White Balance | Gray World / 色溫估計 |
| Gamma | 冪次函數，gamma=2.2 |
| CCM | 3×3 矩陣乘法 |

面試最常問：**Demosaicing 的原理** 和 **Gamma 的意義**
