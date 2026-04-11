"""
Assignment 04 — ISP Pipeline
=================================
目標：實作簡化版 ISP：Bayer → Demosaic → White Balance → Gamma

執行：python assignment.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def generate_bayer_raw(size=256):
    """生成模擬的 Bayer RGGB raw image"""
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    rgb[:, :size//3] = [200, 50, 50]
    rgb[:, size//3:2*size//3] = [50, 200, 50]
    rgb[:, 2*size//3:] = [50, 50, 200]
    rgb[80:180, 80:180] = [220, 220, 220]

    noise = np.random.normal(0, 5, rgb.shape).astype(np.int16)
    rgb = np.clip(rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # RGGB pattern: R at (even,even), G at (even,odd) and (odd,even), B at (odd,odd)
    bayer = np.zeros((size, size), dtype=np.uint8)
    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]

    return bayer, rgb


# ── Task 1：Bilinear Demosaicing ─────────────────────────────────────────
def bilinear_demosaic(bayer: np.ndarray) -> np.ndarray:
    """
    實作 Bilinear Demosaicing（RGGB pattern）。

    每個 pixel 在 Bayer 中只有一個 channel 的值，需要從鄰居插值出另外兩個 channel。

    插值規則（以 R channel 為例）：
    - R 已知的位置（even row, even col）：直接使用，不插值
    - G 位置（橫/縱鄰居有 R）：取上下左右 R 的平均
        R_est = (R[i-1,j] + R[i+1,j] + R[i,j-1] + R[i,j+1]) / 4
    - B 位置（對角鄰居有 R）：取四個對角 R 的平均
        R_est = (R[i-1,j-1] + R[i-1,j+1] + R[i+1,j-1] + R[i+1,j+1]) / 4

    G、B channel 插值邏輯相同，只是已知位置不同。

    提示：先把每個 channel 的已知值放到獨立 array（非已知位置填 0），
    再用 cv2.filter2D 搭配適當的插值 kernel 做加權平均。
    最後 np.stack 三個 channel 成 (H, W, 3) 的 RGB 圖。
    """
    h, w = bayer.shape
    rgb = np.zeros((h, w, 3), dtype=np.float32)

    R_known = np.zeros((h, w), dtype=np.float32)
    G_known = np.zeros((h, w), dtype=np.float32)
    B_known = np.zeros((h, w), dtype=np.float32)

    R_known[0::2, 0::2] = bayer[0::2, 0::2]
    G_known[0::2, 1::2] = bayer[0::2, 1::2]
    G_known[1::2, 0::2] = bayer[1::2, 0::2]
    B_known[1::2, 1::2] = bayer[1::2, 1::2]

    # TODO: 對每個 channel 設計並套用插值 kernel
    # 最後填入 rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

    return np.clip(rgb, 0, 255).astype(np.uint8)


def task1_demosaic(bayer, gt_rgb):
    print("=== Task 1: Bilinear Demosaicing ===")

    result = bilinear_demosaic(bayer)
    cv_result = cv2.cvtColor(bayer, cv2.COLOR_BayerRG2RGB)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (bayer, "Bayer Raw", 'gray'),
        (gt_rgb, "Ground Truth RGB", None),
        (result, "Bilinear (manual)", None),
        (cv_result, "OpenCV Demosaic", None),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task1_demosaic.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_demosaic.png")

    return result


# ── Task 2：White Balance（Gray World）─────────────────────────────────
def gray_world_white_balance(img_rgb: np.ndarray) -> np.ndarray:
    """
    實作 Gray World 白平衡假設。

    假設：一張自然圖片所有像素的平均顏色應該是中性灰。

    公式：
        mean_all = (mean_R + mean_G + mean_B) / 3

        gain_R = mean_all / mean_R
        gain_G = 1.0            （G channel 作為基準，不動）
        gain_B = mean_all / mean_B

        R' = clip(R × gain_R, 0, 255)
        G' = G
        B' = clip(B × gain_B, 0, 255)

    把增益乘到對應 channel 後 clip 到 0-255。
    """
    img_float = img_rgb.astype(np.float32)

    mean_r = img_float[:,:,0].mean()
    mean_g = img_float[:,:,1].mean()
    mean_b = img_float[:,:,2].mean()
    mean_all = (mean_r + mean_g + mean_b) / 3

    gain_r = None  # TODO
    gain_g = None  # TODO
    gain_b = None  # TODO

    result = img_float.copy()
    # TODO: 把增益乘到對應 channel

    return np.clip(result, 0, 255).astype(np.uint8)


def task2_white_balance(img_rgb):
    print("=== Task 2: White Balance ===")

    img_warm = img_rgb.copy().astype(np.float32)
    img_warm[:,:,0] = np.clip(img_warm[:,:,0] * 1.4, 0, 255)
    img_warm[:,:,2] = np.clip(img_warm[:,:,2] * 0.6, 0, 255)
    img_warm = img_warm.astype(np.uint8)

    result = gray_world_white_balance(img_warm)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title) in zip(axes, [
        (img_rgb, "Original"),
        (img_warm, "Warm Light (偏黃)"),
        (result, "After AWB"),
    ]):
        ax.imshow(im)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_white_balance.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_white_balance.png")

    return result


# ── Task 3：Gamma Correction ─────────────────────────────────────────────
def apply_gamma(img: np.ndarray, gamma: float) -> np.ndarray:
    """
    實作 Gamma Correction。

    公式：
        output = (input / 255) ^ (1/γ) × 255

        γ = 2.2 → 把線性光 encoding 成人眼感知空間（sRGB 標準）
        γ = 1.0 → 不做任何校正（pass-through）

    步驟：
    1. 把 uint8 除以 255，轉成 float32 的 0-1 範圍
    2. 套用 np.power(x, 1.0 / gamma)
    3. 乘以 255，clip 到 0-255，轉回 uint8
    """
    img_float = img.astype(np.float32) / 255.0
    result = None  # TODO
    return np.clip(result, 0, 255).astype(np.uint8) if result is not None else img


def task3_gamma(img_rgb):
    print("=== Task 3: Gamma Correction ===")

    dark = (img_rgb.astype(np.float32) / 255.0) ** 2.2
    dark = (dark * 255).astype(np.uint8)

    gamma_22 = apply_gamma(dark, gamma=2.2)
    gamma_15 = apply_gamma(dark, gamma=1.5)
    gamma_10 = apply_gamma(dark, gamma=1.0)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (dark, "Linear light (dark)"),
        (gamma_10, "γ=1.0 (no correction)"),
        (gamma_15, "γ=1.5"),
        (gamma_22, "γ=2.2 (sRGB)"),
    ]):
        ax.imshow(im)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task3_gamma.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_gamma.png")


# ── Task 4（Bonus）：完整 Mini-ISP Pipeline ────────────────────────────
def task4_bonus_full_pipeline(bayer, gt_rgb):
    """
    把 Task 1~3 串成完整的 ISP pipeline：
    Bayer → Demosaic → White Balance → Gamma → 輸出

    對每個步驟後的結果計算與 ground truth 的 PSNR，
    觀察每個 stage 對畫質的影響。

    PSNR 公式：20 × log10(255 / sqrt(MSE))
    """
    print("=== Task 4 (Bonus): Full ISP Pipeline ===")

    def psnr(img1, img2):
        mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
        return 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')

    # TODO: 串接 pipeline 並在每個 stage 後計算 PSNR
    print("  → TODO: 串接 pipeline，計算各 stage 的 PSNR")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bayer, gt_rgb = generate_bayer_raw(size=256)
    print(f"Bayer raw 尺寸：{bayer.shape}")

    demosaiced = task1_demosaic(bayer, gt_rgb)

    if demosaiced.sum() > 0:
        task2_white_balance(demosaiced)
        task3_gamma(demosaiced)
    else:
        task2_white_balance(gt_rgb)
        task3_gamma(gt_rgb)

    task4_bonus_full_pipeline(bayer, gt_rgb)

    print("\n完成！查看 output/ 資料夾。")
