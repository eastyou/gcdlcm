# gcdlcm

[![CI](https://github.com/eastyou/gcdlcm/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/gcdlcm/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

一个面向小学数学课堂的最大公因数与最小公倍数教学工具。它可以在命令行里完成求值、展示短除步骤、判断互质、生成应用题，也能一键生成可打印的 A4 练习纸和概念演示页。全部代码只依赖 Python 标准库。

计算规则与教材一致：几个数公有的因数中最大的一个叫最大公因数；公有的倍数中最小的一个叫最小公倍数；两个数的最大公因数为 1 时称它们互质。两数相乘等于它们的最大公因数与最小公倍数之积。

## 特性

- 纯标准库实现，零第三方依赖，Python 3.9 及以上可用。
- `gcd` 与 `lcm` 支持一次传入 2 到 10 个数，只接受 1 到 100000 的整数。
- `solve` 同时给出质因数分解、短除法每一步与两个结果，便于课堂讲解。
- `coprime` 判断互质并附带最大公因数，让结论有依据。
- `word` 内置彩带裁剪、地砖铺贴、报数相遇、班车同时发车四种应用题模板。
- `sheet` 生成 A4 练习纸，混合四种题型，可附加参考答案页，同一个 seed 结果完全可复现。
- `demo` 生成短除法竖式 SVG 与概念卡片，适合投影或打印。
- 所有非法输入都会得到中文错误提示，并以退出码 2 结束，方便脚本判断。

## 安装

```console
$ python3 -m pip install .
$ gcdlcm --help
```

不安装也可以直接以模块方式运行：

```console
$ python3 -m gcdlcm --help
```

## 使用

### 求最大公因数

```console
$ gcdlcm gcd --numbers 12,18,24
12、18、24 的最大公因数是 6
```

### 求最小公倍数

```console
$ gcdlcm lcm --numbers 4,6,10
4、6、10 的最小公倍数是 60
```

### 输出质因数分解与短除步骤

```console
$ gcdlcm solve --a 12 --b 18
12 = 2^2 × 3
18 = 2 × 3^2
短除步骤：
  用公因数 2 同时除 12 和 18，得到 6 和 9
  用公因数 3 同时除 6 和 9，得到 2 和 3
  2 和 3 已经互质，短除结束
最大公因数 = 2 × 3 = 6
最小公倍数 = 2 × 3 × 2 × 3 = 36
```

### 判断互质

```console
$ gcdlcm coprime --a 9 --b 28
9 和 28 互质（最大公因数为 1）
$ gcdlcm coprime --a 12 --b 18
12 和 18 不互质（最大公因数为 6）
```

### 生成应用题

```console
$ gcdlcm word --type gcd --a 12 --b 18
【彩带裁剪】
题目：手工课上，老师拿来两条彩带，一条长 12 厘米，另一条长 18 厘米。要把它们都剪成同样长的小段且没有剩余，每段最长是多少厘米？两条彩带一共能剪成多少段？
算式：最大公因数 (12, 18) = 6
答案：每段最长 6 厘米；12 厘米剪成 2 段，18 厘米剪成 3 段，一共 5 段。
提示：每段长度要同时整除两个长度，问“最长”就是求最大公因数。
```

```console
$ gcdlcm word --type lcm --a 4 --b 6 --template bus
【班车同时发车】
题目：1 路公交车每 4 分钟发一班，2 路公交车每 6 分钟发一班。两路车在 8:00 同时发车，至少再过多少分钟两路车又同时发车？
算式：最小公倍数 (4, 6) = 12
答案：至少再过 12 分钟，两路车再次同时发车。
提示：同时发车的间隔要同时是两个发车间隔的倍数，问“至少”就是求最小公倍数。
```

### 生成 A4 练习纸

```console
$ gcdlcm sheet --count 8 --seed 1 -o sheet.html --answers
已生成练习纸：sheet.html（共 8 题）
```

生成的 `sheet.html` 用浏览器打开即可打印：第一页是题目，加了 `--answers` 时会另起一页输出参考答案。

### 生成演示页

```console
$ gcdlcm demo -o demo.html
已生成演示页：demo.html
```

演示页包含六张概念卡片、12 和 18 的短除法竖式 SVG，以及四组常见数对的对照表。

### 参数

| 子命令 | 参数 | 说明 |
| --- | --- | --- |
| `gcd` | `--numbers` | 必填，逗号分隔的 2 到 10 个整数，每个数在 1 到 100000 之间 |
| `lcm` | `--numbers` | 必填，规则同上，结果必须小于 1e15 |
| `solve` | `--a`、`--b` | 必填，各为 1 到 100000 的整数 |
| `coprime` | `--a`、`--b` | 必填，各为 1 到 100000 的整数 |
| `word` | `--type` | 必填，取 `gcd`、`lcm`，也接受模板名 `ribbon`、`tile`、`meet`、`bus` |
| `word` | `--a`、`--b` | 必填，各为 1 到 100000 的整数 |
| `word` | `--template` | 可选，指定模板；必须与题型匹配 |
| `sheet` | `--count` | 可选，题目数量，默认 8，范围 1 到 50 |
| `sheet` | `--seed` | 可选，随机种子，默认 1，范围 0 到 2^31-1 |
| `sheet` | `-o`、`--output` | 必填，输出 HTML 文件路径 |
| `sheet` | `--answers` | 可选，追加参考答案页 |
| `demo` | `-o`、`--output` | 必填，输出 HTML 文件路径 |

### 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 执行成功 |
| 2 | 输入非法、超出范围或写文件失败，错误信息以「错误：」开头打印到标准错误 |
| 2 | 命令行参数缺失或类型错误，由参数解析器报错 |

例如：

```console
$ gcdlcm gcd --numbers 12,,18
错误：--numbers 中有空项，请检查逗号位置
$ echo $?
2
```

```console
$ gcdlcm lcm --numbers 99991,99989,99971,99961,99929,99923,99877,99871
错误：最小公倍数 99912025897064911969 超出可处理范围（须小于 1e15）
```

## 作为库使用

```python
from gcdlcm import (
    gcd_many,
    lcm_many,
    prime_factors,
    short_division_steps,
    make_word_problem,
    make_questions,
    render_sheet,
)

print(gcd_many([12, 18, 24]))       # 6
print(lcm_many([4, 6, 10]))         # 60
print(prime_factors(360))           # {2: 3, 3: 2, 5: 1}

for line in short_division_steps(12, 18):
    print(line)

problem = make_word_problem("lcm", 4, 6)
print(problem.answer)               # 至少再过 12 天，两人又会同一天去图书馆。

page = render_sheet(make_questions(8, 1), answers=True)
with open("sheet.html", "w", encoding="utf-8") as handle:
    handle.write(page)
```

所有对外函数都带类型注解，输入校验失败时抛出中文 `ValueError`。

## 开发与测试

```console
$ python3 -m unittest discover -s tests -v
```

测试文件为 `tests/test_gcdlcm.py`，共 130 个测试方法，覆盖核心算法、边界与非法输入、命令行退出码与标准错误、HTML 能否被 `html.parser` 解析、以及 seed 的可复现性。测试生成的 HTML 全部写入临时目录，不留在仓库中。

## License

[MIT](LICENSE) © 2026 eastyou
