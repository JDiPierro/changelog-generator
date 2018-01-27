# Changelog Generator

Avoid changelog related merge conflicts by having a separate file for each set of pending changes.

## Usage

During your development process add yaml files to the `changelogs` folder.

During your build process you can use our docker image to generate your changelog:

Jenkinsfile example:
```groovy
stage("Update changelog") {
    sh "docker run --rm --mount src="$(pwd)",target=/project,type=bind jdipierro/yamlclog:0.1.0 ${version} --save --cleanup"
    sh "git add -A changelogs/"
    sh "git add CHANGELOG.md"
    sh "git commit -m 'Jenkins updated changelog for version ${version}'"
    sh "git push origin"
}
```

The generator is only a single file so you could also pull it into your own codebase and run it directly:

```bash
python generate_changelog.py ${version} --save --cleanup
```


### Changelog Files

All files in the `changelogs` directory that end in `.yml` or `.yaml` will be pulled into the generated changelog. The name of the file is not used.

Each file should define a dictionary with at least one key containing a list or dictionary. Top level keys should be one of `['added', 'fixed', 'changed', 'deprecated', 'removed', 'security']`. More information on when to use each is available at [KeepAChangelog](http://keepachangelog.com).

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
