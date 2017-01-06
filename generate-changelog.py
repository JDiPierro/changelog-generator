#!/usr/bin/env python
import yaml
import argparse
from glob import iglob
from jinja2 import Template
from datetime import date
from os import remove as delete_file
from os import path

CHANGELOG_SECTIONS = ['added', 'changed', 'fixed', 'deprecated', 'removed']
CHANGELOG_TEMPLATE = Template("""
{%- macro section(possible_changes, title) %}
{%- if possible_changes is defined and possible_changes|length > 0 %}
## {{ title }}
{{ possible_changes }}
{%- endif %}{%- endmacro %}

# {{ version_num }}{% if version_codename is defined %} "{{ version_codename }}"{%- endif %} - {{ release_date }}
{{- section(added, "Added") }}
{{- section(changed, "Changed") }}
{{- section(fixed, "Fixed") }}
{{- section(deprecated, "Deprecated") }}
{{- section(removed, "Removed") }}
""")


class Changes:
    def __init__(self, version_num, version_codename):
        scriptdir = path.dirname(path.realpath(__file__))
        if 'changelogs' not in scriptdir:
            raise Exception("This script should be located at 'PROJECT/changelogs/generator/generate-changelog.py'")
        self.base_dir = scriptdir[0:str.find(scriptdir, 'changelogs')]
        self.version_num = version_num
        self.version_codename = version_codename
        self.input_files = []
        self.added = []
        self.changed = []
        self.fixed = []
        self.deprecated = []
        self.removed = []
        self._rendered = None

        # Start the Engines!
        self.generate()

    def generate(self):
        """ Process each yaml file in the top-level 'changelogs' directory """
        glob_pattern = '{}/changelogs/*.y*ml'.format(self.base_dir)
        for clog_path in iglob(glob_pattern):
            self.input_files.append(clog_path)
            with open(clog_path) as clog_file:
                clog_dict = yaml.load(clog_file)
            self.add(clog_dict)

    def add(self, clog_dict):
        """ Add a set of changes """
        for clog_section in clog_dict.keys():
            section = str.lower(clog_section)
            if section not in CHANGELOG_SECTIONS:
                raise Exception(
                    "Don't know what to do with changelog section '{}'. Valid sections are: {}".format(
                        clog_section, CHANGELOG_SECTIONS
                    ))
            section_changes = getattr(self, section)
            section_changes += self._parse_section(clog_dict.get(section))
            setattr(self, section, section_changes)

    @staticmethod
    def _parse_section(clog_section_yaml):
        """ Transform the section for display if necessary """
        if clog_section_yaml is None:
            # Nothing provided for this section
            return []
        if isinstance(clog_section_yaml, list):
            # Print it as it is
            return clog_section_yaml
        if not isinstance(clog_section_yaml, dict):
            raise Exception("Error in this section: \n{}".format(clog_section_yaml))

        # Convert a subsections into a list of dicts so each line displays as "subsection: change"
        section_changes = []
        for subsection, changes in clog_section_yaml.iteritems():
            if isinstance(changes, list):
                section_changes.extend([{subsection: change} for change in changes])
            else:
                section_changes.append({subsection: changes})
        return section_changes

    def render(self):
        if self._rendered is not None:
            return self._rendered
        yamlfmt = lambda lst: yaml.dump(lst, default_flow_style=False, width=1024)

        # Build the context for the jinja template
        jinja_args = dict(
            release_date=date.today().isoformat(),
            version_num=self.version_num,
        )
        if self.version_codename:
            jinja_args['version_codename'] = self.version_codename

        have_changes = False
        for section in CHANGELOG_SECTIONS:
            section_attr = getattr(self, section)
            if len(section_attr) > 0:
                have_changes = True
                jinja_args[section] = yamlfmt(section_attr)

        if not have_changes:
            raise Exception("No changes found. " +
                            "Please ensure properly formatted yaml files are present in the `changelogs` directory.")

        # Render the jinja template
        self._rendered = CHANGELOG_TEMPLATE.render(**jinja_args).strip()
        return self._rendered

    def save(self):
        # Load old changelog data
        changelog_path = '{}/CHANGELOG.md'.format(self.base_dir)
        with open(changelog_path, 'r') as original_changelog:
            old_changelog = original_changelog.read()

        # Write new data to the top of the file
        with open(changelog_path, 'w') as master_changelog:
            master_changelog.write("{}\n\n{}".format(self.render(), old_changelog))

    def cleanup(self):
        """Delete the files at the specified paths"""
        for input_file in self.input_files:
            delete_file(input_file)


def main():
    parser = argparse.ArgumentParser(description='Changelog Generator')
    parser.add_argument('version_num')
    parser.add_argument('version_codename', nargs='?')
    parser.add_argument('--save', action='store_true',
                        help='Save the generated changelog out to the top level CHANGELOG.md')
    parser.add_argument('--cleanup', action='store_true',
                        help='Remove yaml files when finished. Only has an effect when used with --save')

    cli_args = parser.parse_args()

    # Generate changelog section
    changes = Changes(cli_args.version_num, cli_args.version_codename)
    print "{}\n\n".format(changes.render())

    if cli_args.save:
        changes.save()
        print "CHANGELOG.md updated"
        if cli_args.cleanup:
            changes.cleanup()
            print "Yaml files deleted"

if __name__ == "__main__":
    main()
