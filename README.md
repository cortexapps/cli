# Cortex CLI

**cortexapps-cli** implements a command line interface for cortexapps.

## Cortex CLI is in alpha

Cortex CLI is currently in alpha test mode while we work out installation
and configuration issues with our alpha testsers.  It is not offically
supported by Cortex.

## Installing Cortex CLI

Cortex CLI is available on PyPI:

```console
$ python -m pip install cortexapps-cli
```

Alternatively, in a venv environment:
```
VENV_DIR = /tmp/cortex # this can be any writable directory
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
