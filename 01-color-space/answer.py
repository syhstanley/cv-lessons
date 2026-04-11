"""
Answer 01 — 色彩空間轉換
=================================
執行：python answer.py
輸出：output/ 資料夾下的各種轉換結果圖
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def load_or_generate_image():
    test_path = "test.jpg"
    if os.path.exists(test_path):
        img = cv2.imread(test_path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for i in range(256):
            for j in range(256):
                img[i, j] = [i, j, 128]
        return img


# ── Task 1：RGB → YUV 手動計算 vs OpenCV ────────────────────────────────
def task1_rgb_to_yuv(img_rgb):
    print("=== Task 1: RGB → YUV ===")

    img_float = img_rgb.astype(np.float32)
    R, G, B = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]

    Y = 0.299 * R + 0.587 * G + 0.114 * B
    U = -0.147 * R - 0.289 * G + 0.436 * B + 128
    V = 0.615 * R - 0.515 * G - 0.100 * B + 128

    Y = np.clip(Y, 0, 255).astype(np.uint8)
    U = np.clip(U, 0, 255).astype(np.uint8)
    V = np.clip(V, 0, 255).astype(np.uint8)

    img_yuv_manual = np.stack([Y, U, V], axis=2)
    img_yuv_cv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YUV)

    # 驗證差異
    diff = np.abs(img_yuv_manual.astype(np.int32) - img_yuv_cv.astype(np.int32))
    print(f"  手動 vs OpenCV 最大差異：{diff.max()}（因浮點係數略有不同）")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes[0].imshow(img_rgb)
    axes[0].set_title("Original RGB")
    axes[1].imshow(img_yuv_cv[:,:,0], cmap='gray')
    axes[1].set_title("Y Channel (Luma)")
    axes[2].imshow(img_yuv_cv[:,:,1], cmap='RdBu')
    axes[2].set_title("U Channel (Cb)")
    axes[3].imshow(img_yuv_cv[:,:,2], cmap='RdBu')
    axes[3].set_title("V Channel (Cr)")
    plt.suptitle("Task 1: RGB → YUV Channels")
    plt.savefig("output/task1_yuv.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_yuv.png")

    return img_yuv_cv


# ── Task 2：YUV Chroma Subsampling 4:4:4 → 4:2:0 ────────────────────────
def task2_chroma_subsampling(img_yuv):
    print("=== Task 2: Chroma Subsampling ===")

    Y = img_yuv[:,:,0]
    U = img_yuv[:,:,1]
    V = img_yuv[:,:,2]
    h, w = Y.shape

    # 4:2:0：U/V 水平+垂直各縮小一半，再放大回原尺寸
    U_small = cv2.resize(U, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
    V_small = cv2.resize(V, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)

    U_420 = cv2.resize(U_small, (w, h), interpolation=cv2.INTER_LINEAR)
    V_420 = cv2.resize(V_small, (w, h), interpolation=cv2.INTER_LINEAR)

    img_444 = np.stack([Y, U, V], axis=2)
    img_420 = np.stack([Y, U_420, V_420], axis=2)

    # 計算差異（只看 U/V channel）
    diff_u = np.abs(U.astype(np.int32) - U_420.astype(np.int32)).astype(np.uint8)
    diff_v = np.abs(V.astype(np.int32) - V_420.astype(np.int32)).astype(np.uint8)

    # 轉回 RGB 比較
    rgb_444 = cv2.cvtColor(img_444, cv2.COLOR_YUV2RGB)
    rgb_420 = cv2.cvtColor(img_420, cv2.COLOR_YUV2RGB)
    diff_rgb = np.abs(rgb_444.astype(np.int32) - rgb_420.astype(np.int32)).astype(np.uint8)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (rgb_444, "4:4:4 (原始)", None),
        (rgb_420, "4:2:0 (Subsampled)", None),
        (diff_rgb * 5, "RGB 差異 ×5", None),
        (diff_u * 5, "U channel 差異 ×5", 'hot'),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.suptitle("Task 2: 4:4:4 vs 4:2:0 Chroma Subsampling")
    plt.savefig("output/task2_subsampling.png", dpi=120, bbox_inches='tight')
    plt.close()
    print(f"  U channel 最大差異：{diff_u.max()}")
    print("  → output/task2_subsampling.png")


# ── Task 3：HSV 顏色遮罩（找出圖中特定顏色）────────────────────────────
def task3_hsv_mask(img_rgb):
    print("=== Task 3: HSV Color Masking ===")

    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    # 紅色的 H 值在 0-10 或 170-180
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    result = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (img_rgb, "Original", None),
        (mask, "Red Mask", 'gray'),
        (result, "Masked Result", None),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_hsv_mask.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_hsv_mask.png")


# ── Task 4（Bonus）：BT.601 vs BT.709 差異 ──────────────────────────────
def task4_bonus_bt601_vs_bt709(img_rgb):
    print("=== Task 4 (Bonus): BT.601 vs BT.709 ===")

    img_float = img_rgb.astype(np.float32)
    R, G, B = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]

    # BT.601
    Y_601 = 0.299 * R + 0.587 * G + 0.114 * B

    # BT.709
    Y_709 = 0.2126 * R + 0.7152 * G + 0.0722 * B

    diff = np.abs(Y_601 - Y_709)
    print(f"  Y channel 最大差異：{diff.max():.2f}")
    print(f"  Y channel 平均差異：{diff.mean():.4f}")
    print("  主要差異：BT.709 對綠色權重更高（0.7152 vs 0.587）")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title) in zip(axes, [
        (np.clip(Y_601, 0, 255).astype(np.uint8), "BT.601 Y"),
        (np.clip(Y_709, 0, 255).astype(np.uint8), "BT.709 Y"),
        (np.clip(diff * 5, 0, 255).astype(np.uint8), "差異 ×5"),
    ]):
        ax.imshow(im, cmap='gray')
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task4_bt601_vs_bt709.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_bt601_vs_bt709.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img_rgb = load_or_generate_image()
    print(f"圖片尺寸：{img_rgb.shape}")

    img_yuv = task1_rgb_to_yuv(img_rgb)
    task2_chroma_subsampling(img_yuv)
    task3_hsv_mask(img_rgb)
    task4_bonus_bt601_vs_bt709(img_rgb)

    print("\n完成！查看 output/ 資料夾。")
