#!/usr/bin/env python3
"""
========================================================
纠缠共振持续迭代实验 v2
========================================================

改进：每次迭代用当前码重新确定错误位（基于校验子）
而不是固定初始错误位
"""

import numpy as np
from datetime import datetime

class ResonanceIterV2:
    def __init__(self):
        # 纠缠映射（数据位影响校验位）
        self.data_to_parity = {
            0: [1],       # D0 → P0
            3: [1, 4],    # D1 → P0, P2
            5: [2, 4],    # D2 → P1, P2
            6: [2],       # D3 → P1
        }

        # 校验位→数据位
        self.parity_to_data = {
            1: [0, 3, 6],
            2: [0, 5, 6],
            4: [3, 5],
        }

        np.random.seed(int(datetime.now().timestamp()) % 100000)

        print("=" * 60)
        print("  纠缠共振持续迭代实验 v2")
        print("=" * 60)

    def encode(self, data):
        D0, D1, D2, D3 = data[0], data[1], data[2], data[3]
        code = [0] * 7
        code[0] = D0
        code[3] = D1
        code[5] = D2
        code[6] = D3
        code[1] = D0 ^ D1 ^ D3
        code[2] = D0 ^ D2 ^ D3
        code[4] = D1 ^ D2 ^ D3
        return code

    def syndrome(self, code):
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0

    def get_error_pos(self, syndrome):
        mapping = {1:1, 2:2, 3:0, 4:4, 5:3, 6:5, 7:6}
        return mapping.get(syndrome)

    def get_entangled(self, error_pos):
        """获取纠缠位"""
        entangled = set()
        if error_pos in self.data_to_parity:
            entangled.update(self.data_to_parity[error_pos])
        if error_pos in self.parity_to_data:
            entangled.update(self.parity_to_data[error_pos])
        entangled.discard(error_pos)
        return list(entangled)

    def resonance_flip(self, code, error_pos):
        new_code = code.copy()
        entangled = self.get_entangled(error_pos)
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code, [error_pos] + entangled

    def run_trial(self, max_iter=50):
        """单次试验"""
        data = [np.random.randint(0, 2) for _ in range(4)]
        original = self.encode(data)

        current = original.copy()
        error_pos = np.random.randint(0, 7)
        current[error_pos] ^= 1

        history = [current]
        states_seen = {tuple(current): 0}

        for i in range(max_iter):
            syndrome = self.syndrome(current)
            detected_pos = self.get_error_pos(syndrome)

            if detected_pos is None:
                detected_pos = np.random.randint(0, 7)

            after_flip, flipped = self.resonance_flip(current, detected_pos)

            if tuple(after_flip) in states_seen:
                return {
                    'original': original,
                    'history': history,
                    'final': current,
                    'loop': True,
                    'loop_at': states_seen[tuple(after_flip)],
                    'total_iter': i,
                    'unique_states': len(states_seen),
                    'back': current == original,
                }

            current = after_flip
            states_seen[tuple(current)] = i + 1
            history.append(current)

        return {
            'original': original,
            'history': history,
            'final': current,
            'loop': False,
            'total_iter': max_iter,
            'unique_states': len(states_seen),
            'back': current == original,
        }

    def run(self, n=30, max_iter=100):
        print(f"运行 {n} 次试验，每次最多 {max_iter} 次迭代...")
        results = []
        for i in range(n):
            results.append(self.run_trial(max_iter))
            if (i + 1) % 10 == 0:
                print(f"  进度: {i+1}/{n}")
        return results

    def analyze(self, results):
        total = len(results)
        n_loop = sum(1 for r in results if r['loop'])
        n_back = sum(1 for r in results if r['back'])
        avg_iter = np.mean([r['total_iter'] for r in results])
        avg_states = np.mean([r['unique_states'] for r in results])

        print(f"\n{'='*60}")
        print("  实验结果分析")
        print(f"{'='*60}")
        print(f"\n总实验: {total}")
        print(f"检测到循环: {n_loop}/{total} = {n_loop/total*100:.1f}%")
        print(f"回到原始码: {n_back}/{total} = {n_back/total*100:.1f}%")
        print(f"平均迭代: {avg_iter:.1f}")
        print(f"平均唯一状态: {avg_states:.1f}")

        return {'total': total, 'n_loop': n_loop, 'n_back': n_back}

    def show_examples(self, results, n=6):
        print(f"\n{'='*60}")
        print("  典型例子")
        print(f"{'='*60}")
        for i, r in enumerate(results[:n]):
            print(f"\n例子{i+1}:")
            print(f"  原始: {r['original']}")
            print(f"  最终: {r['final']}")
            print(f"  迭代: {r['total_iter']}, 状态: {r['unique_states']}, 循环: {r['loop']}")

            if len(r['history']) <= 15:
                print(f"  演变: {' → '.join([str(h) for h in r['history']])}")


def main():
    exp = ResonanceIterV2()
    results = exp.run(n=30, max_iter=100)
    exp.show_examples(results, n=6)
    exp.analyze(results)


if __name__ == "__main__":
    main()