"""
Answer 08 — Video 特有處理
=================================
執行：python answer.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def generate_interlaced_pair(size=256):
    def make_frame(cx):
        img = np.ones((size, size), dtype=np.uint8) * 80
        for i in range(0, size, 16):
            img[i, :] = 60
            img[:, i] = 60
        cv2.rectangle(img, (cx, 80), (cx+60, 180), 220, -1)
        return img

    frame_odd = make_frame(cx=60)
    frame_even = make_frame(cx=70)

    interlaced = np.zeros((size, size), dtype=np.uint8)
    interlaced[0::2, :] = frame_odd[0::2, :]
    interlaced[1::2, :] = frame_even[1::2, :]

    return interlaced, frame_odd, frame_even


# ── Task 1：Bob Deinterlacing ────────────────────────────────────────────
def bob_deinterlace(interlaced: np.ndarray, use_odd_field: bool = True) -> np.ndarray:
    h, w = interlaced.shape
    result = np.zeros((h, w), dtype=np.float32)

    if use_odd_field:
        # 奇數行直接複製
        result[0::2, :] = interlaced[0::2, :]
        # 偶數行：上下奇數行線性插值
        for i in range(1, h - 1, 2):
            result[i, :] = (result[i-1, :] + interlaced[i+1, :]) / 2
        # 最後一行 edge case
        if h % 2 == 0:
            result[h-1, :] = result[h-2, :]
    else:
        # 偶數行直接複製
        result[1::2, :] = interlaced[1::2, :]
        # 奇數行插值
        result[0, :] = interlaced[1, :]
        for i in range(2, h - 1, 2):
            result[i, :] = (interlaced[i-1, :] + interlaced[i+1, :]) / 2
        if h % 2 == 1:
            result[h-1, :] = result[h-2, :]

    return np.clip(result, 0, 255).astype(np.uint8)


def task1_bob(interlaced, frame_odd, frame_even):
    print("=== Task 1: Bob Deinterlacing ===")

    bob_odd = bob_deinterlace(interlaced, use_odd_field=True)
    bob_even = bob_deinterlace(interlaced, use_odd_field=False)

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    print(f"  Bob (odd field) PSNR vs frame_odd:  {psnr(bob_odd, frame_odd):.2f} dB")
    print(f"  Bob (even field) PSNR vs frame_even: {psnr(bob_even, frame_even):.2f} dB")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (interlaced, "Interlaced\n（注意梳子狀）"),
        (frame_odd, "Ground Truth\n（Odd field）"),
        (bob_odd, "Bob（Odd field）"),
        (bob_even, "Bob（Even field）"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task1_bob.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_bob.png")

    return bob_odd, bob_even


# ── Task 2：Weave Deinterlacing ──────────────────────────────────────────
def weave_deinterlace(field1: np.ndarray, field2: np.ndarray) -> np.ndarray:
    h, w = field1.shape
    result = np.zeros((h, w), dtype=np.uint8)
    result[0::2, :] = field1[0::2, :]  # 奇數行來自 field1
    result[1::2, :] = field2[1::2, :]  # 偶數行來自 field2
    return result


def task2_weave(interlaced, frame_odd, frame_even):
    print("=== Task 2: Weave Deinterlacing ===")

    field1 = frame_odd.copy()
    field2 = frame_even.copy()
    weave_result = weave_deinterlace(field1, field2)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title) in zip(axes, [
        (interlaced, "Interlaced"),
        (weave_result, "Weave（靜態好，移動有 comb）"),
        (np.abs(frame_odd.astype(int) - frame_even.astype(int)).astype(np.uint8),
         "Field Difference（差異大 = 移動）"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_weave.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_weave.png")

    return weave_result


# ── Task 3：Motion-Adaptive Deinterlacing ────────────────────────────────
def motion_adaptive_deinterlace(interlaced: np.ndarray,
                                 field1: np.ndarray,
                                 field2: np.ndarray,
                                 motion_threshold: int = 20) -> np.ndarray:
    weave = weave_deinterlace(field1, field2)
    bob = bob_deinterlace(interlaced, use_odd_field=True)

    # Motion map：field 差異大的地方是移動區域
    diff = np.abs(field1.astype(np.int32) - field2.astype(np.int32))
    motion_mask = diff > motion_threshold

    # 靜態 → Weave（高解析度），動態 → Bob（無 comb）
    result = np.where(motion_mask, bob, weave).astype(np.uint8)

    return result


def task3_adaptive(interlaced, frame_odd, frame_even):
    print("=== Task 3: Motion-Adaptive Deinterlacing ===")

    weave = task2_weave(interlaced, frame_odd, frame_even)
    adaptive = motion_adaptive_deinterlace(interlaced, frame_odd, frame_even, motion_threshold=15)

    diff = np.abs(frame_odd.astype(int) - frame_even.astype(int)).astype(np.uint8)

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    print(f"  Weave PSNR vs frame_odd:    {psnr(weave, frame_odd):.2f} dB")
    print(f"  Adaptive PSNR vs frame_odd: {psnr(adaptive, frame_odd):.2f} dB")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (frame_odd, "Odd Field (GT)"),
        (weave, "Weave（有 comb）"),
        (adaptive, "Motion-Adaptive"),
        (diff * 3, "Motion Map ×3"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_adaptive.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_adaptive.png")


# ── Task 4：Scaling / Interpolation 比較 ────────────────────────────────
def task4_scaling(img):
    print("=== Task 4: Scaling Interpolation 比較 ===")

    h, w = img.shape
    small = cv2.resize(img, (w//4, h//4))

    methods = {
        "Nearest": cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST),
        "Bilinear": cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR),
        "Bicubic":  cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC),
        "Lanczos":  cv2.resize(small, (w, h), interpolation=cv2.INTER_LANCZOS4),
    }

    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Original")
    axes[0].axis('off')

    for ax, (name, im) in zip(axes[1:], methods.items()):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        mse = np.mean((img.astype(np.float32) - im.astype(np.float32))**2)
        psnr = 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')
        ax.set_title(f"{name}\nPSNR={psnr:.1f}dB")
        ax.axis('off')

    plt.savefig("output/task4_scaling.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_scaling.png")
    # Lanczos ringing：sinc 函數的旁波瓣，在強邊緣兩側出現振盪
    # Realtek Polyphase：把 filter 拆成多相（每個 phase 對應一個 sub-pixel 位置），
    # 用查表快速計算，比直接 Lanczos 快得多


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    interlaced, frame_odd, frame_even = generate_interlaced_pair(size=256)
    print(f"影像尺寸：{interlaced.shape}")

    bob_odd, bob_even = task1_bob(interlaced, frame_odd, frame_even)
    weave = task2_weave(interlaced, frame_odd, frame_even)
    task3_adaptive(interlaced, frame_odd, frame_even)
    task4_scaling(frame_odd)

    print("\n完成！查看 output/ 資料夾。")
