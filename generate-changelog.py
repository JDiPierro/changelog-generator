#!/usr/bin/env python

import argparse
from os import path
from changelog_generator import Changeset


def main():
    parser = argparse.ArgumentParser(description='Changelog Generator')
    parser.add_argument('version_num')
    parser.add_argument('version_codename', nargs='?')
    parser.add_argument('--save', action='store_true',
                        help='Save the generated changelog out to the top level CHANGELOG.md')
    parser.add_argument('--cleanup', action='store_true',
                        help='Remove yaml files when finished. Only has an effect when used with --save')

    cli_args = parser.parse_args()

    scriptdir = path.dirname(path.realpath(__file__))
    if 'changelogs/generator' not in scriptdir:
        raise Exception("This script should be located at 'PROJECT_DIR/changelogs/generator/generate.py'")
    project_dir = scriptdir[0:str.find(scriptdir, 'changelogs')]

    # Generate changelog section
    changes = Changeset(project_dir, cli_args.version_num, cli_args.version_codename)
    changes.generate()
    print "{}\n\n".format(changes.render())

    if cli_args.save:
        changes.save()
        print "CHANGELOG.md updated"
        if cli_args.cleanup:
            changes.cleanup()
            print "Yaml files deleted"

if __name__ == "__main__":
    main()
