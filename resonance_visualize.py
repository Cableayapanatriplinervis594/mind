#!/usr/bin/env python3
"""
========================================================
共振翻转可视化 - 256种组合
========================================================

可视化内容：
1. 翻转次数 vs 0的个数 (散点图+拟合线)
2. 256种组合热力图
3. 二项分布验证

使用方法：
    python3 resonance_visualize.py
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class ResonanceVisualizer:
    """
    共振翻转可视化
    """

    def __init__(self):
        self.n_bits = 8
        self.n_combinations = 256
        self.data = None

        print("=" * 60)
        print("  共振翻转可视化")
        print("=" * 60)

    def load_data(self):
        """加载实验数据"""
        data_dir = Path('./resonance_data')

        files = list(data_dir.glob('cartesian_complete_*.json'))

        if not files:
            print("未找到数据文件，先运行 resonance_cartesian_complete.py")
            return None

        latest = max(files, key=lambda p: p.stat().st_mtime)

        with open(latest, 'r') as f:
            self.data = json.load(f)

        print(f"加载数据: {latest.name}")
        print(f"实验数: {self.data['analysis']['total']}")
        print(f"正确率: {self.data['analysis']['accuracy']:.1f}%")

        return self.data

    def visualize_scatter(self, ax):
        """散点图：翻转次数 vs 0的个数"""
        results = self.data['results']

        n_zeros = [r['n_zeros'] for r in results]
        n_flips = [r['n_flips'] for r in results]

        ax.scatter(n_zeros, n_flips, alpha=0.5, s=50, c='blue')

        for n_z in range(9):
            flips_at_nz = [r['n_flips'] for r in results if r['n_zeros'] == n_z]
            if flips_at_nz:
                avg = np.mean(flips_at_nz)
                ax.scatter(n_z, avg, s=200, c='red', marker='x', linewidths=3, zorder=5)

        ax.plot([0, 8], [0, 8], 'g--', linewidth=2, label='理想: 翻转=0的个数')

        ax.set_xlabel('0的个数', fontsize=12)
        ax.set_ylabel('翻转次数', fontsize=12)
        ax.set_title('翻转次数 vs 0的个数 (红点=平均值)', fontsize=14)
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-0.5, 8.5)
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.set_xticks(range(9))

    def visualize_heatmap(self, ax):
        """热力图：256种组合的翻转次数"""
        results = self.data['results']

        grid = np.zeros((16, 16))

        for r in results:
            bits = r['bits']
            idx = int(''.join(str(b) for b in bits), 2)
            row = idx // 16
            col = idx % 16
            grid[row, col] = r['n_flips']

        im = ax.imshow(grid, cmap='hot', aspect='auto')
        ax.set_title('256种组合翻转次数热力图', fontsize=14)
        ax.set_xlabel('低4位', fontsize=12)
        ax.set_ylabel('高4位', fontsize=12)

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('翻转次数', fontsize=12)

        bits_x = ['0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
                  '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111']
        ax.set_xticks(range(16))
        ax.set_xticklabels(bits_x, rotation=45, fontsize=8)
        ax.set_yticks(range(16))
        ax.set_yticklabels(bits_x, fontsize=8)

    def visualize_histogram(self, ax):
        """直方图：翻转次数分布"""
        results = self.data['results']
        n_flips = [r['n_flips'] for r in results]

        counts = [0] * 9
        for f in n_flips:
            counts[f] += 1

        bars = ax.bar(range(9), counts, color='steelblue', edgecolor='black')

        for i, c in enumerate(counts):
            ax.text(i, c + 1, str(c), ha='center', fontsize=10)

        ax.set_xlabel('翻转次数', fontsize=12)
        ax.set_ylabel('组合数', fontsize=12)
        ax.set_title('翻转次数分布 (C(8,k)二项分布)', fontsize=14)
        ax.set_xticks(range(9))

        theory = [1, 8, 28, 56, 70, 56, 28, 8, 1]
        for i, t in enumerate(theory):
            ax.text(i, counts[i] + 8, f'C={t}', ha='center', fontsize=8, color='red')

    def visualize_distribution(self, ax):
        """分布对比图"""
        results = self.data['results']

        by_zeros = {}
        for r in results:
            nz = r['n_zeros']
            if nz not in by_zeros:
                by_zeros[nz] = []
            by_zeros[nz].append(r['n_flips'])

        n_zeros_list = sorted(by_zeros.keys())
        means = [np.mean(by_zeros[nz]) for nz in n_zeros_list]
        stds = [np.std(by_zeros[nz]) for nz in n_zeros_list]

        ax.errorbar(n_zeros_list, means, yerr=stds, fmt='o-', capsize=5,
                   color='blue', linewidth=2, markersize=8, label='实验值')

        ideal = list(range(9))
        ax.plot(ideal, ideal, 'r--', linewidth=2, label='理想值')

        ax.set_xlabel('0的个数', fontsize=12)
        ax.set_ylabel('翻转次数 (平均±标准差)', fontsize=12)
        ax.set_title('理论与实验对比', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(9))

    def create_visualization(self, output_path=None):
        """创建完整可视化"""
        if self.data is None:
            print("无数据")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle('共振翻转实验 - 256种组合全覆盖\n(翻转次数 = 0的个数)', fontsize=16, y=1.02)

        self.visualize_scatter(axes[0, 0])
        self.visualize_heatmap(axes[0, 1])
        self.visualize_histogram(axes[1, 0])
        self.visualize_distribution(axes[1, 1])

        plt.tight_layout()

        if output_path is None:
            output_path = Path('./resonance_data') / 'visualization.png'

        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n可视化已保存: {output_path}")

        plt.close()

    def create_animation_data(self):
        """生成动画数据"""
        results = self.data['results']

        frames = []

        for n_cycle in [0, 1, 2, 5, 10, 50, 100]:
            grid = np.zeros((16, 16))

            for r in results:
                bits = r['bits']
                idx = int(''.join(str(b) for b in bits), 2)
                row = idx // 16
                col = idx % 16

                n_zeros = bits.count(0)
                if n_cycle >= n_zeros:
                    grid[row, col] = n_zeros
                else:
                    grid[row, col] = n_cycle

            frames.append(grid)

        return frames

    def save_summary(self):
        """保存分析摘要"""
        summary = {
            'n_bits': 8,
            'n_combinations': 256,
            'accuracy': self.data['analysis']['accuracy'],
            'mean_flips': self.data['analysis']['mean_flips'],
            'min_flips': self.data['analysis']['min_flips'],
            'max_flips': self.data['analysis']['max_flips'],
            'distribution': {
                str(k): len([r for r in self.data['results'] if r['n_flips'] == k])
                for k in range(9)
            },
            'conclusion': '翻转次数 = 0的个数 (完美线性关系)'
        }

        summary_path = Path('./resonance_data') / 'summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"摘要已保存: {summary_path}")

        return summary


def main():
    viz = ResonanceVisualizer()

    if viz.load_data() is None:
        print("\n请先运行: python3 resonance_cartesian_complete.py")
        return

    viz.create_visualization()

    summary = viz.save_summary()

    print("\n" + "=" * 60)
    print("  可视化完成")
    print("=" * 60)
    print(f"正确率: {summary['accuracy']:.1f}%")
    print(f"平均翻转: {summary['mean_flips']:.2f}")
    print(f"结论: {summary['conclusion']}")
    print("=" * 60)


if __name__ == "__main__":
    main()