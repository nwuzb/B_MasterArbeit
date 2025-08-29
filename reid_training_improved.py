#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ReID模型训练改进版本 - 针对目标尺寸优化
包含训练结果可视化和多尺寸处理策略
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json

def analyze_bbox_sizes(gt_file_path, save_dir):
    """
    分析边界框尺寸分布，为ReID模型提供尺寸选择依据
    """
    sizes = []
    areas = []
    aspect_ratios = []
    
    # 读取GT数据
    with open(gt_file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 6:
                w, h = float(parts[4]), float(parts[5])
                if w > 0 and h > 0:
                    sizes.append((w, h))
                    areas.append(w * h)
                    aspect_ratios.append(w / h)
    
    # 统计分析
    widths = [s[0] for s in sizes]
    heights = [s[1] for s in sizes]
    
    stats = {
        'total_objects': len(sizes),
        'width_stats': {
            'min': min(widths), 'max': max(widths), 
            'mean': np.mean(widths), 'std': np.std(widths),
            'percentiles': np.percentile(widths, [10, 25, 50, 75, 90]).tolist()
        },
        'height_stats': {
            'min': min(heights), 'max': max(heights),
            'mean': np.mean(heights), 'std': np.std(heights),
            'percentiles': np.percentile(heights, [10, 25, 50, 75, 90]).tolist()
        },
        'area_stats': {
            'min': min(areas), 'max': max(areas),
            'mean': np.mean(areas), 'std': np.std(areas),
            'percentiles': np.percentile(areas, [10, 25, 50, 75, 90]).tolist()
        }
    }
    
    # 保存统计结果
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, 'bbox_size_analysis.json'), 'w') as f:
        json.dump(stats, f, indent=2)
    
    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 宽度分布
    axes[0,0].hist(widths, bins=50, alpha=0.7, color='blue')
    axes[0,0].axvline(np.mean(widths), color='red', linestyle='--', label=f'Mean: {np.mean(widths):.1f}')
    axes[0,0].set_xlabel('Width (pixels)')
    axes[0,0].set_ylabel('Frequency')
    axes[0,0].set_title('Bounding Box Width Distribution')
    axes[0,0].legend()
    
    # 高度分布
    axes[0,1].hist(heights, bins=50, alpha=0.7, color='green')
    axes[0,1].axvline(np.mean(heights), color='red', linestyle='--', label=f'Mean: {np.mean(heights):.1f}')
    axes[0,1].set_xlabel('Height (pixels)')
    axes[0,1].set_ylabel('Frequency')
    axes[0,1].set_title('Bounding Box Height Distribution')
    axes[0,1].legend()
    
    # 面积分布
    axes[1,0].hist(areas, bins=50, alpha=0.7, color='orange')
    axes[1,0].axvline(np.mean(areas), color='red', linestyle='--', label=f'Mean: {np.mean(areas):.1f}')
    axes[1,0].set_xlabel('Area (pixels²)')
    axes[1,0].set_ylabel('Frequency')
    axes[1,0].set_title('Bounding Box Area Distribution')
    axes[1,0].legend()
    
    # 宽高比分布
    axes[1,1].hist(aspect_ratios, bins=50, alpha=0.7, color='purple')
    axes[1,1].axvline(np.mean(aspect_ratios), color='red', linestyle='--', label=f'Mean: {np.mean(aspect_ratios):.2f}')
    axes[1,1].set_xlabel('Aspect Ratio (W/H)')
    axes[1,1].set_ylabel('Frequency')
    axes[1,1].set_title('Aspect Ratio Distribution')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'bbox_size_analysis.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    return stats

def adaptive_resize_with_padding(image, target_size, min_size_threshold=8):
    """
    自适应缩放策略 - 针对不同尺寸目标优化
    
    Args:
        image: 输入图像
        target_size: 目标尺寸 (正方形)
        min_size_threshold: 最小尺寸阈值
    """
    h, w = image.shape[:2]
    
    # 处理极小目标（小于阈值）
    if min(w, h) < min_size_threshold:
        # 使用双三次插值放大小目标
        scale_factor = max(2, min_size_threshold / min(w, h))
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        w, h = new_w, new_h
    
    # 计算缩放比例（保持长宽比）
    scale = min(target_size / w, target_size / h)
    
    # 缩放图像
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    
    # 选择合适的插值方法
    if scale > 1:
        # 放大使用双三次插值
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    else:
        # 缩小使用面积插值
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # 创建目标尺寸的画布（使用灰色填充而非黑色，减少域偏移）
    canvas = np.full((target_size, target_size, 3), 128, dtype=np.uint8)
    
    # 居中放置
    y_offset = (target_size - new_h) // 2
    x_offset = (target_size - new_w) // 2
    
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas, scale, (x_offset, y_offset, new_w, new_h)

