"""最大公因数与最小公倍数的核心算法。

本模块只使用 Python 标准库，所有对外函数都做输入校验：
只接受 1..100000 的整数，bool、浮点数、字符串一律拒绝。
"""

import math
from typing import Dict, List, Sequence, Tuple

# 单个数值的合法范围
MIN_VALUE = 1
MAX_VALUE = 100000
# 最小公倍数结果的合法上界（不含）
LCM_LIMIT = 10 ** 15
# 一组数的个数范围
MIN_COUNT = 2
MAX_COUNT = 10


def check_value(value: int, name: str) -> int:
    """校验一个数值是否为 1..100000 的整数，返回其本身。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("%s必须是整数" % name)
    if value < MIN_VALUE or value > MAX_VALUE:
        raise ValueError("%s必须在 %d 到 %d 之间" % (name, MIN_VALUE, MAX_VALUE))
    return value


def _check_group(values: Sequence[int]) -> List[int]:
    """校验一组数值：2..10 个、每项都是合法整数。"""
    if values is None:
        raise ValueError("数值列表不能为空")
    items = list(values)
    if len(items) < MIN_COUNT:
        raise ValueError("至少需要 %d 个数" % MIN_COUNT)
    if len(items) > MAX_COUNT:
        raise ValueError("最多支持 %d 个数" % MAX_COUNT)
    checked: List[int] = []
    for index, item in enumerate(items):
        checked.append(check_value(item, "第 %d 个数" % (index + 1)))
    return checked


def gcd(a: int, b: int) -> int:
    """求两个正整数的最大公因数（辗转相除法）。"""
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    return math.gcd(left, right)


def lcm(a: int, b: int) -> int:
    """求两个正整数的最小公倍数，结果必须小于 1e15。"""
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    result = left // math.gcd(left, right) * right
    if result >= LCM_LIMIT:
        raise ValueError("最小公倍数 %d 超出可处理范围（须小于 1e15）" % result)
    return result


def gcd_many(values: Sequence[int]) -> int:
    """求一组数的最大公因数。"""
    items = _check_group(values)
    result = items[0]
    for item in items[1:]:
        result = math.gcd(result, item)
    return result


def lcm_many(values: Sequence[int]) -> int:
    """求一组数的最小公倍数，结果必须小于 1e15。"""
    items = _check_group(values)
    result = items[0]
    for item in items[1:]:
        result = result // math.gcd(result, item) * item
        if result >= LCM_LIMIT:
            raise ValueError("最小公倍数 %d 超出可处理范围（须小于 1e15）" % result)
    return result


def prime_factors(n: int) -> Dict[int, int]:
    """返回质因数分解结果，键为质数、值为指数，按质数升序排列。"""
    value = check_value(n, "数值")
    factors: Dict[int, int] = {}
    remain = value
    divisor = 2
    while divisor * divisor <= remain:
        while remain % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            remain = remain // divisor
        divisor += 1 if divisor == 2 else 2
    if remain > 1:
        factors[remain] = factors.get(remain, 0) + 1
    return factors


def factor_text(n: int) -> str:
    """生成质因数分解的等式文本，例如 ``12 = 2^2 × 3``。"""
    value = check_value(n, "数值")
    if value == 1:
        return "1 = 1（1 既不是质数，也不是合数）"
    parts: List[str] = []
    for base, exponent in prime_factors(value).items():
        if exponent == 1:
            parts.append(str(base))
        else:
            parts.append("%d^%d" % (base, exponent))
    return "%d = %s" % (value, " × ".join(parts))


def _smallest_prime_factor(n: int) -> int:
    """返回 n 的最小质因数；n 为 1 时返回 1。"""
    if n < 2:
        return 1
    candidate = 2
    while candidate * candidate <= n:
        if n % candidate == 0:
            return candidate
        candidate += 1
    return n


def _common_steps(a: int, b: int) -> List[Tuple[int, int, int]]:
    """内部函数：返回短除过程，每项为 (除去的质因数, 左侧被除数, 右侧被除数)。"""
    left, right = a, b
    steps: List[Tuple[int, int, int]] = []
    while True:
        common = math.gcd(left, right)
        if common == 1:
            return steps
        divisor = _smallest_prime_factor(common)
        steps.append((divisor, left, right))
        left = left // divisor
        right = right // divisor


def short_division_steps(a: int, b: int) -> List[str]:
    """输出两数短除（竖式）求最大公因数的文字步骤。"""
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    lines: List[str] = []
    rows = _common_steps(left, right)
    divisors: List[int] = []
    cur_left, cur_right = left, right
    for divisor, row_left, row_right in rows:
        divisors.append(divisor)
        lines.append(
            "用公因数 %d 同时除 %d 和 %d，得到 %d 和 %d"
            % (divisor, row_left, row_right, row_left // divisor, row_right // divisor)
        )
        cur_left = row_left // divisor
        cur_right = row_right // divisor
    if not divisors:
        lines.append("%d 和 %d 没有大于 1 的公因数，短除立即结束" % (left, right))
    elif math.gcd(cur_left, cur_right) == 1:
        lines.append("%d 和 %d 已经互质，短除结束" % (cur_left, cur_right))
    greatest = 1
    for divisor in divisors:
        greatest *= divisor
    lines.append("最大公因数 = %s = %d" % (" × ".join(str(d) for d in divisors) if divisors else "1", greatest))
    least = greatest * cur_left * cur_right
    if divisors:
        lines.append(
            "最小公倍数 = %s × %d × %d = %d"
            % (" × ".join(str(d) for d in divisors), cur_left, cur_right, least)
        )
    else:
        lines.append("最小公倍数 = %d × %d = %d" % (left, right, least))
    return lines


def short_division_rows(a: int, b: int) -> List[List[int]]:
    """短除竖式的结构化数据：每行为 [除数, 被除数左, 被除数右]。"""
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    rows: List[List[int]] = []
    for divisor, row_left, row_right in _common_steps(left, right):
        rows.append([divisor, row_left, row_right])
    return rows


def is_coprime(a: int, b: int) -> bool:
    """判断两个数是否互质（最大公因数为 1）。"""
    return gcd(a, b) == 1
