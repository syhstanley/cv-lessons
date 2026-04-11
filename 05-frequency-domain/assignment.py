"""
Assignment 05 — 頻域濾波
=================================
目標：用 FFT 實作 LPF / HPF，觀察頻譜，並消除週期性噪聲

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
        return cv2.resize(img, (256, 256))
    else:
        img = np.zeros((256, 256), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 200, -1)
        cv2.circle(img, (190, 60), 30, 150, -1)
        return img


def add_periodic_noise(img, freq=20, amplitude=40):
    """加入週期性正弦噪聲（模擬電磁干擾）"""
    h, w = img.shape
    noise = amplitude * np.sin(2 * np.pi * freq * np.arange(w) / w)
    noisy = img.astype(np.float32) + noise[np.newaxis, :]
    return np.clip(noisy, 0, 255).astype(np.uint8)


# ── Task 1：FFT 頻譜視覺化 ───────────────────────────────────────────────
def task1_visualize_spectrum(img):
    print("=== Task 1: FFT 頻譜視覺化 ===")

    # TODO: 計算 FFT 並視覺化
    # 步驟：
    # 1. np.fft.fft2(img)
    # 2. np.fft.fftshift(...)  移 DC 到中心
    # 3. 取 magnitude：np.abs(...)
    # 4. log scale：np.log1p(magnitude)
    # 5. 正規化到 0-255

    F = None  # TODO: np.fft.fft2(img)
    F_shift = None  # TODO: np.fft.fftshift(F)
    magnitude = None  # TODO: np.abs(F_shift)
    log_magnitude = None  # TODO: np.log1p(magnitude)

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
    TODO: 生成 Ideal Low-Pass Filter mask
    - shape: (H, W)
    - cutoff: 截止頻率（距中心的像素距離）
    - 中心以內 = 1，以外 = 0
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist = None  # TODO: np.sqrt((Y - cy)**2 + (X - cx)**2)
    mask = None  # TODO: (dist <= cutoff).astype(np.float32)
    return mask


def make_gaussian_lpf(shape, sigma):
    """
    TODO: 生成 Gaussian Low-Pass Filter mask
    H(u,v) = exp(-D² / 2σ²)
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist_sq = None  # TODO: (Y - cy)**2 + (X - cx)**2
    mask = None  # TODO: np.exp(-dist_sq / (2 * sigma**2))
    return mask


def apply_freq_filter(img, mask):
    """
    TODO: 在頻域套用 mask，返回過濾後的空間域影像
    步驟：fft2 → fftshift → 乘 mask → ifftshift → ifft2 → 取實部
    """
    F = np.fft.fft2(img.astype(np.float32))
    F_shift = np.fft.fftshift(F)

    # TODO: 套用 mask
    G_shift = None  # F_shift * mask

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
    print("=== Task 3: HPF ===")

    shape = img.shape
    gauss_lpf = make_gaussian_lpf(shape, sigma=20)

    if gauss_lpf is None:
        print("  → 需要先完成 Task 2")
        return

    # HPF = 1 - LPF
    gauss_hpf = 1.0 - gauss_lpf

    lpf_result = apply_freq_filter(img, gauss_lpf)
    hpf_result = apply_freq_filter(img, gauss_hpf)

    # HPF + original → 銳化效果
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
    TODO: 找出頻譜中週期性噪聲的亮點，用 Notch filter 消除

    步驟：
    1. 計算含噪聲圖片的 FFT
    2. 視覺化頻譜，找出噪聲頻率對應的亮點位置
    3. 在那個位置附近設為 0（notch）
    4. 逆 FFT 恢復圖片
    """
    print("=== Task 4: Notch Filter（週期性噪聲）===")

    noisy = add_periodic_noise(img, freq=20, amplitude=50)

    F = np.fft.fft2(noisy.astype(np.float32))
    F_shift = np.fft.fftshift(F)
    magnitude = np.log1p(np.abs(F_shift))

    # TODO: 設計 Notch mask
    # 1. 先觀察 magnitude 找亮點位置
    # 2. 建立 mask（全 1），在亮點位置設為 0
    mask = np.ones_like(F_shift, dtype=np.float32)

    # 頻率 freq=20 對應頻譜位置：
    h, w = noisy.shape
    # 水平方向的週期噪聲 → 頻譜在 (cy, cx ± freq_bin)
    cy, cx = h // 2, w // 2
    freq_bin = int(20 * w / w)  # = 20 pixels from center

    # TODO: 在 (cy, cx+freq_bin) 和 (cy, cx-freq_bin) 附近設 mask=0
    # radius = 3
    # Y, X = np.ogrid[:h, :w]
    # for dy, dx in [(cy, cx+freq_bin), (cy, cx-freq_bin)]:
    #     mask[np.sqrt((Y-dy)**2 + (X-dx)**2) < radius] = 0

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
