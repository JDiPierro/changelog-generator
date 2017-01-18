import unittest2
from changelog_generator import Changeset
from changelog_generator.changeset import CHANGELOG_SECTIONS
from os import path


class ChangelogGeneratorTests(unittest2.TestCase):
    test_dir = path.dirname(path.realpath(__file__))

    def _add_file(self, sample_name):
        self.changes.add_file("{}/changelogs/{}.yml".format(self.test_dir, sample_name))

    def setUp(self):
        self.changes = Changeset(self.test_dir, "1.0.0", "TestChanges")

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



