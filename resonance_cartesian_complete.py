#!/usr/bin/env python3
"""
========================================================
笛卡尔积全实验 v3 - 完整256覆盖
========================================================

对8位张量的全部2^8 = 256种组合做实验

使用方法：
    python3 resonance_cartesian_complete.py
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from itertools import product

class CompleteCartesianExperiment:
    """
    完整笛卡尔积实验
    覆盖 00000000 到 11111111 全部256种
    """

    def __init__(self, n_bits=8):
        self.n_bits = n_bits
        self.n_combinations = 2 ** n_bits
        self.frequencies = [1e12, 2e12]
        self.resonance_freq = np.abs(self.frequencies[1] - self.frequencies[0]) / 2

        print("=" * 60)
        print("  笛卡尔积全实验 v3")
        print("  完整256覆盖")
        print("=" * 60)
        print(f"位长度: {n_bits}")
        print(f"组合数: {self.n_combinations} (2^{n_bits})")

    def phase(self, pos, t):
        return 2 * np.pi * self.frequencies[pos] * t

    def superposition(self, t):
        psi = np.exp(1j * self.phase(0, t)) + np.exp(1j * self.phase(1, t))
        return psi / 2

    def measure(self, bits, t, threshold=0.7):
        psi = self.superposition(t)
        prob = np.abs(psi)**2
        new_bits = bits.copy()

        if prob > threshold:
            for i in range(len(new_bits)):
                if bits[i] == 0:
                    new_bits[i] = 1
                    break

        return new_bits, prob

    def run_single(self, bits, n_cycles=100):
        state = bits.copy()
        flips = 0
        probs = []
        T = 1.0 / self.resonance_freq

        for i in range(n_cycles):
            t = i * T
            new_state, prob = self.measure(state, t)
            probs.append(prob)

            if new_state != state:
                flips += 1
                state = new_state

        return {
            'bits': bits,
            'n_flips': flips,
            'n_zeros': bits.count(0),
            'n_ones': bits.count(1),
            'final_bits': state
        }

    def run_all(self):
        """运行全部256种组合"""
        print(f"\n开始全部{self.n_combinations}种组合实验...")
        print("-" * 50)

        all_results = []
        zero_count_flip = {}

        for combo in range(self.n_combinations):
            bits = [(combo >> i) & 1 for i in range(self.n_bits)]
            n_zeros = bits.count(0)

            result = self.run_single(bits)
            all_results.append(result)

            if n_zeros not in zero_count_flip:
                zero_count_flip[n_zeros] = []
            zero_count_flip[n_zeros].append(result['n_flips'])

            if (combo + 1) % 64 == 0:
                print(f"  进度: {combo + 1}/{self.n_combinations}")

        print(f"  完成: {self.n_combinations}/{self.n_combinations}")

        return all_results, zero_count_flip

    def analyze(self, all_results, zero_count_flip):
        """分析所有结果"""
        print(f"\n{'='*60}")
        print("  汇总分析")
        print(f"{'='*60}")

        n_flips_list = [r['n_flips'] for r in all_results]
        n_zeros_list = [r['n_zeros'] for r in all_results]

        print(f"\n总实验数: {len(all_results)}")
        print(f"总翻转次数: {sum(n_flips_list)}")
        print(f"平均翻转: {np.mean(n_flips_list):.2f}")
        print(f"最小翻转: {min(n_flips_list)}")
        print(f"最大翻转: {max(n_flips_list)}")

        print(f"\n按0的个数分组:")
        for n_zeros in sorted(zero_count_flip.keys()):
            flips = zero_count_flip[n_zeros]
            print(f"  {n_zeros}个0: {len(flips)}种, 平均翻转={np.mean(flips):.2f}")

        print(f"\n理论分析:")
        print(f"  翻转次数 ≈ 张量中0的个数")
        print(f"  因为每次概率>阈值时，会翻转第一个遇到的0")

        # 验证
        correct = 0
        for r in all_results:
            if r['n_zeros'] > 0:
                if r['n_flips'] > 0:
                    correct += 1
            else:
                if r['n_flips'] == 0:
                    correct += 1

        print(f"\n理论验证:")
        print(f"  正确预测: {correct}/{len(all_results)} = {correct/len(all_results)*100:.1f}%")

        return {
            'total': len(all_results),
            'total_flips': sum(n_flips_list),
            'mean_flips': float(np.mean(n_flips_list)),
            'min_flips': int(min(n_flips_list)),
            'max_flips': int(max(n_flips_list)),
            'zero_count_flip': {k: [int(x) for x in v] for k, v in zero_count_flip.items()},
            'accuracy': correct / len(all_results) * 100
        }


def main():
    exp = CompleteCartesianExperiment(n_bits=8)

    all_results, zero_count_flip = exp.run_all()

    analysis = exp.analyze(all_results, zero_count_flip)

    full_results = {
        'timestamp': datetime.now().isoformat(),
        'n_bits': 8,
        'n_combinations': 256,
        'results': all_results,
        'analysis': analysis
    }

    filepath = Path('./resonance_data') / f"cartesian_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath.parent.mkdir(exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  结果已保存: {filepath}")
    print(f"{'='*60}")

    return full_results


if __name__ == "__main__":
    main()