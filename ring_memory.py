#!/usr/bin/env python3
"""
========================================================
环形纠缠结构
========================================================

环形纠缠：每个位置只与相邻两个位置纠缠
0 ↔ 1 ↔ 2 ↔ 3 ↔ 4 ↔ 5 ↔ 6 ↔ 0
"""

import numpy as np

class RingMemory:
    def __init__(self):
        # 环形纠缠：相邻位置纠缠
        self.entanglement = {
            0: [1, 6],
            1: [0, 2],
            2: [1, 3],
            3: [2, 4],
            4: [3, 5],
            5: [4, 6],
            6: [5, 0],
        }

        print("=" * 60)
        print("  环形纠缠结构")
        print("=" * 60)
        print(f"纠缠: {self.entanglement}")

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

    def evolve(self, code, max_iter=1000):
        seen = {tuple(code): 0}
        history = [code]
        for i in range(max_iter):
            syndrome = self.syndrome(code)
            error_pos = syndrome % 7 if syndrome > 0 else i % 7
            next_code = self.resonance_flip(code, error_pos)
            key = tuple(next_code)
            if key in seen:
                return {
                    'loop': True,
                    'loop_len': i + 1 - seen[key],
                    'total_states': len(seen),
                    'history': history,
                }
            code = next_code
            seen[key] = i + 1
            history.append(code)
        return {'loop': False, 'total_states': len(seen), 'history': history}

    def run(self):
        print("\n测试所有256种状态...")

        loop_lens = []
        total_states_list = []

        for n in range(256):
            code = [(n >> i) & 1 for i in range(7)]
            result = self.evolve(code)
            loop_lens.append(result['loop_len'])
            total_states_list.append(result['total_states'])

        print(f"\n{'='*60}")
        print("  分析结果")
        print(f"{'='*60}")

        print(f"\n循环长度分布:")
        loop_len_counts = {}
        for ll in loop_lens:
            loop_len_counts[ll] = loop_len_counts.get(ll, 0) + 1
        for ll in sorted(loop_len_counts.keys()):
            print(f"  长度{ll}: {loop_len_counts[ll]}次")

        print(f"\n状态数分布:")
        state_counts = {}
        for ts in total_states_list:
            state_counts[ts] = state_counts.get(ts, 0) + 1
        for ts in sorted(state_counts.keys()):
            print(f"  {ts}个状态: {state_counts[ts]}次")

        # 分析丢失vs保留
        lost = sum(1 for ts in total_states_list if ts == 3)
        kept = sum(1 for ts in total_states_list if ts == 2)
        print(f"\n丢失初始(ts=3): {lost}/256 = {lost/256*100:.1f}%")
        print(f"保留初始(ts=2): {kept}/256 = {kept/256*100:.1f}%")

        # 例子
        print(f"\n{'='*60}")
        print("  循环例子")
        print(f"{'='*60}")

        shown_lens = set()
        for n in range(256):
            code = [(n >> i) & 1 for i in range(7)]
            result = self.evolve(code)
            if result['loop'] and result['loop_len'] not in shown_lens:
                shown_lens.add(result['loop_len'])
                h = result['history']
                print(f"\n循环长度{result['loop_len']}: {h[:5]}... (共{result['total_states']}状态)")

            if len(shown_lens) >= 6:
                break


if __name__ == "__main__":
    exp = RingMemory()
    exp.run()