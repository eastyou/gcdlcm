"""gcdlcm：最大公因数与最小公倍数的教学工具。

提供核心算法、应用题模板、练习纸生成与命令行入口。
"""

from .core import (
    LCM_LIMIT,
    MAX_VALUE,
    MIN_VALUE,
    check_value,
    factor_text,
    gcd,
    gcd_many,
    is_coprime,
    lcm,
    lcm_many,
    prime_factors,
    short_division_rows,
    short_division_steps,
)
from .sheet import Question, make_questions, render_demo, render_sheet
from .word import WordProblem, make_word_problem

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "MIN_VALUE",
    "MAX_VALUE",
    "LCM_LIMIT",
    "check_value",
    "gcd",
    "lcm",
    "gcd_many",
    "lcm_many",
    "prime_factors",
    "factor_text",
    "short_division_steps",
    "short_division_rows",
    "is_coprime",
    "Question",
    "make_questions",
    "render_sheet",
    "render_demo",
    "WordProblem",
    "make_word_problem",
]