class TrainingLogger:
    """训练过程记录器"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.train_losses = []
        self.learning_rates = []
        self.epoch_times = []
        self.gpu_memory_usage = []
        
    def log_epoch(self, epoch, loss, lr, time_elapsed, gpu_memory=None):
        """记录每个epoch的信息"""
        self.train_losses.append(loss)
        self.learning_rates.append(lr)
        self.epoch_times.append(time_elapsed)
        if gpu_memory:
            self.gpu_memory_usage.append(gpu_memory)
            
        # 实时保存日志
        log_data = {
            'epoch': epoch,
            'loss': loss,
            'learning_rate': lr,
            'time_elapsed': time_elapsed,
            'gpu_memory': gpu_memory
        }
        
        log_file = os.path.join(self.log_dir, 'training_log.json')
        
        # 读取现有日志或创建新的
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
            
        logs.append(log_data)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def plot_training_curves(self):
        """绘制训练曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        # 损失曲线
        axes[0,0].plot(epochs, self.train_losses, 'b-', linewidth=2)
        axes[0,0].set_xlabel('Epoch')
        axes[0,0].set_ylabel('Triplet Loss')
        axes[0,0].set_title('Training Loss Curve')
        axes[0,0].grid(True, alpha=0.3)
        
        # 学习率曲线
        axes[0,1].plot(epochs, self.learning_rates, 'r-', linewidth=2)
        axes[0,1].set_xlabel('Epoch')
        axes[0,1].set_ylabel('Learning Rate')
        axes[0,1].set_title('Learning Rate Schedule')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].set_yscale('log')
        
        # 训练时间
        axes[1,0].plot(epochs, self.epoch_times, 'g-', linewidth=2)
        axes[1,0].set_xlabel('Epoch')
        axes[1,0].set_ylabel('Time (minutes)')
        axes[1,0].set_title('Training Time per Epoch')
        axes[1,0].grid(True, alpha=0.3)
        
        # GPU内存使用
        if self.gpu_memory_usage:
            axes[1,1].plot(epochs, self.gpu_memory_usage, 'm-', linewidth=2)
            axes[1,1].set_xlabel('Epoch')
            axes[1,1].set_ylabel('GPU Memory (GB)')
            axes[1,1].set_title('GPU Memory Usage')
            axes[1,1].grid(True, alpha=0.3)
        else:
            axes[1,1].text(0.5, 0.5, 'No GPU Memory Data', 
                          ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('GPU Memory Usage')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.log_dir, 'training_curves.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        # 保存训练总结
        summary = {
            'total_epochs': len(self.train_losses),
            'final_loss': self.train_losses[-1],
            'best_loss': min(self.train_losses),
            'best_epoch': self.train_losses.index(min(self.train_losses)) + 1,
            'total_training_time': sum(self.epoch_times),
            'average_epoch_time': np.mean(self.epoch_times)
        }
        
        with open(os.path.join(self.log_dir, 'training_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
            
        return summary

def evaluate_feature_quality(model, dataloader, device, num_samples=1000):
    """评估特征质量"""
    model.eval()
    features = []
    labels = []
    
    with torch.no_grad():
        for i, (anchor, positive, negative) in enumerate(dataloader):
            if i * dataloader.batch_size >= num_samples:
                break
                
            anchor = anchor.to(device)
            anchor_feat = model(anchor)
            
            features.append(anchor_feat.cpu().numpy())
            labels.extend([f"batch_{i}_sample_{j}" for j in range(anchor.size(0))])
    
    features = np.vstack(features)
    
    # 计算特征统计
    feature_stats = {
        'feature_dim': features.shape[1],
        'feature_norm_mean': np.mean(np.linalg.norm(features, axis=1)),
        'feature_norm_std': np.std(np.linalg.norm(features, axis=1)),
        'feature_mean': np.mean(features, axis=0).tolist(),
        'feature_std': np.std(features, axis=0).tolist(),
    }
    
    # 计算特征间距离分布
    from sklearn.metrics.pairwise import cosine_distances
    sample_indices = np.random.choice(len(features), min(500, len(features)), replace=False)
    sample_features = features[sample_indices]
    distances = cosine_distances(sample_features)
    
    feature_stats['cosine_distance_mean'] = np.mean(distances)
    feature_stats['cosine_distance_std'] = np.std(distances)
    
    return feature_stats

# 使用示例和建议
if __name__ == "__main__":
    print("ReID训练改进建议:")
    print("1. 使用analyze_bbox_sizes()分析目标尺寸分布")
    print("2. 根据分析结果选择合适的输入尺寸:")
    print("   - 如果大部分目标在30-90像素: 使用96×96输入")
    print("   - 如果目标尺寸较大: 使用128×128或160×160")
    print("3. 使用adaptive_resize_with_padding()处理不同尺寸目标")
    print("4. 使用TrainingLogger记录和可视化训练过程")
    print("5. 使用evaluate_feature_quality()评估特征质量")
