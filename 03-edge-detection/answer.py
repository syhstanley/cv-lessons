"""
Answer 03 — 邊緣偵測
=================================
執行：python answer.py
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
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)

    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float32)

    # cv2.filter2D 做卷積（注意：filter2D 做的是 correlation，Sobel kernel 對稱所以等效）
    Gx = cv2.filter2D(img.astype(np.float32), -1, Kx)
    Gy = cv2.filter2D(img.astype(np.float32), -1, Ky)

    magnitude = np.sqrt(Gx**2 + Gy**2)
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)

    direction = np.degrees(np.arctan2(Gy, Gx))  # -180 ~ 180 degrees

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
        (np.abs(Gx).astype(np.uint8), "Gx (manual)"),
        (np.abs(Gy).astype(np.uint8), "Gy (manual)"),
        (mag, "Magnitude (manual)"),
        (cv_mag, "Magnitude (OpenCV)"),
        (((direction + 180) / 360 * 255).astype(np.uint8), "Direction (color-coded)"),
    ]
    for ax, (im, title) in zip(axes.flat, data):
        ax.imshow(im, cmap='gray')
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task1_sobel.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_sobel.png")

    return mag, direction


# ── Task 2：Non-Maximum Suppression ─────────────────────────────────────
def non_maximum_suppression(magnitude: np.ndarray, direction: np.ndarray) -> np.ndarray:
    h, w = magnitude.shape
    result = np.zeros_like(magnitude)
    angle = direction % 180  # 0 ~ 180

    for i in range(1, h - 1):
        for j in range(1, w - 1):
            a = angle[i, j]

            # 量化到 4 個方向
            if (0 <= a < 22.5) or (157.5 <= a <= 180):
                # 水平方向（左右鄰居）
                p, q = magnitude[i, j-1], magnitude[i, j+1]
            elif 22.5 <= a < 67.5:
                # 斜 45° 方向
                p, q = magnitude[i+1, j-1], magnitude[i-1, j+1]
            elif 67.5 <= a < 112.5:
                # 垂直方向（上下鄰居）
                p, q = magnitude[i-1, j], magnitude[i+1, j]
            else:
                # 斜 135° 方向
                p, q = magnitude[i-1, j-1], magnitude[i+1, j+1]

            # 只保留局部最大值
            if magnitude[i, j] >= p and magnitude[i, j] >= q:
                result[i, j] = magnitude[i, j]

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
    # 低閾值適合：圖案簡單、對比明確；高閾值適合：複雜紋理、只要強邊緣


# ── Task 4（Bonus）：用 Laplacian 做模糊偵測 ───────────────────────────
def task4_bonus_blur_detection(img):
    print("=== Task 4 (Bonus): 模糊偵測 ===")

    sigmas = [0, 1, 2, 4, 8, 16]
    scores = []

    for sigma in sigmas:
        blurred = img if sigma == 0 else cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)
        lap = cv2.Laplacian(blurred, cv2.CV_64F)
        scores.append(lap.var())

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(sigmas, scores, 'o-', color='steelblue')
    axes[0].set_xlabel("Blur sigma")
    axes[0].set_ylabel("Laplacian Variance (Sharpness Score)")
    axes[0].set_title("Sharpness vs Blur Level")
    axes[0].grid(True)

    # 視覺化不同模糊程度
    sample_sigmas = [0, 2, 8]
    for i, s in enumerate(sample_sigmas):
        blurred = img if s == 0 else cv2.GaussianBlur(img, (0, 0), sigmaX=s)

    axes[1].bar([str(s) for s in sigmas], scores, color='steelblue')
    axes[1].set_xlabel("Blur sigma")
    axes[1].set_ylabel("Sharpness Score")
    axes[1].set_title("Bar Chart: Sharpness Score")

    plt.savefig("output/task4_blur_detection.png", dpi=120, bbox_inches='tight')
    plt.close()
    print(f"  sigma=0 score: {scores[0]:.1f}, sigma=16 score: {scores[-1]:.1f}")
    print("  → output/task4_blur_detection.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img = load_or_generate_image()
    print(f"圖片尺寸：{img.shape}")

    mag, direction = task1_sobel(img)
    nms = task2_nms(mag, direction)
    task3_canny_full(img)
    task4_bonus_blur_detection(img)

    print("\n完成！查看 output/ 資料夾。")
