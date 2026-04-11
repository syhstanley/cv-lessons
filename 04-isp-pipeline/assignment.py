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


# ── 生成模擬 Bayer Raw Image ─────────────────────────────────────────────
def generate_bayer_raw(size=256):
    """
    生成模擬的 Bayer RGGB raw image
    實際上從 RGB 圖片反向生成，模擬 sensor 輸出
    """
    # 創建測試 RGB 圖片
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    # 左半：紅色，右半：藍色，中間帶：綠色
    rgb[:, :size//3] = [200, 50, 50]
    rgb[:, size//3:2*size//3] = [50, 200, 50]
    rgb[:, 2*size//3:] = [50, 50, 200]
    # 加一個白色矩形
    rgb[80:180, 80:180] = [220, 220, 220]

    # 加 sensor noise
    noise = np.random.normal(0, 5, rgb.shape).astype(np.int16)
    rgb = np.clip(rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # 轉成 Bayer RGGB（每個 pixel 只保留一個 channel）
    bayer = np.zeros((size, size), dtype=np.uint8)
    # RGGB pattern:
    # R G R G ...
    # G B G B ...
    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]  # R
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]  # G
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]  # G
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]  # B

    return bayer, rgb  # 同時返回原始 RGB 作為 ground truth


# ── Task 1：Bilinear Demosaicing ─────────────────────────────────────────
def bilinear_demosaic(bayer: np.ndarray) -> np.ndarray:
    """
    TODO: 實作 Bilinear Demosaicing（RGGB pattern）

    RGGB 位置：
    - R  在 (even row, even col)
    - G1 在 (even row, odd col)
    - G2 在 (odd row, even col)
    - B  在 (odd row, odd col)

    插值規則（以 R channel 為例）：
    - R 位置本身：直接取值
    - G 位置：取上下左右的 R 平均
    - B 位置：取四個對角的 R 平均

    提示：用 cv2.filter2D 配合不同 kernel 可以優雅地實作
    """
    h, w = bayer.shape
    rgb = np.zeros((h, w, 3), dtype=np.float32)

    # 先把每個 channel 的已知值填入
    R_known = np.zeros((h, w), dtype=np.float32)
    G_known = np.zeros((h, w), dtype=np.float32)
    B_known = np.zeros((h, w), dtype=np.float32)

    R_known[0::2, 0::2] = bayer[0::2, 0::2]
    G_known[0::2, 1::2] = bayer[0::2, 1::2]
    G_known[1::2, 0::2] = bayer[1::2, 0::2]
    B_known[1::2, 1::2] = bayer[1::2, 1::2]

    # TODO: 用 kernel 插值每個 channel
    # R channel 插值 kernel：
    #   R 位置 → kernel [1]
    #   G 位置（水平/垂直鄰居）→ kernel [0.25, 0, 0.25; 0, 0, 0; 0.25, 0, 0.25] 或類似
    #   B 位置（對角鄰居）→ kernel [[0.25, 0, 0.25], [0, 0, 0], [0.25, 0, 0.25]]

    # 簡化版：直接用 cv2.resize 或鄰居平均
    # （完整版應該分別對 R/G/B 位置用不同 kernel）

    # TODO: 填入 rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

    return np.clip(rgb, 0, 255).astype(np.uint8)


def task1_demosaic(bayer, gt_rgb):
    print("=== Task 1: Bilinear Demosaicing ===")

    result = bilinear_demosaic(bayer)

    # OpenCV 內建 demosaic 作為對照
    cv_result = cv2.cvtColor(bayer, cv2.COLOR_BayerRG2RGB)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    data = [
        (bayer, "Bayer Raw", 'gray'),
        (gt_rgb, "Ground Truth RGB", None),
        (result, "Bilinear (manual)", None),
        (cv_result, "OpenCV Demosaic", None),
    ]
    for ax, (im, title, cmap) in zip(axes, data):
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
    TODO: 實作 Gray World 白平衡
    假設：整張圖的平均顏色應該是灰色
    計算各 channel 的增益讓平均值相等
    """
    img_float = img_rgb.astype(np.float32)

    mean_r = img_float[:,:,0].mean()
    mean_g = img_float[:,:,1].mean()
    mean_b = img_float[:,:,2].mean()
    mean_all = (mean_r + mean_g + mean_b) / 3

    # TODO: 計算各 channel 增益
    gain_r = None  # TODO: mean_all / mean_r
    gain_g = None  # TODO: 1.0
    gain_b = None  # TODO: mean_all / mean_b

    result = img_float.copy()
    # TODO: 套用增益
    # result[:,:,0] *= gain_r
    # ...

    return np.clip(result, 0, 255).astype(np.uint8)


def task2_white_balance(img_rgb):
    print("=== Task 2: White Balance ===")

    # 模擬偏黃光源（增強 R、降低 B）
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
    TODO: 實作 Gamma Correction
    output = (input / 255)^(1/gamma) * 255
    注意：要先把 uint8 → float，做完再轉回 uint8
    """
    img_float = img.astype(np.float32) / 255.0
    # TODO: 套用 gamma
    result = None  # np.power(img_float, 1.0 / gamma) * 255
    return np.clip(result, 0, 255).astype(np.uint8) if result is not None else img


def task3_gamma(img_rgb):
    print("=== Task 3: Gamma Correction ===")

    # 模擬線性光（偏暗）→ 加 gamma encoding
    dark = (img_rgb.astype(np.float32) / 255.0) ** 2.2  # 模擬線性光
    dark = (dark * 255).astype(np.uint8)

    gamma_22 = apply_gamma(dark, gamma=2.2)
    gamma_15 = apply_gamma(dark, gamma=1.5)
    gamma_10 = apply_gamma(dark, gamma=1.0)  # 不做 gamma

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
    TODO: 把 Task 1~3 串起來，做完整的 ISP pipeline：
    Bayer → Demosaic → WB → Gamma → 輸出
    計算輸出與 ground truth 的 PSNR
    """
    print("=== Task 4 (Bonus): Full ISP Pipeline ===")

    # PSNR 計算
    def psnr(img1, img2):
        mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
        if mse == 0:
            return float('inf')
        return 20 * np.log10(255.0 / np.sqrt(mse))

    # TODO: 串接 pipeline 並計算 PSNR
    print("  → TODO: 串接 pipeline，計算 PSNR")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bayer, gt_rgb = generate_bayer_raw(size=256)
    print(f"Bayer raw 尺寸：{bayer.shape}")
    print(f"Ground truth RGB 尺寸：{gt_rgb.shape}")

    demosaiced = task1_demosaic(bayer, gt_rgb)

    if demosaiced.sum() > 0:  # 如果 Task 1 有實作
        task2_white_balance(demosaiced)
        task3_gamma(demosaiced)
    else:
        task2_white_balance(gt_rgb)
        task3_gamma(gt_rgb)

    task4_bonus_full_pipeline(bayer, gt_rgb)

    print("\n完成！查看 output/ 資料夾。")
