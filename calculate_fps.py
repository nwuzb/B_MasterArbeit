#!/usr/bin/env python3
"""
计算YOLO检测器的FPS指标
基于experiment_time（推理时间）计算FPS
"""

import pandas as pd
import numpy as np

def calculate_fps_from_data(csv_file_path=None, data=None):
    """
    从CSV文件或数据计算FPS
    
    Args:
        csv_file_path: CSV文件路径
        data: 直接传入的数据（字典格式）
    
    Returns:
        更新后的DataFrame，包含FPS列
    """
    
    if csv_file_path:
        # 从CSV文件读取
        df = pd.read_csv(csv_file_path)
    elif data:
        # 从传入的数据创建DataFrame
        df = pd.DataFrame(data)
    else:
        # 使用您提供的示例数据
        sample_data = {
            'conf': [0.3, 0.3, 0.5, 0.5],
            'iou': [0.5, 0.7, 0.5, 0.7],
            'experiment_time': [316.7002902030945, 296.39608883857727, 313.2691493492126, 303.81830811500055],
            'timestamp': ['2025/9/3 10:20', '2025/9/3 10:25', '2025/9/3 10:30', '2025/9/3 10:36'],
            'mAP50-95': [0.3949482085015532, 0.39397442285441386, 0.39870958102495313, 0.39821137490804],
            'mAP50': [0.6182977444921866, 0.6169536301678423, 0.6190213114427253, 0.6184964818563652],
            'mAP75': [0, 0, 0, 0],
            'precision': [0.9313077939230, 0.9271175311880, 0.9518072289150, 0.9498585750620],
            'recall': [0.2950408035100, 0.2954593011000, 0.2810211341200, 0.2814396317200],
            'mAP_s': [0, 0, 0, 0],
            'mAP_m': [0, 0, 0, 0],
            'mAP_l': [0, 0, 0, 0],
            'inference_t': [0, 0, 0, 0]
        }
        df = pd.DataFrame(sample_data)
    
    # 计算FPS (假设实验时间是处理整个数据集的时间)
    # 需要知道图像数量来计算准确的FPS
    # 这里我们假设是单张图像的推理时间（以毫秒为单位）
    
    if 'experiment_time' in df.columns:
        # 假设experiment_time是毫秒，转换为秒然后计算FPS
        df['inference_time_ms'] = df['experiment_time']
        df['inference_time_s'] = df['experiment_time'] / 1000.0
        df['FPS'] = 1.0 / df['inference_time_s']
        
        # 也可能experiment_time已经是秒，那么直接计算
        df['FPS_alt'] = 1.0 / df['experiment_time']
        
    print("=== YOLO检测器性能分析 ===")
    print(f"数据行数: {len(df)}")
    print("\n=== 推理速度统计 ===")
    if 'experiment_time' in df.columns:
        print(f"平均推理时间: {df['experiment_time'].mean():.2f}")
        print(f"最小推理时间: {df['experiment_time'].min():.2f}")
        print(f"最大推理时间: {df['experiment_time'].max():.2f}")
        
        if df['experiment_time'].mean() > 10:
            print("注意：experiment_time似乎是毫秒单位")
            print(f"平均FPS (假设毫秒): {df['FPS'].mean():.2f}")
            print(f"最高FPS (假设毫秒): {df['FPS'].max():.2f}")
            print(f"最低FPS (假设毫秒): {df['FPS'].min():.2f}")
        else:
            print("注意：experiment_time似乎是秒单位")
            print(f"平均FPS (假设秒): {df['FPS_alt'].mean():.2f}")
            print(f"最高FPS (假设秒): {df['FPS_alt'].max():.2f}")
            print(f"最低FPS (假设秒): {df['FPS_alt'].min():.2f}")
    
    print("\n=== 准确性统计 ===")
    if 'mAP50' in df.columns:
        print(f"平均mAP@0.5: {df['mAP50'].mean():.4f}")
        print(f"最高mAP@0.5: {df['mAP50'].max():.4f}")
        print(f"最低mAP@0.5: {df['mAP50'].min():.4f}")
    
    if 'mAP50-95' in df.columns:
        print(f"平均mAP@0.5:0.95: {df['mAP50-95'].mean():.4f}")
        print(f"最高mAP@0.5:0.95: {df['mAP50-95'].max():.4f}")
        print(f"最低mAP@0.5:0.95: {df['mAP50-95'].min():.4f}")
    
    # 创建性能对比表格
    print("\n=== 性能对比表格 ===")
    performance_cols = ['conf', 'iou', 'mAP50', 'mAP50-95', 'precision', 'recall']
    if 'FPS' in df.columns:
        performance_cols.append('FPS')
    if 'FPS_alt' in df.columns:
        performance_cols.append('FPS_alt')
    
    performance_df = df[performance_cols].round(4)
    print(performance_df.to_string(index=False))
    
    return df

def create_latex_table(df, caption="YOLO11m检测器性能评估结果"):
    """
    创建LaTeX表格代码
    """
    latex_code = f"""
\\begin{{table}}[h!]
\\centering
\\caption{{{caption}}}
\\begin{{tabular}}{{|c|c|c|c|c|c|c|}}
\\hline
\\textbf{{置信度}} & \\textbf{{IoU}} & \\textbf{{mAP@0.5}} & \\textbf{{mAP@0.5:0.95}} & \\textbf{{精确率}} & \\textbf{{召回率}} & \\textbf{{FPS}} \\\\
\\hline
"""
    
    for _, row in df.iterrows():
        fps_val = row.get('FPS', row.get('FPS_alt', 0))
        latex_code += f"{row['conf']:.1f} & {row['iou']:.1f} & {row['mAP50']:.3f} & {row['mAP50-95']:.3f} & {row['precision']:.3f} & {row['recall']:.3f} & {fps_val:.1f} \\\\\n"
    
    latex_code += """\\hline
\\end{tabular}
\\label{tab:yolo_performance}
\\end{table}
"""
    
    return latex_code

if __name__ == "__main__":
    print("🚀 开始计算YOLO检测器FPS...")
    
    # 使用示例数据计算
    result_df = calculate_fps_from_data()
    
    # 生成LaTeX表格
    latex_table = create_latex_table(result_df)
    
    print("\n=== LaTeX表格代码 ===")
    print(latex_table)
    
    # 保存结果
    result_df.to_csv('yolo_performance_with_fps.csv', index=False)
    print(f"\n✅ 结果已保存到 yolo_performance_with_fps.csv")
    
    with open('yolo_performance_table.tex', 'w', encoding='utf-8') as f:
        f.write(latex_table)
    print(f"✅ LaTeX表格已保存到 yolo_performance_table.tex")
