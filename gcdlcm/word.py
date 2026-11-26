"""应用题模板：把最大公因数、最小公倍数放进生活情境。"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .core import check_value, gcd, lcm

# 每种题型可用的模板，顺序固定
GCD_TEMPLATES: List[str] = ["ribbon", "tile"]
LCM_TEMPLATES: List[str] = ["meet", "bus"]

# 模板名到中文名的映射
TEMPLATE_NAMES: Dict[str, str] = {
    "ribbon": "彩带裁剪",
    "tile": "地砖铺贴",
    "meet": "报数相遇",
    "bus": "班车同时发车",
}

# 类型别名到规范类型名
_KIND_ALIASES: Dict[str, str] = {
    "gcd": "gcd",
    "hcf": "gcd",
    "最大公因数": "gcd",
    "最大公约数": "gcd",
    "lcm": "lcm",
    "最小公倍数": "lcm",
    "ribbon": "gcd",
    "彩带裁剪": "gcd",
    "tile": "gcd",
    "地砖铺贴": "gcd",
    "meet": "lcm",
    "报数相遇": "lcm",
    "bus": "lcm",
    "班车同时发车": "lcm",
}


@dataclass
class WordProblem:
    """一道应用题的结构化信息。"""

    kind: str
    template: str
    title: str
    text: str
    expression: str
    answer: str
    hint: str


def normalize_kind(text: str) -> str:
    """把 gcd/lcm 或模板名归一成 ``gcd`` / ``lcm``，非法值抛出中文错误。"""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("题型不能为空，可选值：gcd、lcm")
    key = text.strip().lower()
    if key in _KIND_ALIASES:
        return _KIND_ALIASES[key]
    raise ValueError(
        "未知题型 %s，可选值：gcd（最大公因数）、lcm（最小公倍数），"
        "或模板名 ribbon、tile、meet、bus" % text
    )


def _templates_for(kind: str) -> List[str]:
    """返回某类型下的模板名列表。"""
    if kind == "gcd":
        return GCD_TEMPLATES
    if kind == "lcm":
        return LCM_TEMPLATES
    raise ValueError("未知题型 %s，可选值：gcd、lcm" % kind)


def _build_gcd(template: str, a: int, b: int, value: int) -> WordProblem:
    """构建最大公因数类应用题。"""
    if template == "ribbon":
        left = a // value
        right = b // value
        return WordProblem(
            kind="gcd",
            template=template,
            title=TEMPLATE_NAMES[template],
            text=(
                "手工课上，老师拿来两条彩带，一条长 %d 厘米，另一条长 %d 厘米。"
                "要把它们都剪成同样长的小段且没有剩余，每段最长是多少厘米？"
                "两条彩带一共能剪成多少段？" % (a, b)
            ),
            expression="最大公因数 (%d, %d) = %d" % (a, b, value),
            answer=(
                "每段最长 %d 厘米；%d 厘米剪成 %d 段，%d 厘米剪成 %d 段，一共 %d 段。"
                % (value, a, left, b, right, left + right)
            ),
            hint="每段长度要同时整除两个长度，问“最长”就是求最大公因数。",
        )
    if template == "tile":
        rows = a // value
        cols = b // value
        return WordProblem(
            kind="gcd",
            template=template,
            title=TEMPLATE_NAMES[template],
            text=(
                "教室地面是一个长 %d 分米、宽 %d 分米的长方形。"
                "用边长是整分米数的正方形地砖正好铺满，地砖的边长最大是多少分米？"
                "一共需要多少块地砖？" % (a, b)
            ),
            expression="最大公因数 (%d, %d) = %d" % (a, b, value),
            answer=(
                "地砖边长最大 %d 分米；横向铺 %d 块，纵向铺 %d 块，一共 %d 块。"
                % (value, rows, cols, rows * cols)
            ),
            hint="地砖边长要同时整除长和宽，求最大边长就是求最大公因数。",
        )
    raise ValueError("未知模板 %s，可选值：ribbon、tile" % template)


def _build_lcm(template: str, a: int, b: int, value: int) -> WordProblem:
    """构建最小公倍数类应用题。"""
    if template == "meet":
        return WordProblem(
            kind="lcm",
            template=template,
            title=TEMPLATE_NAMES[template],
            text=(
                "小明每 %d 天去一次图书馆，小红每 %d 天去一次。"
                "今天两人同时去了图书馆，至少再过多少天两人又会同一天去？" % (a, b)
            ),
            expression="最小公倍数 (%d, %d) = %d" % (a, b, value),
            answer="至少再过 %d 天，两人又会同一天去图书馆。" % value,
            hint="再次同一天的天数要同时是两个天数的倍数，问“至少”就是求最小公倍数。",
        )
    if template == "bus":
        return WordProblem(
            kind="lcm",
            template=template,
            title=TEMPLATE_NAMES[template],
            text=(
                "1 路公交车每 %d 分钟发一班，2 路公交车每 %d 分钟发一班。"
                "两路车在 8:00 同时发车，至少再过多少分钟两路车又同时发车？" % (a, b)
            ),
            expression="最小公倍数 (%d, %d) = %d" % (a, b, value),
            answer="至少再过 %d 分钟，两路车再次同时发车。" % value,
            hint="同时发车的间隔要同时是两个发车间隔的倍数，问“至少”就是求最小公倍数。",
        )
    raise ValueError("未知模板 %s，可选值：meet、bus" % template)


def make_word_problem(
    kind: str, a: int, b: int, template: Optional[str] = None
) -> WordProblem:
    """按题型生成一道应用题；template 为空时使用该类型的第一个模板。"""
    kind_name = normalize_kind(kind)
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    allowed = _templates_for(kind_name)
    if template is None:
        chosen = allowed[0]
    else:
        if not isinstance(template, str) or template.strip().lower() not in allowed:
            raise ValueError(
                "模板 %s 不适用于 %s，可选值：%s"
                % (str(template), kind_name, "、".join(allowed))
            )
        chosen = template.strip().lower()
    if kind_name == "gcd":
        value = gcd(left, right)
        return _build_gcd(chosen, left, right, value)
    value = lcm(left, right)
    return _build_lcm(chosen, left, right, value)


def format_word_problem(problem: WordProblem) -> str:
    """把应用题排成适合命令行输出的多行文本。"""
    lines: List[str] = [
        "【%s】" % problem.title,
        "题目：%s" % problem.text,
        "算式：%s" % problem.expression,
        "答案：%s" % problem.answer,
        "提示：%s" % problem.hint,
    ]
    return "\n".join(lines)


def template_options() -> str:
    """返回可直接打印的模板清单。"""
    parts: List[str] = []
    for name in GCD_TEMPLATES + LCM_TEMPLATES:
        parts.append("%s（%s）" % (name, TEMPLATE_NAMES[name]))
    return "、".join(parts)
