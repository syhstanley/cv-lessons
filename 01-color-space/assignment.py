"""
Assignment 01 — 色彩空間轉換
=================================
目標：熟悉 RGB / YUV / HSV 的轉換與視覺差異

執行：python assignment.py
輸出：output/ 資料夾下的各種轉換結果圖
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)

# ── 載入測試圖片（或自動生成漸層圖）──────────────────────────────────────
def load_or_generate_image():
    """如果有圖片就用，沒有就生成彩色漸層測試圖"""
    test_path = "test.jpg"
    if os.path.exists(test_path):
        img = cv2.imread(test_path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        # 生成 256x256 彩色漸層圖
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for i in range(256):
            for j in range(256):
                img[i, j] = [i, j, 128]
        return img


# ── Task 1：RGB → YUV 手動計算 vs OpenCV ────────────────────────────────
def task1_rgb_to_yuv(img_rgb):
    print("=== Task 1: RGB → YUV ===")

    # TODO: 用 BT.601 公式手動實作 RGB → YUV 轉換
    # Y  =  0.299R + 0.587G + 0.114B
    # U  = -0.147R - 0.289G + 0.436B  (+128 offset)
    # V  =  0.615R - 0.515G - 0.100B  (+128 offset)

    img_float = img_rgb.astype(np.float32)
    R, G, B = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]

    # --- 填入你的實作 ---
    Y = None  # TODO
    U = None  # TODO
    V = None  # TODO
    # --------------------

    # OpenCV 版本（用來對照）
    img_yuv_cv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YUV)

    # 視覺化
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
    print("  → 輸出：output/task1_yuv.png")

    return img_yuv_cv


# ── Task 2：YUV Chroma Subsampling 4:4:4 → 4:2:0 ────────────────────────
def task2_chroma_subsampling(img_yuv):
    print("=== Task 2: Chroma Subsampling ===")

    Y = img_yuv[:,:,0]
    U = img_yuv[:,:,1]
    V = img_yuv[:,:,2]

    # TODO: 實作 4:2:0 subsampling
    # 步驟：把 U、V 縮小到一半（水平+垂直），再放大回原尺寸
    # 提示：cv2.resize()，用 INTER_LINEAR

    U_420 = None  # TODO: 先縮小再放大
    V_420 = None  # TODO: 先縮小再放大

    # 組合回 YUV
    # img_reconstructed = np.stack([Y, U_420, V_420], axis=2)

    # 問題：4:2:0 和 4:4:4 的視覺差異在哪裡？邊緣？色彩過渡？
    # 把差異圖存到 output/task2_diff.png
    print("  → TODO: 完成 Chroma Subsampling 並比較差異")


# ── Task 3：HSV 顏色遮罩（找出圖中特定顏色）────────────────────────────
def task3_hsv_mask(img_rgb):
    print("=== Task 3: HSV Color Masking ===")

    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    # TODO: 找出圖中「偏紅色」的區域
    # 紅色的 H 值在 0-10 或 170-180
    # 提示：cv2.inRange()

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = None  # TODO: cv2.inRange(img_hsv, lower_red1, upper_red1)
    mask2 = None  # TODO: cv2.inRange(img_hsv, lower_red2, upper_red2)
    # mask = cv2.bitwise_or(mask1, mask2)

    # 把 mask 套到原圖，只保留紅色部分
    # result = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)

    print("  → TODO: 完成 HSV 遮罩")


# ── Task 4（Bonus）：BT.601 vs BT.709 差異 ──────────────────────────────
def task4_bonus_bt601_vs_bt709(img_rgb):
    """
    BT.601 用於 SD（480p、576p）
    BT.709 用於 HD（720p、1080p）
    係數不同，轉換出的 Y 值略有差異

    BT.709 公式：
    Y = 0.2126R + 0.7152G + 0.0722B

    TODO: 實作 BT.709 Y channel，與 BT.601 Y 比較差異有多大？
    """
    print("=== Task 4 (Bonus): BT.601 vs BT.709 ===")
    print("  → TODO: 比較兩種標準的 Y channel 差異")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img_rgb = load_or_generate_image()
    print(f"圖片尺寸：{img_rgb.shape}")

    img_yuv = task1_rgb_to_yuv(img_rgb)
    task2_chroma_subsampling(img_yuv)
    task3_hsv_mask(img_rgb)
    task4_bonus_bt601_vs_bt709(img_rgb)

    print("\n完成！查看 output/ 資料夾。")
