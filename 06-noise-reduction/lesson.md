# Lesson 06 — Noise Reduction（NR）

## Realtek 的 NR 在哪裡用？

- **Camera SoC**：低光環境噪聲很重
- **TV SoC**：廣播訊號傳輸帶來的噪聲
- **Monitor**：HDMI 訊號品質問題

NR 是 Realtek ISP 和 TV pipeline 的核心模組，分三類：

---

## 1. Spatial NR（空間域降噪）

在單一 frame 內做，利用空間鄰域。

### 代表：Bilateral Filter（已在 Lesson 02 學過）

**Non-Local Means（NLM）**：更強的空間 NR
- 不只看鄰近像素，看整張圖中**相似的 patch**
- 相似 patch 的加權平均
- 計算量大，通常用近似版本（如 BM3D）

```
NLM(x) = Σ w(x, y) · I(y) / Σ w(x, y)
where w(x, y) = exp(-‖P(x) - P(y)‖² / h²)
```
P(x) = x 為中心的 patch，h = 濾波強度

---

## 2. Temporal NR（時域降噪）

利用**多個 frame** 的時間關聯性去噪。

### 核心思想
靜態背景在不同 frame 中值應該相同，差異是噪聲：

```
Output(t) = α · Input(t) + (1-α) · Output(t-1)
```
- α ≈ 0.3~0.5（小 α → 強降噪 but 動態物體拖影）
- 這就是 **IIR Temporal Filter**（無限衝激響應）

### 問題：Motion Ghost（拖影）

移動的物體前後 frame 位置不同，直接混合會產生殘影。

**解法：Motion-Adaptive Temporal NR**
```
if motion_detected(x, y):
    α = 1.0  （不混合，用當前 frame）
else:
    α = 0.3  （強混合，充分降噪）
```

Motion detection 通常用 frame difference：
```
diff(x,y) = |I(t)(x,y) - I(t-1)(x,y)|
if diff > threshold → motion
```

---

## 3. 3D NR = Spatial + Temporal

同時在空間域和時域做 NR，效果最好：

1. 先做 Temporal NR（跨 frame）
2. 再做 Spatial NR（單 frame 內）

Realtek TV SoC 的 NR 就是 3D NR。

---

## 4. 噪聲模型

| 噪聲類型 | 來源 | 對應 Filter |
|----------|------|------------|
| Gaussian noise | Thermal noise（相機電路） | Gaussian / Bilateral |
| Salt-and-pepper | Sensor 壞點 | Median |
| Periodic noise | 電磁干擾 | Notch filter（頻域） |
| Fixed pattern noise | Sensor 一致性差異 | PRNU calibration |

---

## 重點整理

- **Spatial NR**：Bilateral、NLM — 單 frame，保邊
- **Temporal NR**：IIR 混合 — 多 frame，需 motion detection
- **3D NR**：兩者結合
- Motion-Adaptive 是 Temporal NR 的關鍵

---

## 面試常問

> Q：Temporal NR 在移動物體上為什麼會有拖影？如何解決？

A：因為移動物體前後 frame 位置不同，混合後形成殘影。
解法：用 frame difference 做 motion detection，移動區域不做時域混合（α→1）。
