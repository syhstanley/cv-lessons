"""
Assignment 03 — 邊緣偵測
=================================
目標：從頭實作 Sobel，理解 Canny pipeline

執行：python assignment.py

📐 公式推導參考（../formula_prove.md）：
    P11 — Sobel Gradient Direction 的幾何意義  → Task 1
    P10 — Laplacian Variance 作為清晰度指標    → Task 4
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def load_or_generate_image():
    test_path = "test.jpg"
    if os.path.exists(test_path):
        return cv2.imread(test_path, cv2.IMREAD_GRAYSCALE)
    else:
        img = np.zeros((256, 256), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 200, -1)
        cv2.circle(img, (190, 190), 40, 150, -1)
        return img


# ── Task 1：手動實作 Sobel ───────────────────────────────────────────────
def manual_sobel(img: np.ndarray):
    """
    手動實作 Sobel edge detection，返回 (Gx, Gy, magnitude, direction)。

    公式：
        Gx = Kx ⊛ I    （水平方向卷積，偵測垂直邊緣）
        Gy = Ky ⊛ I    （垂直方向卷積，偵測水平邊緣）

        Magnitude = sqrt(Gx² + Gy²)
        Direction = arctan2(Gy, Gx)   單位：degrees，範圍 -180 ~ 180

    步驟：
    1. 定義水平和垂直的 Sobel kernel（已提供）
    2. 對影像分別做卷積，得到 Gx 和 Gy（可用 cv2.filter2D）
    3. 計算 Magnitude，clip 到 0-255 後轉 uint8
    4. 計算 Direction，用 np.degrees(np.arctan2(...)) 轉成角度

    📐 Gradient Direction 為何代表邊緣法向量，見 ../formula_prove.md P11
    """
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)

    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float32)

    Gx = None  # TODO
    Gy = None  # TODO
    magnitude = None  # TODO
    direction = None  # TODO

    return Gx, Gy, magnitude, direction


def task1_sobel(img):
    print("=== Task 1: Sobel ===")

    img_blur = cv2.GaussianBlur(img, (3, 3), sigmaX=1)
    Gx, Gy, mag, direction = manual_sobel(img_blur)

    cv_sobel_x = cv2.Sobel(img_blur, cv2.CV_64F, 1, 0, ksize=3)
    cv_sobel_y = cv2.Sobel(img_blur, cv2.CV_64F, 0, 1, ksize=3)
    cv_mag = np.clip(np.sqrt(cv_sobel_x**2 + cv_sobel_y**2), 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    data = [
        (img, "Original"),
        (Gx, "Gx (manual)") if Gx is not None else (np.zeros_like(img), "Gx (TODO)"),
        (Gy, "Gy (manual)") if Gy is not None else (np.zeros_like(img), "Gy (TODO)"),
        (mag, "Magnitude (manual)") if mag is not None else (np.zeros_like(img), "Magnitude (TODO)"),
        (cv_mag, "Magnitude (OpenCV)"),
        (direction, "Direction") if direction is not None else (np.zeros_like(img), "Direction (TODO)"),
    ]
    for ax, (im, title) in zip(axes.flat, data):
        if im is not None and im.ndim == 2:
            ax.imshow(np.abs(im) if im.dtype == np.float32 else im, cmap='gray')
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task1_sobel.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_sobel.png")

    return mag, direction


# ── Task 2：Non-Maximum Suppression ─────────────────────────────────────
def non_maximum_suppression(magnitude: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """
    實作 Canny 的 Non-Maximum Suppression（邊緣細化）。

    角度量化規則（angle = direction % 180）：

        angle ∈ [0°, 22.5°) ∪ [157.5°, 180°]  → 水平，比較 (i, j-1) 和 (i, j+1)
        angle ∈ [22.5°, 67.5°)                 → 45°，比較 (i+1, j-1) 和 (i-1, j+1)
        angle ∈ [67.5°, 112.5°)                → 垂直，比較 (i-1, j) 和 (i+1, j)
        angle ∈ [112.5°, 157.5°)               → 135°，比較 (i-1, j-1) 和 (i+1, j+1)

    判斷條件：
        if magnitude(i,j) >= neighbor1 AND magnitude(i,j) >= neighbor2:
            result(i,j) = magnitude(i,j)   # 是局部最大值，保留
        else:
            result(i,j) = 0                # 非最大值，抑制

    步驟：
    1. 把 direction 轉到 0-180° 範圍（direction % 180）
    2. 雙層迴圈遍歷每個非邊界 pixel（跳過第 0 行/列和最後行/列）
    3. 根據角度查表選鄰居，比較大小決定是否保留
    """
    h, w = magnitude.shape
    result = np.zeros_like(magnitude)

    # TODO: 實作上述邏輯

    return result


def task2_nms(mag, direction):
    print("=== Task 2: Non-Maximum Suppression ===")

    if mag is None or direction is None:
        print("  → 需要先完成 Task 1")
        return None

    mag_norm = np.clip(mag, 0, 255).astype(np.uint8) if mag.max() > 1 else mag
    nms_result = non_maximum_suppression(mag_norm.astype(np.float32), direction)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(mag_norm, cmap='gray')
    axes[0].set_title("Magnitude (before NMS)")
    axes[1].imshow(nms_result, cmap='gray')
    axes[1].set_title("After NMS (edges thinned)")
    for ax in axes:
        ax.axis('off')
    plt.savefig("output/task2_nms.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_nms.png")

    return nms_result


# ── Task 3：Double Threshold + Hysteresis ────────────────────────────────
def task3_canny_full(img):
    """
    用 OpenCV Canny 測試不同閾值組合，觀察 hysteresis 效果。
    先對影像做 Gaussian blur（5×5，sigma=1.4）去噪，
    再用三組不同的 low/high threshold 跑 Canny，
    比較邊緣數量和品質的差異。

    思考：high threshold 越高時，強邊緣和弱邊緣分別有什麼變化？
    """
    print("=== Task 3: Canny（閾值比較）===")

    img_blur = cv2.GaussianBlur(img, (5, 5), sigmaX=1.4)

    configs = [
        (10, 30, "low=10, high=30"),
        (50, 150, "low=50, high=150"),
        (100, 200, "low=100, high=200"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title("Original")
    axes[0].axis('off')

    for ax, (lo, hi, title) in zip(axes[1:], configs):
        edges = cv2.Canny(img_blur, lo, hi)
        ax.imshow(edges, cmap='gray')
        ax.set_title(title)
        ax.axis('off')

    plt.savefig("output/task3_canny.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_canny.png")


# ── Task 4（Bonus）：用 Laplacian 做模糊偵測 ───────────────────────────
def task4_bonus_blur_detection(img):
    """
    Realtek Camera Auto Focus 的評估方法：
    用 Laplacian variance 衡量影像的清晰度（越高 = 越清晰）。

    公式：
        Sharpness Score = Var(∇²I)
                       = Var(Laplacian(I))

        其中 Var 是 variance（方差），越高表示圖片邊緣越多、越清晰。

    步驟：
    1. 對同一張圖用不同 sigma（0, 1, 2, 4, 8, 16）做 Gaussian blur
    2. 對每個模糊版本用 cv2.Laplacian 計算拉普拉斯，再取 .var()
    3. 畫出 sigma vs sharpness score 的折線圖並存檔
    4. 觀察：score 如何隨模糊程度單調遞減？

    📐 為什麼 Laplacian Variance 能衡量清晰度，見 ../formula_prove.md P10
    """
    print("=== Task 4 (Bonus): 模糊偵測 ===")

    sigmas = [0, 1, 2, 4, 8, 16]
    scores = []

    for sigma in sigmas:
        blurred = img if sigma == 0 else cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)
        lap = cv2.Laplacian(blurred, cv2.CV_64F)
        score = None  # TODO: 計算 Laplacian 的 variance
        scores.append(score)

    # TODO: 用 matplotlib 畫出 sigma vs score 的折線圖並存檔
    print("  → TODO: 完成模糊程度 vs Laplacian variance 曲線")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img = load_or_generate_image()
    print(f"圖片尺寸：{img.shape}")

    mag, direction = task1_sobel(img)
    nms = task2_nms(mag, direction)
    task3_canny_full(img)
    task4_bonus_blur_detection(img)

    print("\n完成！查看 output/ 資料夾。")
