"""Render a template with explicit values."""
from .template import VARIABLE, Template


def render(t: Template, values: dict) -> str:
    missing = [v for v in t.used if v not in values]
    if missing:
        raise KeyError(f"{t.path}: no value for variable(s): {', '.join(missing)}")
    return VARIABLE.sub(lambda m: values[m.group(1)], t.body)
