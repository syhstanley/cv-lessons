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
import urllib.request

os.makedirs("output", exist_ok=True)

_SAMPLE_URL  = ""
_SAMPLE_PATH = os.path.join(_SAMPLE_URL, "test2.jpg")


def _ensure_sample_image():
    if not os.path.exists(_SAMPLE_PATH):
        print("  → 下載 sample image（只需一次）...")
        try:
            urllib.request.urlretrieve(_SAMPLE_URL, _SAMPLE_PATH)
            print(f"  → 已儲存至 {_SAMPLE_PATH}")
        except Exception as e:
            print(f"  → 下載失敗（{e}），改用合成圖")


def generate_interlaced_pair(size=256):
    def make_frame(center_x):
        img = np.ones((size, size), dtype=np.uint8) * 80
        for i in range(0, size, 16):
            img[i, :] = 60
            img[:, i] = 60

        cy = 130
        r = 48
        cv2.circle(img, (center_x, cy), r, 220, -1)
        return img

    frame_odd = make_frame(center_x=90)
    frame_even = make_frame(center_x=100)

    interlaced = np.zeros((size, size), dtype=np.uint8)
    interlaced[0::2, :] = frame_odd[0::2, :]
    interlaced[1::2, :] = frame_even[1::2, :]

    return interlaced, frame_odd, frame_even

# ── Task 1：Bob Deinterlacing ────────────────────────────────────────────
def bob_deinterlace(interlaced: np.ndarray, use_odd_field: bool = True) -> np.ndarray:
    """
    實作 Bob Deinterlacing。

    選擇使用奇數行或偶數行的 field，對缺少的行做線性插值：

    公式（以 use_odd_field=True 為例）：
        奇數行  i = 0, 2, 4, ... ：Output[i] = Interlaced[i]        （直接複製）
        偶數行  i = 1, 3, 5, ... ：Output[i] = (Output[i-1] + Interlaced[i+1]) / 2  （線性插值）
        最後一行（若無下方鄰居）：Output[H-1] = Output[H-2]          （複製上一行）

    use_odd_field=False 時對換奇偶邏輯，第一行無上方鄰居時複製下一行。
    """
    h, w = interlaced.shape
    result = np.zeros((h, w), dtype=np.float32)

    if use_odd_field:
        result[0::2, :] = interlaced[0::2, :]
        # TODO: 對偶數行做插值（上下奇數行的平均），處理最後一行的邊界
        for i in range(1, h-1, 2):
            result[i, :] = (result[i-1, :] + interlaced[i+1, :])/2
        if h % 2 == 0:
            result[h-1, :] = result[h-2, :]

    else:
        result[1::2, :] = interlaced[1::2, :]
        # TODO: 對奇數行做插值，處理第一行和最後一行的邊界
        result[0, :] = interlaced[1, :]
        for i in range(2, h-1, 2):
            result[i, :] = (result[i-1, :] + interlaced[i+1, :])/2
        if h % 2 == 1:
            result[h-1, :] = result[h-2, :]

    return np.clip(result, 0, 255).astype(np.uint8)


def task1_bob(interlaced, frame_odd, frame_even):
    print("=== Task 1: Bob Deinterlacing ===")

    bob_odd = bob_deinterlace(interlaced, use_odd_field=True)
    bob_even = bob_deinterlace(interlaced, use_odd_field=False)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (interlaced, "Interlaced\n comb"),
        (frame_odd, "Ground Truth\n Odd field"),
        (bob_odd, "Bob Odd field"),
        (bob_even, "Bob Even field"),
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
    result[0::2, :] = field1[0::2, :]
    result[1::2, :] = field2[1::2, :]

    return result


def task2_weave(interlaced, frame_odd, frame_even):
    print("=== Task 2: Weave Deinterlacing ===")

    weave_result = weave_deinterlace(frame_odd, frame_even)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title) in zip(axes, [
        (interlaced, "Interlaced"),
        (weave_result, "Weave(static good, moving has comb)"),
        (np.abs(frame_odd.astype(int) - frame_even.astype(int)).astype(np.uint8),
         "Field Difference"),
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

    公式：
        diff(x, y)        = |field1(x, y) - field2(x, y)|
        motion(x, y)      = True   if diff(x, y) > threshold
                            False  otherwise

        Output(x, y) = Bob(x, y)    if motion(x, y)   （動態：無拖影）
                       Weave(x, y)  otherwise          （靜態：高解析度）

    步驟：
    1. 分別算出 Weave 和 Bob 的結果
    2. 計算兩個 field 的差值，超過 threshold 視為移動
    3. 用 np.where(motion_mask, bob, weave) 做 per-pixel 選擇
    """
    weave = weave_deinterlace(field1, field2)
    bob = bob_deinterlace(interlaced, use_odd_field=True)

    diff = np.abs(field1.astype(np.int32) - field2.astype(np.int32))
    motion_mask = np.where(diff>motion_threshold, True, False)  # TODO: diff > motion_threshold

    if motion_mask is None:
        return weave

    result = np.where(motion_mask, bob, weave)  # TODO: np.where(motion_mask, bob, weave)
    return result if result is not None else weave


def task3_adaptive(interlaced, frame_odd, frame_even):
    print("=== Task 3: Motion-Adaptive Deinterlacing ===")

    weave = task2_weave(interlaced, frame_odd, frame_even)
    adaptive = motion_adaptive_deinterlace(interlaced, frame_odd, frame_even, motion_threshold=15)

    diff = np.abs(frame_odd.astype(int) - frame_even.astype(int)).astype(np.uint8)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (frame_odd, "Odd Field"),
        (weave, "Weave comb"),
        (adaptive, "Motion-Adaptive"),
        (diff * 3, "Motion Map *3"),
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
