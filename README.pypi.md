# Cortex CLI

**cortexapps-cli** implements a command line interface for cortexapps.

## Installing Cortex CLI

Cortex CLI is available on PyPI:

```console
$ python -m pip install cortexapps-cli
```

Alternatively, in a venv environment:
```
VENV_DIR=~/.venv/cortex
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install cortexapps-cli
cortex -v
```

Cortex CLI officially supports Python 3.7+.

## Configuration
Cortex CLI requires a configuration file that requires, at a minimum, a Cortex API key.

You will be prompted to create a configuration file on the first request:

```
/# cortex catalog list
Cortex CLI config file /root/.cortex/config does not exist.  Create (Y/N)?
Y
Created file: /root/.cortex/config
Edit this file and replace the string 'REPLACE_WITH_YOUR_CORTEX_API_KEY' with the contents
of your Cortex API key and then retry your command.
```

## Help
Run cortex -h to see a list of all commands.

Run cortex <command> -h to see detailed help for each command.

Run cortex <command> <subcommand> -h for detailed help for each subcommand.
