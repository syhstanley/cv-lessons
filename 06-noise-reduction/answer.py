"""
Answer 06 — Noise Reduction
=================================
執行：python answer.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


def generate_video_sequence(num_frames=10, size=256):
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
    results = []
    prev_output = None

    for frame in frames:
        frame_f = frame.astype(np.float32)
        if prev_output is None:
            output = frame_f
        else:
            output = alpha * frame_f + (1 - alpha) * prev_output

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
        (alpha_03[last], "IIR α=0.3\n（強降噪，注意拖影）"),
        (alpha_07[last], "IIR α=0.7\n（弱降噪，少拖影）"),
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
    diff = np.abs(frame_curr.astype(np.int32) - frame_prev.astype(np.int32))
    motion_mask = diff > threshold
    return motion_mask


def task2_motion_detection(frames):
    print("=== Task 2: Motion Detection ===")

    t = 5
    motion = detect_motion(frames[t], frames[t-1], threshold=20)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (im, title, cmap) in zip(axes, [
        (frames[t-1], f"Frame {t-1}", 'gray'),
        (frames[t], f"Frame {t}", 'gray'),
        (motion.astype(np.uint8) * 255, "Motion Mask", 'gray'),
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
    results = []
    prev_output = None

    for frame in frames:
        frame_f = frame.astype(np.float32)

        if prev_output is None:
            output = frame_f
        else:
            prev_uint8 = np.clip(prev_output, 0, 255).astype(np.uint8)
            motion_mask = detect_motion(frame, prev_uint8, threshold=motion_threshold)

            # motion area → alpha_motion（= 1.0, 不混合），靜態 → alpha_static
            alpha_map = np.where(motion_mask, alpha_motion, alpha_static).astype(np.float32)
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
    plt.suptitle("Task 3: Naive IIR vs Motion-Adaptive NR")
    plt.savefig("output/task3_adaptive.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_adaptive.png")


# ── Task 4（Bonus）：PSNR 評估 ─────────────────────────────────────────
def task4_bonus_psnr(frames):
    print("=== Task 4 (Bonus): PSNR 評估 ===")

    clean_frames = generate_clean_sequence(num_frames=len(frames), size=frames[0].shape[0])

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    iir_03 = iir_temporal_nr(frames, alpha=0.3)
    adaptive = motion_adaptive_temporal_nr(frames)

    # 對所有 frame 計算平均 PSNR
    psnr_noisy   = np.mean([psnr(frames[t], clean_frames[t]) for t in range(len(frames))])
    psnr_spatial = np.mean([psnr(cv2.bilateralFilter(frames[t], 9, 75, 9), clean_frames[t]) for t in range(len(frames))])
    psnr_iir     = np.mean([psnr(iir_03[t], clean_frames[t]) for t in range(len(frames))])
    psnr_adp     = np.mean([psnr(adaptive[t], clean_frames[t]) for t in range(len(frames))])

    print(f"  Noisy:          {psnr_noisy:.2f} dB")
    print(f"  Spatial NR:     {psnr_spatial:.2f} dB")
    print(f"  Temporal NR:    {psnr_iir:.2f} dB")
    print(f"  Adaptive NR:    {psnr_adp:.2f} dB")

    fig, ax = plt.subplots(figsize=(8, 4))
    methods = ["Noisy", "Spatial NR\n(Bilateral)", "Temporal NR\n(IIR α=0.3)", "Adaptive NR"]
    scores = [psnr_noisy, psnr_spatial, psnr_iir, psnr_adp]
    bars = ax.bar(methods, scores, color=['gray', 'steelblue', 'orange', 'green'])
    ax.set_ylabel("PSNR (dB)")
    ax.set_title("Noise Reduction 效果比較")
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
