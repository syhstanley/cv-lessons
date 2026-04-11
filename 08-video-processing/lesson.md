# Lesson 08 — Video 特有處理

## 1. Deinterlacing（去交錯）

### 什麼是 Interlaced？

傳統 TV 廣播（SD/HD broadcast）使用 **Interlaced scanning**：
- 每個 frame 分成奇數行（odd field）和偶數行（even field）
- 兩個 field 時間差半個 frame（1/60 秒 for NTSC）

```
Field 1（奇數行）：  行 1, 3, 5, 7, ...
Field 2（偶數行）：  行 2, 4, 6, 8, ...
```

現代顯示器都是 **Progressive**（每次顯示完整 frame），所以需要 Deinterlacing。

---

### Deinterlacing 方法

**① Bob（Line Doubling）**
- 最簡單：把缺少的行複製上面/下面的行
- 或用線性插值（上下行平均）
- 問題：移動物體會模糊

**② Weave（Field Merging）**
- 直接把兩個 field 合併
- 靜態場景沒問題，移動物體有 comb artifact（梳子狀）

**③ Motion-Adaptive Deinterlacing（Realtek 用的）**
- 靜態區域：Weave（保留解析度）
- 動態區域：Bob（避免 artifact）
- Motion detection 同 Lesson 06

**④ Edge-based Bob（ELA — Edge-based Line Average）**
- 沿邊緣方向插值（不是垂直插值）
- 斜線邊緣不會鋸齒

```
ELA：找最匹配的方向 d，用 (line[n-1][x-d] + line[n+1][x+d]) / 2
```

---

## 2. Interpolation（插值）in Video

### Frame Interpolation（幀插值）
- 電影 24fps → 電視 60fps，需要插入中間幀
- 最簡單：copy 前一幀
- 更好：Motion Compensation（根據運動向量做 blend）

### Scaling Interpolation
影像縮放時需要插值：

| 方法 | 品質 | 速度 |
|------|------|------|
| Nearest Neighbor | 最差（鋸齒） | 最快 |
| Bilinear | 中等 | 快 |
| Bicubic | 好 | 中 |
| Lanczos | 最好 | 慢 |

Realtek TV SoC 做 scaling 用 **Polyphase filter**（多相濾波器），品質接近 Lanczos。

---

## 3. Motion Estimation / Compensation

### 什麼是 Motion Vector（MV）？
```
frame(t) 的 block(x, y) 的內容
在 frame(t-1) 的 (x+mvx, y+mvy) 位置
```

### Block Matching
最常用的 ME 方法：
1. 把當前 frame 切成 N×N block（如 16×16）
2. 在前一 frame 搜尋最相似的位置（最小化 SAD）
3. 相似位置的偏移就是 Motion Vector

**SAD（Sum of Absolute Differences）**：
```
SAD(dx, dy) = Σ |B_curr(x,y) - B_prev(x+dx, y+dy)|
```

### 用途
- H.264/HEVC 壓縮（減少時間冗餘）
- Frame rate conversion
- Deinterlacing

---

## 重點整理

| 技術 | 應用 |
|------|------|
| Deinterlacing | 廣播訊號顯示 |
| Motion-Adaptive | 動靜態區域分別處理 |
| Scaling（Bicubic/Lanczos） | 解析度轉換 |
| Motion Estimation | 壓縮、幀插值 |

---

## 面試常問

> Q：Deinterlacing 的 comb artifact 是什麼？如何避免？

A：Weave 方法把兩個 field 合併時，移動物體因前後 field 有時間差，水平邊緣會出現梳子狀條紋。
解法：對移動區域改用 Bob 插值，靜態區域用 Weave。
