#!/usr/bin/env python3
"""
验证标准(7,4)汉明码校验子计算
"""

class VerifyHamming:
    def __init__(self):
        # 标准(7,4)汉明码
        # 位置: 0=D0, 1=P0, 2=P1, 3=D1, 4=P2, 5=D2, 6=D3
        # 校验位: 1, 2, 4
        pass

    def encode(self, data):
        D0, D1, D2, D3 = data[0], data[1], data[2], data[3]
        code = [0] * 7
        code[0] = D0
        code[3] = D1
        code[5] = D2
        code[6] = D3
        code[1] = D0 ^ D1 ^ D3  # P0
        code[2] = D0 ^ D2 ^ D3  # P1
        code[4] = D1 ^ D2 ^ D3  # P2
        return code

    def syndrome(self, code):
        s0 = code[1] ^ code[0] ^ code[3] ^ code[6]
        s1 = code[2] ^ code[0] ^ code[5] ^ code[6]
        s2 = code[4] ^ code[3] ^ code[5] ^ code[6]
        return (s2 << 2) | (s1 << 1) | s0

    def verify(self):
        print("验证标准(7,4)汉明码校验子计算")
        print("=" * 60)

        # 测试各种数据
        test_cases = [
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 0, 1, 0],
        ]

        for data in test_cases:
            code = self.encode(data)
            syndrome = self.syndrome(code)
            print(f"数据: {data} → 码: {code} → 校验子: {syndrome}")

        print("\n" + "=" * 60)
        print("测试单比特错误检测")
        print("=" * 60)

        # 生成正确码
        data = [1, 0, 1, 1]
        original = self.encode(data)
        print(f"\n原始数据: {data}")
        print(f"原始码:   {original} (校验子: {self.syndrome(original)})")

        # 翻转每个位置
        print("\n单比特翻转各位置:")
        for pos in range(7):
            test = original.copy()
            test[pos] ^= 1
            syn = self.syndrome(test)
            print(f"  翻转位置{pos}: {test} → 校验子={syn} (应为{pos})")


if __name__ == "__main__":
    v = VerifyHamming()
    v.verify()