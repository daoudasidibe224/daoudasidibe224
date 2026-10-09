import unittest
import xml.etree.ElementTree as ET

from profile_assets import parse_calendar, activity, banner


class CalendarTests(unittest.TestCase):
    def test_counts_match_their_own_dates(self):
        source = '''<td data-date="2026-10-01" id="d1"></td>
        <td data-date="2026-10-02" id="d2"></td>
        <td data-date="2026-10-03" id="d3"></td>
        <tool-tip for="d3">1 contribution on October 3rd.</tool-tip>
        <tool-tip for="d1">1,024 contributions on October 1st.</tool-tip>
        <tool-tip for="d2">No contributions on October 2nd.</tool-tip>'''
        self.assertEqual(parse_calendar(source), {"2026-10-01": 1024, "2026-10-02": 0, "2026-10-03": 1})

    def test_missing_or_changed_markup_does_not_fabricate_counts(self):
        for source in ('<html>rate limited</html>', '<td data-date="2026-10-01" id="d1"></td>'):
            with self.assertRaises(ValueError):
                parse_calendar(source)

    def test_assets_are_valid_and_expose_verified_values(self):
        data = {"updated": "2026-10-09", "year": 2026, "year_contributions": 467,
                "public_repositories": 8, "days": [{"date": "2026-10-09", "count": 4}]}
        for theme in ("dark", "light"):
            ET.fromstring(banner(theme))
            root = ET.fromstring(activity(data, theme))
            self.assertIn('467 contributions en 2026', ''.join(root.itertext()))
            self.assertIn('2026-10-09 : 4 contributions', ''.join(root.itertext()))


if __name__ == '__main__':
    unittest.main()
