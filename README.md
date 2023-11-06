# Cortex CLI

**cortexapps-cli** implements a command line interface for cortexapps.

# Installation

## pypi.org
The cortexapps-cli package is published to [pypi.org](https://pypi.org/project/cortexapps-cli/).  Refer
to the instructions there to install using [pip](https://pypi.org/project/pip/).

## homebrew
The package will be published to homebrew in the future, but we need your help!

In order to be accepted to [homebrew-core](https://github.com/Homebrew/homebrew-core), a repository has to be 'notable'. This
is determined by running an [audit](https://docs.brew.sh/Adding-Software-to-Homebrew#testing-and-auditing-the-formula)
of the homebrew formula.  Currently, this results in the following:

```
brew audit --strict --new-formula --online cortexapps-cli
cortexapps-cli
  * GitHub repository not notable enough (<30 forks, <30 watchers and <75 stars)
Error: 1 problem in 1 formula detected.
```

Please help us by watching and starring https://github.com/cortexapps/cli.  Once we're 'notable', we'll
throw a small party for ourselves and then submit a PR to homebrew-core.

### Workaround for installing via local homebrew formula
This is a temporary solution until we reach 'notable' status and get the formula added to [homebrew-core](https://github.com/Homebrew/homebrew-core).

Run the following commands to download the homebrew formula from this repo into your local homebrew tap:

```
curl -L -H "Accept: application/vnd.github.VERSION.raw" -o $(brew --repository)/Library/Taps/homebrew/homebrew-core/Formula/c/cortexapps-cli.rb https://api.github.com/repos/cortexapps/cli/contents/homebrew/cortexapps-cli.rb
HOMEBREW_NO_INSTALL_FROM_API=1 brew install --build-from-source cortexapps-cli
```

# Usage

## Config file
The CLI requires an API key for all operations.  This key is stored in a config file whose default location is `~/.cortex/config`.
This path can be overridden with the `-c` flag.

Minimal contents of the file:
```
[default]
api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
```

If you have multiple Cortex instances, you can create a section for each, for example:
```
[default]
api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY

[my-test]
api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
base_url = https://app.cortex.mycompany.com
```

**NOTE:** if not supplied, base_url defaults to https://app.getcortexapp.com

The CLI will retrieve configuration data from the `[default]` section unless you pass the `-t/--tenant` flag.

For example, to list all entities in the my-test tenant, run the following command:
```
cortex -t my-test catalog list
```

If the config file does not exist, the CLI will prompt you to create it.

## Commands
Run `cortex -h` to see a list of all commands.

Run `cortex <subcommand> -h` to see a list of all commands for each subcommand.

For example:
```
$ cortex audit-logs -h
usage: cortex CLI audit-logs [-h] {get} ...

positional arguments:
  {get}       audit logs help
    get       retrieve audit logs

options:
  -h, --help  show this help message and exit
```
