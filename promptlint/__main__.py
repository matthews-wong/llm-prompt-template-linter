import argparse
import glob
import os
import sys

from .render import render
from .rules import lint
from .template import parse

EXTENSION = ".prompt"


def load(path: str):
    with open(path, encoding="utf-8") as handle:
        return parse(path, handle.read())


def collect(target: str) -> list:
    if os.path.isdir(target):
        return sorted(glob.glob(os.path.join(target, f"*{EXTENSION}")))
    return [target]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="promptlint")
    parser.add_argument("target", help="a .prompt file or a directory of them")
    parser.add_argument("values", nargs="*", help="name=value pairs, with --render")
    parser.add_argument("--render", action="store_true", help="print the rendered prompt")
    args = parser.parse_args(argv)

    if args.render:
        values = dict(pair.split("=", 1) for pair in args.values)
        try:
            print(render(load(args.target), values))
        except KeyError as error:
            print(error.args[0], file=sys.stderr)
            return 1
        return 0

    paths = collect(args.target)
    if not paths:
        print(f"no {EXTENSION} files under {args.target}", file=sys.stderr)
        return 1
    findings = [f for path in paths for f in lint(load(path))]
    for finding in findings:
        print(finding)
    print(f"{len(paths)} file(s), {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
