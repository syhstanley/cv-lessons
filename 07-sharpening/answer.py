"""
Answer 07 — 影像銳化與畫質增強
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
        cv2.rectangle(img, (40, 40), (180, 180), 180, -1)
        cv2.circle(img, (128, 128), 50, 100, -1)
        for i in range(20, 240, 10):
            img[i, 20:240] = np.clip(img[i, 20:240].astype(int) + 40, 0, 255)
        return img.astype(np.uint8)


def simulate_blur(img, sigma=2.0):
    return cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)


# ── Task 1：Unsharp Masking ──────────────────────────────────────────────
def unsharp_masking(img: np.ndarray, radius: float, amount: float,
                    threshold: int = 0) -> np.ndarray:
    blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=radius)
    img_f = img.astype(np.float32)
    blurred_f = blurred.astype(np.float32)

    high_freq = img_f - blurred_f

    if threshold > 0:
        high_freq[np.abs(high_freq) < threshold] = 0

    result = img_f + amount * high_freq
    return np.clip(result, 0, 255).astype(np.uint8)


def task1_usm(img_blur):
    print("=== Task 1: Unsharp Masking ===")

    configs = [
        (1.0, 1.0, 0, "radius=1, amount=1"),
        (2.0, 1.5, 0, "radius=2, amount=1.5"),
        (2.0, 2.5, 0, "radius=2, amount=2.5\n（過度銳化，注意 halo）"),
        (2.0, 1.5, 15, "radius=2, amount=1.5\nthreshold=15"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes.flat[0].imshow(img_blur, cmap='gray', vmin=0, vmax=255)
    axes.flat[0].set_title("Input (blurred)")
    axes.flat[0].axis('off')

    for ax, (r, a, t, title) in zip(axes.flat[1:], configs):
        result = unsharp_masking(img_blur, radius=r, amount=a, threshold=t)
        ax.imshow(result, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=9)
        ax.axis('off')

    plt.savefig("output/task1_usm.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_usm.png")


# ── Task 2：Laplacian Sharpening ─────────────────────────────────────────
def laplacian_sharpening(img: np.ndarray, k: float = 1.0) -> np.ndarray:
    lap = cv2.Laplacian(img, cv2.CV_64F, ksize=3)
    result = img.astype(np.float64) - k * lap
    return np.clip(result, 0, 255).astype(np.uint8)


def task2_laplacian(img_blur):
    print("=== Task 2: Laplacian Sharpening ===")

    results = {
        "Blurred Input": img_blur,
        "k=0.5": laplacian_sharpening(img_blur, k=0.5),
        "k=1.0": laplacian_sharpening(img_blur, k=1.0),
        "k=2.0（過度）": laplacian_sharpening(img_blur, k=2.0),
    }

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (title, im) in zip(axes, results.items()):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_laplacian.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_laplacian.png")


# ── Task 3：Histogram Equalization ──────────────────────────────────────
def manual_histogram_eq(img: np.ndarray) -> np.ndarray:
    # 計算 histogram
    hist = np.zeros(256, dtype=np.float32)
    for val in img.flat:
        hist[val] += 1

    # 計算 CDF
    cdf = np.cumsum(hist)

    # 正規化 CDF（排除 0）
    cdf_min = cdf[cdf > 0].min()
    mapping = np.round((cdf - cdf_min) / (img.size - cdf_min) * 255).astype(np.uint8)

    # 映射
    result = mapping[img]
    return result


def task3_histogram_eq(img):
    print("=== Task 3: Histogram Equalization ===")

    low_contrast = ((img.astype(np.float32) / 255) * 100 + 50).astype(np.uint8)

    manual_result = manual_histogram_eq(low_contrast)
    cv_result = cv2.equalizeHist(low_contrast)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_result = clahe.apply(low_contrast)

    # 驗證 manual vs OpenCV
    diff = np.abs(manual_result.astype(int) - cv_result.astype(int))
    print(f"  Manual vs OpenCV 最大差異：{diff.max()}（通常 ≤ 1，因捨入）")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    images = [low_contrast, manual_result, cv_result, clahe_result]
    titles = ["Low Contrast", "Manual HE", "OpenCV HE", "CLAHE"]

    for i, (im, title) in enumerate(zip(images, titles)):
        axes[0, i].imshow(im, cmap='gray', vmin=0, vmax=255)
        axes[0, i].set_title(title)
        axes[0, i].axis('off')
        axes[1, i].hist(im.flat, bins=256, range=(0, 255), color='steelblue', density=True)
        axes[1, i].set_title(f"{title} Histogram")
        axes[1, i].set_xlim(0, 255)

    plt.savefig("output/task3_histogram_eq.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_histogram_eq.png")


# ── Task 4（Bonus）：Edge-Adaptive Sharpening ────────────────────────────
def task4_bonus_edge_adaptive(img_blur):
    print("=== Task 4 (Bonus): Edge-Adaptive Sharpening ===")

    edges = cv2.Canny(img_blur, 30, 100)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    edge_mask = cv2.dilate(edges, kernel)

    sharpened = unsharp_masking(img_blur, radius=2.0, amount=1.5)

    # 只在邊緣區域套用銳化
    result = np.where(edge_mask > 0, sharpened, img_blur)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (img_blur, "Blurred"),
        (sharpened, "Full USM"),
        (edge_mask, "Edge Mask"),
        (result, "Edge-Adaptive USM"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task4_edge_adaptive.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_edge_adaptive.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img = load_or_generate_image()
    img_blur = simulate_blur(img, sigma=2.0)
    print(f"圖片尺寸：{img.shape}")

    task1_usm(img_blur)
    task2_laplacian(img_blur)
    task3_histogram_eq(img)
    task4_bonus_edge_adaptive(img_blur)

    print("\n完成！查看 output/ 資料夾。")
