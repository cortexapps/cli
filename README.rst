"""""""""""""""""
Cortexapps CLI
"""""""""""""""""
................................................................
A command-line interface for `Cortexapps <https://cortex.io>`_.
................................................................

.. Contents:: |made-with-python| |PyPI version shields.io| |PyPI download month| |PyPI license| |PyPI pyversions|
   :depth: 3


===================
Installation
===================

----------------------
pypi.org
----------------------

.. code:: bash

  pip install cortexapps-cli


Using a python virtual environment:

.. code:: bash

  VENV_DIR=~/.venv/cortex
  python3 -m venv $VENV_DIR
  source $VENV_DIR/bin/activate
  pip install cortexapps-cli


----------------------
homebrew
----------------------

The package will be published to homebrew in the future, but we need your help!

In order to be accepted to `homebrew-core <https://github.com/Homebrew/homebrew-core>`_, a repository has to be 'notable'. This
is determined by running an `audit <https://docs.brew.sh/Adding-Software-to-Homebrew#testing-and-auditing-the-formula>`_
of the homebrew formula.  Currently, this results in the following:

.. code-block::

  brew audit --strict --new-formula --online cortexapps-cli
  cortexapps-cli
    * GitHub repository not notable enough (<30 forks, <30 watchers and <75 stars)
  Error: 1 problem in 1 formula detected.

Please help us by watching and starring https://github.com/cortexapps/cli.  Once we're 'notable', we'll
throw a small party for ourselves and then submit a PR to homebrew-core. 
 
Workaround for homebrew installation
------------------------------------

This is a temporary solution until we reach 'notable' status and get the formula added to `homebrew-core <https://github.com/Homebrew/homebrew-core>`_.

Run the following commands to download the homebrew formula from this repo into your local homebrew tap:

.. code:: bash
                                                                                                          
  curl -L -H "Accept: application/vnd.github.VERSION.raw" -o $(brew --repository)/Library/Taps/homebrew/homebrew-core/Formula/c/cortexapps-cli.rb https://api.github.com/repos/cortexapps/cli/contents/homebrew/cortexapps-cli.rb
  HOMEBREW_NO_INSTALL_FROM_API=1 brew install --build-from-source cortexapps-cli


===================
 Usage
===================

----------------------
Config file
----------------------

The CLI requires an API key for all operations.  This key is stored in a config file whose default location is `~/.cortex/config`.
This path can be overridden with the `-c` flag.

Minimal contents of the file:

.. code-block::

 [default]
 api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY


If you have multiple Cortex instances, you can create a section for each, for example:

.. code-block::

 [default]
 api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY

 [my-test]
 api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
 base_url = https://app.cortex.mycompany.com

**NOTE:** if not supplied, base_url defaults to :code:`https://app.getcortexapp.com`.

The CLI will retrieve configuration data from the :code:`[default]` section unless you pass the :code:`-t/--tenant` flag.

For example, to list all entities in the :code:`my-test` tenant, run the following command:

.. code:: bash

 cortex -t my-test catalog list


If the config file does not exist, the CLI will prompt you to create it.

----------------------
Environment Variables
----------------------

The CLI supports the following environment variables.  If provided, the Cortex config file will not be read.

- CORTEX_API_KEY
- CORTEX_BASE_URL - this is optional if using Cortex cloud; defaults to `https://app.getcortexapp.com`

Example:

.. code-block::

  export CORTEX_API_KEY=<YOUR_API_KEY>

----------------------
Commands
----------------------

Run :code:`cortex -h` to see a list of all commands:

.. code-block:

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


Run :code:`cortex <subcommand> -h` to see a list of all commands for each subcommand.

For example:

.. code:: bash

 cortex audit-logs -h

.. code-block::

 usage: cortex CLI audit-logs [-h] {get} ...

 positional arguments:
   {get}       audit logs help
     get       retrieve audit logs

 options:
   -h, --help  show this help message and exit


===================
Examples
===================

Almost all CLI responses return JSON or YAML.  Tools like `jq <https://jqlang.github.io/jq/>`_ and `yq <https://mikefarah.gitbook.io/yq/>`_ will be helpful to extract content from these responses.

-------------------------------------------
Export from one tenant; import into another
-------------------------------------------

This example shows how to export from a tenant named :code:`myTenant-dev` and import those contents into a tenant
named :code:`myTenant`.

Your cortex config file will require api keys for both tenants.  It would look like this:

.. code-block::

 [myTenant]
 api_key = <your API Key for myTenant>

 [myTenant-dev]
 api_key = <your API Key for myTenant-dev>


**Export**

.. code:: bash

 cortex -t myTenant-dev backup export

.. code-block::

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

**Import**

.. code:: bash

 cortex -t myTenant backup import -d <directory created by export>


**NOTE:** some content will not be exported, including integration configurations and resources that
are automatically imported by Cortex.  Cortex does not have access to any keys, so it cannot export any
integration configurations.

------------------------
Iterate over all domains
------------------------

.. code:: bash

 for domain in `cortex catalog list -t domain | jq -r ".entities[].tag" | sort`; do echo "domain = $domain"; done

----------------------
Iterate over all teams
----------------------

.. code:: bash

 for team in `cortex catalog list -t team | jq -r ".entities[].tag" | sort`; do echo "team = $team"; done

-------------------------
Iterate over all services
-------------------------

.. code:: bash

 for service in `cortex catalog list -t service | jq -r ".entities[].tag" | sort`; do echo "service = $service"; done

-----------------------------
Get git details for a service
-----------------------------

.. code:: bash

 cortex catalog details -t my-service-1 | jq ".git"

