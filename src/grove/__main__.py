"""Allow `python -m grove` as well as the installed `grove` script."""

import sys

from grove.cli import main

if __name__ == "__main__":
    sys.exit(main())
