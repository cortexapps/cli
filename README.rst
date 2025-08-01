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

.. code:: bash

  brew tap cortexapps/tap
  brew install cortexapps-cli

----------------------
docker
----------------------

.. code:: bash

  docker run -e CORTEX_API_KEY=<your API key> cortexapp/cli <Cortex CLI arguments>

===================
 Usage
===================

----------------------
Config file
----------------------

The CLI requires an API key for all operations.  This key is stored in a config file whose default location is `~/.cortex/config`.
This path can be overridden with the `-c` flag.  You will be prompted to create the file if it does not exist.

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

**NOTE:** if not supplied, base_url defaults to :code:`https://api.getcortexapp.com`.

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
- CORTEX_BASE_URL - this is optional if using Cortex cloud; defaults to `https://api.getcortexapp.com`

Example:

.. code-block::

  export CORTEX_API_KEY=<YOUR_API_KEY>

----------------------
Commands
----------------------

Run :code:`cortex` to see a list of options and sub-commands.

Run :code:`cortex <subcommand> -h` to see a list of all commands for each subcommand.

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

  Getting catalog
  -->  my-domain-1
  -->  my-service-1
  -->  my-service-2
  Getting entity-types
  -->  my-entity-type-1
  Getting ip-allowlist
  --> ip-allowlist
  Getting plugins
  --> my-plugin-1
  Getting scorecards
  -->  my-scorecard-1
  Getting workflows
  -->  my-workflow-1

  Export complete!
  Contents available in /Users/myUser/.cortex/export/2025-06-12-14-58-14

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

 for domain in `cortex catalog list -t domain --csv -C tag --sort tag:asc`; do echo "domain = $domain"; done

----------------------
Iterate over all teams
----------------------

**NOTE:** as of June 2025, requires a feature flag enabled to return team entities in the catalog API.  Work with your CSM if you need assistance.

.. code:: bash

 for team in `cortex catalog list -t team --csv -C tag --sort tag:asc`; do echo "team = $team"; done

-------------------------
Iterate over all services
-------------------------

.. code:: bash

 for service in `cortex catalog list -t service --csv -C tag --sort tag:asc`; do echo "service = $service"; done

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

 for service in `cortex catalog list -t service --csv -C tag --sort tag:asc`; do
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

 for domain in `cortex catalog list -t domain --csv -C tag --sort tag:asc`; do
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

  for domain in `cortex catalog list -t domain --csv -C tag --sort tag:asc`; do
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
Create a backup of all scorecards
-----------------------------------------------------------------------------

.. code:: bash
    
   for tag in `cortex scorecards list --csv -C tag`
   do
      echo "backing up: ${tag}"
      cortex scorecards descriptor -t ${tag} > ${tag}.yaml
   done

-----------------------------------------------------------------------------
Create a copy of all scorecards in draft mode
-----------------------------------------------------------------------------

This recipe creates a draft scorecard for all existing scorecards.  It creates each scorecard with a suffix for the scorecard tag of "-draft"
and it appends " Draft" to the end of the existing title.

.. code:: bash
    
   for tag in `cortex scorecards list --csv -C tag`
   do
      cortex scorecards descriptor -t ${tag} | yq '.draft = true | .tag += "-draft" | .name += " Draft"' | cortex scorecards create -f-
   done

-----------------------------------------------------------------------------
Replace scorecards with draft versions and delete the draft versions
-----------------------------------------------------------------------------

This recipe is a companion to the above recipe.  This recipe will replace the versions from
which the drafts were created and delete the drafts.

.. code:: bash
    
   for tag in `cortex scorecards list --csv -C tag --filter tag=.*-draft`
   do
      cortex scorecards descriptor -t ${tag} | yq '.draft = false | .tag |= sub("-draft","") | .name |= sub(" Draft", "")' | cortex scorecards create -f- && cortex scorecards delete -t ${tag}
   done

-----------------------------------------------------------------------------
Get draft scorecards, change draft to false and save on disk
-----------------------------------------------------------------------------

This recipe is similar to the one above, but it does not create a new scorecard in Cortex.  Rather, it makes the changes and saves to a file.

.. code:: bash
    
   for tag in `cortex scorecards list --csv -C tag --filter tag=.*-draft`
   do
      cortex scorecards descriptor -t ${tag} | yq '.draft = false | .tag |= sub("-draft","") | .name |= sub(" Draft", "")' > ${tag}.yaml
   done

-----------------------------------------------------------------------------
Delete all draft scorecards
-----------------------------------------------------------------------------

WARNING: This recipe will delete all draft scorecards.  

.. code:: bash
    
   for tag in `cortex scorecards list -s | jq -r ".scorecards[].tag"`
   do
      cortex scorecards delete -t ${tag}
   done

If you only want to delete some drafts, for example if you followed a recipe that creates draft versions of all existing scorecards, you 
will likely want to run this instead:

.. code:: bash
    
   for tag in `cortex scorecards list -s | jq -r ".scorecards[].tag" | grep "\-draft$"`
   do
      cortex scorecards delete -t ${tag}
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

-----------------------------------------------------------------------------
Add provider for all group type owners where provider is not listed
-----------------------------------------------------------------------------

This recipe adds the value of variable named ``provider`` to any owner for which **type = GROUP** and the provider field is not listed.  This recipe can be used to address this issue from Cortex release notes:
``Starting July 2nd (2024), any group type owners in the x-cortex-owners section of an entity descriptor will require a provider to be explicitly defined.``

