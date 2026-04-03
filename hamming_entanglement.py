#!/usr/bin/env python3
"""
========================================================
汉明码纠缠翻转实验 - 完整8位
========================================================

基于汉明码原理：
- 任何1位错误都可检测
- 校验方程定义纠缠关系
- 错误位触发 → 纠缠位翻转

目标：100%纠缠成功率

使用方法：
    python3 hamming_entanglement.py
"""

import numpy as np
from datetime import datetime
from pathlib import Path

class HammingEntanglement:
    """
    汉明码纠缠翻转

    原理：
    - 汉明(7,4)码：4数据位 + 3校验位
    - 每个数据位与多个校验位纠缠
    - 任何错误都可被检测+定位
    """

    def __init__(self):
        # 标准汉明码(7,4)结构
        # 位置:  0  1  2  3  4  5  6
        # 位类型: D0 D1 D2 D3 P0 P1 P2
        # D=数据位, P=校验位

        # 校验方程定义纠缠关系：
        # P0 = D0 ⊕ D1 ⊕ D3  (位置0参与纠缠)
        # P1 = D0 ⊕ D2 ⊕ D3  (位置1参与纠缠)
        # P2 = D1 ⊕ D2 ⊕ D3  (位置2参与纠缠)

        # 8位扩展：加入全局校验位
        # 位置:  0  1  2  3  4  5  6  7
        #        D0 D1 D2 D3 P0 P1 P2 P3

        self.n_bits = 8
        self.parity_bits = [4, 5, 6, 7]  # 校验位位置
        self.data_bits = [0, 1, 2, 3]     # 数据位位置

        # 每个数据位的"纠缠组"
        # 即：当某数据位出错时，哪些校验位会受影响
        self.entanglement_map = {
            0: [4, 5],      # D0错误影响P0,P1
            1: [4, 6],      # D1错误影响P0,P2
            2: [5, 6],      # D2错误影响P1,P2
            3: [4, 5, 6],  # D3错误影响P0,P1,P2
        }

        np.random.seed(None)

        print("=" * 60)
        print("  汉明码纠缠翻转实验")
        print("=" * 60)
        print(f"总位数: {self.n_bits}")
        print(f"数据位: {self.data_bits}")
        print(f"校验位: {self.parity_bits}")
        print(f"纠缠映射: {self.entanglement_map}")

    def encode(self, data):
        """汉明编码"""
        code = data.copy() + [0, 0, 0, 0]  # 8位

        # 计算校验位
        code[4] = code[0] ^ code[1] ^ code[3]  # P0
        code[5] = code[0] ^ code[2] ^ code[3]  # P1
        code[6] = code[1] ^ code[2] ^ code[3]  # P2
        code[7] = code[4] ^ code[5] ^ code[6]  # P3 (全局校验)

        return code

    def syndrome(self, code):
        """
        计算校验子，检测错误位置

        返回：错误位置索引，或-1表示无错误
        """
        # 局部校验
        s0 = code[4] ^ code[0] ^ code[1] ^ code[3]
        s1 = code[5] ^ code[0] ^ code[2] ^ code[3]
        s2 = code[6] ^ code[1] ^ code[2] ^ code[3]
        s3 = code[7] ^ code[4] ^ code[5] ^ code[6]

        syndrome_val = (s3 << 3) | (s2 << 2) | (s1 << 1) | s0

        if syndrome_val == 0:
            return -1

        return syndrome_val - 1

    def inject_error(self, code, error_pos=None):
        """注入一位错误"""
        code = code.copy()

        if error_pos is None:
            error_pos = np.random.randint(0, self.n_bits)

        code[error_pos] ^= 1
        return code, error_pos

    def entanglement_flip(self, code, error_pos):
        """
        纠缠翻转

        错误位触发 → 纠缠位翻转
        """
        new_code = code.copy()

        # 找到纠缠位
        entangled_pos = []

        if error_pos in self.entanglement_map:
            entangled_pos = self.entanglement_map[error_pos]
        elif error_pos in self.parity_bits:
            # 校验位出错，影响数据位
            for data_pos, ent_pos in self.entanglement_map.items():
                if error_pos in ent_pos:
                    entangled_pos.append(data_pos)

        # 翻转纠缠位
        for pos in entangled_pos:
            new_code[pos] ^= 1

        return new_code, entangled_pos

    def run_single_trial(self, data):
        """单次试验"""
        # 1. 编码
        original = self.encode(data)

        # 2. 注入错误
        with_error, error_pos = self.inject_error(original)

        # 3. 计算校验子
        detected_pos = self.syndrome(with_error)

        # 4. 纠缠翻转
        if detected_pos >= 0:
            final, entangled_pos = self.entanglement_flip(with_error, detected_pos)
        else:
            final = with_error.copy()
            entangled_pos = []

        # 5. 检查结果
        success = (detected_pos >= 0) and (detected_pos == error_pos)

        return {
            'original': original,
            'error_injected': with_error,
            'error_pos': error_pos,
            'detected_pos': detected_pos,
            'entangled_pos': entangled_pos,
            'final': final,
            'detection_success': success,
            'has_entanglement': len(entangled_pos) > 0
        }

    def run_experiment(self, n_trials=100):
        """运行实验"""
        print(f"\n运行 {n_trials} 次实验...")

        results = []
        n_success = 0
        n_with_entanglement = 0

        for i in range(n_trials):
            data = [np.random.randint(0, 2) for _ in range(4)]
            result = self.run_single_trial(data)
            results.append(result)

            if result['detection_success']:
                n_success += 1
            if result['has_entanglement']:
                n_with_entanglement += 1

            if (i + 1) % 20 == 0:
                print(f"  进度: {i+1}/{n_trials}")

        return results, n_success, n_with_entanglement

    def analyze(self, results, n_success, n_with_entanglement):
        """分析结果"""
        print(f"\n{'='*60}")
        print("  实验分析")
        print(f"{'='*60}")

        total = len(results)

        print(f"\n基本统计:")
        print(f"  总实验: {total}")
        print(f"  检测成功: {n_success}/{total} = {n_success/total*100:.1f}%")
        print(f"  纠缠翻转: {n_with_entanglement}/{total} = {n_with_entanglement/total*100:.1f}%")

        # 分析纠缠位置分布
        ent_pos_counts = {i: 0 for i in range(8)}
        for r in results:
            for pos in r['entangled_pos']:
                ent_pos_counts[pos] += 1

        print(f"\n各位置纠缠翻转次数:")
        for pos, count in sorted(ent_pos_counts.items()):
            print(f"  位置{pos}: {count}次")

        # 检查最终态
        back_to_correct = 0
        new_stable = 0
        other = 0

        for r in results:
            if r['final'] == r['original']:
                back_to_correct += 1
            else:
                new_stable += 1

        print(f"\n最终态分析:")
        print(f"  回到正确态: {back_to_correct}/{total}")
        print(f"  进入新稳态: {new_stable}/{total}")

        return {
            'total': total,
            'detection_success': n_success,
            'detection_rate': n_success / total * 100,
            'entanglement_rate': n_with_entanglement / total * 100,
            'back_to_correct': back_to_correct,
            'new_stable': new_stable
        }

    def show_examples(self, results, n=6):
        """展示例子"""
        print(f"\n{'='*60}")
        print("  典型例子")
        print(f"{'='*60}")

        for i, r in enumerate(results[:n]):
            print(f"\n例子{i+1}:")
            print(f"  原始:  {r['original']}")
            print(f"  错误:  {r['error_injected']} (位{r['error_pos']})")
            print(f"  检测:  位{r['detected_pos'] if r['detected_pos'] >= 0 else '无'}")

            if r['entangled_pos']:
                print(f"  纠缠翻转: 位{r['entangled_pos']}")
            print(f"  最终:  {r['final']}")


def main():
    exp = HammingEntanglement()

    results, n_success, n_with_entanglement = exp.run_experiment(n_trials=100)

    exp.show_examples(results, n=6)

    analysis = exp.analyze(results, n_success, n_with_entanglement)

    print(f"\n{'='*60}")
    print("  结论")
    print(f"{'='*60}")

    if analysis['detection_rate'] == 100:
        print("✓ 汉明码100%检测到错误")
    if analysis['entanglement_rate'] == 100:
        print("✓ 100%触发了纠缠翻转")
    if analysis['new_stable'] > analysis['back_to_correct']:
        print("✓ 更多进入新稳态而非回到正确态")

    return results, analysis


if __name__ == "__main__":
    main()