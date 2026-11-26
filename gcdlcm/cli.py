"""命令行入口：gcdlcm。"""

import argparse
import sys
from typing import List, Optional, Sequence

from . import core, sheet, word

PROG = "gcdlcm"


def _ensure_utf8_console() -> None:
    """尽量把标准输出和标准错误切换成 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        if not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            continue


def _parse_numbers(text: str) -> List[int]:
    """解析逗号分隔的整数列表，空项与非整数都会报错。"""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("--numbers 不能为空，请用逗号分隔 2 到 10 个整数")
    parts = [part.strip() for part in text.split(",")]
    if any(part == "" for part in parts):
        raise ValueError("--numbers 中有空项，请检查逗号位置")
    values: List[int] = []
    for part in parts:
        try:
            values.append(int(part))
        except ValueError:
            raise ValueError("--numbers 中的 %s 不是整数" % part)
    return values


def _write_html(path: str, content: str) -> str:
    """把 HTML 写入文件，OSError 转成中文 ValueError。"""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("输出路径不能为空")
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("写入文件 %s 失败：%s" % (path, exc))
    return path


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="最大公因数与最小公倍数教学工具：计算、短除步骤、应用题与练习纸。",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="子命令")

    gcd_parser = subparsers.add_parser("gcd", help="求一组数的最大公因数")
    gcd_parser.add_argument("--numbers", required=True, help="逗号分隔的 2 到 10 个整数")

    lcm_parser = subparsers.add_parser("lcm", help="求一组数的最小公倍数")
    lcm_parser.add_argument("--numbers", required=True, help="逗号分隔的 2 到 10 个整数")

    solve_parser = subparsers.add_parser("solve", help="输出两数的质因数分解、短除步骤与结果")
    solve_parser.add_argument("--a", required=True, type=int, help="第一个数（1 到 100000）")
    solve_parser.add_argument("--b", required=True, type=int, help="第二个数（1 到 100000）")

    coprime_parser = subparsers.add_parser("coprime", help="判断两个数是否互质")
    coprime_parser.add_argument("--a", required=True, type=int, help="第一个数（1 到 100000）")
    coprime_parser.add_argument("--b", required=True, type=int, help="第二个数（1 到 100000）")

    word_parser = subparsers.add_parser("word", help="生成一道最大公因数或最小公倍数应用题")
    word_parser.add_argument(
        "--type", required=True, help="题型：gcd、lcm，或模板名 ribbon、tile、meet、bus"
    )
    word_parser.add_argument("--a", required=True, type=int, help="第一个数（1 到 100000）")
    word_parser.add_argument("--b", required=True, type=int, help="第二个数（1 到 100000）")
    word_parser.add_argument("--template", default=None, help="指定模板（可选）")

    sheet_parser = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=8, help="题目数量，默认 8，范围 1 到 50")
    sheet_parser.add_argument("--seed", type=int, default=1, help="随机种子，默认 1")
    sheet_parser.add_argument("-o", "--output", required=True, help="输出 HTML 文件路径")
    sheet_parser.add_argument("--answers", action="store_true", help="同时生成参考答案页")

    demo_parser = subparsers.add_parser("demo", help="生成短除法竖式与概念卡片演示页")
    demo_parser.add_argument("-o", "--output", required=True, help="输出 HTML 文件路径")
    return parser


def _run(args: argparse.Namespace) -> int:
    """执行子命令，成功返回 0。"""
    command = args.command
    if command is None:
        raise ValueError("请指定子命令，可用：gcd、lcm、solve、coprime、word、sheet、demo")
    if command == "gcd":
        values = _parse_numbers(args.numbers)
        result = core.gcd_many(values)
        print("%s 的最大公因数是 %d" % ("、".join(str(v) for v in values), result))
        return 0
    if command == "lcm":
        values = _parse_numbers(args.numbers)
        result = core.lcm_many(values)
        print("%s 的最小公倍数是 %d" % ("、".join(str(v) for v in values), result))
        return 0
    if command == "solve":
        left = core.check_value(args.a, "第一个数")
        right = core.check_value(args.b, "第二个数")
        print(core.factor_text(left))
        print(core.factor_text(right))
        steps = core.short_division_steps(left, right)
        print("短除步骤：")
        for line in steps[:-2]:
            print("  " + line)
        for line in steps[-2:]:
            print(line)
        return 0
    if command == "coprime":
        left = core.check_value(args.a, "第一个数")
        right = core.check_value(args.b, "第二个数")
        common = core.gcd(left, right)
        if common == 1:
            print("%d 和 %d 互质（最大公因数为 1）" % (left, right))
        else:
            print("%d 和 %d 不互质（最大公因数为 %d）" % (left, right, common))
        return 0
    if command == "word":
        problem = word.make_word_problem(args.type, args.a, args.b, args.template)
        print(word.format_word_problem(problem))
        return 0
    if command == "sheet":
        questions = sheet.make_questions(args.count, args.seed)
        content = sheet.render_sheet(questions, args.answers)
        path = _write_html(args.output, content)
        print("已生成练习纸：%s（共 %d 题）" % (path, len(questions)))
        return 0
    if command == "demo":
        content = sheet.render_demo()
        path = _write_html(args.output, content)
        print("已生成演示页：%s" % path)
        return 0
    raise ValueError("未知子命令 %s" % command)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数，成功返回 0，输入非法返回 2。"""
    _ensure_utf8_console()
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
