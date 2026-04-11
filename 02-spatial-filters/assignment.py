"""
Assignment 02 — 空間域濾波器
=================================
目標：從頭實作 Gaussian / Median / Bilateral，並與 OpenCV 比較

執行：python assignment.py

📐 公式推導參考（../formula_prove.md）：
    P1 — 2D Convolution 的定義與邊界行為        → Task 1
    P2 — Gaussian Kernel 的 Separability 證明   → Task 2, Task 5
    P3 — Gaussian Filter 等於頻域低通濾波器     → Task 2
    P6 — Bilateral Filter 的保邊原理            → Task 4
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
    """
    從頭實作 2D convolution，不使用 cv2 或 scipy。

    公式：
        Output(i, j) = Σ_m Σ_n  Kernel(m, n) × Padded(i+m, j+n)

    步驟：
    1. 根據 kernel 大小計算需要的 padding 量（pad = kernel 邊長 // 2）
    2. 對輸入影像做 replicate padding（邊緣像素向外複製，避免邊界縮小）
    3. 用雙層迴圈對每個輸出 pixel (i, j) 取出對應的鄰域，
       與 kernel 做逐元素乘積後加總
    4. 輸出尺寸與輸入相同，數值 clip 到 0-255

    📐 完整定義與邊界行為推導見 ../formula_prove.md P1
    """
    h, w = img.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    padded = None  # TODO: 用 np.pad 做 replicate padding（mode='edge'）
    output = np.zeros_like(img, dtype=np.float32)

    # TODO: 雙層迴圈，對每個 (i, j) 取出對應鄰域，與 kernel 做逐元素乘積後 sum

    return np.clip(output, 0, 255).astype(np.uint8)


# ── Task 2：Gaussian Kernel 生成 + 應用 ─────────────────────────────────
def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """
    生成 size×size 的 Gaussian kernel。

    公式：
        G(x, y) = exp(-(x² + y²) / (2σ²))

    其中 x, y 是相對中心的座標（中心為 0,0，範圍為 -k ~ k，k = size // 2）。
    生成後除以所有元素的總和做正規化，確保濾波不改變整體亮度。

    📐 為什麼 Gaussian 是好的低通濾波器，見 ../formula_prove.md P3
    """
    k = size // 2
    kernel = np.zeros((size, size), dtype=np.float32)

    # TODO: 用雙層迴圈填入每個位置的 Gaussian 值，再除以總和正規化

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
    """
    從頭實作 Median Filter。

    步驟：
    1. 對影像做 replicate padding（padding 量 = ksize // 2）
    2. 用雙層迴圈對每個 pixel 取出 ksize×ksize 的鄰域
    3. 取鄰域的中值作為輸出
    """
    h, w = img.shape
    pad = ksize // 2
    output = np.zeros_like(img)

    # TODO: 實作上述步驟

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
    """
    用 OpenCV 的 bilateralFilter 觀察 sigma_r（sigmaColor）的影響。
    固定 sigma_s=9，分別測試 sigma_r = 10 / 75 / 150，
    觀察邊緣保留效果的變化，並思考：為什麼 sigma_r 越大，
    行為會越來越接近普通的 Gaussian blur？
    """
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


# ── Task 5（Bonus）：Separable Gaussian ──────────────────────────────────
def task5_bonus_separable_gaussian(img):
    """
    驗證 2D Gaussian 可以分解成兩個 1D convolution 的性質（separability）。

    步驟：
    1. 生成長度 7、sigma=2 的 1D Gaussian kernel（記得正規化）
    2. 先對影像做水平方向的 1D convolution，再對結果做垂直方向的 1D convolution
    3. 直接生成 7×7 的 2D Gaussian kernel，對原圖做一次卷積
    4. 比較兩個結果的差異（應該幾乎為 0）
    5. 計算並列印兩種方法的乘法次數差異（7×7 vs 7+7 次/pixel）

    📐 Separability 數學證明（G(x,y) = G(x)·G(y)）見 ../formula_prove.md P2
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
