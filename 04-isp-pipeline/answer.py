"""
Answer 04 — ISP Pipeline
=================================
執行：python answer.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output_ans", exist_ok=True)

_SAMPLE_URL  = "/home/stanley/cv-lessons/04-isp-pipeline/Image"
_SAMPLE_PATH = os.path.join(_SAMPLE_URL, "test2.png")


def _ensure_sample_image():
    if not os.path.exists(_SAMPLE_PATH):
        print("  → 下載 sample image（只需一次）...")
        try:
            urllib.request.urlretrieve(_SAMPLE_URL, _SAMPLE_PATH)
            print(f"  → 已儲存至 {_SAMPLE_PATH}")
        except Exception as e:
            print(f"  → 下載失敗（{e}），改用合成圖")


def generate_bayer_raw(size=256):
    """下載真實灰階圖，沒網路時 fallback 到合成圖"""
    _ensure_sample_image()
    rgb = None
    if os.path.exists(_SAMPLE_PATH):
        img = cv2.imread(_SAMPLE_PATH)
        if img is not None:
            img = cv2.resize(img, (size, size))
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if rgb is None:
        # fallback：三色色塊
        rgb = np.zeros((size, size, 3), dtype=np.uint8)
        rgb[:, :size//3] = [200, 50, 50]
        rgb[:, size//3:2*size//3] = [50, 200, 50]
        rgb[:, 2*size//3:] = [50, 50, 200]
        rgb[size//4:3*size//4, size//4:3*size//4] = [220, 220, 220]

    # 加上感測器模擬噪聲
    noise = np.random.normal(0, 5, rgb.shape).astype(np.int16)
    rgb = np.clip(rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # RGGB pattern: R at (even,even), G at (even,odd)+(odd,even), B at (odd,odd)
    bayer = np.zeros((size, size), dtype=np.uint8)
    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]

    return bayer, rgb


# ── Task 1：Bilinear Demosaicing ─────────────────────────────────────────
def bilinear_demosaic(bayer: np.ndarray) -> np.ndarray:
    h, w = bayer.shape
    bayer_f = bayer.astype(np.float32)

    # 各 channel 已知值
    R_known = np.zeros((h, w), dtype=np.float32)
    G_known = np.zeros((h, w), dtype=np.float32)
    B_known = np.zeros((h, w), dtype=np.float32)

    R_known[0::2, 0::2] = bayer_f[0::2, 0::2]
    G_known[0::2, 1::2] = bayer_f[0::2, 1::2]
    G_known[1::2, 0::2] = bayer_f[1::2, 0::2]
    B_known[1::2, 1::2] = bayer_f[1::2, 1::2]

    # R channel interpolation kernels
    # R 已知位置：直接用；G 位置（水平垂直鄰居）：0.25 × 4方向；B 位置（對角）：0.25 × 4對角
    K_R_at_G = np.array([[0,    0.25, 0   ],
                          [0.25, 1,    0.25],
                          [0,    0.25, 0   ]], dtype=np.float32)

    K_R_at_B = np.array([[0.25, 0, 0.25],
                          [0,    1, 0   ],
                          [0.25, 0, 0.25]], dtype=np.float32)

    # 用對應 kernel 做 filter，再正規化（用 count mask）
    R_sum = cv2.filter2D(R_known, -1, K_R_at_G)
    R_cnt_G = cv2.filter2D((R_known > 0).astype(np.float32), -1, K_R_at_G)
    R_cnt_G[R_cnt_G == 0] = 1

    # 比較簡潔的做法：直接對 R_known 做 bilinear resize（忽略位置 pattern，快速近似）
    # 更正確的方式：依每個 pixel 位置選不同插值策略
    R_ch = cv2.filter2D(R_known, -1, np.array([[0.25, 0.5, 0.25],
                                                [0.5,  1.0, 0.5 ],
                                                [0.25, 0.5, 0.25]], dtype=np.float32))
    # 已知 R 位置不更動
    R_ch[0::2, 0::2] = R_known[0::2, 0::2]

    # G channel：用十字形 kernel 插值非 G 位置
    K_G = np.array([[0,    0.25, 0   ],
                    [0.25, 1,    0.25],
                    [0,    0.25, 0   ]], dtype=np.float32)
    G_ch = cv2.filter2D(G_known, -1, K_G)
    G_ch[0::2, 1::2] = G_known[0::2, 1::2]
    G_ch[1::2, 0::2] = G_known[1::2, 0::2]

    # B channel：對角插值
    B_ch = cv2.filter2D(B_known, -1, np.array([[0.25, 0.5, 0.25],
                                                [0.5,  1.0, 0.5 ],
                                                [0.25, 0.5, 0.25]], dtype=np.float32))
    B_ch[1::2, 1::2] = B_known[1::2, 1::2]

    rgb = np.stack([R_ch, G_ch, B_ch], axis=2)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def task1_demosaic(bayer, gt_rgb):
    print("=== Task 1: Bilinear Demosaicing ===")

    result = bilinear_demosaic(bayer)
    cv_result = cv2.cvtColor(bayer, cv2.COLOR_BayerRG2RGB)

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    print(f"  Manual PSNR: {psnr(result, gt_rgb):.2f} dB")
    print(f"  OpenCV PSNR: {psnr(cv_result, gt_rgb):.2f} dB")

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
    plt.savefig("output_ans/task1_demosaic.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output_ans/task1_demosaic.png")

    return result


# ── Task 2：White Balance（Gray World）─────────────────────────────────
def gray_world_white_balance(img_rgb: np.ndarray) -> np.ndarray:
    img_float = img_rgb.astype(np.float32)

    mean_r = img_float[:,:,0].mean()
    mean_g = img_float[:,:,1].mean()
    mean_b = img_float[:,:,2].mean()
    mean_all = (mean_r + mean_g + mean_b) / 3

    gain_r = mean_all / mean_r if mean_r > 0 else 1.0
    gain_g = 1.0
    gain_b = mean_all / mean_b if mean_b > 0 else 1.0

    print(f"  AWB gains — R:{gain_r:.3f}, G:{gain_g:.3f}, B:{gain_b:.3f}")

    result = img_float.copy()
    result[:,:,0] = np.clip(result[:,:,0] * gain_r, 0, 255)
    result[:,:,1] = np.clip(result[:,:,1] * gain_g, 0, 255)
    result[:,:,2] = np.clip(result[:,:,2] * gain_b, 0, 255)

    return result.astype(np.uint8)


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
    plt.savefig("output_ans/task2_white_balance.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output_ans/task2_white_balance.png")

    return result


# ── Task 3：Gamma Correction ─────────────────────────────────────────────
def apply_gamma(img: np.ndarray, gamma: float) -> np.ndarray:
    img_float = img.astype(np.float32) / 255.0
    result = np.power(img_float, 1.0 / gamma) * 255.0
    return np.clip(result, 0, 255).astype(np.uint8)


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
    plt.savefig("output_ans/task3_gamma.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output_ans/task3_gamma.png")


# ── Task 4（Bonus）：完整 Mini-ISP Pipeline ────────────────────────────
def task4_bonus_full_pipeline(bayer, gt_rgb):
    print("=== Task 4 (Bonus): Full ISP Pipeline ===")

    def psnr(img1, img2):
        mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
        return 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')

    # Pipeline
    step1 = bilinear_demosaic(bayer)
    step2 = gray_world_white_balance(step1)
    step3 = apply_gamma(step2, gamma=2.2)

    print(f"  Bayer only PSNR:        {psnr(np.stack([bayer,bayer,bayer],2), gt_rgb):.2f} dB")
    print(f"  After Demosaic PSNR:    {psnr(step1, gt_rgb):.2f} dB")
    print(f"  After WB PSNR:          {psnr(step2, gt_rgb):.2f} dB")
    print(f"  After Gamma PSNR:       {psnr(step3, gt_rgb):.2f} dB")

    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (bayer, "Bayer Raw", 'gray'),
        (gt_rgb, "Ground Truth", None),
        (step1, "①Demosaic", None),
        (step2, "②+WB", None),
        (step3, "③+Gamma", None),
    ]):
        ax.imshow(im, cmap=cmap)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output_ans/task4_full_pipeline.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output_ans/task4_full_pipeline.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bayer, gt_rgb = generate_bayer_raw(size=256)
    print(f"Bayer raw 尺寸：{bayer.shape}")

    demosaiced = task1_demosaic(bayer, gt_rgb)
    task2_white_balance(demosaiced)
    task3_gamma(demosaiced)
    task4_bonus_full_pipeline(bayer, gt_rgb)

    print("\n完成！查看 output_ans/ 資料夾。")
