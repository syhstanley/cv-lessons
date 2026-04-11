"""
Assignment 08 — Video 特有處理
=================================
目標：實作 Deinterlacing（Bob / Weave / Motion-Adaptive）+ Scaling

執行：python assignment.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def generate_interlaced_pair(size=256):
    """
    生成一對模擬 interlaced fields：
    奇數行（field 1）的物體在 x=60，偶數行（field 2）的物體在 x=70
    """
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
    """
    實作 Bob Deinterlacing。

    選擇使用奇數行或偶數行的 field，對缺少的行做線性插值：
    - 若 use_odd_field=True：奇數行（0,2,4,...）直接複製，
      偶數行（1,3,5,...）用上方和下方奇數行的平均值補齊
    - 若 use_odd_field=False：反之，偶數行直接複製，奇數行插值

    邊界情況（第一行或最後一行無法雙向插值）：直接複製鄰近行。
    """
    h, w = interlaced.shape
    result = np.zeros((h, w), dtype=np.float32)

    if use_odd_field:
        result[0::2, :] = interlaced[0::2, :]
        # TODO: 對偶數行做插值（上下奇數行的平均），處理最後一行的邊界
    else:
        result[1::2, :] = interlaced[1::2, :]
        # TODO: 對奇數行做插值，處理第一行和最後一行的邊界

    return np.clip(result, 0, 255).astype(np.uint8)


def task1_bob(interlaced, frame_odd, frame_even):
    print("=== Task 1: Bob Deinterlacing ===")

    bob_odd = bob_deinterlace(interlaced, use_odd_field=True)
    bob_even = bob_deinterlace(interlaced, use_odd_field=False)

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
    """
    實作 Weave Deinterlacing。

    把兩個 field 的行合併成一個完整 frame：
    - 奇數行（0,2,4,...）來自 field1
    - 偶數行（1,3,5,...）來自 field2

    靜態場景效果很好（保留完整解析度），
    移動場景兩個 field 有時間差，合併後會出現 comb artifact。
    """
    h, w = field1.shape
    result = np.zeros((h, w), dtype=np.uint8)

    # TODO: 把 field1 的奇數行和 field2 的偶數行合入 result

    return result


def task2_weave(interlaced, frame_odd, frame_even):
    print("=== Task 2: Weave Deinterlacing ===")

    weave_result = weave_deinterlace(frame_odd, frame_even)

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
    """
    實作 Motion-Adaptive Deinterlacing。

    計算兩個 field 的絕對差值作為 motion map：
    - 靜態區域（差值小）：用 Weave（高解析度）
    - 移動區域（差值大）：用 Bob（無 comb artifact）

    步驟：
    1. 分別計算 Weave 和 Bob 的結果
    2. 計算 field1 和 field2 的差值，差值 > threshold 為 motion
    3. 用 np.where 根據 motion mask 選擇 Bob 或 Weave
    """
    weave = weave_deinterlace(field1, field2)
    bob = bob_deinterlace(interlaced, use_odd_field=True)

    diff = np.abs(field1.astype(np.int32) - field2.astype(np.int32))
    motion_mask = None  # TODO: diff > motion_threshold

    if motion_mask is None:
        return weave

    result = None  # TODO: np.where(motion_mask, bob, weave)
    return result if result is not None else weave


def task3_adaptive(interlaced, frame_odd, frame_even):
    print("=== Task 3: Motion-Adaptive Deinterlacing ===")

    weave = task2_weave(interlaced, frame_odd, frame_even)
    adaptive = motion_adaptive_deinterlace(interlaced, frame_odd, frame_even, motion_threshold=15)

    diff = np.abs(frame_odd.astype(int) - frame_even.astype(int)).astype(np.uint8)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (frame_odd, "Odd Field"),
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
    """
    比較四種縮放插值方法的品質差異。

    先把圖縮小到 1/4，再放大回原尺寸，觀察細節損失。
    對每種方法計算 PSNR（與原圖比較）。

    思考：
    - 為什麼 Nearest 有鋸齒？
    - 為什麼 Lanczos 在某些情況會有 ringing artifact？
    """
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


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    interlaced, frame_odd, frame_even = generate_interlaced_pair(size=256)
    print(f"影像尺寸：{interlaced.shape}")

    bob_odd, bob_even = task1_bob(interlaced, frame_odd, frame_even)
    weave = task2_weave(interlaced, frame_odd, frame_even)
    task3_adaptive(interlaced, frame_odd, frame_even)
    task4_scaling(frame_odd)

    print("\n完成！查看 output/ 資料夾。")