.. code-block::

 {
   "repository": "my-org/my-service-1",
   "alias": null,
   "basepath": null,
   "provider": "github"
 }

----------------------------------------------------
Add a suffix to all x-cortex-tag values for services
----------------------------------------------------

.. code:: bash

 for service in `cortex catalog list -t service | jq -r ".entities[].tag" | sort`; do
    cortex catalog descriptor -y -t ${service} | yq '.info.x-cortex-tag |= . + "-suffix"' | cortex catalog create -f-
 done

This example combines several CLI commands:

- the for loop iterates over all services
- the descriptor for each service is retrieved in YAML format
- the YAML descriptor is piped to yq where the value of :code:`x-cortex-tag` is retrieved and modified to add "-suffix" to the end
- the modified YAML is then piped to the cortex catalog command to update the entity in cortex

**NOTE:** Any cortex commands that accept a file as input can also receive input from stdin by specifying a "-" after the -f
parameter.

--------------------------
Add a group to all domains
--------------------------

.. code:: bash

 for domain in `cortex catalog list -t domain | jq -r ".entities[].tag" | sort`; do
    cortex catalog descriptor -y -t ${domain} | yq -e '.info.x-cortex-groups += [ "my-new-group" ]' | cortex catalog create -f-
 done


---------------------------
Remove a group from domains
---------------------------

.. code:: bash

 for domain in `cortex catalog list -t domain -g my-old-group | jq -r ".entities[].tag" | sort`; do
    cortex catalog descriptor -y -t ${domain} | yq -e '.info.x-cortex-groups -= [ "my-old-group" ]' | cortex catalog create -f-
 done

---------------------------------------
Add a domain parent to a single service
---------------------------------------

.. code:: bash

 cortex catalog descriptor -y -t my-service | yq -e '.info.x-cortex-domain-parents += { "tag": "my-new-domain" }' | cortex catalog create -f-

-------------------------------------------
Add a github group as an owner to a service
-------------------------------------------

.. code:: bash

 cortex catalog descriptor -y -t my-service | yq -e '.info.x-cortex-owners += { "name": "my-org/my-team", "type": "GROUP", "provider": "GITHUB" }' | cortex catalog create -f-

-----------------------------------------------------------------------------
Modify all github basepath values for domain entitities, changing '-' to '_'
-----------------------------------------------------------------------------

.. code:: bash

  for domain in `cortex catalog list -t domain | jq -r ".entities[].tag"`; do 
     cortex catalog descriptor -y -t ${domain} | yq ".info.x-cortex-git.github.basepath |= sub(\"-\", \"_\")" | cortex catalog create -f-
  done

-----------------------------------------------------------------------------
Modify deploys based on selection criteria
-----------------------------------------------------------------------------

This example fixes a typo in the deployment environment field, changing PYPI.org to PyPI.org.

It loops over each selected array element based on the search criteria, removes the uuid attribute (because that is not included in the payload), 
assigns the environment attribute to the correct value and invokes the CLI with that input.

.. code:: bash

  cortex deploys list -t cli > /tmp/deploys.json
  for uuid in `cat /tmp/deploys.json | jq -r '.deployments[] | select(.environment=="PYPI.org") | .uuid'`
  do
     cat /tmp/deploys.json | jq ".deployments[] | select (.uuid==\"${uuid}\") | del(.uuid) | .environment = \"PyPI.org\"" | cortex deploys update-by-uuid -t cli -u ${uuid} -f-
  done

-----------------------------------------------------------------------------
Compare scorecard scores and levels for two scorecards
-----------------------------------------------------------------------------

This could be helpful for changing CQL rules (for example for CQL v1 -> CQL v2) and ensuring that scorecards produce the same results.

The following command get all scores for a scorecard, pipes the JSON output to jq and filters it to create a CSV file of the form: 

.. code:: bash
    
   service,score,ladderLevel

.. code:: bash

   cortex scorecards scores -t myScorecard | jq -r '.serviceScores[] | [ .service.tag, .score.ladderLevels[].level.name // "noLevel", .score.summary.score|tostring] | join(",")' | sort > /tmp/scorecard-output.csv

Run this command for two different scorecards and diff the csv files to compare results

.. code:: bash

  export SCORECARD=scorecard1
  cortex scorecards scores -t ${SCORECARD} | jq -r '.serviceScores[] | [ .service.tag, .score.ladderLevels[].level.name // "noLevel", .score.summary.score|tostring] | join(",")' | sort > /tmp/${SCORECARD}.csv

  export SCORECARD=scorecard2
  cortex scorecards scores -t ${SCORECARD} | jq -r '.serviceScores[] | [ .service.tag, .score.ladderLevels[].level.name // "noLevel", .score.summary.score|tostring] | join(",")' | sort > /tmp/${SCORECARD}.csv

  sdiff -s /tmp/scorecard1.csv /tmp/scorecard2.csv

====================================

.. |PyPI download month| image:: https://img.shields.io/pypi/dm/cortexapps-cli.svg
   :target: https://pypi.python.org/pypi/cortexapps-cli/
.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/cortexapps-cli.svg
     :target: https://pypi.python.org/pypi/cortexapps-cli/
.. |PyPI license| image:: https://img.shields.io/pypi/l/cortexapps-cli.svg
     :target: https://pypi.python.org/pypi/cortexapps-cli/
.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/cortexapps-cli.svg
     :target: https://pypi.python.org/pypi/cortexapps-cli/
.. |PyPI status| image:: https://img.shields.io/pypi/status/cortexapps-cli.svg
     :target: https://pypi.python.org/pypi/cortexapps-cli/
.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
    :target: https://www.python.org/