Adjust the value of ``provider`` accordingly.  It must be one of the providers listed in our `public docs <https://docs.cortex.io/docs/reference/basics/ownership>`_.

This recipe does the following:

- It runs the Cortex query as documented in the release notes to find all group type owners where the provider is not defined.  The ``cortex queries`` parameter ``-f-`` indicates that the query input comes from stdin, provided by the here document (the content provided between the two 'EOF' delimiters).
- The recipe waits 10 minutes (denoted by parameter ``-x 600``) for the query to complete.
- It loops over the results of the Cortex query, adding the provider listed in the ``provider`` variable for any group owner where the provider is not defined in the entity.
- The contents of the entity descriptor are changed using yq and then passed as stdin to the cortex catalog subcommand to update the entity. 

.. code:: bash

    provider="GITHUB"
    query_output="query.json"

    cortex queries run -f- -w -x 600 > ${query_output} << EOF
    jq(entity.descriptor(), "[.info.\"x-cortex-owners\" | .[] | select(.type | ascii_downcase == \"group\") | select(.provider == null)] | length") > 0
    EOF

    for entity in `cat ${query_output} | jq -r ".result[].tag"`
    do
       echo "entity = $entity"
       cortex catalog descriptor -y -t ${entity} | yq "with(.info.x-cortex-owners[]; select(.type | downcase == \"group\") | select(.provider == null) | .provider = \"${provider}\" )" | cortex catalog create -f-
    done

-----------------------------------------------------------------------------
Export all workflows
-----------------------------------------------------------------------------

This recipe creates YAML files for each Workflow.  This may be helpful if you are considering enabling GitOps for Workflows and you want to export current Workflows as a starting point.

.. code:: bash

    for workflow in `cortex workflows list --csv --no-headers --columns tag`
    do
       echo "workflow = $workflow"
       cortex workflows get --tag $workflow --yaml > $workflow.yaml
    done

-----------------------------------------------------------------------------
Obfuscating a Cortex export
-----------------------------------------------------------------------------

This script will obfuscate a Cortex backup.  This can be helpful for on-premise customers who may need to provide data to Cortex to help identify performance or usability issues.

.. code:: bash

   # Works off an existing cortex CLI backup.
   # - Create a backup with cortex CLI command: cortex backup export -z 10000
   set -e
   input=$1
   output=$2

   all_file=${output}/all.yaml
   obfuscated_file=${output}/obfuscated.yaml

   echo "Output directory: ${output}"
   translate_file="${output}/translate.csv"

   if [ ! -d ${output} ]; then
      mkdir -p ${output}
   fi

   for yaml in `ls -1 ${input}/catalog/*`
   do
      entity=$(yq ${yaml} | yq ".info.x-cortex-tag")
      new_entity=$(echo ${entity} | md5sum | cut -d' ' -f 1)
      echo "${entity},${new_entity}" >> ${translate_file}
      echo "Creating: $new_entity"
      cat ${yaml} |\
         yq ".info.\"x-cortex-tag\" = \"${new_entity}\" | \
             .info.title=\"${new_entity}\" | \
             del(.info.description) | \
             del(.info.\"x-cortex-link\") | \
             del(.info.\"x-cortex-links\") | \
             del(.info.\"x-cortex-groups\") | \
             del(.info.\"x-cortex-custom-metadata\") | \
             del(.info.\"x-cortex-issues\") | \
             del(.info.\"x-cortex-git\") | \
             del(.info.\"x-cortex-slack\") | \
             del(.info.\"x-cortex-oncall\") | \
             with(.info; \
                select(.\"x-cortex-team\".members != null) | .\"x-cortex-team\".members = {\"name\": \"Cortex User\", \"email\": \"user@example.com\"} \
                 )" >> ${all_file}
      echo "---" >> ${all_file}
   done

   # The longer strings are translated first preventing substrings from being replaced in a longer string
   cat ${translate_file} | sort -r > ${translate_file}.tmp && echo "entity,new_entity" > ${translate_file} && cat ${translate_file}.tmp >> ${translate_file} && rm ${translate_file}.tmp

   python3 - ${all_file} ${translate_file} ${obfuscated_file} << EOF
   import csv
   import re
   import sys

   yaml_file = sys.argv[1]
   translate_file = sys.argv[2]
   output = sys.argv[3]

   with open(yaml_file, 'r') as f:
        bytes = f.read() # read entire file as bytes
        with open(translate_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entity = row['entity']
                new_entity = row['new_entity']
                print("entity = " + entity + ", new_entity = " + new_entity)
                bytes = bytes.replace("tag: " + entity, "tag: " + new_entity)
                bytes = bytes.replace("name: " + entity, "name: " + new_entity)

   f = open(output, "w")
   f.write(bytes)
   f.close()
   EOF

   # change all email addresses
   sed -i 's/email:.*/email: user@example.com/' ${obfuscated_file}

   # change all slack channel names
   sed -i 's/channel:.*/channel: my-slack-channel/' ${obfuscated_file}

   # copy export directory to new directory, without catalog YAML
   rsync -av --exclude='catalog' ${input}/ ${output}
   mkdir -p ${output}/catalog

   # now split single file into multiple that can be passed as parameter to cortex catalog create -f
   cd ${output}/catalog
   yq --no-doc -s '"file_" + $index' ${obfuscated_file}

   # tar it up
   tar_file=$(basename ${output}).tar
   cd ${output}
   rm ${all_file}
   rm ${translate_file} 
   tar -cvf ${tar_file} ./*

   echo "Created: ${output}/${tar_file}"

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
