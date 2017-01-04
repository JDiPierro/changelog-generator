#!/usr/bin/env python
"""
Conduce Changelog Generator

Usage:
  generate-changelog <version_num> [<version_codename>] [--save]

Options:
  --save    Save the generated changelog out to the top level CHANGELOG.md
"""
import glob
import yaml
from docopt import docopt
from jinja2 import Template
from datetime import date


CHANGELOG_SECTIONS = ['added', 'changed', 'fixed', 'deprecated', 'removed']
CHANGELOG_TEMPLATE = Template("""
# {{ version_num }}{% if version_codename is defined %} "{{ version_codename }}"{%- endif %} - {{ release_date }}

{%- if added is defined and added|length > 0 %}
## Added
{{ added }}
{%- endif %}

{%- if changed is defined and changed|length > 0 %}
## Changed
{{ changed }}
{%- endif %}

{%- if deprecated is defined and deprecated|length > 0 %}
## Deprecated
{{ deprecated }}
{%- endif %}

{%- if fixed is defined and fixed|length > 0 %}
## Fixed
{{ fixed }}
{%- endif %}

{%- if removed is defined and removed|length > 0 %}
## Removed
{{ removed }}
{%- endif %}
""")


class Changes:
    added = []
    changed = []
    fixed = []
    deprecated = []
    removed = []

    def __init__(self, version_num, version_codename):
        self.version_num = version_num
        self.version_codename = version_codename
        self.generate()

    def generate(self):
        """ Process each yaml file in the top-level 'changelogs' directory """
        for clog_path in glob.iglob('../changelogs/*.y*ml'):
            with open(clog_path) as clog_file:
                clog_dict = yaml.load(clog_file)
            self.add(clog_dict)

    @staticmethod
    def _parse_section(clog_section_yaml):
        """ Transform the section for display if necessary """
        if clog_section_yaml is None:
            # Nothing provided for this section
            return []
        if isinstance(clog_section_yaml, list):
            # Print it as it is
            return clog_section_yaml

        # Convert a subsections into a list of dicts so each line displays as "subsection: change"
        section_changes = []
        for subsection, changes in clog_section_yaml.iteritems():
            section_changes.extend([{subsection: change} for change in changes])
        return section_changes

    def add(self, clog_dict):
        """ Add a set of changes """
        for section in CHANGELOG_SECTIONS:
            section_changes = getattr(self, section)
            section_changes += self._parse_section(clog_dict.get(section))
            setattr(self, section, section_changes)

    def render(self):
        yamlfmt = lambda lst: yaml.dump(lst, default_flow_style=False)

        # Build the context for the jinja template
        jinja_args = dict(
            release_date=date.today().isoformat(),
            version_num=self.version_num,
        )
        if self.version_codename:
            jinja_args['version_codename'] = self.version_codename

        for section in CHANGELOG_SECTIONS:
            section_attr = getattr(self, section)
            if len(section_attr) > 0:
                jinja_args[section] = yamlfmt(section_attr)

        # Render the jinja template
        return CHANGELOG_TEMPLATE.render(**jinja_args)


def main():
    cli_args = docopt(__doc__)

    # Generate changelog section
    changes = Changes(cli_args['<version_num>'], cli_args['<version_codename>'])
    new_changes = changes.render()

    if cli_args['--save']:
        # Load old changelog data
        with open("../CHANGELOG.md", 'r') as original_changelog:
            old_changelog = original_changelog.read()

        # Write new data to the top of the file
        with open("../CHANGELOG.md", 'w') as master_changelog:
            master_changelog.write("{}\n\n{}".format(new_changes, old_changelog))
        print "CHANGELOG.md updated"
    else:
        print new_changes

if __name__ == "__main__":
    main()
