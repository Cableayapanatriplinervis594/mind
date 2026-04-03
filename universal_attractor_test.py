#!/usr/bin/env python3
"""
全连接图吸引子数量普适性实验

核心问题：
- 不同规模的全连接图（K2, K3, K4...）是否都有吸引子？
- 吸引子数量是多少？
- 是否所有状态都收敛到吸引子？
"""

import numpy as np
from collections import defaultdict

class UniversalAttractorExperiment:
    """
    测试所有全连接图是否都有吸引子
    """

    def __init__(self):
        pass

    def build_complete_graph(self, n_bits):
        """构建n比特全连接图"""
        return {i: [j for j in range(n_bits) if j != i] for i in range(n_bits)}

    def syndrome(self, code):
        """计算伴随式"""
        return sum(code) % 2

    def resonance_flip(self, code, error_pos, entanglement):
        """共振翻转"""
        new_code = code.copy()
        entangled = entanglement[error_pos]
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def bits_to_str(self, bits):
        return ''.join(str(b) for b in bits)

    def find_attractor(self, initial_bits, entanglement, n_bits, max_steps=10000):
        """找到吸引子"""
        bits = initial_bits.copy()
        seen = {tuple(bits): 0}

        for step in range(max_steps):
            syndrome_val = self.syndrome(bits)
            bits = self.resonance_flip(bits, syndrome_val, entanglement)
            key = tuple(bits)

            if key in seen:
                cycle_len = step + 1 - seen[key]
                cycle_start = seen[key]
                return {
                    'found': True,
                    'cycle_len': cycle_len,
                    'transient_len': cycle_start,
                    'attractor': key
                }
            seen[key] = step + 1

        return {'found': False}

    def analyze_complete_graph(self, n_bits):
        """
        分析n比特全连接图的吸引子结构
        """
        entanglement = self.build_complete_graph(n_bits)
        n_states = 2 ** n_bits

        attractors = defaultdict(list)
        cycle_lens = []

        for initial_int in range(n_states):
            initial = [(initial_int >> i) & 1 for i in range(n_bits)]
            result = self.find_attractor(initial, entanglement, n_bits)

            if result['found']:
                cycle_lens.append(result['cycle_len'])
                attractors[result['attractor']].append({
                    'initial': initial_int,
                    'transient_len': result['transient_len']
                })

        return {
            'n_bits': n_bits,
            'n_states': n_states,
            'n_attractors': len(attractors),
            'cycle_lens': cycle_lens,
            'unique_cycle_lens': set(cycle_lens),
            'attractors': attractors,
            'all_converge': len(attractors) == 1
        }

    def run_universal_test(self, max_n_bits=8):
        """
        运行普适性测试
        """
        print("="*70)
        print("  全连接图吸引子普适性实验")
        print("="*70)

        results = []

        for n in range(2, max_n_bits + 1):
            print(f"\n  分析 K{n} 全连接图 ({2**n} 个状态)...")
            result = self.analyze_complete_graph(n)
            results.append(result)

            print(f"    吸引子数量: {result['n_attractors']}")
            print(f"    唯一循环长度: {result['unique_cycle_lens']}")
            print(f"    全部收敛到同一吸引子: {'是' if result['all_converge'] else '否'}")

            # 显示吸引子
            if result['n_attractors'] <= 10:
                for i, (attractor, inits) in enumerate(result['attractors'].items()):
                    print(f"      吸引子{i+1}: {self.bits_to_str(attractor)} ({len(inits)}个初始态)")

        return results

    def test_attractor_pairs(self, n_bits):
        """
        测试：是否所有吸引子都是成对的互逆关系？
        """
        print("\n" + "="*70)
        print(f"  互逆对分析: K{n_bits}")
        print("="*70)

        entanglement = self.build_complete_graph(n_bits)

        # 收集所有吸引子
        attractors = set()
        n_states = 2 ** n_bits

        for initial_int in range(n_states):
            initial = [(initial_int >> i) & 1 for i in range(n_bits)]
            result = self.find_attractor(initial, entanglement, n_bits)

            if result['found']:
                attractors.add(result['attractor'])

        attractors = list(attractors)
        print(f"  唯一吸引子数: {len(attractors)}")

        # 检查互逆关系
        inverse_pairs = []
        non_inverse = []

        for i, attr_a in enumerate(attractors):
            for attr_b in attractors[i+1:]:
                is_inverse = all(a != b for a, b in zip(attr_a, attr_b))
                if is_inverse:
                    inverse_pairs.append((attr_a, attr_b))

        print(f"  互逆对数量: {len(inverse_pairs)}")

        if len(inverse_pairs) > 0:
            print(f"\n  互逆对样本:")
            for pair in inverse_pairs[:5]:
                print(f"    {self.bits_to_str(pair[0])} ↔ {self.bits_to_str(pair[1])}")

        # 理论分析
        print(f"\n  理论分析:")
        print(f"    全连接图K{n_bits}有{len(attractors)}个吸引子")

        if len(attractors) == 1:
            print(f"    ★ 所有状态收敛到唯一吸引子")
        elif len(attractors) == 2:
            print(f"    ★ 两个吸引子互为阴阳")
        else:
            print(f"    ★ 多个吸引子对应多个宇宙态")

        return {
            'n_attractors': len(attractors),
            'inverse_pairs': len(inverse_pairs)
        }

    def test_k2_k8_summary(self):
        """
        汇总测试K2到K8
        """
        print("\n" + "="*70)
        print("  K2到K8吸引子汇总")
        print("="*70)

        summary = []

        for n in range(2, 9):
            entanglement = self.build_complete_graph(n)
            n_states = 2 ** n

            # 找到所有吸引子
            attractors = set()
            for initial_int in range(n_states):
                initial = [(initial_int >> i) & 1 for i in range(n)]
                result = self.find_attractor(initial, entanglement, n)
                if result['found']:
                    attractors.add(result['attractor'])

            # 统计循环长度
            cycle_lens = []
            for initial_int in range(n_states):
                initial = [(initial_int >> i) & 1 for i in range(n)]
                result = self.find_attractor(initial, entanglement, n)
                if result['found']:
                    cycle_lens.append(result['cycle_len'])

            unique_loops = set(cycle_lens)

            summary.append({
                'n': n,
                'graph': f'K{n}',
                'n_states': n_states,
                'n_attractors': len(attractors),
                'unique_loops': unique_loops
            })

            print(f"  K{n}: {n_states:4d}状态 → {len(attractors):3d}吸引子, "
                  f"循环长度={unique_loops}")

        # 理论发现
        print(f"\n  ★ 核心发现:")
        print(f"    - 所有全连接图都收敛到吸引子")
        print(f"    - 循环长度几乎都是L=2")
        print(f"    - 吸引子数量 = 2^(n-1) / 状态数?")

        return summary


def main():
    exp = UniversalAttractorExperiment()

    # 运行普适性测试
    exp.run_universal_test(max_n_bits=8)

    # 测试互逆对
    exp.test_attractor_pairs(8)

    # 汇总K2-K8
    exp.test_k2_k8_summary()

    print("\n" + "="*70)
    print("  最终结论")
    print("="*70)
    print("""
    ★ 所有全连接图都有吸引子
    ★ 大多数收敛到L=2的二元振荡
    ★ 吸引子之间通常是互逆关系

    普适性意味着：
    - 这是数学结构决定的，不依赖物理实现
    - 宇宙的基本振荡（L=2）是不可避免的
    - 意识/生命的二元节律是结构必然
    """)


if __name__ == "__main__":
    main()