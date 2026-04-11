"""
Answer 05 — 頻域濾波
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
        img = cv2.imread(test_path, cv2.IMREAD_GRAYSCALE)
        return cv2.resize(img, (256, 256))
    else:
        img = np.zeros((256, 256), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 200, -1)
        cv2.circle(img, (190, 60), 30, 150, -1)
        return img


def add_periodic_noise(img, freq=20, amplitude=40):
    h, w = img.shape
    noise = amplitude * np.sin(2 * np.pi * freq * np.arange(w) / w)
    noisy = img.astype(np.float32) + noise[np.newaxis, :]
    return np.clip(noisy, 0, 255).astype(np.uint8)


# ── Task 1：FFT 頻譜視覺化 ───────────────────────────────────────────────
def task1_visualize_spectrum(img):
    print("=== Task 1: FFT 頻譜視覺化 ===")

    F = np.fft.fft2(img.astype(np.float32))
    F_shift = np.fft.fftshift(F)
    magnitude = np.abs(F_shift)
    log_magnitude = np.log1p(magnitude)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title("Original Image")
    axes[1].imshow(log_magnitude, cmap='hot')
    axes[1].set_title("FFT Magnitude Spectrum (log)")
    for ax in axes:
        ax.axis('off')
    plt.savefig("output/task1_spectrum.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_spectrum.png")

    return F_shift


# ── Task 2：Ideal vs Gaussian LPF ───────────────────────────────────────
def make_ideal_lpf(shape, cutoff):
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((Y - cy)**2 + (X - cx)**2)
    mask = (dist <= cutoff).astype(np.float32)
    return mask


def make_gaussian_lpf(shape, sigma):
    h, w = shape
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist_sq = (Y - cy)**2 + (X - cx)**2
    mask = np.exp(-dist_sq / (2 * sigma**2)).astype(np.float32)
    return mask


def apply_freq_filter(img, mask):
    F = np.fft.fft2(img.astype(np.float32))
    F_shift = np.fft.fftshift(F)
    G_shift = F_shift * mask
    G = np.fft.ifftshift(G_shift)
    result = np.fft.ifft2(G).real
    return np.clip(result, 0, 255).astype(np.uint8)


def task2_lpf(img):
    print("=== Task 2: LPF（Ideal vs Gaussian）===")

    shape = img.shape
    ideal_mask = make_ideal_lpf(shape, cutoff=30)
    gauss_mask = make_gaussian_lpf(shape, sigma=30)

    ideal_result = apply_freq_filter(img, ideal_mask)
    gauss_result = apply_freq_filter(img, gauss_mask)

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


# ── Task 3：High-pass Filter ────────────────────────────────────────────
def task3_hpf(img):
    print("=== Task 3: HPF ===")

    shape = img.shape
    gauss_lpf = make_gaussian_lpf(shape, sigma=20)
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


# ── Task 4：Notch Filter ─────────────────────────────────────────────────
def task4_notch_filter(img):
    print("=== Task 4: Notch Filter（週期性噪聲）===")

    noisy = add_periodic_noise(img, freq=20, amplitude=50)

    F = np.fft.fft2(noisy.astype(np.float32))
    F_shift = np.fft.fftshift(F)
    magnitude = np.log1p(np.abs(F_shift))

    h, w = noisy.shape
    cy, cx = h // 2, w // 2
    freq_bin = 20  # 頻率 20 → 距中心 20 個 bin

    # 建立 notch mask：在噪聲頻率位置挖洞
    mask = np.ones((h, w), dtype=np.float32)
    radius = 4
    Y, X = np.ogrid[:h, :w]
    for (dy, dx) in [(cy, cx + freq_bin), (cy, cx - freq_bin)]:
        mask[np.sqrt((Y - dy)**2 + (X - dx)**2) < radius] = 0

    filtered_F = F_shift * mask
    result = np.fft.ifft2(np.fft.ifftshift(filtered_F)).real
    result = np.clip(result, 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, (im, title, cmap) in zip(axes.flat, [
        (img, "Original", 'gray'),
        (noisy, "Noisy (週期性干擾)", 'gray'),
        (result, "After Notch Filter", 'gray'),
        (magnitude, "Noisy 頻譜（注意亮點）", 'hot'),
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
