#!/usr/bin/env python3
"""
ASCII全连接图编码跳转实验

设计：
- 使用8比特字节（全连接图K8）
- ASCII字符映射为比特状态
- 输入字符，检查全连接图跳转的下一编码
"""

import numpy as np

class ASCIICompleteGraphCoder:
    """
    ASCII全连接图编码器

    将ASCII字符的8位比特视为全连接图K8的节点
    每个比特翻转会同时影响所有其他比特（纠缠翻转）
    """

    def __init__(self):
        self.n_bits = 8
        self.entanglement = {i: [j for j in range(self.n_bits) if j != i] for i in range(self.n_bits)}

    def char_to_bits(self, char):
        """将字符转换为8位比特"""
        ascii_val = ord(char)
        return [(ascii_val >> i) & 1 for i in range(self.n_bits)]

    def bits_to_int(self, bits):
        """将8位比特转换为整数"""
        return sum(bits[i] << i for i in range(self.n_bits))

    def bits_to_str(self, bits):
        """将比特转为可读字符串"""
        return ''.join(str(b) for b in bits)

    def syndrome(self, code):
        """计算伴随式 (标准8比特简单奇偶校验)"""
        return sum(code) % 2

    def resonance_flip(self, code, error_pos):
        """共振翻转 - 全连接图K8"""
        new_code = code.copy()
        entangled = self.entanglement[error_pos]
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code

    def evolve_single_step(self, bits):
        """单步演化"""
        syndrome_val = self.syndrome(bits)
        error_pos = syndrome_val
        new_bits = self.resonance_flip(bits, error_pos)
        return new_bits, syndrome_val, error_pos

    def test_char_jump(self, char, n_steps=5):
        """
        测试字符的跳转
        """
        print("\n" + "="*70)
        print(f"  输入字符: '{char}' (ASCII {ord(char)})")
        print("="*70)

        bits = self.char_to_bits(char)
        print(f"  初始比特: {self.bits_to_str(bits)} (int={self.bits_to_int(bits)})")

        for step in range(n_steps):
            new_bits, syndrome_val, flip_pos = self.evolve_single_step(bits)
            new_int = self.bits_to_int(new_bits)

            print(f"  Step {step+1}: syndrome={syndrome_val}, flip_pos={flip_pos}")
            print(f"           {self.bits_to_str(bits)} → {self.bits_to_str(new_bits)} (int={new_int})")

            bits = new_bits

        print(f"\n  最终状态: int={self.bits_to_int(bits)}")

        return bits

    def find_attractor(self, char, max_steps=1000):
        """
        找到从字符开始的吸引子
        """
        print("\n" + "="*70)
        print(f"  吸引子搜索: '{char}'")
        print("="*70)

        bits = self.char_to_bits(char)
        seen = {tuple(bits): 0}
        history = [(bits.copy(), None)]

        for step in range(max_steps):
            new_bits, syndrome_val, flip_pos = self.evolve_single_step(bits)
            bits_tuple = tuple(new_bits)

            if bits_tuple in seen:
                cycle_start = seen[bits_tuple]
                cycle_len = step + 1 - cycle_start
                print(f"\n  ★ 检测到吸引子!")
                print(f"     到达步数: {step}")
                print(f"     循环长度: {cycle_len}")
                print(f"     循环起始: Step {cycle_start}")

                cycle_states = history[cycle_start:]
                print(f"\n  循环状态:")
                for i, (s, f) in enumerate(cycle_states[:10]):
                    print(f"     {cycle_start+i}: {self.bits_to_str(s)} (int={self.bits_to_int(s)})")

                return {
                    'found': True,
                    'arrival_steps': step,
                    'cycle_start': cycle_start,
                    'cycle_length': cycle_len,
                    'cycle_states': cycle_states
                }

            seen[bits_tuple] = step + 1
            history.append((new_bits, flip_pos))
            bits = new_bits

        print(f"\n  未在{max_steps}步内找到循环")
        return {'found': False, 'steps': max_steps}

    def scan_full_ascii_attractors(self):
        """
        扫描所有ASCII字符的吸引子
        """
        print("\n" + "="*70)
        print("  全ASCII范围吸引子扫描")
        print("="*70)

        attractors = {}
        char_info = {}

        for ascii_val in range(128):
            char = chr(ascii_val)
            bits = self.char_to_bits(char)

            seen = {tuple(bits): 0}

            for step in range(1000):
                new_bits, _, _ = self.evolve_single_step(bits)
                bits_tuple = tuple(new_bits)

                if bits_tuple in seen:
                    cycle_start = seen[bits_tuple]
                    cycle_len = step + 1 - cycle_start

                    if cycle_len not in attractors:
                        attractors[cycle_len] = []
                        char_info[cycle_len] = []

                    attractors[cycle_len].append(ascii_val)
                    char_info[cycle_len].append({
                        'char': char,
                        'ascii': ascii_val,
                        'bits': self.bits_to_str(bits),
                        'arrival_steps': step,
                        'cycle_start': cycle_start
                    })
                    break

                seen[bits_tuple] = step + 1
                bits = new_bits

        print(f"\n  吸引子分布:")
        for cycle_len in sorted(attractors.keys()):
            chars = attractors[cycle_len]
            print(f"    循环长度={cycle_len}: {len(chars)}个字符")

            if cycle_len <= 10:
                sample = char_info[cycle_len][:5]
                for info in sample:
                    print(f"      '{info['char']}' (ASCII {info['ascii']:3d}) "
                          f"→ {info['arrival_steps']}步后进入循环")

        return attractors

    def analyze_A_to_next(self):
        """
        专门分析'A'的跳转
        """
        print("\n" + "="*70)
        print("  重点分析: 'A' 的跳转路径")
        print("="*70)

        char = 'A'
        bits = self.char_to_bits(char)

        print(f"\n  'A' = ASCII 65 = 二进制 {self.bits_to_str(bits)}")
        print(f"  K8全连接图，每次翻转影响所有8个节点")

        path = [bits.copy()]
        step_info = []

        for step in range(20):
            new_bits, syndrome, flip_pos = self.evolve_single_step(bits)
            path.append(new_bits.copy())
            step_info.append({
                'step': step + 1,
                'syndrome': syndrome,
                'flip_pos': flip_pos,
                'bits': new_bits.copy(),
                'int': self.bits_to_int(new_bits)
            })
            bits = new_bits

        print(f"\n  跳转序列:")
        for info in step_info[:10]:
            print(f"    Step {info['step']:2d}: syndrome={info['syndrome']}, flip={info['flip_pos']} "
                  f"→ int={info['int']:3d} = {self.bits_to_str(info['bits'])}")

        # 寻找循环
        unique_path = []
        seen = set()
        for p in path:
            t = tuple(p)
            if t not in seen:
                seen.add(t)
                unique_path.append(t)

        print(f"\n  唯一状态数: {len(unique_path)}")

        if len(path) > len(unique_path):
            print(f"  ★ 存在循环! 可能在{len(unique_path)}步后进入循环")

        return path, step_info


def main():
    print("="*70)
    print("  ASCII全连接图编码跳转实验")
    print("  8比特K8完全图，syndrome驱动纠缠翻转")
    print("="*70)

    coder = ASCIICompleteGraphCoder()

    # 分析 'A' 的跳转
    path, info = coder.analyze_A_to_next()

    # 找到 'A' 的吸引子
    attractor = coder.find_attractor('A')

    # 全ASCII扫描
    attractors = coder.scan_full_ascii_attractors()

    print("\n" + "="*70)
    print("  理论总结")
    print("="*70)
    print(f"""
    ASCII字符在全连接图K8下的跳转特性：

    1. 每次syndrome翻转会改变多个比特
    2. 这模拟了"宇宙事件"的纠缠效应

    吸引子统计:
    """)

    for cycle_len in sorted(attractors.keys()):
        print(f"      循环长度={cycle_len}: {len(attractors[cycle_len])}个字符")

    print(f"""
    这反映了：
    - 即使是简单的syndrome驱动翻转
    - 在全连接图结构下也会产生复杂的吸引子
    - 宇宙的"信息守恒"可能就体现为这些吸引子
    """)


if __name__ == "__main__":
    main()