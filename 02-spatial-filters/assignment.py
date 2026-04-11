"""
Assignment 02 — 空間域濾波器
=================================
目標：從頭實作 Gaussian / Median / Bilateral，並與 OpenCV 比較

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
        img = cv2.imread(test_path, cv2.IMREAD_GRAYSCALE)
        return img
    else:
        # 生成帶噪聲的測試圖（中間有一條清晰邊緣）
        img = np.zeros((256, 256), dtype=np.uint8)
        img[:, 128:] = 200
        return img


def add_gaussian_noise(img, sigma=25):
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def add_salt_pepper_noise(img, prob=0.05):
    noisy = img.copy()
    rng = np.random.default_rng()
    salt = rng.random(img.shape) < prob / 2
    pepper = rng.random(img.shape) < prob / 2
    noisy[salt] = 255
    noisy[pepper] = 0
    return noisy


# ── Task 1：手動實作 2D Convolution ─────────────────────────────────────
def manual_convolve2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    TODO: 從頭實作 2D convolution（不用 cv2 或 scipy）
    - 注意 padding（用 replicate padding）
    - kernel 假設是奇數大小（3x3、5x5 等）
    - 輸出尺寸與輸入相同
    """
    h, w = img.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    # TODO: 實作 replicate padding
    padded = None  # np.pad(...)

    output = np.zeros_like(img, dtype=np.float32)

    # TODO: 雙層迴圈做卷積
    # for i in range(h):
    #     for j in range(w):
    #         output[i, j] = np.sum(...)

    return np.clip(output, 0, 255).astype(np.uint8)


# ── Task 2：Gaussian Kernel 生成 + 應用 ─────────────────────────────────
def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """
    TODO: 生成 size×size 的 Gaussian kernel
    G(x,y) = exp(-(x²+y²) / 2σ²)，最後正規化讓總和=1
    """
    k = size // 2
    kernel = np.zeros((size, size), dtype=np.float32)

    # TODO: 填入 Gaussian 值
    # for i in range(size):
    #     for j in range(size):
    #         x, y = i - k, j - k
    #         kernel[i, j] = ...

    # TODO: 正規化
    # kernel /= kernel.sum()

    return kernel


def task2_gaussian(img_noisy_gaussian):
    print("=== Task 2: Gaussian Filter ===")

    # 生成 kernel
    kernel_3 = gaussian_kernel(3, sigma=1.0)
    kernel_7 = gaussian_kernel(7, sigma=2.0)

    # 手動卷積
    result_3 = manual_convolve2d(img_noisy_gaussian, kernel_3)
    result_7 = manual_convolve2d(img_noisy_gaussian, kernel_7)

    # OpenCV 版本對照
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
    """
    TODO: 從頭實作 Median Filter
    - 取 ksize×ksize 鄰域的中值
    - 同樣用 replicate padding
    """
    h, w = img.shape
    pad = ksize // 2
    output = np.zeros_like(img)

    # TODO: 實作
    # padded = np.pad(img, pad, mode='edge')
    # for i in range(h):
    #     for j in range(w):
    #         neighborhood = padded[i:i+ksize, j:j+ksize]
    #         output[i, j] = np.median(neighborhood)

    return output


def task3_median(img_noisy_sp):
    print("=== Task 3: Median Filter ===")

    result_manual = manual_median_filter(img_noisy_sp, ksize=3)
    result_cv = cv2.medianBlur(img_noisy_sp, 3)

    # 也對照一下 Gaussian 對 S&P noise 的效果（應該比 Median 差）
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
    """
    Bilateral 實作複雜，這裡主要用 OpenCV 觀察行為，
    重點是調整 sigma_r 的影響
    """
    print("=== Task 4: Bilateral Filter ===")

    # σ_s=9（空間），調整 σ_r 觀察邊緣保留效果
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

    # TODO（思考題）：
    # 在邊緣附近放大看，σ_r=10 和 σ_r=150 的邊緣清晰度有何差異？
    # 為什麼 σ_r 大時行為接近 Gaussian blur？


# ── Task 5（Bonus）：Separable Gaussian ──────────────────────────────────
def task5_bonus_separable_gaussian(img):
    """
    TODO: 驗證 2D Gaussian 可以拆成兩個 1D convolution
    1. 生成 1D Gaussian kernel（長度 7，σ=2）
    2. 先做水平卷積，再做垂直卷積
    3. 與直接做 2D Gaussian 比較差異（應該幾乎為 0）
    4. 計算兩種方法的運算次數差異（7×7 vs 7+7）
    """
    print("=== Task 5 (Bonus): Separable Gaussian ===")
    print("  → TODO: 驗證 separable 性質")


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
