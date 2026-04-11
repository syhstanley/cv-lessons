"""
Assignment 07 — 影像銳化與畫質增強
=================================
目標：實作 USM、Laplacian Sharpening、Histogram EQ

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
    """
    實作 Unsharp Masking（USM）銳化。

    公式：
        HF(x, y)  = I(x, y) - GaussianBlur(I)(x, y)     （高頻細節）

        HF_t(x,y) = HF(x, y)  if |HF(x, y)| ≥ threshold （threshold 抑制）
                    0           otherwise

        Output(x, y) = I(x, y) + amount × HF_t(x, y)

    步驟：
    1. 用指定 radius（sigma）對影像做 Gaussian blur
    2. 計算 high_freq = 原圖 - blur 後的圖
    3. 若 threshold > 0，把 |high_freq| < threshold 的位置設為 0（保護平坦區域）
    4. 結果 = 原圖 + amount × high_freq，clip 到 0-255
    """
    blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=radius)
    img_f = img.astype(np.float32)
    blurred_f = blurred.astype(np.float32)

    high_freq = None  # TODO: 原圖 - 模糊圖

    if high_freq is None:
        return img

    # TODO: 套用 threshold 抑制平坦區域

    result = None  # TODO: 原圖 + amount × high_freq

    return np.clip(result, 0, 255).astype(np.uint8) if result is not None else img


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
    """
    實作 Laplacian Sharpening。

    公式：
        L(x, y)      = ∇²I(x, y)           （二階導數，在邊緣有強響應）
        Output(x, y) = I(x, y) - k · L(x, y)

    用 cv2.Laplacian(img, cv2.CV_64F, ksize=3) 計算，
    係數 k 控制銳化強度，過大會產生 ringing artifact。
    計算完記得 clip 到 0-255 後轉 uint8。
    """
    lap = cv2.Laplacian(img, cv2.CV_64F, ksize=3)
    result = None  # TODO
    return np.clip(result, 0, 255).astype(np.uint8) if result is not None else img


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
    """
    手動實作 Histogram Equalization。

    公式：
        H(v)   = pixel 值為 v 的數量          （histogram）
        CDF(v) = Σ_{k=0}^{v} H(k)            （累積分佈）

        mapping(v) = round( (CDF(v) - CDF_min) / (N - CDF_min) × 255 )

        其中 N = 總 pixel 數，CDF_min = CDF 中最小的非零值

        Output(x, y) = mapping[ Input(x, y) ]

    步驟：
    1. 統計每個灰度值（0-255）的 pixel 數，建立 histogram（長度 256 的 array）
    2. 計算 CDF = np.cumsum(histogram)
    3. 找 CDF_min（cdf[cdf > 0].min()）
    4. 用公式建立 mapping table（長度 256，每個值對應新灰度）
    5. 用 mapping[img] 做查表映射
    """
    hist = np.zeros(256, dtype=np.float32)
    # TODO: 統計每個灰度值的出現次數

    cdf = None  # TODO: np.cumsum(hist)

    # TODO: 正規化 CDF 並建立映射表，再對原圖做映射
    result = None

    return result if result is not None else img


def task3_histogram_eq(img):
    print("=== Task 3: Histogram Equalization ===")

    low_contrast = ((img.astype(np.float32) / 255) * 100 + 50).astype(np.uint8)

    manual_result = manual_histogram_eq(low_contrast)
    cv_result = cv2.equalizeHist(low_contrast)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_result = clahe.apply(low_contrast)

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
    """
    只在邊緣附近做 USM，平坦區域不銳化，減少 artifact。

    步驟：
    1. 用 Canny 偵測邊緣，再用 dilation 把 mask 擴大（覆蓋邊緣附近區域）
    2. 對整張圖做 USM 銳化（radius=2, amount=1.5）
    3. 用 np.where：edge_mask 為 True 的地方用 sharpened，其餘保留原圖

    思考：這樣做相比全圖 USM 有什麼好處？噪聲怎麼變化？
    """
    print("=== Task 4 (Bonus): Edge-Adaptive Sharpening ===")

    edges = cv2.Canny(img_blur, 30, 100)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    edge_mask = cv2.dilate(edges, kernel)

    sharpened = unsharp_masking(img_blur, radius=2.0, amount=1.5)

    result = None  # TODO: np.where(edge_mask > 0, sharpened, img_blur)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (img_blur, "Blurred"),
        (sharpened if sharpened is not None else img_blur, "Full USM"),
        (edge_mask, "Edge Mask"),
        (result if result is not None else img_blur, "Edge-Adaptive USM"),
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
