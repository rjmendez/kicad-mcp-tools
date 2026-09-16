import os
import unittest
from pathlib import Path

from kicad_mcp_tools import (
    Atom,
    atomic_write,
    classify_kicad_report,
    demo,
    generate_electrode_connector_footprint,
    generate_pin_header_footprint,
    parse,
    serialize,
)
from kicad_mcp_tools.mcp_server import (
    classify_drc_report,
    generate_pin_header_footprint as generate_pin_header_footprint_tool,
    mcp,
    parse_kicad_sexpr,
    roundtrip_kicad_sexpr,
)

class KicadSexprCstTests(unittest.TestCase):
    def test_round_trip_preserves_bytes(self):
        sample = (
            b"(kicad_pcb\r\n"
            b'\t(version 20250316)\r\n'
            b'\t(generator "mycomidi")\r\n'
            b'\t(gr_text "A \\"quoted\\" label" (at 10 20))\r\n'
            b")\r\n"
        )
        self.assertEqual(serialize(parse(sample)), sample)

    def test_atom_set_text_preserves_kicad_escape_rules(self):
        atom = Atom(b"x")
        atom.set_text('hello "kicad"\nworld')
        self.assertEqual(atom.text, 'hello "kicad"\nworld')
        self.assertNotIn(b"\n", atom.raw)

    def test_demo_self_check_runs(self):
        demo()


class AtomicWriteTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(__file__).resolve().parent / f"_atomic_write_{os.getpid()}.txt"
        self.addCleanup(lambda: self.path.unlink(missing_ok=True))

    def test_atomic_write_creates_new_file(self):
        atomic_write(self.path, "alpha")
        self.assertEqual(self.path.read_text(encoding="utf-8"), "alpha")

    def test_atomic_write_replaces_existing_contents(self):
        self.path.write_text("before", encoding="utf-8")
        atomic_write(self.path, b"after")
        self.assertEqual(self.path.read_bytes(), b"after")


class DrcClassificationTests(unittest.TestCase):
    def test_distinguishes_clean_findings_and_malformed_drc(self):
        clean = classify_kicad_report({"violations": [], "unconnected_items": []})
        findings = classify_kicad_report(
            '{"violations":[{"type":"clearance"}],"unconnected_items":[]}'
        )
        malformed = classify_kicad_report({"violations": "not-a-list"})

        self.assertEqual(clean.status, "clean")
        self.assertEqual(clean.report_kind, "drc")
        self.assertEqual(findings.status, "findings")
        self.assertEqual(findings.report_kind, "drc")
        self.assertEqual(malformed.status, "malformed")
        self.assertEqual(malformed.error, "Report field 'violations' must be a list.")

    def test_distinguishes_clean_findings_and_malformed_erc(self):
        clean = classify_kicad_report(
            {
                "$schema": "https://schemas.kicad.org/erc.v1.json",
                "sheets": [{"path": "/", "violations": []}],
            }
        )
        findings = classify_kicad_report(
            {
                "$schema": "https://schemas.kicad.org/erc.v1.json",
                "sheets": [{"path": "/", "violations": [{"severity": "error"}]}],
            }
        )
        malformed = classify_kicad_report(
            {
                "$schema": "https://schemas.kicad.org/erc.v1.json",
                "sheets": [{"path": "/", "violations": [None]}],
            }
        )

        self.assertEqual(clean.status, "clean")
        self.assertEqual(clean.report_kind, "erc")
        self.assertEqual(findings.status, "findings")
        self.assertEqual(findings.report_kind, "erc")
        self.assertEqual(malformed.status, "malformed")
        self.assertIn("non-object violation entry", malformed.error)

    def test_none_input_is_unavailable(self):
        result = classify_kicad_report(None)
        self.assertEqual(result.status, "unavailable")


class PinHeaderGeneratorTests(unittest.TestCase):
    def _assert_balanced_and_parseable(self, text: str, expected_pad_count: int):
        self.assertEqual(text.count("("), text.count(")"))
        tree = parse(text.encode("utf-8"))
        footprint = tree.lists[0]
        self.assertEqual(footprint.head, "footprint")
        self.assertEqual(len(footprint.find_all("pad")), expected_pad_count)

    def test_generate_pin_header_4_and_8_pin_footprints(self):
        four_pin = generate_pin_header_footprint(4)
        eight_pin = generate_pin_header_footprint(8)
        self._assert_balanced_and_parseable(four_pin, 4)
        self._assert_balanced_and_parseable(eight_pin, 8)

    def test_generate_electrode_connector_uses_channel_count(self):
        footprint = generate_electrode_connector_footprint(4)
        self.assertIn("MycoMIDI_Electrode_1x04_2.54mm", footprint)
        self._assert_balanced_and_parseable(footprint, 4)


class McpServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_are_registered(self):
        tools = await mcp.list_tools()
        self.assertTrue(
            {
                "parse_kicad_sexpr",
                "roundtrip_kicad_sexpr",
                "classify_drc_report",
                "generate_pin_header_footprint",
            }.issubset({tool.name for tool in tools})
        )

    def test_parse_tool_returns_structured_tree(self):
        result = parse_kicad_sexpr('(footprint "Demo")')
        self.assertEqual(result["kind"], "doc")
        self.assertEqual(result["children"][0]["head"], "footprint")

    def test_roundtrip_and_classification_tools_work_directly(self):
        sample = '(kicad_pcb (version 20250316))'
        roundtrip = roundtrip_kicad_sexpr(sample)
        classification = classify_drc_report('{"violations":[],"unconnected_items":[]}')

        self.assertTrue(roundtrip["round_trip_equal"])
        self.assertEqual(roundtrip["serialized_text"], sample)
        self.assertEqual(classification["status"], "clean")
        self.assertEqual(classification["report_kind"], "drc")

    def test_footprint_tool_returns_parseable_footprint(self):
        footprint = generate_pin_header_footprint_tool(4, 2.54)
        self.assertIn('footprint "PinHeader_1x04_2.54mm"', footprint)
        self.assertEqual(parse(footprint.encode("utf-8")).lists[0].head, "footprint")


if __name__ == "__main__":
    unittest.main()
