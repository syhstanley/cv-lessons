# P12 — Gray World 白平衡假設

關聯 Lesson：**L04 ISP Pipeline（Task 2）**

---

## 假設

一張自然場景的圖片，所有像素在 R、G、B 三個 channel 的平均值應該相等（即整體偏灰）：

$$
\bar{R} = \bar{G} = \bar{B}
$$

## 現實情況

在偏黃光源下（如室內燈）：$\bar{R} > \bar{G} > \bar{B}$

## 校正

讓各 channel 的平均值等於三者平均：

$$
\bar{\mu} = \frac{\bar{R} + \bar{G} + \bar{B}}{3}
$$

$$
\text{gain}_R = \frac{\bar{\mu}}{\bar{R}}, \quad \text{gain}_G = 1.0, \quad \text{gain}_B = \frac{\bar{\mu}}{\bar{B}}
$$

$$
R'(x,y) = \text{clip}(R(x,y) \cdot \text{gain}_R, \; 0, 255)
$$

## 限制

Gray World 假設在以下情況失效：
- 圖片以單一顏色為主（例如一整片草地）
- 人造場景（展覽、廣告牌）
- 日落/日出等極端光源

實際相機的 AWB 算法通常結合 Gray World、白點偵測和機器學習模型。

---

← [P11 Sobel Gradient](P11-sobel-gradient.md) ｜ [回目錄](../formula_prove.md)
