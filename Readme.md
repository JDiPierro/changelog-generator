# Changelog Generator

Avoid changelog related merge conflicts by having a separate file for each set of pending changes.

## Usage

Register this repository as a submodule of your project located at `${project_root}/changelogs/generator`

`git submodule add git@github.com:ConduceInc/changelog-generator.git changelogs/generator`

During your development process add yaml files to the `changelogs` folder.

During your build process call the generator with the `--save` and `--cleanup` flags:

Jenkinsfile example:
```groovy
stage("Update changelog") {
    sh "python changelogs/generator/generate-changelog.py ${version} --save --cleanup"
    sh "git add -A changelogs/"
    sh "git add CHANGELOG.md"
    sh "git commit -m 'Jenkins updated changelog for version ${version}'"
    sh "git push origin"
}
```

Now you're keeping a changelog!

## Changelog Files

All files in the `changelogs` directory that end in `.yml` or `.yaml` will be pulled into the generated changelog. The name of the file is not used.

Each file should define a dictionary with at least one key containing a list or dictionary. Top level keys should be one of `['added', 'fixed', 'changed', 'deprecated', 'removed']`. More information on when to use each is available at [KeepAChangelog](http://keepachangelog.com).

```yaml
added:
  - Cool new features
fixed:
  - A **nasty** bug
```

This renders out to:

```markdown
## Added
- Cool New Features

## Fixed
- A **nasty** bug
```


Both lists and dictionaries are supported under the top-level keys. Second-level dictionaries can contain strings or lists.

```yaml
added:
  Lorem:
    - ipsum
    - dolor
changed:
  sit: amet
deprecated:
  - consectetur: adipiscing
  - elit: sed
```

This would render out as:

```markdown
## Added
- Lorem: ipsum
- Lorem: dolor

## Changed
- sit: amet

## Deprecated
- consectetur: adipiscing
- elit: sed
```
