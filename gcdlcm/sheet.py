"""A4 练习纸与演示页的 HTML 生成（纯字符串拼接，不使用 xml.etree）。"""

import html
import random
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

from .core import check_value, gcd, lcm, short_division_rows
from .word import make_word_problem

MIN_QUESTIONS = 1
MAX_QUESTIONS = 50
MAX_SEED = 2 ** 31 - 1

# 题目类型的中文标签
KIND_LABELS = {
    "gcd": "最大公因数",
    "lcm": "最小公倍数",
    "coprime": "互质判断",
    "word": "应用题",
}


@dataclass
class Question:
    """练习纸上的一道题。"""

    kind: str
    a: int
    b: int
    prompt: str
    answer: str
    steps: List[str] = field(default_factory=list)


def check_count(count: int) -> int:
    """校验题目数量为 1..50 的整数。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ValueError("题目数量必须是整数")
    if count < MIN_QUESTIONS or count > MAX_QUESTIONS:
        raise ValueError("题目数量必须在 %d 到 %d 之间" % (MIN_QUESTIONS, MAX_QUESTIONS))
    return count


def check_seed(seed: int) -> int:
    """校验随机种子为 0..2^31-1 的整数。"""
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("随机种子必须是整数")
    if seed < 0 or seed > MAX_SEED:
        raise ValueError("随机种子必须在 0 到 %d 之间" % MAX_SEED)
    return seed


def _pick_pair(rng: random.Random) -> Tuple[int, int]:
    """在 2..40 中抽取两个不同的整数。"""
    a = rng.randint(2, 40)
    candidates = [value for value in range(2, 41) if value != a]
    b = rng.choice(candidates)
    return a, b


def make_questions(count: int, seed: int) -> List[Question]:
    """按 seed 生成练习纸题目，四种类型循环出现，同 seed 结果一致。"""
    total = check_count(count)
    rng = random.Random(check_seed(seed))
    kinds = ["gcd", "lcm", "coprime", "word"]
    questions: List[Question] = []
    for index in range(total):
        kind = kinds[index % len(kinds)]
        a, b = _pick_pair(rng)
        if kind == "gcd":
            value = gcd(a, b)
            questions.append(
                Question(
                    kind="gcd",
                    a=a,
                    b=b,
                    prompt="求 %d 和 %d 的最大公因数。" % (a, b),
                    answer="最大公因数是 %d。" % value,
                    steps=["%d 和 %d 的公有质因数的积就是最大公因数。" % (a, b)],
                )
            )
        elif kind == "lcm":
            value = lcm(a, b)
            questions.append(
                Question(
                    kind="lcm",
                    a=a,
                    b=b,
                    prompt="求 %d 和 %d 的最小公倍数。" % (a, b),
                    answer="最小公倍数是 %d。" % value,
                    steps=["可以用短除法，也可以用公式：两数之积 ÷ 最大公因数。"],
                )
            )
        elif kind == "coprime":
            value = gcd(a, b)
            if value == 1:
                answer = "互质，因为最大公因数是 1。"
            else:
                answer = "不互质，因为最大公因数是 %d。" % value
            questions.append(
                Question(
                    kind="coprime",
                    a=a,
                    b=b,
                    prompt="判断 %d 和 %d 是否互质，并说明理由。" % (a, b),
                    answer=answer,
                    steps=["互质的判断标准：最大公因数是否为 1。"],
                )
            )
        else:
            word_kind = "gcd" if (index // 4) % 2 == 0 else "lcm"
            problem = make_word_problem(word_kind, a, b)
            questions.append(
                Question(
                    kind="word",
                    a=a,
                    b=b,
                    prompt=problem.text,
                    answer="%s（%s）" % (problem.answer, problem.expression),
                    steps=[problem.hint],
                )
            )
    return questions


def _page(title: str, body: str) -> str:
    """包一层统一的 HTML 文档结构。"""
    head = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>@@TITLE@@</title>\n"
        "<style>\n"
        '@page { size: A4; margin: 16mm; }\n'
        'body { font-family: "Songti SC", "SimSun", serif; color: #1f1f1f; '
        "margin: 0; padding: 16mm; background: #ffffff; line-height: 1.6; }\n"
        "h1 { font-size: 20pt; text-align: center; margin: 0 0 4mm; }\n"
        "h2 { font-size: 14pt; margin: 6mm 0 3mm; border-left: 4px solid #2f6f4f; "
        "padding-left: 3mm; }\n"
        ".meta { display: flex; justify-content: space-between; font-size: 11pt; "
        "border-bottom: 1px solid #cccccc; padding-bottom: 2mm; margin-bottom: 5mm; }\n"
        ".q { margin-bottom: 6mm; page-break-inside: avoid; }\n"
        ".q-head { font-size: 11pt; font-weight: bold; }\n"
        ".q-body { font-size: 11pt; margin-top: 1mm; }\n"
        ".blank { border-bottom: 1px dashed #a0a0a0; height: 6mm; margin-top: 2mm; }\n"
        ".answers { page-break-before: always; }\n"
        ".answer { font-size: 11pt; margin-bottom: 3mm; }\n"
        ".hint { color: #555555; font-size: 10pt; }\n"
        ".cards { display: flex; flex-wrap: wrap; gap: 5mm; }\n"
        ".card { flex: 1 1 40%; border: 1px solid #cccccc; border-radius: 3mm; "
        "padding: 4mm; page-break-inside: avoid; }\n"
        ".card h3 { font-size: 12pt; margin: 0 0 2mm; color: #2f6f4f; }\n"
        ".card p { font-size: 10.5pt; margin: 0; }\n"
        ".diagram { text-align: center; margin: 4mm 0; }\n"
        ".caption { font-size: 10pt; color: #555555; }\n"
        "table { border-collapse: collapse; width: 100%; font-size: 10.5pt; }\n"
        "th, td { border: 1px solid #999999; padding: 2mm; text-align: center; }\n"
        "th { background: #eef4f0; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "@@BODY@@\n"
        "</body>\n"
        "</html>\n"
    )
    return head.replace("@@TITLE@@", html.escape(title)).replace("@@BODY@@", body)


def _meta_line() -> str:
    """练习纸顶部的姓名、班级、日期栏。"""
    return (
        '<div class="meta"><span>姓名：____________</span>'
        "<span>班级：____________</span><span>日期：____________</span></div>"
    )


def render_sheet(questions: Sequence[Question], answers: bool = False) -> str:
    """生成 A4 练习纸 HTML，answers 为真时追加参考答案页。"""
    if questions is None:
        raise ValueError("题目列表不能为空")
    items = list(questions)
    if not items:
        raise ValueError("题目列表不能为空")
    for index, item in enumerate(items):
        if not isinstance(item, Question):
            raise ValueError("第 %d 道题不是 Question 对象" % (index + 1))
    if not isinstance(answers, bool):
        raise ValueError("answers 参数必须是布尔值")

    blocks: List[str] = [
        "<h1>最大公因数与最小公倍数练习纸</h1>",
        _meta_line(),
        '<p class="hint">要求：写出必要的过程，互质判断题要说明理由，应用题要写算式和答句。</p>',
    ]
    for index, item in enumerate(items, 1):
        label = KIND_LABELS.get(item.kind, "练习")
        body_lines = [
            '<div class="q">',
            '<div class="q-head">%d.（%s）</div>' % (index, html.escape(label)),
            '<div class="q-body">%s</div>' % html.escape(item.prompt),
        ]
        if item.kind == "word":
            body_lines.append('<div class="blank"></div>')
            body_lines.append('<div class="blank"></div>')
        else:
            body_lines.append('<div class="blank"></div>')
        body_lines.append("</div>")
        blocks.append("\n".join(body_lines))

    if answers:
        answer_blocks: List[str] = ['<div class="answers">', "<h2>参考答案</h2>"]
        for index, item in enumerate(items, 1):
            answer_blocks.append(
                '<div class="answer">%d. %s</div>' % (index, html.escape(item.answer))
            )
        answer_blocks.append("</div>")
        blocks.append("\n".join(answer_blocks))
    return _page("最大公因数与最小公倍数练习纸", "\n".join(blocks))


def render_short_division_svg(a: int, b: int) -> str:
    """用 SVG 画两数的短除法竖式。"""
    left = check_value(a, "第一个数")
    right = check_value(b, "第二个数")
    rows = short_division_rows(left, right)
    row_height = 34
    top = 34
    height = top + row_height * (len(rows) + 1) + 18
    width = 300
    bar_x = 66
    divisor_x = 44
    left_x = 112
    right_x = 196

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" aria-label="%s">'
        % (
            width,
            height,
            width,
            height,
            html.escape("%d 和 %d 的短除法竖式" % (left, right)),
        ),
        '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (width, height),
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#1f1f1f" stroke-width="2"/>'
        % (bar_x, top - 18, bar_x, height - 26),
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#1f1f1f" stroke-width="2"/>'
        % (bar_x, top - 18, right_x + 44, top - 18),
    ]
    y = top
    for divisor, row_left, row_right in rows:
        parts.append(
            '<text x="%d" y="%d" text-anchor="end" font-size="18" '
            'font-family="monospace" fill="#2f6f4f">%d</text>'
            % (divisor_x, y, divisor)
        )
        parts.append(
            '<text x="%d" y="%d" text-anchor="middle" font-size="18" '
            'font-family="monospace" fill="#1f1f1f">%d</text>' % (left_x, y, row_left)
        )
        parts.append(
            '<text x="%d" y="%d" text-anchor="middle" font-size="18" '
            'font-family="monospace" fill="#1f1f1f">%d</text>' % (right_x, y, row_right)
        )
        y += row_height

    final_left, final_right = left, right
    if rows:
        final_left = rows[-1][1] // rows[-1][0]
        final_right = rows[-1][2] // rows[-1][0]
    parts.append(
        '<text x="%d" y="%d" text-anchor="middle" font-size="18" '
        'font-family="monospace" fill="#1f1f1f">%d</text>' % (left_x, y, final_left)
    )
    parts.append(
        '<text x="%d" y="%d" text-anchor="middle" font-size="18" '
        'font-family="monospace" fill="#1f1f1f">%d</text>' % (right_x, y, final_right)
    )
    parts.append(
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#1f1f1f" stroke-width="2"/>'
        % (bar_x, y + 10, right_x + 44, y + 10)
    )
    parts.append("</svg>")
    return "".join(parts)


def render_demo() -> str:
    """生成概念卡片 + 短除竖式的演示页。"""
    a, b = 12, 18
    value_gcd = gcd(a, b)
    value_lcm = lcm(a, b)
    cards: List[str] = [
        '<div class="card"><h3>最大公因数</h3><p>几个数公有的因数叫公因数，其中最大的一个叫最大公因数，'
        "记作 (%d, %d) = %d。</p></div>" % (a, b, value_gcd),
        '<div class="card"><h3>最小公倍数</h3><p>几个数公有的倍数叫公倍数，其中最小的一个叫最小公倍数，'
        "记作 [%d, %d] = %d。</p></div>" % (a, b, value_lcm),
        '<div class="card"><h3>互质</h3><p>两个数的最大公因数是 1 时，这两个数互质。'
        "互质的两个数不一定都是质数，例如 8 和 9。</p></div>",
        '<div class="card"><h3>重要关系</h3><p>对任意两个正整数 a、b，都有 '
        "a × b = 最大公因数 × 最小公倍数。本例：%d × %d = %d = %d × %d。</p></div>"
        % (a, b, a * b, value_gcd, value_lcm),
        '<div class="card"><h3>短除法要点</h3><p>每次都用两个数的公有的质因数去除，'
        "除到两个商互质为止；左边所有除数相乘是最大公因数。</p></div>",
        '<div class="card"><h3>易错提醒</h3><p>最小公倍数等于所有除数与最后两个商连乘，'
        "不要漏掉最后的商；短除只能用公因数，不能只除某一个数。</p></div>",
    ]
    diagram = (
        '<div class="diagram">%s<p class="caption">%d 和 %d 的短除法竖式：'
        "左侧除数的积 2 × 3 = %d 是最大公因数；再乘最后两个商 2 × 3，"
        "得最小公倍数 %d。</p></div>"
        % (render_short_division_svg(a, b), a, b, value_gcd, value_lcm)
    )
    table_rows: List[str] = []
    for pair in [(4, 6), (8, 12), (9, 15), (7, 10)]:
        table_rows.append(
            "<tr><td>%d 和 %d</td><td>%d</td><td>%d</td></tr>"
            % (pair[0], pair[1], gcd(pair[0], pair[1]), lcm(pair[0], pair[1]))
        )
    table = (
        "<h2>常见数对对照</h2>\n"
        "<table>\n<tr><th>数对</th><th>最大公因数</th><th>最小公倍数</th></tr>\n"
        + "\n".join(table_rows)
        + "\n</table>"
    )
    body = "\n".join(
        [
            "<h1>最大公因数与最小公倍数</h1>",
            '<p class="hint">短除法竖式图解与概念卡片，可直接打印。</p>',
            '<h2>概念卡片</h2>',
            '<div class="cards">',
            "\n".join(cards),
            "</div>",
            "<h2>短除法图解</h2>",
            diagram,
            table,
        ]
    )
    return _page("最大公因数与最小公倍数演示页", body)
