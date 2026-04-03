#!/usr/bin/env python3
"""
========================================================
真实汉明码错误检测实验
========================================================

使用标准汉明码：
1. 编码：数据位 + 奇偶校验位
2. 引入随机错误
3. 通过校验推断错误位置
4. 纠正错误

使用方法：
    python3 hamming_experiment.py
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path

class HammingCodeExperiment:
    """
    汉明码错误检测实验
    """

    def __init__(self, n_data_bits=4):
        """
        初始化

        n_data_bits: 数据位个数 (4 → 7位汉明码)
        """
        self.n_data_bits = n_data_bits
        self.n_parity_bits = self._calc_parity_bits(n_data_bits)
        self.n_total_bits = n_data_bits + self.n_parity_bits

        print("=" * 60)
        print("  真实汉明码错误检测实验")
        print("=" * 60)
        print(f"数据位: {n_data_bits}")
        print(f"校验位: {self.n_parity_bits}")
        print(f"总位: {self.n_total_bits}")

    def _calc_parity_bits(self, k):
        """计算校验位个数: 2^p >= k + p + 1"""
        p = 0
        while 2 ** p < k + p + 1:
            p += 1
        return p

    def encode(self, data_bits):
        """
        汉明编码

        data_bits: 数据位列表 [d0, d1, d2, d3]
        return: 编码后位列表 [p0, p1, d0, p2, d1, d2, d3] (7位)
        """
        n = self.n_total_bits
        code = [0] * n

        data_idx = 0
        for i in range(n):
            if (i + 1) & i != 0:
                code[i] = data_bits[data_idx]
                data_idx += 1

        for p in range(self.n_parity_bits):
            p_pos = (2 ** p) - 1
            xor_sum = 0
            for i in range(n):
                if (i + 1) & (2 ** p):
                    xor_sum ^= code[i]
            code[p_pos] = xor_sum

        return code

    def add_error(self, code, error_pos=None):
        """
        引入错误

        如果error_pos=None，随机选择一个位置
        """
        code_with_error = code.copy()

        if error_pos is None:
            error_pos = np.random.randint(0, len(code_with_error))

        code_with_error[error_pos] ^= 1

        return code_with_error, error_pos

    def detect(self, received):
        """
        检测错误位置

        return: 错误位置 (0起), -1表示无错误
        """
        n = len(received)
        syndrome = 0

        for p in range(self.n_parity_bits):
            p_pos = (2 ** p) - 1
            xor_sum = received[p_pos]

            for i in range(n):
                if (i + 1) & (2 ** p) and i != p_pos:
                    xor_sum ^= received[i]

            if xor_sum:
                syndrome |= (2 ** p)

        return syndrome - 1 if syndrome > 0 else -1

    def correct(self, received, error_pos):
        """纠正错误"""
        if error_pos >= 0 and error_pos < len(received):
            received[error_pos] ^= 1
        return received

    def decode(self, code):
        """解码：提取数据位"""
        n = len(code)
        data_bits = []

        for i in range(n):
            if (i + 1) & i != 0:
                data_bits.append(code[i])

        return data_bits

    def run_single_experiment(self, data_bits, error_pos=None):
        """
        运行单个实验

        1. 编码
        2. 引入错误
        3. 检测错误
        4. 纠正
        5. 解码
        """
        original = data_bits.copy()

        encoded = self.encode(data_bits)

        received, true_error_pos = self.add_error(encoded, error_pos)

        detected_pos = self.detect(received)

        corrected = self.correct(received.copy(), detected_pos)

        decoded = self.decode(corrected)

        success = (decoded == original)

        return {
            'original': original,
            'encoded': encoded,
            'received': received,
            'true_error_pos': true_error_pos,
            'detected_pos': detected_pos,
            'corrected': corrected,
            'decoded': decoded,
            'success': success,
            'detection_correct': detected_pos == true_error_pos
        }

    def run_random_errors(self, n_trials=100, error_rate=0.3):
        """
        运行随机错误实验
        """
        print(f"\n运行 {n_trials} 次随机错误实验...")

        results = []
        success_count = 0
        detection_correct_count = 0

        for i in range(n_trials):
            data_bits = [np.random.randint(0, 2) for _ in range(self.n_data_bits)]

            if np.random.random() < error_rate:
                error_pos = np.random.randint(0, self.n_total_bits)
            else:
                error_pos = None

            result = self.run_single_experiment(data_bits, error_pos)
            results.append(result)

            if result['success']:
                success_count += 1
            if result['detection_correct']:
                detection_correct_count += 1

            if (i + 1) % 20 == 0:
                print(f"  进度: {i+1}/{n_trials}")

        return results, success_count, detection_correct_count

    def run_all_single_bit_errors(self):
        """
        对每一位单独引入错误（笛卡尔积覆盖）
        """
        print(f"\n对全部 {self.n_total_bits} 位单独引入错误...")

        results = []

        data_bits = [1] * self.n_data_bits

        encoded = self.encode(data_bits)

        for error_pos in range(self.n_total_bits):
            received, _ = self.add_error(encoded, error_pos)
            detected_pos = self.detect(received)

            result = {
                'error_pos': error_pos,
                'received': received,
                'detected_pos': detected_pos,
                'correct': detected_pos == error_pos
            }
            results.append(result)

            status = "✓" if result['correct'] else "✗"
            print(f"  错误位{error_pos}: 检测位{detected_pos} {status}")

        return results

    def analyze(self, results, success_count, detection_count, n_trials):
        """分析结果"""
        print(f"\n{'='*60}")
        print("  实验结果分析")
        print(f"{'='*60}")

        print(f"\n总实验次数: {n_trials}")
        print(f"纠错成功: {success_count}/{n_trials} = {success_count/n_trials*100:.1f}%")
        print(f"检测正确: {detection_count}/{n_trials} = {detection_count/n_trials*100:.1f}%")

        detection_accuracy = sum(1 for r in results if r['detection_correct']) / len(results) * 100

        return {
            'n_trials': n_trials,
            'success_count': success_count,
            'success_rate': success_count / n_trials,
            'detection_count': detection_count,
            'detection_rate': detection_count / n_trials,
            'detection_accuracy': detection_accuracy
        }


def main():
    exp = HammingCodeExperiment(n_data_bits=4)

    print("\n" + "=" * 60)
    print("  实验1: 全位单错误覆盖")
    print("=" * 60)
    single_results = exp.run_all_single_bit_errors()

    all_correct = all(r['correct'] for r in single_results)
    print(f"\n单错误检测: {'全部正确 ✓' if all_correct else '有错误 ✗'}")

    print("\n" + "=" * 60)
    print("  实验2: 随机错误")
    print("=" * 60)
    results, success, detection = exp.run_random_errors(n_trials=100, error_rate=0.3)

    analysis = exp.analyze(results, success, detection, 100)

    full_results = {
        'timestamp': datetime.now().isoformat(),
        'n_data_bits': 4,
        'n_total_bits': 7,
        'single_bit_results': single_results,
        'random_error_results': [
            {
                'success': r['success'],
                'detection_correct': r['detection_correct'],
                'true_error_pos': r['true_error_pos'],
                'detected_pos': r['detected_pos']
            } for r in results
        ],
        'analysis': analysis
    }

    filepath = Path('./resonance_data') / f"hamming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath.parent.mkdir(exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)

    print(f"\n结果已保存: {filepath}")

    return full_results


if __name__ == "__main__":
    main()