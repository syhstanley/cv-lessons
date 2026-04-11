"""
Assignment 05 — 頻域濾波
=================================
目標：用 FFT 實作 LPF / HPF，觀察頻譜，並消除週期性噪聲

執行：python assignment.py

📐 公式推導參考（../formula_prove.md）：
    P4 — Convolution Theorem（空間卷積 = 頻域乘法）  → Task 1, Task 2
    P3 — Gaussian Filter 等於頻域低通濾波器          → Task 2
    P5 — Ideal LPF 的 Ringing（Gibbs Phenomenon）   → Task 2
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
        return cv2.resize(img, (256, 256))
    else:
        img = np.zeros((256, 256), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 200, -1)
        cv2.circle(img, (190, 60), 30, 150, -1)
        return img


def add_periodic_noise(img, freq=20, amplitude=40):
    """加入水平方向的週期性正弦噪聲（模擬電磁干擾）"""
    h, w = img.shape
    noise = amplitude * np.sin(2 * np.pi * freq * np.arange(w) / w)
    noisy = img.astype(np.float32) + noise[np.newaxis, :]
    return np.clip(noisy, 0, 255).astype(np.uint8)


# ── Task 1：FFT 頻譜視覺化 ───────────────────────────────────────────────
def task1_visualize_spectrum(img):
    """
    計算影像的 2D FFT 並視覺化頻譜。

    公式：
        F(u, v) = Σ_x Σ_y  f(x,y) · exp(-j2π(ux/M + vy/N))

        Magnitude Spectrum = |F(u, v)|
        Log Spectrum       = log(1 + |F(u, v)|)   （log1p 壓縮動態範圍）

    步驟：
    1. np.fft.fft2(img) → 計算 2D DFT
    2. np.fft.fftshift(F) → 把 DC（低頻）移到圖中央
    3. np.abs(F_shift) → 取 magnitude
    4. np.log1p(magnitude) → log scale，讓暗部細節可見
    5. 顯示原圖和頻譜並存檔

    觀察：頻譜中心是低頻（平均亮度），邊緣是高頻（細節、邊緣、噪聲）。

    📐 空間域 convolution 為何等價於頻域乘法，見 ../formula_prove.md P4
    """
    print("=== Task 1: FFT 頻譜視覺化 ===")

    F = None        # TODO: 計算 FFT
    F_shift = None  # TODO: fftshift
    magnitude = None       # TODO: np.abs
    log_magnitude = None   # TODO: np.log1p

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title("Original Image")

    if log_magnitude is not None:
        axes[1].imshow(log_magnitude, cmap='hot')
        axes[1].set_title("FFT Magnitude Spectrum (log)")
    else:
        axes[1].set_title("TODO: 計算頻譜")

    for ax in axes:
        ax.axis('off')
    plt.savefig("output/task1_spectrum.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_spectrum.png")

    return F_shift


# ── Task 2：Ideal vs Gaussian LPF ───────────────────────────────────────
def make_ideal_lpf(shape, cutoff):
    """
    生成 Ideal Low-Pass Filter mask。

    公式：
        D(u, v) = sqrt((u - cy)² + (v - cx)²)   （距頻譜中心的距離）

        H(u, v) = 1  if D(u, v) ≤ cutoff
                  0  otherwise

    對頻譜中每個點計算到中心 (cy, cx) 的距離，
    距離 ≤ cutoff 的設為 1（保留），其他設為 0（濾除）。
    返回 float32 的 2D mask。

    📐 為何硬截斷會產生 Ringing，見 ../formula_prove.md P5
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist = None   # TODO: 計算每點到 (cy, cx) 的距離
    mask = None   # TODO: 距離 ≤ cutoff 的位置為 1
    return mask


