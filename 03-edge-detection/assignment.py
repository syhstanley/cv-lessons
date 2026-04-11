"""
Assignment 03 — 邊緣偵測
=================================
目標：從頭實作 Sobel，理解 Canny pipeline

執行：python assignment.py
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
        # 生成幾何形狀測試圖
        img = np.zeros((256, 256), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 200, -1)
        cv2.circle(img, (190, 190), 40, 150, -1)
        return img


# ── Task 1：手動實作 Sobel ───────────────────────────────────────────────
def manual_sobel(img: np.ndarray):
    """
    TODO: 手動實作 Sobel edge detection
    返回 (Gx, Gy, magnitude, direction)
    """
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)

    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float32)

    # TODO: 用 cv2.filter2D 或 Lesson 02 的 manual_convolve2d 做卷積
    Gx = None  # TODO
    Gy = None  # TODO

    # TODO: 計算 magnitude 和 direction
    magnitude = None  # TODO: sqrt(Gx² + Gy²)，clip 到 0-255
    direction = None  # TODO: arctan2(Gy, Gx)，單位：degrees

    return Gx, Gy, magnitude, direction


def task1_sobel(img):
    print("=== Task 1: Sobel ===")

    # 先加一點 Gaussian blur 去噪
    img_blur = cv2.GaussianBlur(img, (3, 3), sigmaX=1)

    Gx, Gy, mag, direction = manual_sobel(img_blur)
    cv_sobel_x = cv2.Sobel(img_blur, cv2.CV_64F, 1, 0, ksize=3)
    cv_sobel_y = cv2.Sobel(img_blur, cv2.CV_64F, 0, 1, ksize=3)
    cv_mag = np.sqrt(cv_sobel_x**2 + cv_sobel_y**2)
    cv_mag = np.clip(cv_mag, 0, 255).astype(np.uint8)

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
    TODO: 實作 Canny 的 Non-Maximum Suppression
    - 把 gradient direction 量化到 4 個方向（0°, 45°, 90°, 135°）
    - 在每個方向上，只保留局部最大值的 pixel
    - 非最大值設為 0（邊緣細化）

    步驟：
    1. 把 direction 轉到 0-180°（角度對稱）
    2. 量化角度到最近的 45° 倍數
    3. 比較 pixel 和其方向上的兩個鄰居
    4. 如果不是最大值，設為 0
    """
    h, w = magnitude.shape
    result = np.zeros_like(magnitude)

    # TODO: 實作 NMS
    # angle = direction % 180
    # for i in range(1, h-1):
    #     for j in range(1, w-1):
    #         ...

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
    用 OpenCV Canny 測試不同閾值，觀察 hysteresis 效果
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

    # TODO（思考題）：
    # high threshold 越高 → 強邊緣越少，弱邊緣也不容易連上
    # 什麼場景適合低閾值？什麼場景需要高閾值？


# ── Task 4（Bonus）：用 Laplacian 做模糊偵測 ───────────────────────────
def task4_bonus_blur_detection(img):
    """
    Realtek Camera 的 Auto Focus 評估方法之一：
    計算圖片的 Laplacian variance，越高表示越清晰
    TODO: 對同一張圖做不同程度的 blur，計算各自的 Laplacian variance
    並畫出 blur sigma vs sharpness score 的曲線
    """
    print("=== Task 4 (Bonus): 模糊偵測 ===")

    sigmas = [0, 1, 2, 4, 8, 16]
    scores = []

    for sigma in sigmas:
        if sigma == 0:
            blurred = img
        else:
            blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)
        # TODO: 計算 Laplacian variance
        lap = cv2.Laplacian(blurred, cv2.CV_64F)
        score = None  # TODO: lap.var()

    # TODO: 畫出 sigma vs score 曲線
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
