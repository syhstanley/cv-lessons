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


# ── 生成模擬 Interlaced 影像 ─────────────────────────────────────────────
def generate_interlaced_pair(size=256):
    """
    生成一對模擬 interlaced fields：
    - 靜態背景 + 移動的物體
    - Field 1（奇數行）：物體在左
    - Field 2（偶數行）：物體在右（移動了 10px）
    """
    def make_frame(cx):
        img = np.ones((size, size), dtype=np.uint8) * 80
        # 靜態格線背景
        for i in range(0, size, 16):
            img[i, :] = 60
            img[:, i] = 60
        # 移動的矩形
        cv2.rectangle(img, (cx, 80), (cx+60, 180), 220, -1)
        return img

    frame_odd = make_frame(cx=60)   # 奇數行的 frame（物體在 x=60）
    frame_even = make_frame(cx=70)  # 偶數行的 frame（物體在 x=70，移動了）

    # 建立 interlaced frame（奇數行來自 frame_odd，偶數行來自 frame_even）
    interlaced = np.zeros((size, size), dtype=np.uint8)
    interlaced[0::2, :] = frame_odd[0::2, :]   # 奇數行
    interlaced[1::2, :] = frame_even[1::2, :]  # 偶數行

    return interlaced, frame_odd, frame_even


# ── Task 1：Bob Deinterlacing ────────────────────────────────────────────
def bob_deinterlace(interlaced: np.ndarray, use_odd_field: bool = True) -> np.ndarray:
    """
    TODO: 實作 Bob Deinterlacing
    - 選用奇數行或偶數行的 field
    - 缺少的行用上下行線性插值補充
    """
    h, w = interlaced.shape
    result = np.zeros_like(interlaced, dtype=np.float32)

    if use_odd_field:
        # 奇數行直接複製
        result[0::2, :] = interlaced[0::2, :]
        # TODO: 偶數行插值（上下奇數行的平均）
        for i in range(1, h-1, 2):
            result[i, :] = None  # (result[i-1, :] + interlaced[i+1, :]) / 2
            if result[i, 0] is None or result[i].sum() == 0:
                result[i, :] = result[i-1, :]  # fallback: 複製上一行
        if h % 2 == 0:
            result[h-1, :] = result[h-2, :]  # 最後一行

    else:
        # 偶數行直接複製
        result[1::2, :] = interlaced[1::2, :]
        # TODO: 奇數行插值
        for i in range(0, h, 2):
            if i == 0:
                result[i, :] = interlaced[1, :]
            elif i == h-1 or i+1 >= h:
                result[i, :] = result[i-1, :]
            else:
                result[i, :] = None  # (interlaced[i-1, :] + interlaced[i+1, :]) / 2
                if result[i, 0] is None or result[i].sum() == 0:
                    result[i, :] = result[i-1, :]

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
    TODO: 實作 Weave Deinterlacing
    把兩個 field 的行合併成一個 frame：
    - 奇數行來自 field1
    - 偶數行來自 field2
    """
    h, w = field1.shape
    result = np.zeros((h, w), dtype=np.uint8)

    # TODO: 合併兩個 field
    # result[0::2, :] = field1[0::2, :]
    # result[1::2, :] = field2[1::2, :]

    return result


def task2_weave(interlaced, frame_odd, frame_even):
    print("=== Task 2: Weave Deinterlacing ===")

    # Weave 需要兩個 field 分開
    field1 = frame_odd.copy()
    field2 = frame_even.copy()

    weave_result = weave_deinterlace(field1, field2)

    # 觀察靜態背景（weave 很好）vs 移動物體（有 comb artifact）
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
    TODO: 實作 Motion-Adaptive Deinterlacing
    - 計算兩個 field 的差異 → motion mask
    - 靜態區域：用 Weave（高解析度）
    - 動態區域：用 Bob（無 comb artifact）
    """
    weave = weave_deinterlace(field1, field2)
    bob = bob_deinterlace(interlaced, use_odd_field=True)

    # TODO: 計算 motion map
    diff = np.abs(field1.astype(np.int32) - field2.astype(np.int32))
    motion_mask = None  # diff > motion_threshold

    if motion_mask is None:
        return weave

    # TODO: 靜態 → Weave，動態 → Bob
    result = None  # np.where(motion_mask, bob, weave)

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
        (adaptive, "Motion-Adaptive\n（TODO）"),
        (diff * 3, "Motion Map"),
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

    # 先縮小到 1/4，再放大回原尺寸
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
        # TODO: 計算 PSNR 與原圖比較
        mse = np.mean((img.astype(np.float32) - im.astype(np.float32))**2)
        psnr = 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')
        ax.set_title(f"{name}\nPSNR={psnr:.1f}dB")
        ax.axis('off')

    plt.savefig("output/task4_scaling.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_scaling.png")

    # TODO（思考題）：
    # 為什麼 Lanczos 在某些情況會有 ringing？
    # Realtek 的 Polyphase filter 是如何在品質與速度間取得平衡的？


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    interlaced, frame_odd, frame_even = generate_interlaced_pair(size=256)
    print(f"影像尺寸：{interlaced.shape}")

    bob_odd, bob_even = task1_bob(interlaced, frame_odd, frame_even)
    weave = task2_weave(interlaced, frame_odd, frame_even)
    task3_adaptive(interlaced, frame_odd, frame_even)
    task4_scaling(frame_odd)

    print("\n完成！查看 output/ 資料夾。")
