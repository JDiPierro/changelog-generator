import unittest2
from changelog_generator.generate_changelog import Changeset, CHANGELOG_SECTIONS
from os import path
from freezegun import freeze_time


class ChangelogGeneratorTests(unittest2.TestCase):
    test_dir = path.dirname(path.realpath(__file__))

    def _add_file(self, sample_name):
        self.changes.add_file("{}/changelogs/{}.yml".format(self.test_dir, sample_name))

    def setUp(self):
        test_changelogs_dir = "{}/changelogs".format(self.test_dir)
        self.changes = Changeset(test_changelogs_dir, "1.0.0", "TestChanges")

    def test_full(self):
        self.changes.project_dir = self.test_dir
        self.changes.generate()

        with open("{}/changelogs/rendered".format(self.test_dir)) as full_output_file:
            expectation = full_output_file.read().strip()

        with freeze_time("2017-01-18"):
            self.assertEqual(self.changes.render(), expectation)

    def test_basic_yaml_loading(self):
        self._add_file("basic")

        self.assertEqual(len(self.changes.added), 2, "Not all additions were parsed.")
        self.assertEqual(len(self.changes.changed), 3, "Not all changes were parsed.")

    def test_sections_case_insensitive(self):
        for section in CHANGELOG_SECTIONS:
            section_upper = str.upper(section)
            self.changes.add({section_upper: ["Foo"]})

            result = getattr(self.changes, section)
            self.assertEqual(len(result), 1, "'{}' not parsed.".format(section_upper))
            self.assertEqual(result[0], "Foo")

    def test_dict_parsing(self):
        change_input = {
            "added": {
                "Foo": ["bar", "baz"]
            }
        }
        self.changes.add(change_input)

        self.assertEqual(len(self.changes.added), 2, "Subsection list not parsed correctly")
        self.assertEqual(self.changes.added[0], {'Foo': 'bar'})
        self.assertEqual(self.changes.added[1], {'Foo': 'baz'})

    def test_sorting(self):
        change_input = {
            "added": {
                "B": "bar",
                "C": ["foo", "laf"],
                "A": ["baz"],
            }
        }
        self.changes.add(change_input)
        self.changes._sort()

        self.assertEqual(self.changes.added[0].keys()[0], "A")
        self.assertEqual(self.changes.added[1].keys()[0], "B")
        self.assertEqual(self.changes.added[2].keys()[0], "C")
        self.assertEqual(self.changes.added[3].keys()[0], "C")
