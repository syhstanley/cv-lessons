"""
Assignment 06 — Noise Reduction
=================================
目標：實作 Temporal NR + Motion-Adaptive 機制

執行：python assignment.py

📐 公式推導參考（../formula_prove.md）：
    P7 — IIR Temporal Filter 的頻率響應（Z-Transform 分析）→ Task 1, Task 3
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import urllib.request

os.makedirs("output", exist_ok=True)

_SAMPLE_URL  = None
_SAMPLE_PATH = None


def _ensure_sample_image():
    if not os.path.exists(_SAMPLE_PATH):
        print("  → 下載 sample image（只需一次）...")
        try:
            urllib.request.urlretrieve(_SAMPLE_URL, _SAMPLE_PATH)
            print(f"  → 已儲存至 {_SAMPLE_PATH}")
        except Exception as e:
            print(f"  → 下載失敗（{e}），改用合成圖")


def generate_video_sequence(num_frames=10, size=256):
    """
    生成模擬影片：真實圖片背景 + 移動白色方塊 + Gaussian noise
    背景使用下載的 sample image（灰階），讓 Temporal NR 效果更真實可見。
    """
    #_ensure_sample_image()

    # 嘗試載入真實圖作為背景
    bg = None
    # if os.path.exists(_SAMPLE_PATH):
    #     img = cv2.imread(_SAMPLE_PATH, cv2.IMREAD_GRAYSCALE)
    #     if img is not None:
    #         bg = cv2.resize(img, (size, size)).astype(np.float32)

    if bg is None:
        # fallback：格線合成背景
        bg = np.ones((size, size), dtype=np.float32) * 100
        for i in range(0, size, 20):
            bg[i, :] = 80
            bg[:, i] = 80

    frames = []
    for t in range(num_frames):
        frame = bg.copy()
        # 移動的白色方塊（模擬運動物體）
        cx = 20 + t * 18
        cy = size // 2
        r = 22
        frame[max(0, cy-r):cy+r, max(0, cx-r):min(size, cx+r)] = 240
        # 加入 Gaussian noise（這就是 Temporal NR 要消除的對象）
        noise = np.random.normal(0, 20, frame.shape)
        frame = np.clip(frame + noise, 0, 255).astype(np.uint8)
        frames.append(frame)

    return frames

def generate_clean_sequence(num_frames=10, size=256):
    """生成無噪聲的 clean frames，用於 PSNR 計算"""
    frames = []
    bg = np.ones((size, size), dtype=np.float32) * 100
    for i in range(0, size, 20):
        bg[i, :] = 80
        bg[:, i] = 80

    for t in range(num_frames):
        frame = bg.copy()
        cx = 50 + t * 15
        cy = 128
        Y, X = np.ogrid[:size, :size]
        frame[(X - cx)**2 + (Y - cy)**2 < 25**2] = 220
        frames.append(np.clip(frame, 0, 255).astype(np.uint8))

    return frames
# ── Task 1：Simple IIR Temporal NR ──────────────────────────────────────
def iir_temporal_nr(frames: list, alpha: float) -> list:
    """
    實作簡單的 IIR Temporal NR。

    公式（IIR 低通濾波器）：
        Y(t) = α · X(t) + (1 - α) · Y(t-1)

        X(t)   = 當前 noisy frame
        Y(t)   = 當前輸出（降噪後）
        Y(t-1) = 上一個輸出（歷史累積）
        α      = blending factor（0 < α < 1）

        α → 1 : 依賴當前 frame，降噪效果弱
        α → 0 : 依賴歷史 frame，降噪效果強但移動物體有拖影

    第一個 frame 沒有 Y(t-1)，直接令 Y(0) = X(0)。

    📐 IIR 的 Z-Transform 與頻率響應分析，見 ../formula_prove.md P7
    """
    results = []
    prev_output = None

    for frame in frames:
        frame_f = frame.astype(np.float32)
        if prev_output is None:
            output = frame_f
        else:
            output = alpha* frame_f + (1-alpha)*prev_output  # TODO: IIR 混合公式

        if output is None:
            output = frame_f

        prev_output = output
        results.append(np.clip(output, 0, 255).astype(np.uint8))

    return results


def task1_iir_temporal(frames):
    print("=== Task 1: IIR Temporal NR ===")

    alpha_03 = iir_temporal_nr(frames, alpha=0.3)
    alpha_07 = iir_temporal_nr(frames, alpha=0.7)

    last = len(frames) - 1
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (frames[last], f"Noisy frame {last}"),
        (alpha_03[last], "IIR α=0.3\n large denoise, motion ghost"),
        (alpha_07[last], "IIR α=0.7\n less denoise"),
        (frames[0], "Reference frame 0"),
    ]):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task1_iir.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task1_iir.png")

    return alpha_03


# ── Task 2：Motion Detection ─────────────────────────────────────────────
def detect_motion(frame_curr: np.ndarray, frame_prev: np.ndarray,
                  threshold: int = 20) -> np.ndarray:
    """
    用 frame difference 做 motion detection。

    公式：
        diff(x, y) = |I_curr(x, y) - I_prev(x, y)|

        motion_mask(x, y) = True   if diff(x, y) > threshold
                            False  otherwise

    注意：uint8 相減會溢位，要先轉成 int32 再取絕對值。
    """
    diff = abs(frame_curr - frame_prev)        # TODO: 計算絕對差值
    motion_mask = diff>threshold  # TODO: diff > threshold
    return motion_mask


def task2_motion_detection(frames):
    print("=== Task 2: Motion Detection ===")

    t = 5
    motion = detect_motion(frames[t], frames[t-1], threshold=20)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (frames[t-1], f"Frame {t-1}", 'gray'),
        (frames[t], f"Frame {t}", 'gray'),
        (motion.astype(np.uint8) * 255 if motion is not None else np.zeros_like(frames[0]),
         "Motion Mask", 'gray'),
    ]):
        ax.imshow(im, cmap=cmap, vmin=0, vmax=255)
        ax.set_title(title)
        ax.axis('off')
    plt.savefig("output/task2_motion.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task2_motion.png")

    return motion


# ── Task 3：Motion-Adaptive Temporal NR ─────────────────────────────────
def motion_adaptive_temporal_nr(frames: list, alpha_static: float = 0.2,
                                  alpha_motion: float = 1.0,
                                  motion_threshold: int = 20) -> list:
    """
    實作 Motion-Adaptive Temporal NR。

    公式：
        α(x, y) = α_motion  if motion_mask(x, y) = True    （通常 α_motion = 1.0）
                  α_static   otherwise                       （通常 α_static = 0.2）

        Y(t, x, y) = α(x,y) · X(t, x,y) + (1 - α(x,y)) · Y(t-1, x,y)

    效果：
        靜止區域：α=0.2，強力時域混合 → 大幅降噪
        移動區域：α=1.0，直接用當前 frame → 無拖影

    步驟：
    1. 用 detect_motion 取得 motion mask（bool array）
    2. 用 np.where 建立 per-pixel 的 alpha_map
    3. 套用 IIR 公式計算 output
    """
    results = []
    prev_output = None

    for frame in frames:
        frame_f = frame.astype(np.float32)

        if prev_output is None:
            output = frame_f
        else:
            prev_uint8 = np.clip(prev_output, 0, 255).astype(np.uint8)
            motion_mask = detect_motion(frame, prev_uint8, threshold=motion_threshold)

            if motion_mask is None:
                output = alpha_static * frame_f + (1 - alpha_static) * prev_output
            else:
                alpha_map = np.where(motion_mask, alpha_motion, alpha_static)  # TODO: np.where(motion_mask, alpha_motion, alpha_static)
                if alpha_map is None:
                    output = alpha_static * frame_f + (1 - alpha_static) * prev_output
                else:
                    output = alpha_map * frame_f + (1 - alpha_map) * prev_output

        prev_output = output
        results.append(np.clip(output, 0, 255).astype(np.uint8))

    return results


def task3_adaptive(frames):
    print("=== Task 3: Motion-Adaptive Temporal NR ===")

    naive_nr = iir_temporal_nr(frames, alpha=0.3)
    adaptive_nr = motion_adaptive_temporal_nr(frames, alpha_static=0.2, alpha_motion=1.0)

    fig, axes = plt.subplots(3, 5, figsize=(20, 12))
    for col, t in enumerate([0, 2, 4, 6, 8]):
        axes[0, col].imshow(frames[t], cmap='gray', vmin=0, vmax=255)
        axes[0, col].set_title(f"Noisy t={t}")
        axes[1, col].imshow(naive_nr[t], cmap='gray', vmin=0, vmax=255)
        axes[1, col].set_title(f"IIR α=0.3 t={t}")
        axes[2, col].imshow(adaptive_nr[t], cmap='gray', vmin=0, vmax=255)
        axes[2, col].set_title(f"Adaptive t={t}")
    for ax in axes.flat:
        ax.axis('off')
    plt.suptitle("Task 3: 比較 Naive IIR vs Motion-Adaptive NR\n (motion ghost difference)")
    plt.savefig("output/task3_adaptive.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_adaptive.png")


# ── Task 4（Bonus）：PSNR 評估 NR 效果 ─────────────────────────────────
def task4_bonus_psnr(frames):
    """
    生成對應的 clean frames（同一場景但沒有 noise），
    計算各種 NR 方法的平均 PSNR 並比較：
    - Noisy（無 NR）
    - Spatial NR（單 frame，用 Bilateral filter）
    - Temporal NR（IIR，alpha=0.3）
    - Motion-Adaptive NR

    最後畫成長條圖。
    """
    print("=== Task 4 (Bonus): PSNR 評估 ===")

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    # TODO: 生成 clean frames，計算各方法 PSNR 並畫圖
    clean_frames = generate_clean_sequence(num_frames=len(frames), size=frames[0].shape[0])
    iir_frames = iir_temporal_nr(frames, alpha=0.3)
    adaptive_frames = motion_adaptive_temporal_nr(frames)

    psnr_noisy   = np.mean([psnr(frames[t], clean_frames[t]) for t in range(len(frames))])
    psnr_spatial = np.mean([psnr(cv2.bilateralFilter(frames[t], 9, 75, 9), clean_frames[t]) for t in range(len(frames))])
    psnr_iir     = np.mean([psnr(iir_frames[t], clean_frames[t]) for t in range(len(frames))])
    psnr_adp     = np.mean([psnr(adaptive_frames[t], clean_frames[t]) for t in range(len(frames))])

    print(f"  Noisy:          {psnr_noisy:.2f} dB")
    print(f"  Spatial NR:     {psnr_spatial:.2f} dB")
    print(f"  Temporal NR:    {psnr_iir:.2f} dB")
    print(f"  Adaptive NR:    {psnr_adp:.2f} dB")

    fig, ax = plt.subplots(figsize=(8, 4))
    methods = ["Noisy", "Spatial NR\n(Bilateral)", "Temporal NR\n(IIR α=0.3)", "Adaptive NR"]
    scores = [psnr_noisy, psnr_spatial, psnr_iir, psnr_adp]
    bars = ax.bar(methods, scores, color=['gray', 'steelblue', 'orange', 'green'])
    ax.set_ylabel("PSNR (dB)")
    ax.set_title("Noise Reduction ")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{score:.1f}", ha='center', va='bottom')
    plt.savefig("output/task4_psnr.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task4_psnr.png")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("生成模擬影片序列...")
    frames = generate_video_sequence(num_frames=10, size=256)
    print(f"生成 {len(frames)} frames，尺寸 {frames[0].shape}")

    task1_iir_temporal(frames)
    task2_motion_detection(frames)
    task3_adaptive(frames)
    task4_bonus_psnr(frames)

    print("\n完成！查看 output/ 資料夾。")
