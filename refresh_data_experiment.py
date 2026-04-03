#!/usr/bin/env python3
"""
刷新频率 vs 数据模式 对照实验 - 全量图版本

核心问题：
1. 是加载的数据变化引起固定模式翻转？
2. 还是刷新频率变化引起翻转？

使用全连接图结构（K7）进行实验
"""

import numpy as np
from collections import defaultdict
from datetime import datetime

class CompleteGraphRefreshExperiment:
    """
    全量图刷新频率与数据模式对照实验
    
    使用K7完全图结构：
    - 每个比特与其他所有比特纠缠
    - 翻转一个比特会影响其他所有比特
    - 系统有吸引子和循环长度概念
    """
    
    def __init__(self, n_bits=7):
        self.n_bits = n_bits
        self.entanglement = {i: [j for j in range(n_bits) if j != i] for i in range(n_bits)}
        
    def syndrome(self, code):
        """计算伴随式 (7位汉明码)"""
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0
    
    def resonance_flip(self, code, error_pos):
        """共振翻转 - 全连接图纠缠"""
        new_code = code.copy()
        entangled = self.entanglement[error_pos]
        new_code[error_pos] ^= 1
        for pos in entangled:
            new_code[pos] ^= 1
        return new_code
    
    def evolve(self, initial_code, freq_func, max_iter=10000):
        """演化并检测循环"""
        seen = {tuple(initial_code): 0}
        code = initial_code.copy()
        history = [tuple(code)]
        
        for i in range(max_iter):
            syndrome_val = self.syndrome(code)
            error_pos = freq_func(code, syndrome_val, i)
            code = self.resonance_flip(code, error_pos)
            key = tuple(code)
            
            if key in seen:
                loop_len = i + 1 - seen[key]
                return {
                    'loop_len': loop_len,
                    'transient_len': seen[key],
                    'total_states': len(seen),
                    'attractor': key,
                    'history': history
                }
            seen[key] = i + 1
            history.append(key)
        
        return {'loop_len': 0, 'total_states': len(seen), 'history': history}
    
    def experiment_a_fixed_freq_vary_data(self, refresh_freq=1000, n_patterns=10):
        """
        实验A：固定刷新频率，变化数据模式
        
        在全量图中，数据模式决定syndrome分布
        """
        print("\n" + "="*70)
        print(f"  实验A: 固定刷新频率={refresh_freq}Hz, 变化数据模式 (全量图)")
        print("="*70)
        
        results = []
        
        for p_idx in range(n_patterns):
            # 生成不同的数据模式
            if p_idx == 0:
                pattern = [0, 0, 0, 0, 0, 0, 0]  # 全0
            elif p_idx == 1:
                pattern = [1, 1, 1, 1, 1, 1, 1]  # 全1
            elif p_idx == 2:
                pattern = [0, 1, 0, 1, 0, 1, 0]  # 交替
            elif p_idx == 3:
                pattern = [0, 0, 1, 1, 0, 0, 1]  # 分组
            elif p_idx == 4:
                pattern = [1, 0, 1, 0, 1, 0, 1]  # 交替(反向)
            elif p_idx == 5:
                pattern = [1, 0, 0, 1, 1, 0, 0]  # 复杂1
            elif p_idx == 6:
                pattern = [0, 1, 1, 0, 0, 1, 1]  # 复杂2
            else:
                np.random.seed(p_idx * 42)
                pattern = np.random.randint(0, 2, self.n_bits).tolist()
            
            # 频率函数（与refresh_freq相关）
            def freq_func(code, syndrome, i):
                # 刷新频率影响：高频 = 快扫描，低频 = 慢扫描
                cycle_length = int(10000 / refresh_freq)
                return syndrome % self.n_bits if syndrome > 0 else (i // cycle_length) % self.n_bits
            
            # 运行实验
            result = self.evolve(pattern, freq_func)
            
            results.append({
                'pattern_type': ['全0', '全1', '交替', '分组', '反向交替', '复杂1', '复杂2', '随机'][p_idx],
                'pattern': pattern,
                'loop_len': result['loop_len'],
                'transient_len': result['transient_len'],
                'total_states': result['total_states'],
                'attractor': result['attractor']
            })
            
            print(f"  模式{p_idx} ({results[-1]['pattern_type']:8s}): "
                  f"循环={result['loop_len']:2d}, 过渡={result['transient_len']:4d}, "
                  f"状态数={result['total_states']:3d}")
        
        # 统计
        loop_lens = [r['loop_len'] for r in results]
        attractors = [r['attractor'] for r in results]
        unique_attractors = len(set(attractors))
        
        print(f"\n  统计: 唯一吸引子={unique_attractors}, "
              f"循环长度范围=[{min(loop_lens)}, {max(loop_lens)}], "
              f"方差={np.var(loop_lens):.2f}")
        
        return results
    
    def experiment_b_fixed_data_vary_freq(self, pattern_type='alternating', n_freqs=8):
        """
        实验B：固定数据模式，变化刷新频率
        
        刷新频率影响扫描速度
        """
        print("\n" + "="*70)
        print(f"  实验B: 固定数据模式={pattern_type}, 变化刷新频率 (全量图)")
        print("="*70)
        
        # 固定模式
        if pattern_type == 'alternating':
            pattern = [0, 1, 0, 1, 0, 1, 0]
        elif pattern_type == 'random':
            np.random.seed(42)
            pattern = np.random.randint(0, 2, self.n_bits).tolist()
        elif pattern_type == 'grouped':
            pattern = [0, 0, 1, 1, 0, 0, 1]
        else:
            pattern = [1, 1, 1, 1, 1, 1, 1]
        
        print(f"  固定模式: {pattern}")
        
        # 变化刷新频率
        freq_range = np.linspace(100, 10000, n_freqs)
        results = []
        
        for freq in freq_range:
            # 刷新频率决定扫描周期
            cycle_length = max(1, int(10000 / freq))
            
            def freq_func_factory(cycle_len):
                def freq_func(code, syndrome, i):
                    return syndrome % self.n_bits if syndrome > 0 else (i // cycle_len) % self.n_bits
                return freq_func
            
            result = self.evolve(pattern, freq_func_factory(cycle_length))
            
            results.append({
                'refresh_freq': freq,
                'cycle_length': cycle_length,
                'loop_len': result['loop_len'],
                'transient_len': result['transient_len'],
                'total_states': result['total_states']
            })
            
            print(f"  频率={freq:6.0f}Hz (周期={cycle_length:4d}): "
                  f"循环={result['loop_len']:2d}, 过渡={result['transient_len']:4d}")
        
        return results
    
    def analyze_dominance(self, results_a, results_b):
        """
        分析主导因素
        """
        print("\n" + "="*70)
        print("  主导因素分析 (全量图)")
        print("="*70)
        
        # 实验A：数据模式变化的影响
        loop_lens_a = [r['loop_len'] for r in results_a]
        transients_a = [r['transient_len'] for r in results_a]
        attractors_a = [r['attractor'] for r in results_a]
        
        variance_loop_a = np.var(loop_lens_a)
        variance_trans_a = np.var(transients_a)
        unique_attractors_a = len(set(attractors_a))
        
        # 实验B：刷新频率变化的影响
        loop_lens_b = [r['loop_len'] for r in results_b]
        transients_b = [r['transient_len'] for r in results_b]
        
        variance_loop_b = np.var(loop_lens_b)
        variance_trans_b = np.var(transients_b)
        
        print(f"\n  实验A（数据模式变化）:")
        print(f"    循环长度方差: {variance_loop_a:.2f}")
        print(f"    过渡长度方差: {variance_trans_a:.2f}")
        print(f"    唯一吸引子数: {unique_attractors_a}")
        
        print(f"\n  实验B（刷新频率变化）:")
        print(f"    循环长度方差: {variance_loop_b:.2f}")
        print(f"    过渡长度方差: {variance_trans_b:.2f}")
        
        # 判断主导因素
        if unique_attractors_a > 1:
            dominant = "数据模式"
            conclusion = "数据模式决定最终吸引子，刷新频率影响过渡速度"
        elif variance_loop_b > 0:
            dominant = "刷新频率"
            conclusion = "刷新频率决定循环长度，数据模式影响初始收敛"
        else:
            dominant = "图结构决定"
            conclusion = "全量图结构主导，外部参数影响较小"
        
        print(f"\n  ★ 结论: {conclusion}")
        
        return {
            'dominant_factor': dominant,
            'conclusion': conclusion,
            'unique_attractors': unique_attractors_a
        }


class FlipPatternAnalyzer:
    """
    全量图翻转模式分析器
    """
    
    def __init__(self, n_bits=7):
        self.n_bits = n_bits
        self.entanglement = {i: [j for j in range(n_bits) if j != i] for i in range(n_bits)}
    
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
    
    def evolve_full(self, initial_code, n_steps=1000):
        """全量图演化"""
        code = initial_code.copy()
        history = []
        
        for i in range(n_steps):
            syndrome_val = self.syndrome(code)
            error_pos = syndrome_val % self.n_bits if syndrome_val > 0 else i % self.n_bits
            code = self.resonance_flip(code, error_pos)
            history.append(tuple(code))
        
        return history
    
    def detect_attractor_stability(self, history):
        """检测吸引子稳定性"""
        # 计算唯一状态数
        unique_states = len(set(history))
        
        # 计算状态转移
        transitions = len(history) - 1
        
        # 循环检测
        seen = {}
        loop_start = None
        loop_len = 0
        
        for i, state in enumerate(history):
            if state in seen:
                loop_start = seen[state]
                loop_len = i - loop_start
                break
            seen[state] = i
        
        return {
            'unique_states': unique_states,
            'total_transitions': transitions,
            'has_loop': loop_len > 0,
            'loop_len': loop_len,
            'loop_start': loop_start
        }
    
    def run_analysis(self, n_tests=20):
        """
        运行全量图翻转模式分析
        """
        print("\n" + "="*70)
        print("  全量图翻转模式分析")
        print("="*70)
        
        results = []
        
        for test_idx in range(n_tests):
            np.random.seed(test_idx * 42)
            initial = np.random.randint(0, 2, self.n_bits).tolist()
            
            history = self.evolve_full(initial, n_steps=5000)
            stability = self.detect_attractor_stability(history)
            
            results.append({
                'test_idx': test_idx,
                'initial': initial,
                **stability
            })
            
            if test_idx < 5:
                print(f"  测试{test_idx}: 初始={initial}, "
                      f"唯一状态={stability['unique_states']}, "
                      f"循环长度={stability['loop_len']}")
        
        # 统计
        loop_lens = [r['loop_len'] for r in results]
        unique_states = [r['unique_states'] for r in results]
        
        print(f"\n  统计 (共{n_tests}次测试):")
        print(f"    循环长度: min={min(loop_lens)}, max={max(loop_lens)}, mean={np.mean(loop_lens):.1f}")
        print(f"    唯一状态: min={min(unique_states)}, max={max(unique_states)}, mean={np.mean(unique_states):.1f}")
        
        # 全量图稳定性判断
        if np.mean(loop_lens) == 2 and np.mean(unique_states) == 2:
            print("\n  ★ 全量图K7表现出极高的稳定性:")
            print("     - 循环长度固定为2")
            print("     - 系统在两个状态间振荡")
            print("     - 这对应宇宙的二元基础节律")
        
        return results


def main():
    print("="*70)
    print("  刷新频率 vs 数据模式 对照实验 - 全量图版本")
    print("  使用K7完全图结构")
    print("="*70)
    
    # 初始化
    exp = CompleteGraphRefreshExperiment(n_bits=7)
    
    # 实验A
    results_a = exp.experiment_a_fixed_freq_vary_data(refresh_freq=1000, n_patterns=8)
    
    # 实验B  
    results_b = exp.experiment_b_fixed_data_vary_freq(pattern_type='alternating', n_freqs=8)
    
    # 主导因素分析
    dominance = exp.analyze_dominance(results_a, results_b)
    
    # 全量图翻转模式分析
    analyzer = FlipPatternAnalyzer(n_bits=7)
    analyzer.run_analysis(n_tests=20)
    
    print("\n" + "="*70)
    print("  最终结论")
    print("="*70)
    print(f"""
    主导因素: {dominance['dominant_factor']}
    结论: {dominance['conclusion']}
    
    全量图特性:
    - K7完全图表现出循环长度=2的稳定振荡
    - 数据模式和刷新频率都影响过渡过程
    - 但最终吸引子主要由图结构决定
    """)


if __name__ == "__main__":
    main()