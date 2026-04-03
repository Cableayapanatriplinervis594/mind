#!/usr/bin/env python3
"""
分析丢失初始状态的数据特征
"""

import numpy as np

class AnalyzeLost:
    def __init__(self):
        self.data_to_parity = {
            0: [1],
            3: [1, 4],
            5: [2, 4],
            6: [2],
        }
        self.parity_to_data = {
            1: [0, 3, 6],
            2: [0, 5, 6],
            4: [3, 5],
        }

    def syndrome(self, code):
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0

    def resonance_flip(self, code, syndrome):
        error_pos = syndrome % 7 if syndrome > 0 else 0
        new_code = code.copy()
        entangled = set()
        if error_pos in self.data_to_parity:
            entangled.update(self.data_to_parity[error_pos])
        if error_pos in self.parity_to_data:
            entangled.update(self.parity_to_data[error_pos])
        entangled.discard(error_pos)
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def evolve(self, code, max_iter=100):
        seen = {tuple(code): 0}
        history = [code]
        for i in range(max_iter):
            syndrome = self.syndrome(code)
            next_code = self.resonance_flip(code, syndrome)
            key = tuple(next_code)
            if key in seen:
                loop_start = seen[key]
                return {
                    'in_loop': tuple(code) in seen,
                    'loop_start': loop_start,
                    'total_states': len(seen),
                    'history': history,
                }
            code = next_code
            seen[key] = i + 1
            history.append(code)
        return {'in_loop': False, 'total_states': len(seen), 'history': history}

    def run(self):
        print("分析丢失初始状态的数据特征")
        print("=" * 60)

        lost_examples = []
        kept_examples = []

        for n in range(256):
            code = [(n >> i) & 1 for i in range(7)]
            result = self.evolve(code)

            features = {
                'code': code,
                'n_ones': sum(code),
                'syndrome': self.syndrome(code),
                'is_valid_hamming': self.syndrome(code) == 0,
            }

            if result['total_states'] == 3:
                lost_examples.append(features)
            else:
                kept_examples.append(features)

        print(f"\n总状态: 256")
        print(f"丢失初始(状态数=3): {len(lost_examples)}")
        print(f"保留初始(状态数=2): {len(kept_examples)}")

        print(f"\n{'='*60}")
        print("  特征对比")
        print(f"{'='*60}")

        # 汉明码有效态分析
        lost_valid = sum(1 for x in lost_examples if x['is_valid_hamming'])
        kept_valid = sum(1 for x in kept_examples if x['is_valid_hamming'])
        print(f"\n原始是有效汉明码(校验子=0):")
        print(f"  丢失组: {lost_valid}/{len(lost_examples)} = {lost_valid/len(lost_examples)*100:.1f}%")
        print(f"  保留组: {kept_valid}/{len(kept_examples)} = {kept_valid/len(kept_examples)*100:.1f}%")

        # 1的个数分析
        lost_ones = [x['n_ones'] for x in lost_examples]
        kept_ones = [x['n_ones'] for x in kept_examples]
        print(f"\n1的个数平均:")
        print(f"  丢失组: {np.mean(lost_ones):.2f}")
        print(f"  保留组: {np.mean(kept_ones):.2f}")

        # 校验子分析
        lost_syn = [x['syndrome'] for x in lost_examples]
        kept_syn = [x['syndrome'] for x in kept_examples]
        print(f"\n校验子分布:")
        print(f"  丢失组: ", end="")
        for s in range(8):
            print(f"syn={s}:{sum(1 for x in lost_syn if x==s)} ", end="")
        print(f"\n  保留组: ", end="")
        for s in range(8):
            print(f"syn={s}:{sum(1 for x in kept_syn if x==s)} ", end="")
        print()

        # 具体例子
        print(f"\n{'='*60}")
        print("  丢失组例子")
        print(f"{'='*60}")
        for x in lost_examples[:5]:
            print(f"  {x['code']} ones={x['n_ones']} syn={x['syndrome']} 汉明码={'是' if x['is_valid_hamming'] else '否'}")

        print(f"\n{'='*60}")
        print("  保留组例子")
        print(f"{'='*60}")
        for x in kept_examples[:5]:
            print(f"  {x['code']} ones={x['n_ones']} syn={x['syndrome']} 汉明码={'是' if x['is_valid_hamming'] else '否'}")


if __name__ == "__main__":
    exp = AnalyzeLost()
    exp.run()