"""Assignment 02 · Mini linter: template solution."""

import argparse
import ast
import re
import sys
from dataclasses import dataclass

ALL_CODES = ("PLP001", "PLP002", "PLP003", "PLP004", "PLP005")
MUTABLE_LITERALS = (ast.List, ast.Dict, ast.Set)
MUTABLE_CALLS = {"list", "dict", "set"}
NOQA_RE = re.compile(r"#\s*noqa(?::\s*([A-Z0-9,\s]+))?")


@dataclass(frozen=True, order=True)
class Finding:
    line: int
    col: int
    code: str
    message: str


class Checker(ast.NodeVisitor):
    def __init__(self):
        self.findings = []
        self.imports = {}            # bound name -> the import node that bound it
        self.used = set()            # every name that appears in the code

    def report(self, node, code, message):
        self.findings.append(Finding(node.lineno, node.col_offset + 1, code, message))

    # PLP001: collected here, reported in finish() once all names are known.
    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name.split(".")[0]] = node
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module != "__future__":
            for alias in node.names:
                self.imports[alias.asname or alias.name] = node
        self.generic_visit(node)

    def visit_Name(self, node):
        self.used.add(node.id)
        self.generic_visit(node)

    def finish(self, tree):
        for statement in tree.body:                  # module-level __all__ = ["a", "b"]
            if (
                isinstance(statement, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "__all__" for t in statement.targets)
                and isinstance(statement.value, (ast.List, ast.Tuple))
            ):
                self.used.update(
                    e.value for e in statement.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                )
        for name, node in self.imports.items():
            if name not in self.used:
                self.report(node, "PLP001", f"'{name}' imported but unused")

    # PLP002
    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.report(node, "PLP002", "bare except")
        self.generic_visit(node)

    # PLP003
    def visit_FunctionDef(self, node):
        defaults = node.args.defaults + [d for d in node.args.kw_defaults if d is not None]
        for default in defaults:
            if isinstance(default, MUTABLE_LITERALS) or (
                isinstance(default, ast.Call)
                and isinstance(default.func, ast.Name)
                and default.func.id in MUTABLE_CALLS
            ):
                self.report(default, "PLP003", f"mutable default argument in '{node.name}'")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    # PLP004
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.report(node, "PLP004", "print found")
        self.generic_visit(node)

    # PLP005
    def visit_Compare(self, node):
        for op, right in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant) and right.value is None:
                self.report(node, "PLP005", "comparison to None: use 'is' or 'is not'")
                break                                # one finding per comparison
        self.generic_visit(node)


def _suppressed(lines, finding):
    if not 1 <= finding.line <= len(lines):
        return False
    noqa = NOQA_RE.search(lines[finding.line - 1])
    if noqa is None:
        return False
    if noqa.group(1) is None:                        # bare "# noqa": everything on the line
        return True
    return finding.code in {code.strip() for code in noqa.group(1).split(",")}


def lint(source, select=None):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [Finding(error.lineno or 1, error.offset or 1, "PLP000", f"syntax error: {error.msg}")]
    checker = Checker()
    checker.visit(tree)
    checker.finish(tree)
    selected = set(ALL_CODES if select is None else select)
    lines = source.splitlines()
    return sorted(
        f for f in checker.findings
        if f.code in selected and not _suppressed(lines, f)
    )


def format_finding(path, finding):
    return f"{path}:{finding.line}:{finding.col}: {finding.code} {finding.message}"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="minilint", description="A tiny Python linter.")
    parser.add_argument("files", nargs="+")
    parser.add_argument("--select", help="comma-separated rule codes, e.g. PLP001,PLP004")
    args = parser.parse_args(argv)
    select = [code.strip() for code in args.select.split(",")] if args.select else None

    count = 0
    for path in args.files:
        with open(path, encoding="utf-8") as file:
            findings = lint(file.read(), select)
        for finding in findings:
            print(format_finding(path, finding))
        count += len(findings)
    print(f"Found {count} problem(s)." if count else "All checks passed.")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
