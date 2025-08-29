#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对原始ReID训练代码的修改建议
针对获得ReID的代码_Colab_RelD_Training.ipynb的改进
"""

# ====================== 修改1: 改进的智能缩放函数 ======================
def smart_resize_with_padding_improved(image, target_size, analysis_mode=False):
    """
    改进的智能缩放函数，包含尺寸分析功能
    
    Args:
        image: 输入图像
        target_size: 目标尺寸
        analysis_mode: 是否返回分析信息
    """
    h, w = image.shape[:2]
    original_size = (w, h)
    
    # 记录原始尺寸用于分析
    size_info = {
        'original_width': w,
        'original_height': h,
        'original_area': w * h,
        'aspect_ratio': w / h if h > 0 else 0
    }
    
    # 处理极小图像的改进策略
    min_threshold = 8
    if min(w, h) < min_threshold:
        # 使用更好的插值方法处理极小图像
        scale_up = max(2.0, min_threshold / min(w, h))
        temp_w, temp_h = int(w * scale_up), int(h * scale_up)
        image = cv2.resize(image, (temp_w, temp_h), interpolation=cv2.INTER_CUBIC)
        w, h = temp_w, temp_h
        size_info['upscaled'] = True
        size_info['upscale_factor'] = scale_up
    else:
        size_info['upscaled'] = False

    # 计算缩放比例
    scale = min(target_size / w, target_size / h)
    
    # 计算新的尺寸
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    
    # 选择合适的插值方法
    if scale > 1:
        interpolation = cv2.INTER_CUBIC  # 放大时使用三次插值
    else:
        interpolation = cv2.INTER_AREA   # 缩小时使用区域插值
    
    resized = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
    
    # 使用灰色填充而不是黑色，减少域偏移
    canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)  # 使用更自然的灰色
    
    # 计算居中位置
    y_offset = (target_size - new_h) // 2
    x_offset = (target_size - new_w) // 2
    
    # 将缩放后的图像放置在画布中心
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    size_info.update({
        'final_width': new_w,
        'final_height': new_h,
        'scale_factor': scale,
        'padding': (x_offset, y_offset),
        'target_size': target_size
    })
    
    if analysis_mode:
        return canvas, size_info
    else:
        return canvas

# ====================== 修改2: 添加训练监控和可视化 ======================
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
import datetime

class ReIDTrainingMonitor:
    """ReID训练监控器"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 训练记录
        self.training_log = {
            'start_time': datetime.datetime.now().isoformat(),
            'epochs': [],
            'losses': [],
            'learning_rates': [],
            'gpu_memory': [],
            'batch_times': [],
            'size_statistics': defaultdict(list)
        }
        
        # 实时图表
        plt.ion()  # 开启交互模式
        
    def log_batch(self, epoch, batch_idx, loss, lr, gpu_memory=None, batch_time=None):
        """记录批次信息"""
        log_entry = {
            'epoch': epoch,
            'batch': batch_idx,
            'loss': loss,
            'lr': lr,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if gpu_memory is not None:
            log_entry['gpu_memory'] = gpu_memory
            
        if batch_time is not None:
            log_entry['batch_time'] = batch_time
            
        # 保存到文件
        log_file = os.path.join(self.log_dir, f'batch_log_epoch_{epoch}.json')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_epoch(self, epoch, avg_loss, lr, epoch_time, gpu_memory=None):
        """记录epoch信息"""
        self.training_log['epochs'].append(epoch)
        self.training_log['losses'].append(avg_loss)
        self.training_log['learning_rates'].append(lr)
        
        if gpu_memory is not None:
            self.training_log['gpu_memory'].append(gpu_memory)
            
        # 保存完整日志
        with open(os.path.join(self.log_dir, 'training_log.json'), 'w') as f:
            json.dump(self.training_log, f, indent=2)
        
        # 绘制实时曲线
        self.plot_real_time_curves()
    
    def plot_real_time_curves(self):
        """绘制实时训练曲线"""
        if len(self.training_log['losses']) < 2:
            return
            
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        epochs = self.training_log['epochs']
        
        # 损失曲线
        axes[0].clear()
        axes[0].plot(epochs, self.training_log['losses'], 'b-', linewidth=2, marker='o')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Triplet Loss')
        axes[0].set_title('Training Loss')
        axes[0].grid(True, alpha=0.3)
        
        # 学习率曲线
        axes[1].clear()
        axes[1].plot(epochs, self.training_log['learning_rates'], 'r-', linewidth=2, marker='s')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Learning Rate')
        axes[1].set_title('Learning Rate Schedule')
        axes[1].set_yscale('log')
        axes[1].grid(True, alpha=0.3)
        
        # GPU内存使用
        if self.training_log['gpu_memory']:
            axes[2].clear()
            axes[2].plot(epochs, self.training_log['gpu_memory'], 'g-', linewidth=2, marker='^')
            axes[2].set_xlabel('Epoch')
            axes[2].set_ylabel('GPU Memory (GB)')
            axes[2].set_title('GPU Memory Usage')
            axes[2].grid(True, alpha=0.3)
        else:
            axes[2].text(0.5, 0.5, 'No GPU Data', ha='center', va='center', transform=axes[2].transAxes)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.log_dir, 'training_progress.png'), dpi=150, bbox_inches='tight')
        plt.pause(0.1)  # 短暂暂停以更新显示
    
    def analyze_size_distribution(self, size_data):
        """分析并可视化尺寸分布"""
        if not size_data:
            return
            
        # 提取尺寸信息
        widths = [s['original_width'] for s in size_data]
        heights = [s['original_height'] for s in size_data]
        areas = [s['original_area'] for s in size_data]
        aspect_ratios = [s['aspect_ratio'] for s in size_data if s['aspect_ratio'] > 0]
        
        # 创建分析图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 宽度分布
        axes[0,0].hist(widths, bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0,0].axvline(np.mean(widths), color='red', linestyle='--', 
                         label=f'Mean: {np.mean(widths):.1f}')
        axes[0,0].axvline(np.median(widths), color='orange', linestyle='--', 
                         label=f'Median: {np.median(widths):.1f}')
        axes[0,0].set_xlabel('Width (pixels)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title('Bounding Box Width Distribution')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # 高度分布
        axes[0,1].hist(heights, bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[0,1].axvline(np.mean(heights), color='red', linestyle='--', 
                         label=f'Mean: {np.mean(heights):.1f}')
        axes[0,1].axvline(np.median(heights), color='orange', linestyle='--', 
                         label=f'Median: {np.median(heights):.1f}')
        axes[0,1].set_xlabel('Height (pixels)')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].set_title('Bounding Box Height Distribution')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # 面积分布
        axes[1,0].hist(areas, bins=30, alpha=0.7, color='purple', edgecolor='black')
        axes[1,0].axvline(np.mean(areas), color='red', linestyle='--', 
                         label=f'Mean: {np.mean(areas):.1f}')
        axes[1,0].set_xlabel('Area (pixels²)')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title('Bounding Box Area Distribution')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # 长宽比分布
        axes[1,1].hist(aspect_ratios, bins=30, alpha=0.7, color='orange', edgecolor='black')
        axes[1,1].axvline(np.mean(aspect_ratios), color='red', linestyle='--', 
                         label=f'Mean: {np.mean(aspect_ratios):.2f}')
        axes[1,1].set_xlabel('Aspect Ratio (W/H)')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].set_title('Aspect Ratio Distribution')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.log_dir, 'size_distribution_analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        # 保存统计信息
        stats = {
            'total_samples': len(size_data),
            'width_stats': {
                'min': min(widths), 'max': max(widths), 'mean': np.mean(widths),
                'median': np.median(widths), 'std': np.std(widths),
                'percentiles': {
                    '10th': np.percentile(widths, 10),
                    '25th': np.percentile(widths, 25),
                    '75th': np.percentile(widths, 75),
                    '90th': np.percentile(widths, 90)
                }
            },
            'height_stats': {
                'min': min(heights), 'max': max(heights), 'mean': np.mean(heights),
                'median': np.median(heights), 'std': np.std(heights),
                'percentiles': {
                    '10th': np.percentile(heights, 10),
                    '25th': np.percentile(heights, 25),
                    '75th': np.percentile(heights, 75),
                    '90th': np.percentile(heights, 90)
                }
            },
            'recommended_input_size': self._recommend_input_size(widths, heights)
        }
        
        with open(os.path.join(self.log_dir, 'size_statistics.json'), 'w') as f:
            json.dump(stats, f, indent=2)
            
        return stats
    
    def _recommend_input_size(self, widths, heights):
        """基于尺寸分布推荐输入尺寸"""
        # 计算75百分位数作为推荐基准
        width_75 = np.percentile(widths, 75)
        height_75 = np.percentile(heights, 75)
        max_75 = max(width_75, height_75)
        
        # 推荐尺寸选择
        if max_75 <= 64:
            return 96
        elif max_75 <= 96:
            return 128
        elif max_75 <= 128:
            return 160
        else:
            return 224

