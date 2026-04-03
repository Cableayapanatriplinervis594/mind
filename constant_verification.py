#!/usr/bin/env python3
"""
========================================================
常数验证实验
========================================================

验证：78%是否是理论值75%的近似

理论分析：
- 8个位置中，有纠缠对的是 0,1,2,5,6,7 (6个)
- 没有纠缠对的是 3,4 (2个)
- 理论成功率 = 6/8 = 75%

实验：测试不同样本量，看是否稳定在75%
"""

import numpy as np
from datetime import datetime
from pathlib import Path

class ConstantVerification:
    def __init__(self, n_bits=8):
        self.n_bits = n_bits

        # 纠缠对
        self.entangled_pairs = [(0, 5), (1, 6), (2, 7)]

        # 位置到纠缠对的映射
        self.pos_to_pair = {}
        for pair in self.entangled_pairs:
            for p in pair:
                self.pos_to_pair[p] = pair

        np.random.seed(None)

        print("=" * 60)
        print("  常数验证实验")
        print("  验证 75% 理论成功率")
        print("=" * 60)

        # 统计有纠缠的位置
        self.has_entanglement = set()
        for pair in self.entangled_pairs:
            self.has_entanglement.update(pair)

        print(f"\n纠缠对: {self.entangled_pairs}")
        print(f"有纠缠的位置: {sorted(self.has_entanglement)}")
        print(f"无纠缠的位置: {sorted(set(range(n_bits)) - self.has_entanglement)}")
        print(f"\n理论成功率: {len(self.has_entanglement)}/{n_bits} = {len(self.has_entanglement)/n_bits*100:.1f}%")

    def inject_error_and_flip(self, correct_bits):
        """注入错误 + 纠缠翻转"""
        bits = correct_bits.copy()

        # 随机注入一位错误
        error_pos = np.random.randint(0, self.n_bits)
        bits[error_pos] ^= 1

        # 检查是否触发纠缠
        if error_pos in self.pos_to_pair:
            pair = self.pos_to_pair[error_pos]
            partner = pair[0] if pair[1] == error_pos else pair[1]
            bits[partner] ^= 1  # 纠缠翻转
            return bits, True, error_pos, partner
        else:
            return bits, False, error_pos, -1

    def run_trial(self, n_samples):
        """运行一组实验"""
        n_success = 0
        n_total = n_samples

        for _ in range(n_samples):
            correct = [np.random.randint(0, 2) for _ in range(self.n_bits)]
            _, success, _, _ = self.inject_error_and_flip(correct)
            if success:
                n_success += 1

        return n_success, n_total

    def run_verification(self):
        """验证实验"""
        sample_sizes = [100, 500, 1000, 5000, 10000]

        print("\n" + "=" * 60)
        print("  不同样本量的实验结果")
        print("=" * 60)

        print(f"\n{'样本量':<10} {'成功次数':<10} {'成功率':<10} {'与75%的偏差':<10}")
        print("-" * 40)

        results = []

        for n in sample_sizes:
            n_success, n_total = self.run_trial(n)
            rate = n_success / n_total * 100
            deviation = abs(rate - 75.0)

            print(f"{n:<10} {n_success:<10} {rate:<10.2f}% {deviation:<10.2f}%")

            results.append({
                'n_samples': n,
                'n_success': n_success,
                'rate': rate,
                'deviation': deviation
            })

        avg_rate = np.mean([r['rate'] for r in results])
        avg_deviation = np.mean([r['deviation'] for r in results])

        print("-" * 40)
        print(f"{'平均':<10} {'':<10} {avg_rate:<10.2f}% {avg_deviation:<10.2f}%")

        print(f"\n结论:")
        print(f"  理论值: 75.0%")
        print(f"  实验均值: {avg_rate:.2f}%")
        print(f"  平均偏差: {avg_deviation:.2f}%")

        if avg_deviation < 2.0:
            print(f"\n✓ 验证成功！成功率确实接近常数 75%")
        else:
            print(f"\n⚠️ 偏差较大，需要进一步分析")

        return results


def main():
    exp = ConstantVerification(n_bits=8)
    results = exp.run_verification()

    return results


if __name__ == "__main__":
    main()