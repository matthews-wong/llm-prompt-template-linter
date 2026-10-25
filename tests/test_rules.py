import unittest

from promptlint.rules import lint
from promptlint.template import parse

GOOD = """---
name: ask
version: 0.1.0
variables: [question, context]
untrusted: [context]
---
Answer {{question}}.
<context>
{{context}}
</context>
"""


def codes(path, text):
    return sorted(f.code for f in lint(parse(path, text)))


class RuleTests(unittest.TestCase):
    def test_clean_template_has_no_findings(self):
        self.assertEqual(codes("ask.prompt", GOOD), [])

    def test_missing_header(self):
        self.assertEqual(codes("ask.prompt", "Hello {{x}}"), ["PL001"])

    def test_unterminated_header_counts_as_missing(self):
        self.assertEqual(codes("ask.prompt", "---\nname: ask\nbody"), ["PL001"])

    def test_bad_version(self):
        self.assertEqual(codes("ask.prompt", GOOD.replace("0.1.0", "1.0")), ["PL002"])

    def test_name_must_match_file(self):
        self.assertEqual(codes("other.prompt", GOOD), ["PL003"])

    def test_undeclared_and_unused_variables(self):
        text = GOOD.replace("{{question}}", "{{topic}}")
        self.assertEqual(codes("ask.prompt", text), ["PL004", "PL005"])

    def test_unbalanced_braces(self):
        self.assertIn("PL006", codes("ask.prompt", GOOD + "{{oops"))

    def test_untrusted_must_be_delimited(self):
        text = GOOD.replace("<context>\n", "").replace("\n</context>", "")
        self.assertEqual(codes("ask.prompt", text), ["PL007"])

    def test_finding_message_names_the_variable(self):
        text = GOOD.replace("{{question}}", "{{topic}}")
        messages = [f.message for f in lint(parse("ask.prompt", text))]
        self.assertTrue(any("'topic'" in m for m in messages))
