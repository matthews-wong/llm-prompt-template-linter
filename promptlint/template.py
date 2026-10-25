"""Parse a prompt template file into a header and a body."""
import re
from dataclasses import dataclass

VARIABLE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
HEADER_FENCE = "---"


@dataclass(frozen=True)
class Template:
    path: str
    meta: dict
    body: str
    has_header: bool

    @property
    def declared(self) -> list:
        return _as_list(self.meta.get("variables", ""))

    @property
    def untrusted(self) -> list:
        return _as_list(self.meta.get("untrusted", ""))

    @property
    def used(self) -> list:
        return list(dict.fromkeys(VARIABLE.findall(self.body)))


def _as_list(raw: str) -> list:
    return [item.strip() for item in raw.strip("[] ").split(",") if item.strip()]


def parse(path: str, text: str) -> Template:
    lines = text.splitlines()
    if not lines or lines[0].strip() != HEADER_FENCE:
        return Template(path, {}, text, has_header=False)
    meta = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == HEADER_FENCE:
            body = "\n".join(lines[index + 1:])
            return Template(path, meta, body, has_header=True)
        key, _, value = line.partition(":")
        if value:
            meta[key.strip()] = value.strip()
    # An unterminated header is treated as no header: the whole file is body.
    return Template(path, {}, text, has_header=False)
