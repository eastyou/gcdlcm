"""以 python -m gcdlcm 方式运行命令行。"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