def make_gaussian_lpf(shape, sigma):
    """
    生成 Gaussian Low-Pass Filter mask。

    公式：
        D²(u, v) = (u - cy)² + (v - cx)²

        H(u, v) = exp(-D²(u, v) / (2σ²))

    σ 越大 → 截止頻率越高 → 保留更多高頻 → 越清晰
    σ 越小 → 截止頻率越低 → 更模糊，與 Gaussian blur 等效

    📐 Gaussian 在頻域為何仍是 Gaussian，見 ../formula_prove.md P3
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist_sq = None  # TODO: (Y-cy)² + (X-cx)²
    mask = None     # TODO: exp(-dist_sq / (2*sigma²))
    return mask


def apply_freq_filter(img, mask):
    """
    在頻域套用 mask，返回過濾後的空間域影像。

    流程（Convolution Theorem）：
        F = FFT2(f)                   1. 空間域 → 頻域
        F_shift = fftshift(F)         2. DC 移到中心
        G_shift = H × F_shift         3. 頻域乘法 = 空間域卷積
        G = ifftshift(G_shift)        4. DC 移回原位
        g = Re[ IFFT2(G) ]            5. 逆 DFT，取實部
        output = clip(g, 0, 255)      6. 轉回 uint8
    """
    F = np.fft.fft2(img.astype(np.float32))
    F_shift = np.fft.fftshift(F)

    G_shift = None  # TODO: F_shift × mask

    if G_shift is None:
        return img

    G = np.fft.ifftshift(G_shift)
    result = np.fft.ifft2(G).real
    return np.clip(result, 0, 255).astype(np.uint8)


def task2_lpf(img):
    print("=== Task 2: LPF（Ideal vs Gaussian）===")

    shape = img.shape
    ideal_mask = make_ideal_lpf(shape, cutoff=30)
    gauss_mask = make_gaussian_lpf(shape, sigma=30)

    ideal_result = apply_freq_filter(img, ideal_mask) if ideal_mask is not None else img
    gauss_result = apply_freq_filter(img, gauss_mask) if gauss_mask is not None else img

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (img, "Original"),
        (ideal_result, "Ideal LPF (r=30)\n觀察 ringing"),
        (gauss_result, "Gaussian LPF (σ=30)\n無 ringing"),
        (cv2.GaussianBlur(img, (0,0), sigmaX=10), "cv2 Gaussian Blur"),
    ]):
        ax.imshow(im, cmap='gray')
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_lpf.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_lpf.png")


# ── Task 3：High-pass Filter（HPF = 1 - LPF）───────────────────────────
def task3_hpf(img):
    """
    HPF = 1 - LPF，高通濾波器保留高頻（邊緣細節）。

    用 make_gaussian_lpf 生成 LPF mask，再用 1 減去它得到 HPF mask。
    分別套用兩個 mask，並把 HPF 結果疊加回原圖（係數 0.5）觀察銳化效果。
    """
    print("=== Task 3: HPF ===")

    shape = img.shape
    gauss_lpf = make_gaussian_lpf(shape, sigma=20)

    if gauss_lpf is None:
        print("  → 需要先完成 Task 2")
        return

    gauss_hpf = 1.0 - gauss_lpf

    lpf_result = apply_freq_filter(img, gauss_lpf)
    hpf_result = apply_freq_filter(img, gauss_hpf)

    sharpened = np.clip(
        img.astype(np.float32) + 0.5 * hpf_result.astype(np.float32),
        0, 255
    ).astype(np.uint8)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (img, "Original"),
        (lpf_result, "Gaussian LPF\n（低頻，模糊）"),
        (hpf_result, "Gaussian HPF\n（高頻，邊緣）"),
        (sharpened, "Original + 0.5×HPF\n（銳化）"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_hpf.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_hpf.png")


# ── Task 4：週期性噪聲消除（Notch Filter）──────────────────────────────
def task4_notch_filter(img):
    """
    用 Notch Filter 消除週期性噪聲。

    週期性噪聲在頻譜上會出現明顯的亮點，位置對應噪聲頻率。
    水平方向頻率為 freq=20 的噪聲，亮點在頻譜中心左右各偏移 20 個 bin 處。

    步驟：
    1. 對含噪聲影像計算 FFT 並觀察頻譜
    2. 建立全為 1 的 mask
    3. 在噪聲頻率對應的位置（中心左右各 20 個 bin）附近（半徑約 4）設為 0
    4. 套用 mask 後逆 FFT 回空間域
    5. 比較原圖、含噪聲圖、濾波後圖的頻譜
    """
    print("=== Task 4: Notch Filter（週期性噪聲）===")

    noisy = add_periodic_noise(img, freq=20, amplitude=50)

    F = np.fft.fft2(noisy.astype(np.float32))
    F_shift = np.fft.fftshift(F)
    magnitude = np.log1p(np.abs(F_shift))

    h, w = noisy.shape
    cy, cx = h // 2, w // 2

    mask = np.ones((h, w), dtype=np.float32)
    # TODO: 在 (cy, cx+20) 和 (cy, cx-20) 附近半徑 4 的範圍設 mask=0

    filtered_F = F_shift * mask
    result = np.fft.ifft2(np.fft.ifftshift(filtered_F)).real
    result = np.clip(result, 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, (im, title, cmap) in zip(axes.flat, [
        (img, "Original", 'gray'),
        (noisy, "Noisy (週期性干擾)", 'gray'),
        (result, "After Notch Filter", 'gray'),
        (magnitude, "Noisy 頻譜", 'hot'),
        (np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(img.astype(np.float32))))), "原始頻譜", 'hot'),
        (np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(result.astype(np.float32))))), "濾波後頻譜", 'hot'),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task4_notch.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_notch.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img = load_or_generate_image()
    print(f"圖片尺寸：{img.shape}")

    task1_visualize_spectrum(img)
    task2_lpf(img)
    task3_hpf(img)
    task4_notch_filter(img)

    print("\n完成！查看 output/ 資料夾。")
