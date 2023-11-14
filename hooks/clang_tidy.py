#!/usr/bin/env python3
"""Wrapper script for clang-tidy."""
import re
import sys
from typing import List

from hooks.utils import StaticAnalyzerCmd


class ClangTidyCmd(StaticAnalyzerCmd):
    """Class for the clang-tidy command."""

    command = "clang-tidy"
    lookbehind = "LLVM version "

    def __init__(self, args: List[str]):
        super().__init__(self.command, self.lookbehind, args)
        self.parse_args(args)
        self.edit_in_place = "-fix" in self.args or "--fix-errors" in self.args

    def run(self):
        """Run clang-tidy. If --fix-errors is passed in, then return code will be 0, even if there are errors."""
        for filename in self.files:
            self.run_command([filename] + self.args)
            # Warnings generated aren't important.
            self.stderr = re.sub(rb"[\d,]+ warning \S+\s+", b"", self.stderr)
            self.stderr = re.sub(rb"[\d]+ warnings generated\S+\s+", b"", self.stderr)
            self.stderr = re.sub(rb"Suppressed [0-9]+ warnings \([0-9]+ in non-user code.*\s+", b"", self.stderr)
            self.stderr = re.sub(rb"Use -header-filter=\.\* to display errors from all non-system headers\. Use -system-headers to display errors from system headers as well\.\s+", b"", self.stderr)
            if len(self.stderr) > 0 and "--fix-errors" in self.args:
                print(self.stderr)
                self.returncode = 1
            self.exit_on_error()


def main(argv: List[str] = sys.argv):
    cmd = ClangTidyCmd(argv)
    cmd.run()


if __name__ == "__main__":
    main()
