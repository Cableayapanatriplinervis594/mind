#!/usr/bin/env python3
"""
========================================================
标准(7,4)汉明码 - 共振扫描纠正实验
========================================================

实验：
1. 生成随机正确标准汉明码
2. 随机注入一个单位错误（翻转任意一位）
3. 用固定频扫（共振）
4. 观测：是否自动纠正回正确状态

如果共振能纠正 → 和汉明码效果相同
如果共振不能纠正 → 进入新稳态
"""

import numpy as np
from datetime import datetime

class HammingResonanceCorrect:
    def __init__(self):
        # 位置: 0=D0, 1=P0, 2=P1, 3=D1, 4=P2, 5=D2, 6=D3
        self.parity_pos = [1, 2, 4]

        np.random.seed(int(datetime.now().timestamp()) % 100000)

        print("=" * 60)
        print("  标准(7,4)汉明码 - 共振扫描纠正实验")
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

    def inject_error(self, code):
        """注入一个单位错误"""
        err_code = code.copy()
        pos = np.random.randint(0, 7)
        err_code[pos] ^= 1
        return err_code, pos

    def resonance_scan(self, code):
        """
        共振扫描：模拟固定频率激发
        简单模型：翻转所有位一次（模拟共振翻转）
        """
        new_code = code.copy()
        for i in range(7):
            new_code[i] ^= 1
        return new_code

    def hamming_correct(self, code):
        """标准汉明码纠正"""
        new_code = code.copy()
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        syndrome = (s2 << 2) | (s1 << 1) | s0

        syndrome_to_pos = {1:1, 2:2, 3:0, 4:4, 5:3, 6:5, 7:6}
        if syndrome in syndrome_to_pos:
            new_code[syndrome_to_pos[syndrome]] ^= 1
        return new_code, syndrome

    def run_trial(self):
        data = [np.random.randint(0, 2) for _ in range(4)]
        original = self.encode(data)

        with_error, error_pos = self.inject_error(original)

        after_resonance = self.resonance_scan(with_error)

        after_hamming, syndrome = self.hamming_correct(with_error)

        resonance_corrected = (after_resonance == original)
        hamming_corrected = (after_hamming == original)

        return {
            'data': data,
            'original': original,
            'error_pos': error_pos,
            'with_error': with_error,
            'after_resonance': after_resonance,
            'after_hamming': after_hamming,
            'syndrome': syndrome,
            'resonance_corrected': resonance_corrected,
            'hamming_corrected': hamming_corrected,
        }

    def run(self, n=100):
        print(f"运行 {n} 次试验...")
        results = []
        for i in range(n):
            results.append(self.run_trial())
            if (i + 1) % 20 == 0:
                print(f"  进度: {i+1}/{n}")
        return results

    def analyze(self, results):
        total = len(results)
        n_res = sum(1 for r in results if r['resonance_corrected'])
        n_ham = sum(1 for r in results if r['hamming_corrected'])

        print(f"\n{'='*60}")
        print("  实验结果分析")
        print(f"{'='*60}")
        print(f"\n总实验: {total}")
        print(f"共振扫描纠正: {n_res}/{total} = {n_res/total*100:.1f}%")
        print(f"汉明码纠正: {n_ham}/{total} = {n_ham/total*100:.1f}%")

        return {'total': total, 'n_res': n_res, 'n_ham': n_ham}

    def show_examples(self, results, n=6):
        print(f"\n{'='*60}")
        print("  典型例子")
        print(f"{'='*60}")
        for i, r in enumerate(results[:n]):
            print(f"\n例子{i+1}:")
            print(f"  数据:   {r['data']}")
            print(f"  原始码: {r['original']}")
            print(f"  错误位: {r['error_pos']}")
            print(f"  错误码: {r['with_error']}")
            print(f"  校验子: {r['syndrome']}")
            print(f"  共振后: {r['after_resonance']} → {'纠正' if r['resonance_corrected'] else '未纠正'}")
            print(f"  汉明码: {r['after_hamming']} → {'纠正' if r['hamming_corrected'] else '未纠正'}")


def main():
    exp = HammingResonanceCorrect()
    results = exp.run(n=100)
    exp.show_examples(results, n=6)
    a = exp.analyze(results)

    print(f"\n{'='*60}")
    print("  结论")
    print(f"{'='*60}")
    print(f"共振扫描纠正率: {a['n_res']/a['total']*100:.1f}%")
    print(f"汉明码纠正率: {a['n_ham']/a['total']*100:.1f}%")

    if a['n_res'] == a['n_ham']:
        print("\n✓ 共振扫描效果与汉明码相同")
    elif a['n_res'] < a['n_ham']:
        print("\n✗ 共振扫描不能像汉明码那样纠正错误")


if __name__ == "__main__":
    main()