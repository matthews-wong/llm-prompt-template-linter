"""Lint rules. Each check returns a list of Finding."""
import os
import re
from dataclasses import dataclass

from .template import Template

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
DELIMITER_TAG = re.compile(r"<([A-Za-z_][\w-]*)>\s*\{\{\s*{var}\s*\}\}\s*</\1>")


@dataclass(frozen=True)
class Finding:
    path: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.code} {self.message}"


def check_header(t: Template) -> list:
    if not t.has_header:
        return [Finding(t.path, "PL001", "missing header (--- fenced block)")]
    findings = [
        Finding(t.path, "PL001", f"header has no '{key}'")
        for key in ("name", "version")
        if key not in t.meta
    ]
    version = t.meta.get("version")
    if version is not None and not SEMVER.match(version):
        findings.append(Finding(t.path, "PL002", f"version '{version}' is not MAJOR.MINOR.PATCH"))
    name = t.meta.get("name")
    stem = os.path.splitext(os.path.basename(t.path))[0]
    if name is not None and name != stem:
        findings.append(Finding(t.path, "PL003", f"name '{name}' does not match file '{stem}'"))
    return findings


def check_variables(t: Template) -> list:
    if not t.has_header:
        return []
    findings = [
        Finding(t.path, "PL004", f"variable '{v}' is used but not declared")
        for v in t.used
        if v not in t.declared
    ]
    findings += [
        Finding(t.path, "PL005", f"variable '{v}' is declared but never used")
        for v in t.declared
        if v not in t.used
    ]
    return findings


def check_braces(t: Template) -> list:
    if t.body.count("{{") == t.body.count("}}"):
        return []
    return [Finding(t.path, "PL006", "unbalanced '{{' and '}}'")]


def check_untrusted(t: Template) -> list:
    return [
        Finding(t.path, "PL007", f"untrusted variable '{v}' is not wrapped in a tag")
        for v in t.untrusted
        if not re.search(DELIMITER_TAG.pattern.replace("{var}", re.escape(v)), t.body)
    ]


CHECKS = (check_header, check_variables, check_braces, check_untrusted)


def lint(t: Template) -> list:
    return [finding for check in CHECKS for finding in check(t)]
