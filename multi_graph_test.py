#!/usr/bin/env python3
"""
========================================================
测试多种图结构的动力学行为
========================================================

测试7种不同的图结构：
1. 汉明码结构
2. 完全图
3. 环形
4. 星形（中心辐射）
5. 二分图
6. 链形
7. 网格(2x3)
"""

import numpy as np

class MultiGraphTest:
    def __init__(self):
        self.graphs = {
            '汉明码': {
                0: [1],
                1: [0, 3, 6],
                2: [0, 5, 6],
                3: [1, 4],
                4: [3, 5],
                5: [2, 4],
                6: [1, 2],
            },
            '完全图': {i: [j for j in range(7) if j != i] for i in range(7)},
            '环形': {
                0: [1, 6],
                1: [0, 2],
                2: [1, 3],
                3: [2, 4],
                4: [3, 5],
                5: [4, 6],
                6: [5, 0],
            },
            '星形': {
                0: [1, 2, 3, 4, 5, 6],
                1: [0],
                2: [0],
                3: [0],
                4: [0],
                5: [0],
                6: [0],
            },
            '二分图': {
                0: [1, 2, 3],
                1: [0, 4, 5],
                2: [0, 4, 6],
                3: [0, 5, 6],
                4: [1, 2],
                5: [1, 3],
                6: [2, 3],
            },
            '链形': {
                0: [1],
                1: [0, 2],
                2: [1, 3],
                3: [2, 4],
                4: [3, 5],
                5: [4, 6],
                6: [5],
            },
            '网格(2x3)': {
                0: [1, 3],
                1: [0, 2, 4],
                2: [1, 5],
                3: [0, 4],
                4: [1, 3, 5],
                5: [2, 4],
                6: [],
            },
        }

        print("=" * 70)
        print("  多种图结构动力学测试")
        print("=" * 70)

        for name, g in self.graphs.items():
            edges = sum(len(v) for v in g.values()) // 2
            print(f"{name}: {edges}条边")

    def syndrome(self, code):
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0

    def resonance_flip(self, code, error_pos, entanglement):
        new_code = code.copy()
        entangled = entanglement.get(error_pos, [])
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def evolve(self, code, entanglement, max_iter=1000):
        seen = {tuple(code): 0}
        history = [code]
        for i in range(max_iter):
            syndrome = self.syndrome(code)
            error_pos = syndrome % 7 if syndrome > 0 else i % 7
            next_code = self.resonance_flip(code, error_pos, entanglement)
            key = tuple(next_code)
            if key in seen:
                loop_len = i + 1 - seen[key]
                return {
                    'loop': True,
                    'loop_len': loop_len,
                    'total_states': len(seen),
                    'history': history,
                }
            code = next_code
            seen[key] = i + 1
            history.append(code)
        return {'loop': False, 'total_states': len(seen), 'history': history}

    def test_graph(self, name, entanglement):
        loop_lens = []
        total_states_list = []

        for n in range(256):
            code = [(n >> i) & 1 for i in range(7)]
            result = self.evolve(code, entanglement)
            loop_lens.append(result['loop_len'])
            total_states_list.append(result['total_states'])

        # 统计
        loop_len_counts = {}
        for ll in loop_lens:
            loop_len_counts[ll] = loop_len_counts.get(ll, 0) + 1

        state_counts = {}
        for ts in total_states_list:
            state_counts[ts] = state_counts.get(ts, 0) + 1

        lost = sum(1 for ts in total_states_list if ts > 2)
        kept = sum(1 for ts in total_states_list if ts == 2)

        return {
            'loop_lens': loop_lens,
            'total_states': total_states_list,
            'loop_len_counts': loop_len_counts,
            'state_counts': state_counts,
            'lost_rate': lost / 256 * 100,
            'kept_rate': kept / 256 * 100,
        }

    def run(self):
        results = {}

        print("\n" + "=" * 70)
        print("  测试结果")
        print("=" * 70)

        for name, entanglement in self.graphs.items():
            print(f"\n【{name}】")
            r = self.test_graph(name, entanglement)

            print(f"  丢失初始率: {r['lost_rate']:.1f}%")
            print(f"  保留初始率: {r['kept_rate']:.1f}%")

            print(f"  循环长度分布:", end=" ")
            for ll in sorted(r['loop_len_counts'].keys()):
                print(f"长度{ll}:{r['loop_len_counts'][ll]} ", end="")
            print()

            print(f"  状态数分布:", end=" ")
            for ts in sorted(r['state_counts'].keys()):
                print(f"{ts}状态:{r['state_counts'][ts]} ", end="")
            print()

            results[name] = r

        # 汇总对比
        print("\n" + "=" * 70)
        print("  汇总对比")
        print("=" * 70)
        print(f"{'结构':<10} {'丢失率':<10} {'保留率':<10} {'循环长度':<15}")
        print("-" * 50)
        for name, r in results.items():
            main_loop_len = max(r['loop_len_counts'].keys(), key=lambda x: r['loop_len_counts'][x])
            print(f"{name:<10} {r['lost_rate']:<10.1f} {r['kept_rate']:<10.1f} {main_loop_len}({r['loop_len_counts'][main_loop_len]}次)")

        return results


if __name__ == "__main__":
    exp = MultiGraphTest()
    results = exp.run()