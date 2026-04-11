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
import urllib.request

os.makedirs("output", exist_ok=True)

_SAMPLE_URL  = "/home/stanley/cv-lessons/01-color-space/Image"
_SAMPLE_PATH = os.path.join(_SAMPLE_URL, "test.png")


def _ensure_sample_image():
    if not os.path.exists(_SAMPLE_PATH):
        print("  → 下載 sample image（只需一次）...")
        try:
            urllib.request.urlretrieve(_SAMPLE_URL, _SAMPLE_PATH)
            print(f"  → 已儲存至 {_SAMPLE_PATH}")
        except Exception as e:
            print(f"  → 下載失敗（{e}），改用合成圖")


def load_or_generate_image():
    """下載真實彩色圖，沒網路時 fallback 到漸層合成圖"""
    _ensure_sample_image()
    if os.path.exists(_SAMPLE_PATH):
        img = cv2.imread(_SAMPLE_PATH)
        if img is not None:
            img = cv2.resize(img, (512, 512))
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # fallback：彩色漸層合成圖
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            img[i, j] = [i // 2, j // 2, 128]
    return img


# ── Task 1：RGB → YUV 手動計算 vs OpenCV ────────────────────────────────
def task1_rgb_to_yuv(img_rgb):
    print("=== Task 1: RGB → YUV ===")

    # 用 BT.601 公式手動計算 Y、U、V channel
    # 公式：
    #   Y  =  0.299R + 0.587G + 0.114B
    #   U  = -0.147R - 0.289G + 0.436B  （結果加 128 offset）
    #   V  =  0.615R - 0.515G - 0.100B  （結果加 128 offset）
    # 注意先把 img 轉成 float32 再計算，避免整數溢位

    img_float = img_rgb.astype(np.float32)
    R, G, B = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]

    Y = 0.299*R + 0.587*G + 0.114*B  # TODO
    U =-0.147*R - 0.289*G + 0.436*B + 128  # TODO
    V = 0.615*R - 0.515*G - 0.100*B + 128  # TODO

    Y = np.clip(Y, 0, 255).astype(np.uint8)
    U = np.clip(U, 0, 255).astype(np.uint8)
    V = np.clip(V, 0, 255).astype(np.uint8)

    img_yuv = np.stack([Y,U,V], axis=2)

    # OpenCV 版本（用來對照）
    img_yuv_cv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YUV)
    diff = np.abs(img_yuv.astype(np.int32) - img_yuv_cv.astype(np.int32))
    diff = 255 - diff.astype(np.uint8)
    print(f"  手動 vs OpenCV 最大差異：{diff.max()}（因浮點係數略有不同）")

    fig, axes = plt.subplots(2, 5, figsize=(16, 8))
    axes[0][0].imshow(img_rgb)
    axes[0][0].set_title("Original RGB")

    axes[1][0].imshow(diff)
    axes[1][0].set_title("Difference")

    axes[0][1].imshow(img_yuv_cv)
    axes[0][1].set_title("CV2 YUV")

    axes[0][2].imshow(img_yuv_cv[:,:,0], cmap='gray')
    axes[0][2].set_title("CV2 Y (Luma)")

    axes[0][3].imshow(img_yuv_cv[:,:,1], cmap='RdBu')
    axes[0][3].set_title("CV2 U (Cb)")

    axes[0][4].imshow(img_yuv_cv[:,:,2], cmap='RdBu')
    axes[0][4].set_title("CV2 V (Cr)")

    axes[1][1].imshow(img_yuv)
    axes[1][1].set_title("Manual YUV ")

    axes[1][2].imshow(img_yuv[:,:,0], cmap='gray')
    axes[1][2].set_title("Y (Luma)")

    axes[1][3].imshow(img_yuv[:,:,1], cmap='RdBu')
    axes[1][3].set_title("U (Cb)")

    axes[1][4].imshow(img_yuv[:,:,2], cmap='RdBu')
    axes[1][4].set_title("V (Cr)")
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

    # 實作 4:2:0 chroma subsampling：
    # 把 U 和 V channel 縮小成原來的 1/2（水平和垂直各縮一半），
    # 再放大回原尺寸，模擬 subsampling 的失真效果。
    # 縮放用 cv2.resize，插值方式用 INTER_LINEAR。
    # 最後把結果和原始 4:4:4 比較，觀察色彩細節的差異在哪裡。
    h, w = Y.shape

    # down sample
    U_sub = cv2.resize(U, (w//2, h//2), interpolation = cv2.INTER_LINEAR)
    V_sub = cv2.resize(V, (w//2, h//2), interpolation = cv2.INTER_LINEAR)

    # up sample
    U_420 = cv2.resize(U_sub, (w, h), interpolation = cv2.INTER_LINEAR)  # TODO
    V_420 = cv2.resize(V_sub, (w, h), interpolation = cv2.INTER_LINEAR)  # TODO

    img_420 = np.stack([Y, U_420, V_420], axis=2)
    img_420_rgb = cv2.cvtColor(img_420, cv2.COLOR_YUV2RGB)
    img_444 = np.stack([Y, U, V], axis=2)
    img_444_rgb = cv2.cvtColor(img_444, cv2.COLOR_YUV2RGB)

    diff_u = 255 - np.abs(U.astype(np.int32) - U_420.astype(np.int32)).astype(np.uint8)
    diff_v = 255 - np.abs(V.astype(np.int32) - V_420.astype(np.int32)).astype(np.uint8)
    diff_rgb = 255 - np.abs(img_444.astype(np.int32) - img_420.astype(np.int32)).astype(np.uint8)

    fig, axes = plt.subplots(3, 5, figsize=(20, 12))
    axes[0][0].imshow(img_444_rgb)
    axes[0][0].set_title("4:4:4 (RGB)")
    axes[1][0].imshow(img_420_rgb)
    axes[1][0].set_title("4:2:0 (RGB)")
    axes[2][0].imshow(diff_rgb, cmap='gray')
    axes[2][0].set_title("Difference")

    axes[0][1].imshow(img_444)
    axes[0][1].set_title("4:4:4 (YUV)")
    axes[1][1].imshow(img_420)
    axes[1][1].set_title("4:2:0 (YUV)")

    axes[0][2].imshow(img_444[:,:,0], cmap='gray')
    axes[0][2].set_title("4:4:4 (Y)")
    axes[1][2].imshow(img_420[:,:,0], cmap='gray')
    axes[1][2].set_title("4:2:0 (Y)")

    axes[0][3].imshow(img_444[:,:,1], cmap='RdBu')
    axes[0][3].set_title("4:4:4 (U)")
    axes[1][3].imshow(img_420[:,:,1], cmap='RdBu')
    axes[1][3].set_title("4:2:0 (U)")
    axes[2][3].imshow(diff_u, cmap='gray')
    axes[2][3].set_title("U Difference")
    
    axes[0][4].imshow(img_444[:,:,2], cmap='RdBu')
    axes[0][4].set_title("4:4:4 (V)")
    axes[1][4].imshow(img_420[:,:,2], cmap='RdBu')
    axes[1][4].set_title("4:2:0 (V)")
    axes[2][4].imshow(diff_v, cmap='gray')
    axes[2][4].set_title("V Difference")
    
    plt.savefig("output/task2_chroma_subsampling.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_chroma_subsampling.png")


# ── Task 3：HSV 顏色遮罩（找出圖中特定顏色）────────────────────────────
def task3_hsv_mask(img_rgb):
    print("=== Task 3: HSV Color Masking ===")

    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    # 在 HSV 空間中找出圖片裡的紅色區域：
    # 紅色的 H 值分佈在兩個範圍（0-10 和 170-180），需要分別建立 mask 再合併。
    # 使用 cv2.inRange 建立每個範圍的 binary mask，
    # 再用 cv2.bitwise_or 合併，最後用 cv2.bitwise_and 套到原圖上。

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)  # TODO
    mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)  # TODO
    mask = cv2.bitwise_or(mask1, mask2)
    img_masked = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (img_rgb, "Original", None),
        (mask, "Red Mask", 'gray'),
        (img_masked, "Masked Result", None),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_hsv_mask.png", dpi=120, bbox_inches='tight')
    plt.close()

# ── Task 4（Bonus）：BT.601 vs BT.709 差異 ──────────────────────────────
def task4_bonus_bt601_vs_bt709(img_rgb):
    """
    BT.601 用於 SD（480p、576p），BT.709 用於 HD（720p、1080p），
    兩者的 Y channel 係數不同：
      BT.601：Y = 0.299R + 0.587G + 0.114B
      BT.709：Y = 0.2126R + 0.7152G + 0.0722B

    分別計算兩種標準的 Y channel，用差異圖（差值 ×5 放大）觀察影響最大的區域，
    並計算最大差異和平均差異。
    """
    print("=== Task 4 (Bonus): BT.601 vs BT.709 ===")
    print("  → TODO: 比較兩種標準的 Y channel 差異")
    img_float = img_rgb.astype(np.float32)
    R, G, B = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]
    Y_601 = 0.299*R + 0.587*G + 0.114*B
    Y_709 = 0.2126*R + 0.7152*G + 0.0722*B
    diff = np.abs(Y_601 - Y_709)
    print(f"  Y channel 最大差異：{diff.max():.2f}")
    print(f"  Y channel 平均差異：{diff.mean():.4f}")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (img_rgb, "Original", None),
        (Y_601, "BT.601 Y", 'gray'),
        (Y_709, "BT.709 Y", 'gray'),
        (diff, "Difference", 'gray'),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task4_bonus_bt601_vs_bt709.png", dpi=120, bbox_inches='tight')
    plt.close()



# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img_rgb = load_or_generate_image()
    print(f"圖片尺寸：{img_rgb.shape}")

    img_yuv = task1_rgb_to_yuv(img_rgb)
    task2_chroma_subsampling(img_yuv)
    task3_hsv_mask(img_rgb)
    task4_bonus_bt601_vs_bt709(img_rgb)

    print("\n完成！查看 output/ 資料夾。")