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
            print("stderr before substitution: ", self.stderr)
            self.stderr = re.sub(rb"[\d,]+ warning \S+\s+", b"", self.stderr)
            self.stderr = re.sub(rb"[\d,]+ warnings \S+\s+", b"", self.stderr)
            self.stderr = re.sub(rb"[\d,]+ Use -header-filter \S+\s+", b"", self.stderr)
            self.stderr = re.sub(rb"[\d,]+ Use -system-headers \S+\s+", b"", self.stderr)
            print("stderr after substitution: ", self.stderr)
            if len(self.stderr) > 0 and "--fix-errors" in self.args:
                print(self.stderr)
                self.returncode = 1
            self.exit_on_error()


def main(argv: List[str] = sys.argv):
    cmd = ClangTidyCmd(argv)
    cmd.run()


if __name__ == "__main__":
    main()
