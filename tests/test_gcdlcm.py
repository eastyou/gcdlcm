"""gcdlcm 的单元测试（仅使用标准库 unittest）。"""

import contextlib
import html
import html.parser
import io
import os
import tempfile
import unittest
from typing import List, Optional, Tuple

from gcdlcm import core, sheet, word
from gcdlcm.cli import main


class _TagCollector(html.parser.HTMLParser):
    """收集 HTML 标签，用于检查输出能否被解析。"""

    def __init__(self) -> None:
        super().__init__()
        self.tags: List[str] = []
        self.closed: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self.tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        self.closed.append(tag)


def _parse_ok(text: str) -> Tuple[List[str], List[str]]:
    """解析 HTML 文本，返回 (开始标签, 结束标签)。"""
    parser = _TagCollector()
    parser.feed(text)
    parser.close()
    return parser.tags, parser.closed


class TestCoreBasics(unittest.TestCase):
    def test_gcd_basic(self) -> None:
        self.assertEqual(core.gcd(12, 18), 6)

    def test_gcd_same_number(self) -> None:
        self.assertEqual(core.gcd(97, 97), 97)

    def test_gcd_with_one(self) -> None:
        self.assertEqual(core.gcd(1, 100000), 1)

    def test_gcd_reversed_order(self) -> None:
        self.assertEqual(core.gcd(18, 12), 6)

    def test_gcd_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd(0, 18)

    def test_gcd_rejects_negative(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd(-4, 8)

    def test_gcd_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd(True, 8)

    def test_gcd_rejects_float(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd(12.0, 18)

    def test_gcd_rejects_too_large(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd(100001, 18)

    def test_lcm_basic(self) -> None:
        self.assertEqual(core.lcm(4, 6), 12)

    def test_lcm_coprime_pair(self) -> None:
        self.assertEqual(core.lcm(7, 10), 70)

    def test_lcm_same_number(self) -> None:
        self.assertEqual(core.lcm(36, 36), 36)

    def test_lcm_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.lcm(4, 0)

    def test_lcm_respects_product_relation(self) -> None:
        self.assertEqual(core.gcd(24, 36) * core.lcm(24, 36), 24 * 36)


class TestGroups(unittest.TestCase):
    def test_gcd_many_three(self) -> None:
        self.assertEqual(core.gcd_many([12, 18, 24]), 6)

    def test_gcd_many_two(self) -> None:
        self.assertEqual(core.gcd_many([8, 12]), 4)

    def test_gcd_many_one_common(self) -> None:
        self.assertEqual(core.gcd_many([9, 28, 35]), 1)

    def test_gcd_many_too_few(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd_many([12])

    def test_gcd_many_too_many(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd_many([2] * 11)

    def test_gcd_many_empty(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd_many([])

    def test_gcd_many_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            core.gcd_many([True, 4])

    def test_lcm_many_three(self) -> None:
        self.assertEqual(core.lcm_many([4, 6, 10]), 60)

    def test_lcm_many_two(self) -> None:
        self.assertEqual(core.lcm_many([12, 18]), 36)

    def test_lcm_many_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.lcm_many([4, 0, 6])

    def test_lcm_many_overflow(self) -> None:
        values = [99991, 99989, 99971, 99961, 99929, 99923, 99877, 99871]
        with self.assertRaises(ValueError):
            core.lcm_many(values)


class TestFactorization(unittest.TestCase):
    def test_prime_factors_12(self) -> None:
        self.assertEqual(core.prime_factors(12), {2: 2, 3: 1})

    def test_prime_factors_prime(self) -> None:
        self.assertEqual(core.prime_factors(97), {97: 1})

    def test_prime_factors_one(self) -> None:
        self.assertEqual(core.prime_factors(1), {})

    def test_prime_factors_power(self) -> None:
        self.assertEqual(core.prime_factors(1024), {2: 10})

    def test_prime_factors_sorted_keys(self) -> None:
        self.assertEqual(list(core.prime_factors(360).keys()), [2, 3, 5])

    def test_prime_factors_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.prime_factors(0)

    def test_prime_factors_rejects_negative(self) -> None:
        with self.assertRaises(ValueError):
            core.prime_factors(-12)

    def test_prime_factors_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            core.prime_factors(False)

    def test_factor_text_12(self) -> None:
        self.assertEqual(core.factor_text(12), "12 = 2^2 × 3")

    def test_factor_text_one(self) -> None:
        self.assertIn("1 = 1", core.factor_text(1))

    def test_factor_text_prime(self) -> None:
        self.assertEqual(core.factor_text(13), "13 = 13")


class TestShortDivision(unittest.TestCase):
    def test_steps_12_18_summary(self) -> None:
        steps = core.short_division_steps(12, 18)
        self.assertEqual(steps[-2], "最大公因数 = 2 × 3 = 6")
        self.assertEqual(steps[-1], "最小公倍数 = 2 × 3 × 2 × 3 = 36")

    def test_steps_12_18_first_line(self) -> None:
        steps = core.short_division_steps(12, 18)
        self.assertEqual(steps[0], "用公因数 2 同时除 12 和 18，得到 6 和 9")

    def test_steps_coprime_pair(self) -> None:
        steps = core.short_division_steps(9, 28)
        self.assertEqual(steps[0], "9 和 28 没有大于 1 的公因数，短除立即结束")
        self.assertEqual(steps[-2], "最大公因数 = 1 = 1")

    def test_steps_identical_numbers(self) -> None:
        steps = core.short_division_steps(97, 97)
        self.assertIn("用公因数 97 同时除 97 和 97，得到 1 和 1", steps)

    def test_steps_power_pair(self) -> None:
        steps = core.short_division_steps(8, 12)
        self.assertEqual(steps[-2], "最大公因数 = 2 × 2 = 4")
        self.assertEqual(steps[-1], "最小公倍数 = 2 × 2 × 2 × 3 = 24")

    def test_steps_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.short_division_steps(0, 12)

    def test_rows_12_18(self) -> None:
        self.assertEqual(core.short_division_rows(12, 18), [[2, 12, 18], [3, 6, 9]])

    def test_rows_coprime(self) -> None:
        self.assertEqual(core.short_division_rows(9, 28), [])

    def test_rows_same_number(self) -> None:
        self.assertEqual(core.short_division_rows(97, 97), [[97, 97, 97]])

    def test_rows_rejects_large(self) -> None:
        with self.assertRaises(ValueError):
            core.short_division_rows(200000, 4)

    def test_is_coprime_true(self) -> None:
        self.assertTrue(core.is_coprime(9, 28))

    def test_is_coprime_false(self) -> None:
        self.assertFalse(core.is_coprime(12, 18))

    def test_is_coprime_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            core.is_coprime(0, 5)


class TestWordProblems(unittest.TestCase):
    def test_default_template_is_ribbon(self) -> None:
        problem = word.make_word_problem("gcd", 12, 18)
        self.assertEqual(problem.template, "ribbon")
        self.assertEqual(problem.title, "彩带裁剪")

    def test_ribbon_answer_content(self) -> None:
        problem = word.make_word_problem("gcd", 12, 18)
        self.assertIn("每段最长 6 厘米", problem.answer)
        self.assertIn("一共 5 段", problem.answer)

    def test_tile_template(self) -> None:
        problem = word.make_word_problem("gcd", 12, 18, "tile")
        self.assertIn("地砖", problem.text)
        self.assertIn("6 分米", problem.answer)

    def test_meet_template(self) -> None:
        problem = word.make_word_problem("lcm", 4, 6)
        self.assertEqual(problem.template, "meet")
        self.assertIn("至少再过 12 天", problem.answer)

    def test_bus_template(self) -> None:
        problem = word.make_word_problem("lcm", 4, 6, "bus")
        self.assertIn("公交车", problem.text)
        self.assertIn("12 分钟", problem.answer)

    def test_chinese_alias_kind(self) -> None:
        self.assertEqual(word.normalize_kind("最小公倍数"), "lcm")
        self.assertEqual(word.normalize_kind("最大公因数"), "gcd")

    def test_template_name_as_kind(self) -> None:
        self.assertEqual(word.normalize_kind("meet"), "lcm")
        self.assertEqual(word.normalize_kind("tile"), "gcd")

    def test_unknown_kind(self) -> None:
        with self.assertRaises(ValueError):
            word.make_word_problem("nope", 4, 6)

    def test_unknown_template(self) -> None:
        with self.assertRaises(ValueError):
            word.make_word_problem("gcd", 4, 6, "meet")

    def test_template_case_insensitive(self) -> None:
        problem = word.make_word_problem("gcd", 12, 18, "RIBBON")
        self.assertEqual(problem.template, "ribbon")

    def test_word_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            word.make_word_problem("gcd", 0, 6)

    def test_word_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            word.make_word_problem("gcd", True, 6)

    def test_format_word_problem_lines(self) -> None:
        text = word.format_word_problem(word.make_word_problem("gcd", 12, 18))
        self.assertIn("【彩带裁剪】", text)
        self.assertIn("题目：", text)
        self.assertIn("算式：最大公因数 (12, 18) = 6", text)
        self.assertIn("答案：", text)
        self.assertIn("提示：", text)

    def test_template_options_text(self) -> None:
        text = word.template_options()
        for name in ("ribbon", "tile", "meet", "bus"):
            self.assertIn(name, text)


class TestQuestionMaker(unittest.TestCase):
    def test_count_matches(self) -> None:
        self.assertEqual(len(sheet.make_questions(8, 1)), 8)
        self.assertEqual(len(sheet.make_questions(1, 0)), 1)

    def test_seed_reproducible(self) -> None:
        first = sheet.make_questions(8, 1)
        second = sheet.make_questions(8, 1)
        self.assertEqual([q.prompt for q in first], [q.prompt for q in second])

    def test_different_seed_changes(self) -> None:
        first = sheet.make_questions(8, 1)
        second = sheet.make_questions(8, 2)
        self.assertNotEqual([q.prompt for q in first], [q.prompt for q in second])

    def test_kinds_cycle(self) -> None:
        kinds = [q.kind for q in sheet.make_questions(4, 1)]
        self.assertEqual(kinds, ["gcd", "lcm", "coprime", "word"])

    def test_values_in_range(self) -> None:
        for item in sheet.make_questions(20, 5):
            self.assertGreaterEqual(item.a, 2)
            self.assertLessEqual(item.a, 40)
            self.assertGreaterEqual(item.b, 2)
            self.assertLessEqual(item.b, 40)
            self.assertNotEqual(item.a, item.b)

    def test_gcd_answer_correct(self) -> None:
        for item in sheet.make_questions(12, 3):
            if item.kind == "gcd":
                self.assertIn("最大公因数是 %d" % core.gcd(item.a, item.b), item.answer)

    def test_lcm_answer_correct(self) -> None:
        for item in sheet.make_questions(12, 3):
            if item.kind == "lcm":
                self.assertIn("最小公倍数是 %d" % core.lcm(item.a, item.b), item.answer)

    def test_coprime_answer_correct(self) -> None:
        for item in sheet.make_questions(12, 7):
            if item.kind == "coprime":
                expected = core.gcd(item.a, item.b) == 1
                self.assertEqual(item.answer.startswith("互质"), expected)

    def test_word_kinds_alternate(self) -> None:
        questions = sheet.make_questions(12, 1)
        word_questions = [q for q in questions if q.kind == "word"]
        self.assertGreaterEqual(len(word_questions), 2)
        self.assertIn("彩带", word_questions[0].prompt)
        self.assertIn("图书馆", word_questions[1].prompt)

    def test_count_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(0, 1)

    def test_count_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(51, 1)

    def test_count_bool_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(True, 1)

    def test_seed_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(4, -1)

    def test_seed_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(4, 2 ** 31)

    def test_seed_bool_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sheet.make_questions(4, True)

    def test_max_seed_accepted(self) -> None:
        self.assertEqual(len(sheet.make_questions(2, 2 ** 31 - 1)), 2)


class TestRenderSheet(unittest.TestCase):
    def _questions(self) -> List[sheet.Question]:
        return sheet.make_questions(4, 1)

    def test_sheet_has_doctype(self) -> None:
        text = sheet.render_sheet(self._questions())
        self.assertTrue(text.startswith("<!DOCTYPE html>"))

    def test_sheet_parses(self) -> None:
        tags, _ = _parse_ok(sheet.render_sheet(self._questions()))
        self.assertIn("html", tags)
        self.assertIn("body", tags)
        self.assertIn("div", tags)

    def test_sheet_contains_a4_style(self) -> None:
        text = sheet.render_sheet(self._questions())
        self.assertIn("A4", text)
        self.assertIn("@page", text)

    def test_sheet_answers_section(self) -> None:
        text = sheet.render_sheet(self._questions(), True)
        self.assertIn("参考答案", text)

    def test_sheet_without_answers(self) -> None:
        text = sheet.render_sheet(self._questions(), False)
        self.assertNotIn("参考答案", text)

    def test_sheet_numbering(self) -> None:
        text = sheet.render_sheet(self._questions())
        self.assertIn("1.（最大公因数）", text)
        self.assertIn("4.（应用题）", text)

    def test_sheet_escapes_prompt(self) -> None:
        item = sheet.Question(
            kind="gcd",
            a=4,
            b=6,
            prompt="<script>alert(1)</script>",
            answer="2",
        )
        text = sheet.render_sheet([item])
        self.assertNotIn("<script>alert", text)
        self.assertIn("&lt;script&gt;", text)

    def test_sheet_escapes_answer(self) -> None:
        item = sheet.Question(kind="gcd", a=4, b=6, prompt="题", answer="<b>答</b>")
        text = sheet.render_sheet([item], True)
        self.assertIn("&lt;b&gt;答&lt;/b&gt;", text)

    def test_sheet_rejects_none(self) -> None:
        with self.assertRaises(ValueError):
            sheet.render_sheet(None)

    def test_sheet_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            sheet.render_sheet([])

    def test_sheet_rejects_non_question(self) -> None:
        with self.assertRaises(ValueError):
            sheet.render_sheet([{"kind": "gcd"}])

    def test_sheet_rejects_bad_answers_flag(self) -> None:
        with self.assertRaises(ValueError):
            sheet.render_sheet(self._questions(), "yes")


class TestRenderDemo(unittest.TestCase):
    def test_demo_parses(self) -> None:
        tags, _ = _parse_ok(sheet.render_demo())
        self.assertIn("html", tags)
        self.assertIn("svg", tags)

    def test_demo_has_svg_pair(self) -> None:
        text = sheet.render_demo()
        self.assertIn("<svg", text)
        self.assertIn("</svg>", text)

    def test_demo_has_concept_cards(self) -> None:
        text = sheet.render_demo()
        self.assertIn("概念卡片", text)
        self.assertIn("短除法", text)
        self.assertIn("互质", text)

    def test_demo_has_values(self) -> None:
        text = sheet.render_demo()
        self.assertIn("(12, 18) = 6", text)
        self.assertIn("[12, 18] = 36", text)

    def test_svg_fragment_parses(self) -> None:
        fragment = sheet.render_short_division_svg(12, 18)
        tags, _ = _parse_ok("<html><body>%s</body></html>" % fragment)
        self.assertIn("svg", tags)
        self.assertIn("line", tags)
        self.assertIn("text", tags)

    def test_svg_contains_numbers(self) -> None:
        fragment = sheet.render_short_division_svg(12, 18)
        for value in ("12", "18", "6", "9", "2", "3"):
            self.assertIn(">%s</text>" % value, fragment)

    def test_svg_escapes_aria_label(self) -> None:
        fragment = sheet.render_short_division_svg(12, 18)
        self.assertIn('aria-label="12 和 18 的短除法竖式"', fragment)

    def test_svg_rejects_zero(self) -> None:
        with self.assertRaises(ValueError):
            sheet.render_short_division_svg(0, 18)


class TestCli(unittest.TestCase):
    def _run(self, argv: List[str]) -> Tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_help_exits_zero(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit) as caught:
                main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("gcd", out.getvalue())

    def test_help_lists_all_subcommands(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit):
                main(["--help"])
        text = out.getvalue()
        for name in ("gcd", "lcm", "solve", "coprime", "word", "sheet", "demo"):
            self.assertIn(name, text)

    def test_gcd_ok(self) -> None:
        code, out, err = self._run(["gcd", "--numbers", "12,18,24"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("最大公因数是 6", out)

    def test_gcd_order_preserved(self) -> None:
        code, out, _ = self._run(["gcd", "--numbers", "24,18,12"])
        self.assertEqual(code, 0)
        self.assertIn("24、18、12", out)

    def test_lcm_ok(self) -> None:
        code, out, err = self._run(["lcm", "--numbers", "4,6,10"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("最小公倍数是 60", out)

    def test_solve_ok(self) -> None:
        code, out, _ = self._run(["solve", "--a", "12", "--b", "18"])
        self.assertEqual(code, 0)
        self.assertIn("12 = 2^2 × 3", out)
        self.assertIn("18 = 2 × 3^2", out)
        self.assertIn("短除步骤：", out)
        self.assertIn("最大公因数 = 2 × 3 = 6", out)
        self.assertIn("最小公倍数 = 2 × 3 × 2 × 3 = 36", out)

    def test_coprime_true_output(self) -> None:
        code, out, _ = self._run(["coprime", "--a", "9", "--b", "28"])
        self.assertEqual(code, 0)
        self.assertIn("9 和 28 互质（最大公因数为 1）", out)

    def test_coprime_false_output(self) -> None:
        code, out, _ = self._run(["coprime", "--a", "12", "--b", "18"])
        self.assertEqual(code, 0)
        self.assertIn("不互质（最大公因数为 6）", out)

    def test_word_default(self) -> None:
        code, out, _ = self._run(["word", "--type", "gcd", "--a", "12", "--b", "18"])
        self.assertEqual(code, 0)
        self.assertIn("【彩带裁剪】", out)
        self.assertIn("答案：", out)

    def test_word_with_template(self) -> None:
        code, out, _ = self._run(
            ["word", "--type", "lcm", "--a", "4", "--b", "6", "--template", "bus"]
        )
        self.assertEqual(code, 0)
        self.assertIn("【班车同时发车】", out)

    def test_word_unknown_type_returns_2(self) -> None:
        code, out, err = self._run(["word", "--type", "nope", "--a", "4", "--b", "6"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("错误：", err)

    def test_word_zero_returns_2(self) -> None:
        code, _, err = self._run(["word", "--type", "gcd", "--a", "0", "--b", "6"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_sheet_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sheet.html")
            code, out, err = self._run(["sheet", "--count", "6", "--seed", "1", "-o", path])
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成练习纸", out)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertNotIn("参考答案", content)

    def test_sheet_with_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sheet.html")
            code, _, _ = self._run(
                ["sheet", "--count", "8", "--seed", "2", "-o", path, "--answers"]
            )
            self.assertEqual(code, 0)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("参考答案", content)

    def test_sheet_seed_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = os.path.join(temp_dir, "a.html")
            second = os.path.join(temp_dir, "b.html")
            self._run(["sheet", "--count", "8", "--seed", "7", "-o", first])
            self._run(["sheet", "--count", "8", "--seed", "7", "-o", second])
            with open(first, encoding="utf-8") as handle:
                first_text = handle.read()
            with open(second, encoding="utf-8") as handle:
                second_text = handle.read()
            self.assertEqual(first_text, second_text)

    def test_sheet_count_zero_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sheet.html")
            code, _, err = self._run(["sheet", "--count", "0", "-o", path])
            self.assertEqual(code, 2)
            self.assertIn("错误：", err)
            self.assertFalse(os.path.exists(path))

    def test_sheet_bad_directory_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "missing", "sheet.html")
            code, _, err = self._run(["sheet", "--count", "2", "-o", path])
            self.assertEqual(code, 2)
            self.assertIn("错误：", err)

    def test_demo_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "demo.html")
            code, out, err = self._run(["demo", "-o", path])
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成演示页", out)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("<svg", content)
            self.assertIn("短除法", content)

    def test_demo_bad_directory_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "missing", "demo.html")
            code, _, err = self._run(["demo", "-o", path])
            self.assertEqual(code, 2)
            self.assertIn("错误：", err)

    def test_no_command_returns_2(self) -> None:
        code, _, err = self._run([])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_unknown_command_exits_2(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as caught:
                main(["nope"])
        self.assertEqual(caught.exception.code, 2)

    def test_gcd_empty_item_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers", "12,,18"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_gcd_not_integer_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers", "12,abc"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_gcd_single_value_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers", "12"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_gcd_zero_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers", "12,0"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_gcd_too_many_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers", ",".join(["2"] * 11)])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_gcd_negative_returns_2(self) -> None:
        code, _, err = self._run(["gcd", "--numbers=-4,8"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_lcm_overflow_returns_2(self) -> None:
        numbers = "99991,99989,99971,99961,99929,99923,99877,99871"
        code, _, err = self._run(["lcm", "--numbers", numbers])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_solve_zero_returns_2(self) -> None:
        code, _, err = self._run(["solve", "--a", "0", "--b", "18"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_coprime_with_one(self) -> None:
        code, out, err = self._run(["coprime", "--a", "1", "--b", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("互质（最大公因数为 1）", out)

    def test_sheet_seed_negative_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "sheet.html")
            code, _, err = self._run(["sheet", "--seed", "-1", "-o", path])
            self.assertEqual(code, 2)
            self.assertIn("错误：", err)


if __name__ == "__main__":
    unittest.main()

