from __future__ import annotations

import json
import unittest

from right_tool.cli import find_matches, load_registry, resolve_system


class LookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry()

    def top_system(self, query: str) -> str:
        matches = find_matches(self.registry, query, limit=1)
        self.assertTrue(matches, query)
        self.assertTrue(matches[0]["recommendations"], query)
        return matches[0]["recommendations"][0]["system"]["id"]

    def test_worklist_routes_to_souffle(self):
        self.assertEqual(
            self.top_system("worklist propagation until convergence"),
            "souffle",
        )

    def test_csharp_semantics_routes_to_roslyn(self):
        self.assertEqual(
            self.top_system("c# symbols semantic model overload resolution"),
            "roslyn",
        )

    def test_config_overlay_routes_to_cue(self):
        self.assertEqual(
            self.top_system("yaml schema defaults overlay validation"),
            "cue",
        )

    def test_mixed_document_extraction_routes_to_tika(self):
        self.assertEqual(
            self.top_system("heterogeneous office pdf email extraction"),
            "apache-tika",
        )

    def test_document_conversion_routes_to_pandoc(self):
        self.assertEqual(
            self.top_system("convert markdown docx latex epub"),
            "pandoc",
        )

    def test_show_alias_resolves_tla(self):
        system = resolve_system(self.registry, "TLA+")
        self.assertIsNotNone(system)
        self.assertEqual(system["id"], "tla-plus")

    def test_json_serializable(self):
        result = find_matches(self.registry, "symbolic exact oracle", limit=3)
        json.dumps(result)

    def test_unknown_query_returns_no_matches(self):
        self.assertEqual(find_matches(self.registry, "flibbertigibbet", limit=5), [])


if __name__ == "__main__":
    unittest.main()
