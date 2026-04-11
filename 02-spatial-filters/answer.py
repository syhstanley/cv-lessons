"""
Answer 02 — 空間域濾波器
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
        img[:, 128:] = 200
        return img


def add_gaussian_noise(img, sigma=25):
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def add_salt_pepper_noise(img, prob=0.05):
    noisy = img.copy()
    rng = np.random.default_rng()
    noisy[rng.random(img.shape) < prob / 2] = 255
    noisy[rng.random(img.shape) < prob / 2] = 0
    return noisy


# ── Task 1：手動實作 2D Convolution ─────────────────────────────────────
def manual_convolve2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    h, w = img.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    # Replicate padding
    padded = np.pad(img.astype(np.float32), ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')

    output = np.zeros((h, w), dtype=np.float32)
    for i in range(h):
        for j in range(w):
            region = padded[i:i+kh, j:j+kw]
            output[i, j] = np.sum(region * kernel)

    return np.clip(output, 0, 255).astype(np.uint8)


# ── Task 2：Gaussian Kernel 生成 + 應用 ─────────────────────────────────
def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    k = size // 2
    kernel = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            x, y = i - k, j - k
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    kernel /= kernel.sum()
    return kernel


def task2_gaussian(img_noisy_gaussian):
    print("=== Task 2: Gaussian Filter ===")

    kernel_3 = gaussian_kernel(3, sigma=1.0)
    kernel_7 = gaussian_kernel(7, sigma=2.0)

    result_3 = manual_convolve2d(img_noisy_gaussian, kernel_3)
    result_7 = manual_convolve2d(img_noisy_gaussian, kernel_7)
    cv_result = cv2.GaussianBlur(img_noisy_gaussian, (7, 7), sigmaX=2.0)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, title, im in zip(
        axes,
        ["Noisy (Gaussian)", "Blur σ=1 3×3", "Blur σ=2 7×7", "OpenCV GaussianBlur"],
        [img_noisy_gaussian, result_3, result_7, cv_result]
    ):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_gaussian.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_gaussian.png")


# ── Task 3：Median Filter ────────────────────────────────────────────────
def manual_median_filter(img: np.ndarray, ksize: int) -> np.ndarray:
    h, w = img.shape
    pad = ksize // 2
    output = np.zeros_like(img)
    padded = np.pad(img, pad, mode='edge')
    for i in range(h):
        for j in range(w):
            neighborhood = padded[i:i+ksize, j:j+ksize]
            output[i, j] = np.median(neighborhood)
    return output


def task3_median(img_noisy_sp):
    print("=== Task 3: Median Filter ===")

    result_manual = manual_median_filter(img_noisy_sp, ksize=3)
    result_cv = cv2.medianBlur(img_noisy_sp, 3)
    result_gaussian = cv2.GaussianBlur(img_noisy_sp, (3, 3), sigmaX=1.0)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, title, im in zip(
        axes,
        ["S&P Noisy", "Median (manual)", "Median (OpenCV)", "Gaussian (for compare)"],
        [img_noisy_sp, result_manual, result_cv, result_gaussian]
    ):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_median.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_median.png")


# ── Task 4：Bilateral Filter 觀察 ────────────────────────────────────────
def task4_bilateral(img_noisy_gaussian):
    print("=== Task 4: Bilateral Filter ===")

    results = {
        "Noisy": img_noisy_gaussian,
        "σ_r=10 (強保邊)": cv2.bilateralFilter(img_noisy_gaussian, d=9, sigmaColor=10, sigmaSpace=9),
        "σ_r=75 (平衡)":   cv2.bilateralFilter(img_noisy_gaussian, d=9, sigmaColor=75, sigmaSpace=9),
        "σ_r=150 (接近Gaussian)": cv2.bilateralFilter(img_noisy_gaussian, d=9, sigmaColor=150, sigmaSpace=9),
    }

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (title, im) in zip(axes, results.items()):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=9)
        ax.axis('off')
    plt.suptitle("Task 4: Bilateral Filter — σ_r 的影響")
    plt.savefig("output/task4_bilateral.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_bilateral.png")
    # σ_r 大時，值域差異大的 pixel 也會被納入平均 → 等同 Gaussian blur


# ── Task 5（Bonus）：Separable Gaussian ──────────────────────────────────
def task5_bonus_separable_gaussian(img):
    print("=== Task 5 (Bonus): Separable Gaussian ===")

    size, sigma = 7, 2.0
    k = size // 2

    # 1D kernel
    kernel_1d = np.array([np.exp(-x**2 / (2 * sigma**2)) for x in range(-k, k+1)], dtype=np.float32)
    kernel_1d /= kernel_1d.sum()

    # 2D kernel（直接生成）
    kernel_2d = gaussian_kernel(size, sigma)

    # Separable：先水平再垂直
    img_f = img.astype(np.float32)
    tmp = cv2.filter2D(img_f, -1, kernel_1d.reshape(1, -1))   # 水平
    sep_result = cv2.filter2D(tmp, -1, kernel_1d.reshape(-1, 1))  # 垂直

    # 直接 2D
    direct_result = cv2.filter2D(img_f, -1, kernel_2d)

    diff = np.abs(sep_result - direct_result)
    print(f"  Separable vs Direct 最大差異：{diff.max():.6f}（幾乎為 0）")
    print(f"  運算次數：Direct={size*size} multiplies/pixel，Separable={size+size} multiplies/pixel")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title) in zip(axes, [
        (np.clip(direct_result, 0, 255).astype(np.uint8), "Direct 2D Gaussian"),
        (np.clip(sep_result, 0, 255).astype(np.uint8), "Separable Gaussian"),
        (np.clip(diff * 100, 0, 255).astype(np.uint8), "差異 ×100（幾乎為 0）"),
    ]):
        ax.imshow(im, cmap='gray')
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task5_separable.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task5_separable.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img = load_or_generate_image()
    img_gaussian_noise = add_gaussian_noise(img, sigma=25)
    img_sp_noise = add_salt_pepper_noise(img, prob=0.05)

    print(f"圖片尺寸：{img.shape}")

    task2_gaussian(img_gaussian_noise)
    task3_median(img_sp_noise)
    task4_bilateral(img_gaussian_noise)
    task5_bonus_separable_gaussian(img)

    print("\n完成！查看 output/ 資料夾。")
