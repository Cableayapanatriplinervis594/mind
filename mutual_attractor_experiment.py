#!/usr/bin/env python3
"""
两个全连接图互为吸引子实验

核心问题：
- 全连接图K8的振荡在两个状态间切换
- 这两个状态是否互为吸引子？
- 是否存在互逆关系？

验证：
1. 从状态A出发，是否收敛到状态B？
2. 从状态B出发，是否收敛到状态A？
3. A和B是否是互逆关系？
"""

import numpy as np

class MutualAttractorExperiment:
    """
    互为吸引子的两个全连接图实验
    """

    def __init__(self, n_bits=8):
        self.n_bits = n_bits
        self.entanglement = {i: [j for j in range(n_bits) if j != i]
                              for i in range(n_bits)}

    def syndrome(self, code):
        return sum(code) % 2

    def resonance_flip(self, code, error_pos):
        new_code = code.copy()
        entangled = self.entanglement[error_pos]
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def bits_to_str(self, bits):
        return ''.join(str(b) for b in bits)

    def bits_to_int(self, bits):
        return sum(bits[i] << i for i in range(self.n_bits))

    def evolve_one_step(self, bits):
        """单步演化"""
        syndrome_val = self.syndrome(bits)
        return self.resonance_flip(bits, syndrome_val)

    def find_attractor_pair(self, initial_bits, max_steps=1000):
        """
        找到从初始状态出发的吸引子对
        """
        bits = initial_bits.copy()
        seen = {tuple(bits): 0}
        path = [(0, tuple(bits))]

        for step in range(max_steps):
            bits = self.evolve_one_step(bits)
            key = tuple(bits)

            if key in seen:
                cycle_start = seen[key]
                cycle_len = step + 1 - cycle_start
                cycle_path = path[cycle_start:]

                return {
                    'initial': tuple(initial_bits),
                    'cycle_len': cycle_len,
                    'cycle_start': cycle_start,
                    'attractor_pair': cycle_path,
                    'found': True
                }

            seen[key] = step + 1
            path.append((step + 1, key))

        return {'initial': tuple(initial_bits), 'found': False}

    def is_inverse_pair(self, state_a, state_b):
        """
        检查两个状态是否是互逆关系
        互逆 = 每一位都相反
        """
        return all(a != b for a, b in zip(state_a, state_b))

    def is_complement_pair(self, state_a, state_b):
        """
        检查两个状态是否是补关系
        补 = 所有位加起来是奇数（或某个固定值）
        """
        xor = [a ^ b for a, b in zip(state_a, state_b)]
        syndrome = sum(xor) % 2
        return syndrome == 0

    def are_mutual_attractors(self, pair_a, pair_b, n_steps=10):
        """
        验证两个状态是否互为吸引子

        互为吸引子的定义：
        - 从pair_a出发，n步内到达pair_b
        - 从pair_b出发，n步内到达pair_a
        """
        # 从A到B
        bits_a = list(pair_a)
        a_to_b_steps = None
        for step in range(n_steps):
            bits_a = self.evolve_one_step(bits_a)
            if tuple(bits_a) == pair_b:
                a_to_b_steps = step + 1
                break

        # 从B到A
        bits_b = list(pair_b)
        b_to_a_steps = None
        for step in range(n_steps):
            bits_b = self.evolve_one_step(bits_b)
            if tuple(bits_b) == pair_a:
                b_to_a_steps = step + 1
                break

        return {
            'pair': (pair_a, pair_b),
            'a_to_b_steps': a_to_b_steps,
            'b_to_a_steps': b_to_a_steps,
            'mutual': a_to_b_steps is not None and b_to_a_steps is not None
        }

    def experiment_find_attractor_pairs(self):
        """
        实验1：找到所有8比特全连接图的吸引子对
        """
        print("\n" + "="*70)
        print("  实验1: 寻找全连接图K8的吸引子对")
        print("="*70)

        attractor_pairs = []
        tested = set()

        # 测试所有可能的初始状态（采样）
        for initial_int in range(256):
            initial = [(initial_int >> i) & 1 for i in range(self.n_bits)]
            result = self.find_attractor_pair(initial)

            if result['found'] and result['cycle_len'] == 2:
                # 找到L=2的吸引子对
                pair = tuple(sorted(result['attractor_pair'][0][1]))

                if pair not in tested:
                    tested.add(pair)
                    pair_info = result['attractor_pair']
                    attractor_pairs.append({
                        'pair': pair_info,
                        'cycle_len': 2
                    })

        print(f"\n  找到 {len(attractor_pairs)} 个 L=2 吸引子对")

        for i, ap in enumerate(attractor_pairs[:10]):
            pair_states = ap['pair']
            state0 = self.bits_to_str(pair_states[0][1])
            state1 = self.bits_to_str(pair_states[1][1])
            print(f"    对{i+1}: {state0} ↔ {state1}")

        return attractor_pairs

    def experiment_check_inverse_relation(self):
        """
        实验2：检查吸引子对是否是互逆关系
        """
        print("\n" + "="*70)
        print("  实验2: 检查吸引子对的互逆关系")
        print("="*70)

        # 使用'A'字符的吸引子对
        initial_A = [(65 >> i) & 1 for i in range(self.n_bits)]  # ASCII 65 = 'A'
        result_A = self.find_attractor_pair(initial_A)

        if result_A['found'] and result_A['cycle_len'] == 2:
            pair = result_A['attractor_pair']
            state_A = pair[0][1]
            state_B = pair[1][1]

            print(f"\n  'A' 的吸引子对:")
            print(f"    状态A: {self.bits_to_str(state_A)} (int={self.bits_to_int(state_A)})")
            print(f"    状态B: {self.bits_to_str(state_B)} (int={self.bits_to_int(state_B)})")

            # 检查互逆
            is_inverse = self.is_inverse_pair(state_A, state_B)
            print(f"\n    互逆关系: {'是' if is_inverse else '否'}")

            # 检查异或
            xor_result = [a ^ b for a, b in zip(state_A, state_B)]
            xor_int = self.bits_to_int(xor_result)
            print(f"    A XOR B: {self.bits_to_str(xor_result)} (int={xor_int})")
            print(f"    校验和: {sum(xor_result)}")

            # 检查是否是补关系
            is_complement = self.is_complement_pair(state_A, state_B)
            print(f"    互补关系: {'是' if is_complement else '否'}")

            # 验证互为吸引子
            mutual = self.are_mutual_attractors(state_A, state_B)
            print(f"\n    互为吸引子验证:")
            print(f"      A→B: {mutual['a_to_b_steps']}步")
            print(f"      B→A: {mutual['b_to_a_steps']}步")
            print(f"      互为吸引子: {'是' if mutual['mutual'] else '否'}")

            return {
                'state_A': state_A,
                'state_B': state_B,
                'is_inverse': is_inverse,
                'xor_result': xor_result,
                'is_mutual_attractor': mutual['mutual']
            }

        return None

    def experiment_all_ascii_pairs(self):
        """
        实验3：检查所有ASCII字符的吸引子对关系
        """
        print("\n" + "="*70)
        print("  实验3: 所有ASCII字符的吸引子对分析")
        print("="*70)

        results = []

        for ascii_val in range(128):
            char = chr(ascii_val)
            initial = [(ascii_val >> i) & 1 for i in range(self.n_bits)]

            result = self.find_attractor_pair(initial)

            if result['found'] and result['cycle_len'] == 2:
                pair = result['attractor_pair']
                state_A = pair[0][1]
                state_B = pair[1][1]

                is_inverse = self.is_inverse_pair(state_A, state_B)
                xor_int = self.bits_to_int([a ^ b for a, b in zip(state_A, state_B)])

                results.append({
                    'char': char,
                    'ascii': ascii_val,
                    'state_A': self.bits_to_str(state_A),
                    'state_B': self.bits_to_str(state_B),
                    'is_inverse': is_inverse,
                    'xor': xor_int
                })

        # 统计
        inverse_count = sum(1 for r in results if r['is_inverse'])
        non_inverse_count = len(results) - inverse_count

        print(f"\n  总计 L=2 吸引子: {len(results)} 个字符")
        print(f"    互逆关系: {inverse_count}")
        print(f"    非互逆关系: {non_inverse_count}")

        # 显示样本
        print(f"\n  互逆关系样本:")
        for r in results[:5]:
            if r['is_inverse']:
                print(f"    '{r['char']}': {r['state_A']} ↔ {r['state_B']}")

        print(f"\n  非互逆关系样本:")
        non_inverse = [r for r in results if not r['is_inverse']]
        for r in non_inverse[:5]:
            print(f"    '{r['char']}': {r['state_A']} ↔ {r['state_B']}, xor={r['xor']}")

        return results

    def experiment_mutual_attractor_verification(self):
        """
        实验4：详细验证互为吸引子关系
        """
        print("\n" + "="*70)
        print("  实验4: 互为吸引子详细验证")
        print("="*70)

        # 使用 'A' = 65 = 01000001 的吸引子
        initial = [(65 >> i) & 1 for i in range(self.n_bits)]
        result = self.find_attractor_pair(initial)

        if result['found'] and result['cycle_len'] == 2:
            pair = result['attractor_pair']
            state_A = pair[0][1]
            state_B = pair[1][1]

            print(f"\n  吸引子对: {self.bits_to_str(state_A)} ↔ {self.bits_to_str(state_B)}")
            print(f"\n  从状态A开始的演化:")
            bits = list(state_A)
            for step in range(6):
                print(f"    Step {step}: {self.bits_to_str(bits)}")
                bits = self.evolve_one_step(bits)

            print(f"\n  从状态B开始的演化:")
            bits = list(state_B)
            for step in range(6):
                print(f"    Step {step}: {self.bits_to_str(bits)}")
                bits = self.evolve_one_step(bits)

            # 验证一步互逆
            syndrome_A = self.syndrome(list(state_A))
            next_A = self.resonance_flip(list(state_A), syndrome_A)

            syndrome_B = self.syndrome(list(state_B))
            next_B = self.resonance_flip(list(state_B), syndrome_B)

            print(f"\n  单步验证:")
            print(f"    A的syndrome={syndrome_A}, 下一步={self.bits_to_str(next_A)}")
            print(f"    B的syndrome={syndrome_B}, 下一步={self.bits_to_str(next_B)}")
            print(f"    A的下一步=B: {next_A == state_B}")
            print(f"    B的下一步=A: {next_B == state_A}")


def main():
    print("="*70)
    print("  两个全连接图互为吸引子实验")
    print("  验证：K8振荡的两个状态是否互为吸引子？")
    print("="*70)

    exp = MutualAttractorExperiment(n_bits=8)

    # 实验1：寻找吸引子对
    exp.experiment_find_attractor_pairs()

    # 实验2：检查互逆关系
    exp.experiment_check_inverse_relation()

    # 实验3：所有ASCII分析
    exp.experiment_all_ascii_pairs()

    # 实验4：详细验证
    exp.experiment_mutual_attractor_verification()

    print("\n" + "="*70)
    print("  结论")
    print("="*70)
    print("""
    互为吸引子的定义：
    - A的下一步是B
    - B的下一步是A
    - 形成两步循环 L=2

    关键发现：
    - 所有L=2吸引子对都是一步互达
    - 这就是"二元振荡"的本质
    - A → B → A → B ...
    """)


if __name__ == "__main__":
    main()