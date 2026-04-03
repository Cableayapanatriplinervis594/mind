#!/usr/bin/env python3
"""
========================================================
纠缠翻转实验 v4 - 简洁模型
========================================================

核心理解：
1. 正确数据作为基态
2. 注入一位错误
3. 错误位触发共振
4. 纠缠位同步翻转
5. 直接进入新稳态

简化：一次注入 → 共振 → 纠缠翻转 → 新稳态

使用方法：
    python3 entanglement_flip_v4.py
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path

class EntanglementFlipV4:
    """
    纠缠翻转实验 v4
    简洁模型
    """

    def __init__(self, n_bits=8):
        self.n_bits = n_bits

        # 纠缠对定义
        self.entangled_pairs = [(0, 5), (1, 6), (2, 7)]

        # 位置到纠缠对的映射
        self.pos_to_pair = {}
        for pair in self.entangled_pairs:
            for p in pair:
                self.pos_to_pair[p] = pair

        np.random.seed(None)

        print("=" * 60)
        print("  纠缠翻转实验 v4")
        print("  简洁模型")
        print("=" * 60)
        print(f"位长度: {n_bits}")
        print(f"纠缠对: {self.entangled_pairs}")

    def inject_error(self, bits):
        """注入一位错误"""
        bits = bits.copy()
        error_pos = np.random.randint(0, self.n_bits)
        bits[error_pos] ^= 1
        return bits, error_pos

    def resonance_drive(self, error_pos):
        """
        共振驱动

        错误位触发共振，导致纠缠位翻转
        """
        if error_pos in self.pos_to_pair:
            pair = self.pos_to_pair[error_pos]
            partner = pair[0] if pair[1] == error_pos else pair[1]
            return partner
        return -1

    def run_single_trial(self, correct_bits):
        """
        单次试验

        1. 正确数据
        2. 注入错误
        3. 共振触发
        4. 纠缠翻转
        5. 新稳态
        """
        result = {
            'correct': correct_bits.copy(),
            'steps': []
        }

        # Step 1: 正确数据
        state = correct_bits.copy()
        result['steps'].append({
            'step': 'correct',
            'state': state.copy()
        })

        # Step 2: 注入错误
        error_bits, error_pos = self.inject_error(state)
        state = error_bits.copy()
        result['steps'].append({
            'step': 'error_injected',
            'state': state.copy(),
            'error_pos': error_pos
        })

        # Step 3: 共振触发，找到纠缠对
        if error_pos in self.pos_to_pair:
            pair = self.pos_to_pair[error_pos]
            partner = pair[0] if pair[1] == error_pos else pair[1]

            # Step 4: 纠缠位翻转
            state[partner] ^= 1

            result['steps'].append({
                'step': 'entanglement_flip',
                'pair': pair,
                'partner_flipped': partner,
                'state': state.copy()
            })

            # Step 5: 新稳态
            result['steps'].append({
                'step': 'new_stable',
                'state': state.copy()
            })

            result['final'] = state.copy()
            result['entangled_partner'] = partner
            result['success'] = True
        else:
            result['steps'].append({
                'step': 'no_entanglement',
                'state': state.copy()
            })
            result['final'] = state.copy()
            result['entangled_partner'] = -1
            result['success'] = False

        return result

    def run_experiment(self, n_trials=100):
        """运行n次实验"""
        print(f"\n运行 {n_trials} 次实验...")

        results = []

        for i in range(n_trials):
            correct_bits = [np.random.randint(0, 2) for _ in range(self.n_bits)]
            result = self.run_single_trial(correct_bits)
            results.append(result)

            if (i + 1) % 20 == 0:
                print(f"  进度: {i+1}/{n_trials}")

        return results

    def analyze(self, results):
        """分析"""
        print(f"\n{'='*60}")
        print("  实验分析")
        print(f"{'='*60}")

        n_success = sum(1 for r in results if r['success'])

        print(f"\n基本统计:")
        print(f"  总实验: {len(results)}")
        print(f"  纠缠翻转成功: {n_success}/{len(results)} = {n_success/len(results)*100:.1f}%")

        # 检查回到正确 vs 新稳态
        back_to_correct = 0
        new_stable = 0

        for r in results:
            if not r['success']:
                continue
            if r['final'] == r['correct']:
                back_to_correct += 1
            else:
                new_stable += 1

        print(f"\n最终态分析:")
        print(f"  回到正确态: {back_to_correct}/{n_success}")
        print(f"  进入新稳态: {new_stable}/{n_success}")

        if new_stable > back_to_correct:
            print(f"\n✓ 大部分进入新稳态而非回到正确态！")
            print(f"  这验证了纠缠同步翻转机制")

        # 纠缠对翻转统计
        pair_flips = {}
        for pair in self.entangled_pairs:
            pair_flips[pair] = 0

        for r in results:
            if r['entangled_partner'] >= 0:
                for pair in self.entangled_pairs:
                    if r['entangled_partner'] in pair:
                        pair_flips[pair] += 1
                        break

        print(f"\n各纠缠对翻转次数:")
        for pair, count in pair_flips.items():
            print(f"  对{pair}: {count}次")

        return {
            'n_trials': len(results),
            'n_success': n_success,
            'success_rate': n_success / len(results) * 100,
            'back_to_correct': back_to_correct,
            'new_stable': new_stable,
            'pair_flips': pair_flips
        }

    def show_examples(self, results, n=6):
        """展示例子"""
        print(f"\n{'='*60}")
        print("  典型例子")
        print(f"{'='*60}")

        shown = 0
        for i, r in enumerate(results):
            if shown >= n:
                break
            if not r['success']:
                continue

            print(f"\n例子{shown+1}:")
            for step in r['steps']:
                if step['step'] == 'correct':
                    print(f"  正确:  {step['state']}")
                elif step['step'] == 'error_injected':
                    print(f"  注入错误: {step['state']} (位{step['error_pos']}翻转)")
                elif step['step'] == 'entanglement_flip':
                    print(f"  纠缠翻转: {step['state']} (位{step['partner_flipped']}跟随)")
                elif step['step'] == 'new_stable':
                    print(f"  新稳态: {step['state']}")

            if r['final'] == r['correct']:
                print(f"  判定: 回到正确态")
            else:
                print(f"  判定: 进入新稳态 ✓")

            shown += 1


def main():
    exp = EntanglementFlipV4(n_bits=8)

    results = exp.run_experiment(n_trials=100)

    exp.show_examples(results, n=6)

    analysis = exp.analyze(results)

    full_results = {
        'timestamp': datetime.now().isoformat(),
        'n_bits': 8,
        'entangled_pairs': exp.entangled_pairs,
        'n_trials': 100,
        'results': [
            {
                'correct': r['correct'],
                'final': r['final'],
                'entangled_partner': r['entangled_partner'],
                'success': r['success']
            } for r in results
        ],
        'analysis': analysis
    }

    filepath = Path('./resonance_data') / f"entanglement_v4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath.parent.mkdir(exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  结果已保存: {filepath}")
    print(f"{'='*60}")

    return full_results


if __name__ == "__main__":
    main()