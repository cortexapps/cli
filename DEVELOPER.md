# Cortex CLI Developer guide

# Testing
The CLI uses [just](https://just.systems/man/en/) for automation operations.
Just is a make alternative that aims to remove make's complexities and just be
a command runner.

To test the full project:
```
just test-all
```

Run just to see a list of possible recipes.
```
$ just
Available recipes:
    help
    test testname # Run a single test, ie: just test tests/test_catalog.py
    test-all      # Run all tests
    test-import   # Run import test, a pre-requisite for any tests that rely on test data.
```

# Commit messages
The CLI uses [git-changelog](https://pypi.org/project/git-changelog/) to dynamically generate
the [HISTORY.md](./HISTORY.md) file.

Prefix commits with the words listed in the [Basic convention](https://pawamoy.github.io/git-changelog/usage/#basic-convention)
section of the git-changelog documentation.

Commits that don't use one of these words will be ignored when generating the history.

This project will use the following:
- add
- fix
- change
- remove

# Build process
- Create a feature branch for all changes.
- Merge feature branch to staging branch.
- Multiple changes can be merged to staging and included in a push to main or the single change can be merged to main.
- The merge to main will trigger a new version to be created.
- Versions are automatically bumped using [github-tag-action](https://github.com/anothrNick/github-tag-action).
  - Bumping is based on the merge commit message, defaulting to bumping the patch version.
  - To bump the minor version, use "#minor" in the commit message.
  - To bump the major version, use "#major" in the commit message.
- Merge to main triggers the [publish](https://github.com/cortexapps/cli/actions/workflows/publish.yml) GitHub Actions workflow.

# Updating Poetry dependencies
To update poetry dependencies run:
```
poetry update
poetry lock
```

Commit these files.

TODO: see how other python projects keep dependencies up to date.  It probably makes sense to run this on an
automated basis every 30 days or so to ensure the project is up-to-date and contains available security and
vulnerability fixes.

# Security

# Updating the homebrew recipe
TODO