# ====================== 修改3: 改进的训练函数 ======================
def train_reid_model_improved(data_dir, output_path, num_epochs=50, input_size=128):
    """
    改进的ReID模型训练函数
    添加了完整的监控和可视化功能
    """
    print(f"\n🚀 开始改进版ReID模型训练 (输入尺寸: {input_size}×{input_size})")
    print("=" * 60)
    
    # 创建监控器
    log_dir = os.path.join(os.path.dirname(output_path), "training_logs")
    monitor = ReIDTrainingMonitor(log_dir)
    
    # 收集尺寸数据用于分析
    size_data = []
    
    # 设备配置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🎯 使用设备: {device}")
    
    # 数据预处理 - 使用改进的变换
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((input_size, input_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),  # 减少旋转角度
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.RandomGrayscale(p=0.05),  # 减少灰度化概率
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.1, scale=(0.02, 0.2))  # 减少随机擦除强度
    ])
    
    # 这里需要使用改进的数据集类...
    # [其余训练代码保持类似，但添加监控调用]
    
    print(f"✅ 训练完成！结果保存在: {log_dir}")
    return output_path

# ====================== 修改建议总结 ======================
"""
主要修改建议：

1. 输入尺寸建议：
   - 分析您的Excel数据后，推荐使用96×96作为主要输入尺寸
   - 如果目标较大，可以使用128×128或160×160

2. 处理策略：
   - 小目标（<8像素）：使用三次插值放大
   - 大目标：使用区域插值缩小
   - 统一使用灰色填充而非黑色

3. 训练监控：
   - 添加实时损失可视化
   - 记录GPU内存使用
   - 分析输入尺寸分布
   - 保存详细训练日志

4. 代码修改位置：
   - 替换smart_resize_with_padding函数
   - 在训练循环中添加monitor.log_epoch()调用
   - 在prepare_reid_dataset中收集尺寸统计
   - 添加训练结束后的可视化生成

5. 实验建议：
   - 比较96×96 vs 128×128的性能
   - 测试不同填充策略的效果
   - 分析特征质量指标
"""
