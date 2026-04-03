#!/usr/bin/env python3
"""
========================================================
温度噪声控制方式对比（修正版）
========================================================

两种噪声施加方式：
1. 初始态噪声：开始前扰动一次，然后无噪声演化
2. 演化过程噪声：每步都施加随机翻转（持续扰动）
3. 离散翻转：固定翻转n个比特
"""

import numpy as np
from datetime import datetime

class NoiseControlTest:
    def __init__(self):
        self.entanglement = {i: [j for j in range(7) if j != i] for i in range(7)}

    def syndrome(self, code):
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0

    def resonance_flip(self, code, error_pos):
        new_code = code.copy()
        entangled = self.entanglement[error_pos]
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def evolve(self, code, max_iter=10000):
        """无噪声演化"""
        seen = {tuple(code): 0}
        for i in range(max_iter):
            syndrome = self.syndrome(code)
            error_pos = syndrome % 7 if syndrome > 0 else i % 7
            next_code = self.resonance_flip(code, error_pos)
            key = tuple(next_code)
            if key in seen:
                return {'final': tuple(code), 'loop_len': i + 1 - seen[key], 'states': len(seen)}
            code = next_code
            seen[key] = i + 1
        return {'final': tuple(code)}

    def test_noise_placement(self):
        """噪声施加位置对比"""
        print("=" * 70)
        print("  温度噪声施加方式对比")
        print("=" * 70)

        np.random.seed(42)
        initial = [0, 0, 0, 0, 0, 0, 0]

        print(f"\n基准: 初始态={initial}")
        result_base = self.evolve(initial.copy())
        print(f"无噪声终态: {result_base['final']}")

        print(f"\n{'噪声方式':<35} {'唯一终态':<12} {'回到基准':<10}")
        print("-" * 60)

        noise_levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

        for temp in noise_levels:
            # 方式1：初始态扰动（演化前扰动一次）
            finals1 = []
            for _ in range(50):
                np.random.seed(42 + _)
                noisy = initial.copy()
                for j in range(7):
                    if np.random.random() < temp:
                        noisy[j] ^= 1
                result = self.evolve(noisy)
                finals1.append(result['final'])

            unique1 = len(set(finals1))
            back1 = result_base['final'] in finals1

            # 方式2：演化过程噪声（每步施加）
            finals2 = []
            for _ in range(50):
                np.random.seed(42 + _)
                code = initial.copy()
                for step in range(1000):
                    syndrome = self.syndrome(code)
                    error_pos = syndrome % 7 if syndrome > 0 else step % 7
                    code = self.resonance_flip(code, error_pos)
                    for j in range(7):
                        if np.random.random() < temp:
                            code[j] ^= 1
                finals2.append(tuple(code))

            unique2 = len(set(finals2))
            back2 = result_base['final'] in finals2

            print(f"初始态扰动(1次), p={temp}:    {unique1:<12} {back1}")
            print(f"  演化过程扰动(每步), p={temp}: {unique2:<12} {back2}")

    def test_discrete_flips(self):
        """离散翻转测试"""
        print(f"\n{'='*70}")
        print("  离散翻转（初始态固定翻转n位）")
        print(f"{'='*70}")

        np.random.seed(42)
        initial = [0, 0, 0, 0, 0, 0, 0]
        result_base = self.evolve(initial.copy())
        print(f"基准: {result_base['final']}")

        print(f"\n{'翻转位数':<15} {'唯一终态':<12} {'回到基准'}")
        print("-" * 40)

        for n_flips in range(8):
            finals = []
            for _ in range(100):
                np.random.seed(42 + _)
                noisy = initial.copy()
                if n_flips > 0:
                    flip_pos = np.random.choice(7, min(n_flips, 7), replace=False)
                    for p in flip_pos:
                        noisy[p] ^= 1
                result = self.evolve(noisy)
                finals.append(result['final'])

            unique = len(set(finals))
            back = result_base['final'] in finals
            print(f"翻转{n_flips}位:     {unique:<12} {back}")


if __name__ == "__main__":
    exp = NoiseControlTest()
    exp.test_noise_placement()
    exp.test_discrete_flips()