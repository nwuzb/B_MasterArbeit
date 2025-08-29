#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ReID模型训练结果评估指标 - 类似YOLO的mAP50
为ReID模型提供定量的性能评估指标
"""

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score, average_precision_score
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
import os

class ReIDEvaluationMetrics:
    """ReID模型评估指标计算器 - 类似YOLO的评估方式"""
    
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.model.eval()
        
    def extract_features_batch(self, images):
        """批量提取特征"""
        with torch.no_grad():
            images = images.to(self.device)
            features = self.model(images)
            return features.cpu().numpy()
    
    def compute_distance_matrix(self, features_query, features_gallery):
        """计算查询集和图库集之间的距离矩阵"""
        # L2归一化
        features_query = F.normalize(torch.from_numpy(features_query), p=2, dim=1)
        features_gallery = F.normalize(torch.from_numpy(features_gallery), p=2, dim=1)
        
        # 计算余弦相似度矩阵
        similarity_matrix = torch.mm(features_query, features_gallery.t())
        
        # 转换为距离矩阵 (1 - cosine_similarity)
        distance_matrix = 1 - similarity_matrix
        
        return distance_matrix.numpy()
    
    def compute_reid_map(self, query_features, gallery_features, query_labels, gallery_labels, 
                        thresholds=[0.1, 0.2, 0.3, 0.4, 0.5]):
        """
        计算ReID的mAP指标 - 类似目标检测的mAP@0.5
        
        Args:
            query_features: 查询集特征
            gallery_features: 图库集特征  
            query_labels: 查询集标签
            gallery_labels: 图库集标签
            thresholds: 距离阈值列表
        
        Returns:
            mAP值字典，类似mAP@0.1, mAP@0.2等
        """
        distance_matrix = self.compute_distance_matrix(query_features, gallery_features)
        
        mAP_results = {}
        
        for threshold in thresholds:
            aps = []  # 存储每个查询的AP值
            
            for i, query_label in enumerate(query_labels):
                # 获取当前查询与所有图库样本的距离
                distances = distance_matrix[i]
                
                # 找到正样本（相同ID）
                positive_mask = (gallery_labels == query_label)
                positive_distances = distances[positive_mask]
                negative_distances = distances[~positive_mask]
                
                if len(positive_distances) == 0:
                    continue
                
                # 在给定阈值下计算精度和召回率
                # 认为距离小于阈值的为正确匹配
                tp = np.sum(positive_distances < threshold)  # 真正例
                fp = np.sum(negative_distances < threshold)  # 假正例
                fn = len(positive_distances) - tp            # 假负例
                
                if tp + fp == 0:
                    precision = 0
                else:
                    precision = tp / (tp + fp)
                
                if tp + fn == 0:
                    recall = 0  
                else:
                    recall = tp / (tp + fn)
                
                # 计算AP（这里简化为precision）
                ap = precision
                aps.append(ap)
            
            # 计算mAP
            if len(aps) > 0:
                mAP_results[f'mAP@{threshold}'] = np.mean(aps)
            else:
                mAP_results[f'mAP@{threshold}'] = 0.0
        
        return mAP_results
    
    def compute_cmc_curve(self, query_features, gallery_features, query_labels, gallery_labels, max_rank=10):
        """
        计算CMC曲线 - Cumulative Matching Characteristic
        这是ReID领域的标准评估指标，类似检测中的召回率曲线
        """
        distance_matrix = self.compute_distance_matrix(query_features, gallery_features)
        
        cmc = np.zeros(max_rank)
        
        for i, query_label in enumerate(query_labels):
            # 获取当前查询的距离并排序
            distances = distance_matrix[i]
            sorted_indices = np.argsort(distances)
            
            # 找到第一个正确匹配的位置
            for rank in range(min(max_rank, len(sorted_indices))):
                if gallery_labels[sorted_indices[rank]] == query_label:
                    cmc[rank:] += 1
                    break
        
        # 归一化
        cmc = cmc / len(query_labels)
        
        return cmc
    
    def compute_reid_precision_recall(self, query_features, gallery_features, 
                                    query_labels, gallery_labels, threshold=0.3):
        """计算整体精度和召回率"""
        distance_matrix = self.compute_distance_matrix(query_features, gallery_features)
        
        all_tp, all_fp, all_fn = 0, 0, 0
        
        for i, query_label in enumerate(query_labels):
            distances = distance_matrix[i]
            
            positive_mask = (gallery_labels == query_label)
            positive_distances = distances[positive_mask]
            negative_distances = distances[~positive_mask]
            
            tp = np.sum(positive_distances < threshold)
            fp = np.sum(negative_distances < threshold) 
            fn = len(positive_distances) - tp
            
            all_tp += tp
            all_fp += fp
            all_fn += fn
        
        precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) > 0 else 0
        recall = all_tp / (all_tp + all_fn) if (all_tp + all_fn) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall, 
            'f1_score': f1_score
        }
    
    def compute_feature_quality_metrics(self, features, labels):
        """计算特征质量指标"""
        # 1. 特征归一化程度
        norms = np.linalg.norm(features, axis=1)
        norm_stats = {
            'mean_norm': np.mean(norms),
            'std_norm': np.std(norms),
            'norm_consistency': 1 - np.std(norms)  # 越接近1越好
        }
        
        # 2. 类内和类间距离
        unique_labels = np.unique(labels)
        intra_class_distances = []
        inter_class_distances = []
        
        for label in unique_labels:
            mask = (labels == label)
            class_features = features[mask]
            
            if len(class_features) > 1:
                # 类内距离
                class_distances = []
                for i in range(len(class_features)):
                    for j in range(i+1, len(class_features)):
                        dist = np.linalg.norm(class_features[i] - class_features[j])
                        class_distances.append(dist)
                intra_class_distances.extend(class_distances)
                
                # 类间距离（与其他类的中心点）
                class_center = np.mean(class_features, axis=0)
                for other_label in unique_labels:
                    if other_label != label:
                        other_mask = (labels == other_label)
                        other_features = features[other_mask]
                        if len(other_features) > 0:
                            other_center = np.mean(other_features, axis=0)
                            inter_dist = np.linalg.norm(class_center - other_center)
                            inter_class_distances.append(inter_dist)
        
        intra_mean = np.mean(intra_class_distances) if intra_class_distances else 0
        inter_mean = np.mean(inter_class_distances) if inter_class_distances else 0
        
        separability = inter_mean / intra_mean if intra_mean > 0 else 0
        
        quality_metrics = {
            'intra_class_distance': intra_mean,
            'inter_class_distance': inter_mean,
            'separability_ratio': separability,
            'feature_compactness': 1 / (1 + intra_mean),  # 越紧凑越好
            'feature_discriminability': separability
        }
        
        quality_metrics.update(norm_stats)
        
        return quality_metrics
    
    def evaluate_reid_model(self, test_dataloader, save_dir=None):
        """
        完整的ReID模型评估 - 生成类似YOLO训练结果的评估报告
        """
        print("🔍 开始ReID模型性能评估...")
        
        # 提取所有特征和标签
        all_features = []
        all_labels = []
        
        for batch_idx, (anchor, positive, negative) in enumerate(test_dataloader):
            # 处理anchor样本
            anchor_features = self.extract_features_batch(anchor)
            all_features.append(anchor_features)
            all_labels.extend([f"anchor_{batch_idx}_{i}" for i in range(len(anchor_features))])
        
        all_features = np.vstack(all_features)
        
        # 模拟查询集和图库集的划分
        split_idx = len(all_features) // 2
        query_features = all_features[:split_idx]
        gallery_features = all_features[split_idx:]
        query_labels = np.array([label.split('_')[1] for label in all_labels[:split_idx]])
        gallery_labels = np.array([label.split('_')[1] for label in all_labels[split_idx:]])
        
        # 1. 计算mAP指标
        print("📊 计算mAP指标...")
        map_results = self.compute_reid_map(query_features, gallery_features, 
                                           query_labels, gallery_labels)
        
        # 2. 计算CMC曲线
        print("📈 计算CMC曲线...")
        cmc = self.compute_cmc_curve(query_features, gallery_features, 
                                    query_labels, gallery_labels)
        
        # 3. 计算精度召回率
        print("🎯 计算精度召回率...")
        pr_results = self.compute_reid_precision_recall(query_features, gallery_features,
                                                       query_labels, gallery_labels)
        
        # 4. 计算特征质量指标
        print("⚡ 计算特征质量...")
        quality_metrics = self.compute_feature_quality_metrics(all_features, 
                                                              np.array([l.split('_')[1] for l in all_labels]))
        
        # 整合所有结果
        evaluation_results = {
            'mAP_metrics': map_results,
            'CMC_metrics': {
                'Rank-1': cmc[0],
                'Rank-5': cmc[4] if len(cmc) > 4 else cmc[-1],
                'Rank-10': cmc[9] if len(cmc) > 9 else cmc[-1]
            },
            'precision_recall': pr_results,
            'feature_quality': quality_metrics,
            'model_summary': {
                'total_parameters': sum(p.numel() for p in self.model.parameters()),
                'trainable_parameters': sum(p.numel() for p in self.model.parameters() if p.requires_grad),
                'feature_dimension': all_features.shape[1]
            }
        }
        
        # 打印结果（类似YOLO的输出格式）
        self.print_evaluation_results(evaluation_results)
        
        # 保存结果和可视化
        if save_dir:
            self.save_evaluation_results(evaluation_results, cmc, save_dir)
        
        return evaluation_results
    
    def print_evaluation_results(self, results):
        """打印评估结果 - 模仿YOLO的输出格式"""
        print("\n" + "="*80)
        print(" "*25 + "ReID Model Evaluation Results")
        print("="*80)
        
        # mAP结果
        print("\n📊 mAP Metrics (类似YOLO的mAP@0.5):")
        for metric, value in results['mAP_metrics'].items():
            print(f"   {metric:<15}: {value:.3f}")
        
        # CMC结果
        print("\n🏆 CMC Metrics (Cumulative Matching Characteristic):")
        for metric, value in results['CMC_metrics'].items():
            print(f"   {metric:<15}: {value:.3f}")
        
        # 精度召回率
        print("\n🎯 Precision & Recall:")
        pr = results['precision_recall']
        print(f"   Precision      : {pr['precision']:.3f}")
        print(f"   Recall         : {pr['recall']:.3f}")
        print(f"   F1-Score       : {pr['f1_score']:.3f}")
        
        # 特征质量
        print("\n⚡ Feature Quality Metrics:")
        quality = results['feature_quality']
        print(f"   Separability   : {quality['separability_ratio']:.3f}")
        print(f"   Compactness    : {quality['feature_compactness']:.3f}")
        print(f"   Discriminability: {quality['feature_discriminability']:.3f}")
        
        # 模型信息
        print("\n🔧 Model Summary:")
        summary = results['model_summary']
        print(f"   Parameters     : {summary['total_parameters']:,}")
        print(f"   Feature Dim    : {summary['feature_dimension']}")
        
        print("="*80)
    
    def save_evaluation_results(self, results, cmc, save_dir):
        """保存评估结果和生成可视化图表"""
        os.makedirs(save_dir, exist_ok=True)
        
        # 1. 保存JSON结果
        with open(os.path.join(save_dir, 'reid_evaluation_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        # 2. 生成CMC曲线图
        plt.figure(figsize=(10, 6))
        ranks = range(1, len(cmc) + 1)
        plt.plot(ranks, cmc, 'b-', linewidth=2, marker='o', markersize=4)
        plt.xlabel('Rank', fontsize=12)
        plt.ylabel('Cumulative Matching Accuracy', fontsize=12)
        plt.title('CMC Curve - ReID Model Performance', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.xlim(1, len(cmc))
        plt.ylim(0, 1)
        
        # 标注关键点
        for rank in [1, 5, 10]:
            if rank <= len(cmc):
                plt.annotate(f'Rank-{rank}: {cmc[rank-1]:.3f}', 
                           xy=(rank, cmc[rank-1]), 
                           xytext=(rank+1, cmc[rank-1]+0.05),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, 'cmc_curve.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 生成mAP对比图
        plt.figure(figsize=(10, 6))
        thresholds = [float(k.split('@')[1]) for k in results['mAP_metrics'].keys()]
        map_values = list(results['mAP_metrics'].values())
        
        plt.bar(thresholds, map_values, alpha=0.7, color='skyblue', edgecolor='navy')
        plt.xlabel('Distance Threshold', fontsize=12)
        plt.ylabel('mAP Score', fontsize=12)
        plt.title('mAP at Different Distance Thresholds', fontsize=14)
        plt.grid(True, axis='y', alpha=0.3)
        
        # 添加数值标注
        for i, (threshold, value) in enumerate(zip(thresholds, map_values)):
            plt.text(threshold, value + 0.01, f'{value:.3f}', 
                    ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, 'map_comparison.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 评估结果已保存到: {save_dir}")

def recommend_optimal_input_size(bbox_stats):
    """
    基于目标尺寸统计推荐最优输入尺寸
    
    Args:
        bbox_stats: 边界框统计信息，包含width, height的percentiles
    
    Returns:
        推荐的输入尺寸和理由
    """
    # 获取75百分位数和90百分位数
    width_75 = bbox_stats['width_percentiles'][75]
    height_75 = bbox_stats['height_percentiles'][75]
    width_90 = bbox_stats['width_percentiles'][90]
    height_90 = bbox_stats['height_percentiles'][90]
    
    max_75 = max(width_75, height_75)
    max_90 = max(width_90, height_90)
    
    recommendations = []
    
    # 基于75%的目标推荐主要尺寸
    if max_75 <= 64:
        primary_size = 96
        coverage_75 = "95%+"
    elif max_75 <= 96:
        primary_size = 128  
        coverage_75 = "90%+"
    elif max_75 <= 128:
        primary_size = 160
        coverage_75 = "85%+"
    else:
        primary_size = 224
        coverage_75 = "80%+"
    
    recommendations.append({
        'input_size': primary_size,
        'target_coverage': coverage_75,
        'rationale': f'覆盖75%目标的最优尺寸，max_75={max_75:.1f}px'
    })
    
    # 基于90%的目标推荐高质量尺寸
    if max_90 <= 96:
        high_quality_size = 128
    elif max_90 <= 128:
        high_quality_size = 160
    elif max_90 <= 160:
        high_quality_size = 224
    else:
        high_quality_size = 256
    
    recommendations.append({
        'input_size': high_quality_size, 
        'target_coverage': "90%+",
        'rationale': f'高质量选项，覆盖90%目标，max_90={max_90:.1f}px'
    })
    
    return recommendations

# 使用示例
if __name__ == "__main__":
    print("ReID模型评估指标使用指南:")
    print("1. 使用 ReIDEvaluationMetrics 类似 YOLO 评估模型性能")
    print("2. 主要指标:")
    print("   - mAP@0.1, mAP@0.2, ... (类似YOLO的mAP@0.5)")
    print("   - CMC Rank-1, Rank-5, Rank-10")
    print("   - Precision, Recall, F1-Score")
    print("   - Feature Quality Metrics")
    print("3. 使用 recommend_optimal_input_size() 基于目标尺寸推荐输入尺寸")
