[![PyPi version](https://badgen.net/pypi/v/cortexapps-cli/)](https://pypi.org/project/cortexapps-cli)
[![PyPI download month](https://img.shields.io/pypi/dm/cortexapps-cli.svg)](https://pypi.python.org/pypi/cortexapps-cli/)
[![PyPI license](https://img.shields.io/pypi/l/cortexapps-cli.svg)](https://pypi.python.org/pypi/cortexapps-cli/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/cortexapps-cli.svg)](https://pypi.python.org/pypi/cortexapps-cli/)
![publish](https://github.com/cortexapps/cli/actions/workflows/publish-pypi.yml/badge.svg)

# Cortex CLI

**cortexapps-cli** implements a command line interface for [cortexapps](https://cortex.io).

# Installation

## pypi.org

```
pip install cortexapps-cli
```

Using a python virtual environment:
```
VENV_DIR=~/.venv/cortex
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install cortexapps-cli
```

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
Run `cortex -h` to see a list of all commands:
```
usage: cortex CLI [-h] [-a] [-c CONFIG] [-d] [-n] [-t] [-v]
                  {audit-logs,backup,catalog,custom-data,custom-events,dependencies,deploys,discovery-audit,docs,groups,integrations,ip-allowlist,on-call,packages,plugins,queries,resource-definitions,scorecards,teams-hierarchies,teams}
                  ...

Cortex command line interface

positional arguments:
  {audit-logs,backup,catalog,custom-data,custom-events,dependencies,deploys,discovery-audit,docs,groups,integrations,ip-allowlist,on-call,packages,plugins,queries,resource-definitions,scorecards,teams-hierarchies,teams}
                        sub-command help
    audit-logs          audit log commands
    backup              import/export commands
    catalog             catalog commands
    custom-data         custom_data actions
    custom-events       custom events actions
    dependencies        dependencies commands
    deploys             deploys commands
    discovery-audit     Discovery Audit commands
    docs                OpenAPI doc commands
    groups              groups commands
    integrations        integrations sub-commands
    ip-allowlist        IP Allowlist information
    on-call             get on-call information
    packages            commands to create and modify packages
    plugins             commands to create and access plugins
    queries             run CQL queries
    resource-definitions
                        resource definitions
    scorecards          scorecards API requests
    teams-hierarchies   commands to create and modify team hierarchies
    teams               commands to create and modify teams

options:
  -h, --help            show this help message and exit
  -a , --cliAlias       get CLI parms from [TENANT.aliases] in config file
  -c CONFIG, --config CONFIG
                        Config location, default = ~/.cortex/config
  -d, --debug           Writes request debug information as JSON to stderr
  -n, --noObfuscate     Do not obfuscate bearer token when debugging
  -t , --tenant         tenant name defined in ~/.cortex/config, defaults to 'default'
  -v, --version         show program's version number and exit

Type 'man cortex' for additional details.
```

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

# Examples

Almost all CLI responses return JSON or YAML.  Tools like [jq](https://jqlang.github.io/jq/) and [yq](https://mikefarah.gitbook.io/yq/) will be helpful to extract content from these responses.

## Export from one tenant; import into another

This example shows how to export from a tenant named `myTenant-dev` and import those contents into a tenant
named `myTenant`.

Your cortex config file will require api keys for both tenants.  It would look like this:
```
[myTenant]
api_key = <your API Key for myTenant>

[myTenant-dev]
api_key = <your API Key for myTenant-dev>
``` 

**Export**
```
$ cortex -t myTenant-dev backup export
Getting resource definitions
-->  my-resource-1
Getting catalog entities
-->  my-domain-1
-->  my-service-1
-->  my-service-2
Getting IP Allowlist definitions
Getting scorecards
-->  my-scorecard-1
Getting teams
-->  my-team-1
-->  my-team-2

Export complete!
Contents available in /Users/myUser/.cortex/export/2023-11-19-14-58-14
```

**Import**
```
$ cortex backup import -d <directory created by export>
```

**NOTE:** some content will not be exported, including integration configurations and resources that
are automatically imported by Cortex.  Cortex does not have access to any keys, so it cannot export any
integration configurations.

# Iterate over all domains
```
for domain in `cortex catalog list -t domain | jq -r ".entities[].tag" | sort`; do echo "domain = $domain"; done
```

# Iterate over all teams
```
for team in `cortex catalog list -t team | jq -r ".entities[].tag" | sort`; do echo "team = $team"; done
```

# Iterate over all services
```
for service in `cortex catalog list -t service | jq -r ".entities[].tag" | sort`; do echo "service = $service"; done
```

# Get git details for a service
```
cortex catalog details -t my-service-1 | jq ".git"
```

```
{
  "repository": "my-org/my-service-1",
  "alias": null,
  "basepath": null,
  "provider": "github"
}
```

# Add a suffix to all x-cortex-tag values for services
```
for service in `cortex catalog list -t service | jq -r ".entities[].tag" | sort`; do
   echo "service = $service"
   cortex catalog descriptor -y -t ${service} | yq '.info.x-cortex-tag |= . + "-suffix"' | cortex catalog create -f-
done
```

This example combines several CLI commands:
- the for loop iterates over all services
- the descriptor for each service is retrieved in YAML format
- the YAML descriptor is piped to yq where the value of `x-cortex-tag` is retrieved and modified to add "-suffix" to the end
- the modified YAML is then piped to the cortex catalog command to update the entity in cortex

**NOTE:** Any cortex commands that accept a file as input can also receive input from stdin by specifying a "-" after the -f
parameter.
