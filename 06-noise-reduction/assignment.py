"""
Assignment 06 — Noise Reduction
=================================
目標：實作 Temporal NR + Motion-Adaptive 機制

執行：python assignment.py
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)


# ── 模擬影片序列 ─────────────────────────────────────────────────────────
def generate_video_sequence(num_frames=10, size=256):
    """
    生成模擬影片：靜態背景 + 移動的圓形物體 + Gaussian noise
    返回 list of frames
    """
    frames = []
    bg = np.ones((size, size), dtype=np.float32) * 100  # 灰色背景

    # 加入一些靜態紋理
    for i in range(0, size, 20):
        bg[i, :] = 80
        bg[:, i] = 80

    for t in range(num_frames):
        frame = bg.copy()

        # 移動的圓（從左到右）
        cx = 50 + t * 15
        cy = 128
        Y, X = np.ogrid[:size, :size]
        circle_mask = (X - cx)**2 + (Y - cy)**2 < 25**2
        frame[circle_mask] = 220

        # 加 Gaussian noise
        noise = np.random.normal(0, 20, frame.shape)
        frame = np.clip(frame + noise, 0, 255).astype(np.uint8)
        frames.append(frame)

    return frames


# ── Task 1：Simple IIR Temporal NR ──────────────────────────────────────
def iir_temporal_nr(frames: list, alpha: float) -> list:
    """
    TODO: 實作簡單的 IIR Temporal NR
    Output(t) = alpha * Input(t) + (1 - alpha) * Output(t-1)
    第一個 frame 直接輸出（無前一 frame）
    """
    results = []
    prev_output = None

    for t, frame in enumerate(frames):
        frame_f = frame.astype(np.float32)
        if prev_output is None:
            output = frame_f
        else:
            # TODO: 實作 IIR
            output = None  # alpha * frame_f + (1 - alpha) * prev_output

        if output is None:
            output = frame_f

        prev_output = output
        results.append(np.clip(output, 0, 255).astype(np.uint8))

    return results


def task1_iir_temporal(frames):
    print("=== Task 1: IIR Temporal NR ===")

    alpha_03 = iir_temporal_nr(frames, alpha=0.3)
    alpha_07 = iir_temporal_nr(frames, alpha=0.7)

    # 對比最後一個 frame
    last = len(frames) - 1
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (im, title) in zip(axes, [
        (frames[last], f"Noisy frame {last}"),
        (alpha_03[last], f"IIR α=0.3\n（強降噪，注意拖影）"),
        (alpha_07[last], f"IIR α=0.7\n（弱降噪，少拖影）"),
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
    TODO: 用 frame difference 做 motion detection
    返回 binary mask（True = motion area）
    """
    # TODO: 計算差異
    diff = None  # np.abs(frame_curr.astype(np.int32) - frame_prev.astype(np.int32))
    motion_mask = None  # diff > threshold

    return motion_mask


def task2_motion_detection(frames):
    print("=== Task 2: Motion Detection ===")

    # 對比第 0 和第 5 frame
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
    TODO: 實作 Motion-Adaptive Temporal NR
    - 靜態區域：用 alpha_static（強降噪）
    - 運動區域：用 alpha_motion（不混合，alpha=1 = 直接用當前 frame）
    """
    results = []
    prev_output = None

    for t, frame in enumerate(frames):
        frame_f = frame.astype(np.float32)

        if prev_output is None:
            output = frame_f
        else:
            # TODO: 計算 motion mask
            motion_mask = detect_motion(frame, np.clip(prev_output, 0, 255).astype(np.uint8),
                                         threshold=motion_threshold)

            # TODO: 根據 motion mask 選擇不同 alpha
            if motion_mask is None:
                output = alpha_static * frame_f + (1 - alpha_static) * prev_output
            else:
                # alpha_map: motion area → alpha_motion，靜態 → alpha_static
                alpha_map = None  # TODO: np.where(motion_mask, alpha_motion, alpha_static)
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

    # 展示幾個 frame 的比較
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
    plt.suptitle("Task 3: 比較 Naive IIR vs Motion-Adaptive NR\n（注意移動物體的拖影差異）")
    plt.savefig("output/task3_adaptive.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("  → output/task3_adaptive.png")


# ── Task 4（Bonus）：計算 PSNR 評估 NR 效果 ────────────────────────────
def task4_bonus_psnr(frames):
    """
    TODO: 生成 clean frames（無噪聲），計算各種 NR 的 PSNR
    比較：Noisy / Spatial NR (Bilateral) / Temporal NR / Adaptive NR
    """
    print("=== Task 4 (Bonus): PSNR 評估 ===")

    def psnr(a, b):
        mse = np.mean((a.astype(np.float32) - b.astype(np.float32))**2)
        return 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')

    # TODO: 生成對應的 clean frames 並計算各方法 PSNR
    print("  → TODO: 計算各方法 PSNR 並比較")


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
