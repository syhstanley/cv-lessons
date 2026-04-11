# Lesson 01 — 色彩空間轉換（Color Space Conversion）

## 為什麼重要？

Realtek 的 Camera/TV SoC 輸入的影像格式不一定是 RGB。
- Camera sensor 輸出通常是 **YUV**（or YCbCr）
- Display pipeline 用 **YUV** 傳輸（HDMI、MIPI 都是）
- 壓縮（JPEG、H.264）也是在 YUV 空間做

你若不懂色彩空間，就看不懂硬體 datasheet。

---

## 1. RGB

- 最直觀，三個 channel：R、G、B
- 每個 pixel 用 3 bytes（24-bit color）
- **缺點**：人眼對亮度（Luma）比色彩（Chroma）敏感，RGB 無法分開

---

## 2. YUV / YCbCr

**業界最重要的色彩空間**，TV / Camera 都用這個。

| 符號 | 意義 |
|------|------|
| Y | Luma（亮度） |
| U (Cb) | 藍色色差 |
| V (Cr) | 紅色色差 |

### 轉換公式（BT.601）

```
Y  =  0.299R + 0.587G + 0.114B
U  = -0.147R - 0.289G + 0.436B
V  =  0.615R - 0.515G - 0.100B
```

### 為什麼有用？
- Y 單獨就是灰階圖，可以單獨處理亮度
- **Chroma Subsampling**：人眼對色彩解析度要求低，可以壓縮 U/V
  - 4:4:4 → 每個 pixel 都有 YUV（無壓縮）
  - 4:2:2 → U/V 水平減半（HDMI 常用）
  - 4:2:0 → U/V 水平垂直都減半（H.264 / JPEG 用）

---

## 3. HSV

| 符號 | 意義 |
|------|------|
| H | Hue（色相，0-360°） |
| S | Saturation（飽和度） |
| V | Value（亮度） |

- 適合做「顏色過濾」（例：找圖中所有紅色物體）
- 比 RGB 更接近人類直覺

---

## 4. Bayer Pattern（Camera 特有）

Camera sensor 不是直接輸出 RGB，而是 **Bayer Pattern（RGGB）**：

```
R G R G R G
G B G B G B
R G R G R G
G B G B G B
```

- 每個 pixel 只有一種顏色
- 需要 **Demosaicing** 演算法還原完整 RGB（下一課 ISP 細講）

---

## 重點整理

- RGB ↔ YUV：Display、Camera pipeline 必備
- YUV Subsampling：影響頻寬、壓縮率
- HSV：顏色操作、過濾
- Bayer：Camera raw data 格式

---

## 參考

- OpenCV `cv2.cvtColor()` 支援所有轉換
- BT.601（SD）vs BT.709（HD）轉換係數不同！
