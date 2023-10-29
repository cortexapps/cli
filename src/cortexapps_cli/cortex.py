#!/usr/bin/env python3

import argparse
from argparse import Namespace
from collections import OrderedDict
import configparser
from datetime import datetime
import inspect
import json
import os
import requests
from subprocess import run
import sys
import textwrap
import yaml

# It ain't pretty, but I'm just gonna throw a few globals into the mix.
output_behavior="print"
output=""
replace_string = "REPLACE_WITH_YOUR_CORTEX_API_KEY"
config={}

# Not sure if there is a cleaner way to implement parameter validation when you have subcommands and sub-subcommands.
# For now, this is just a brute force way to manage it.
#
# Potentially, you can override the help class to customize this, https://medium.com/@george.shuklin/simple-implementation-of-help-command-a634711b70e
def validate_input(argv):
    if len(argv)==0:
       parser.print_help()
       sys.exit(2)
  
    if argv[0] == "-h" or argv[0] == "--help" or argv[0] == "-v" or argv[0] == "--version":
       return

    if argv[0] == "integrations":
       if len(argv) == 1:
          print("ERROR! Command provided with no parameters.\n")
          print("Try " + argv[0] + " " + argv[1] + " -h for help")
          sys.exit(2)
       if argv[1] == "-h" or argv[1] == "--help":
          return
       if len(argv) == 2:
          print("ERROR! Command provided with no parameters.\n")
          print("Try " + argv[0] + " " + argv[1] + " -h for help")
          sys.exit(2)
       return

    if len(argv) == 1:
       print("ERROR! Command provided with no parameters.\n")
       print("Try " + argv[0] + " -h for help")
       sys.exit(2)

def read_file(args):
    # Check if file was passed as stdin
    if str(type(args.file)) == "<class '_io.TextIOWrapper'>":
        return args.file.read()
    # import_from_backup passes the file as a string
    elif isinstance(args.file, str):
        with open(args.file, 'rb') as f:
            return f.read()
    else:
        with open(args.file.name, 'rb') as f:
            return f.read()

def read_json_from_yaml(args):
    if str(type(args.file)) == "<class '_io.TextIOWrapper'>":
        data = yaml.safe_load(args.file.read())
    else:
        with open(args.file.name, 'rb') as f:
            data = yaml.safe_load(f)

    return '{ "spec": "' + str(data) + '" }'

def check_config_file(config_file, replace_string):
    if not os.path.isfile(config_file):
        print("Cortex CLI config file " + config_file + " does not exist.  Create (Y/N)?")
        response = input()
        if response == "Y" or response == "y":
            if not os.path.isdir(os.path.dirname(config_file)):
               os.mkdir(os.path.dirname(config_file), 0o700)
            cortex_config_contents = textwrap.dedent('''\
                [default]
                api_key = {replace}

                # Add aliases to create shortcuts.
                # left side = alias name
                # right side = contents that will be provided as parameters to Cortex CLI
                #
                # For example, invoke the 'services' alias with this command:
                # cortex -a services
                [default.aliases]
                services = catalog list -t service
                ''').format(replace=replace_string)
            f = open(config_file, "w")
            f.write(cortex_config_contents)
            f.close()

            print("Created file: " + config_file)
            print("Edit this file and replace the string '" + replace_string + "' with the contents")
            print("of your Cortex API key and then retry your command.")
            sys.exit(0)
        else:
            sys.exit(0)
        

def get_config(config, args, argv, parser):
    check_config_file(args.config, replace_string)

    config_parser = configparser.ConfigParser()
    config_parser.read(args.config)
    tenant_config = config_parser[args.tenant]
    api_key = tenant_config.get('api_key')
    if api_key == replace_string:
        print("Config file " + args.config + " has not been updated to include your Cortex API key.")
        print("Add your key to the file and then retry your command.")
        sys.exit(2)
    config.update({"url": tenant_config.get('base_url', 'https://api.getcortexapp.com')})
    config.update({"api_key": api_key})

    config.update({"debug": args.debug})
    config.update({"noObfuscate": args.noObfuscate})

    if args.cliAlias != None:
        key = args.tenant + '.aliases'
        argv.remove("-a")
        argv.remove(args.cliAlias)
        for word in config_parser[key][args.cliAlias].split():
            argv.append(word)
    args = parser.parse_args(argv)

    return args

def add_argument_accountId(subparser):
    subparser.add_argument(
            '-a', 
            '--accountId', 
            help='AWS account Id',
            required=True,
            default=True,
            metavar=''
    )

def add_argument_alias(subparser, help_text="The github configuration alias defined in Cortex"):
    subparser.add_argument(
            '-a', 
            '--alias', 
            help=help_text,
            required=True,
            default=True,
            metavar=''
    )

def add_argument_callee_tag(subparser, help_text='The entity tag (x-cortex-tag) that identifies the callee entity.'):
    subparser.add_argument(
            '-e',
            '--calleeTag',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_caller_tag(subparser, help_text='The entity tag (x-cortex-tag) that identifies the caller entity.'):
    subparser.add_argument(
            '-r',
            '--callerTag',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_child(subparser, help_text='The child group.'):
    subparser.add_argument(
            '-c',
            '--child',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_departmentTag(subparser):
    subparser.add_argument(
            '-d', 
            '--departmentTag', 
            help='The department entity tag',
            required=True,
            default=True,
            metavar=''
    )

def add_argument_discovery_audit_type(subparser):
    subparser.add_argument(
            '-t', 
            '--type', 
            help='Filter based on type of the vent',
            required=False,
            choices=['NEW_REPOSITORY', 'REPOSITORY_DELETED', 'REPOSITORY_ARCHIVED', 'NEW_K8S_RESOURCE', 'NEW_APM_RESOURCE', 'APM_RESOURCE_NOT_DETECTED', 'NEW_ECS_RESOURCE', 'ECS_RESOURCE_NOT_DETECTED', 'NEW_AWS_RESOURCE', 'AWS_RESOURCE_NOT_DETECTED', 'NEW_GOOGLE_CLOUD_RESOURCE', 'GOOGLE_CLOUD_RESOURCE_NOT_DETECTED'],
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_discovery_audit_source(subparser):
    subparser.add_argument(
            '-s', 
            '--source', 
            help='Filter based on integration source',
            required=False,
            choices=['AWS', 'AZURE_DEVOPS', 'BITBUCKET', 'DATADOG', 'DYNATRACE', 'ECS', 'GCP', 'GITHUB', 'GITLAB', 'INSTANA', 'K8S', 'LIGHTSTEP', 'LAMBDA', 'NEWRELIC', 'SERVICENOW'],
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_end_time(subparser, help_text='End time for audit log retrieve'):
    subparser.add_argument(
            '-e',
            '--endTime',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_entity_tag(subparser, help_text='The entity tag (x-cortex-tag) that identifies the entity.'):
    subparser.add_argument(
            '-e',
            '--entityTag',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_environment(subparser, help_text='The environment name of the deployment to delete.'):
    subparser.add_argument(
            '-e',
            '--environment',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_export_directory(subparser):
    subparser.add_argument(
            '-d', 
            '--directory', 
            help="Directory where export will be created; defaults to ~/.cortex/export/<DATE>",
            required=False,
            default=os.path.expanduser('~') + '/.cortex/export/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            metavar=''
    )

def add_argument_file(subparser, help_text):
    subparser.add_argument(
            '-f', 
            '--file', 
            required=True,
            help=help_text + "; can be passed as stdin with -, example: -f-",
            default=argparse.SUPPRESS,
            type=argparse.FileType('r'),
            metavar=''
    )

def add_argument_force(subparser, help_text='When true, overrides values that were defined in the catalog descriptor. Will be overwritten the next time the catalog descriptor is processed.'):
    subparser.add_argument(
            '-o',
            '--force',
            help=help_text,
            action='store_true',
            default='false'
    )

def add_argument_groups(subparser):
    subparser.add_argument(
            '-g', 
            '--groups', 
            help='Filter based on groups, which correspond to the x-cortex-groups field in the Catalog Descriptor. Accepts a comma-delimited list of groups',
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_id(subparser, help_text='The id of the CQL query'):
    subparser.add_argument(
            '-i',
            '--id',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_import_directory(subparser):
    subparser.add_argument(
            '-d', 
            '--directory', 
            help="Directory containing export contents",
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_includeDrafts(subparser, help_text='Include plugin drafts.'):
    subparser.add_argument(
            '-i',
            '--includeDrafts',
            help=help_text,
            required=False,
            default=True,
            action='store_true'
    )

def add_argument_includeIncoming(subparser, help_text='Including incoming dependencies.'):
    subparser.add_argument(
            '-i',
            '--includeIncoming',
            help=help_text,
            required=False,
            default=True,
            action='store_true'
    )

def add_argument_includeIgnored(subparser, help_text='Flag to include ignored events in result.'):
    subparser.add_argument(
            '-i',
            '--includeIgnored',
            help=help_text,
            required=False,
            default=False,
            action='store_true'
    )

def add_argument_includeOutgoing(subparser, help_text='Including outgoing dependencies.'):
    subparser.add_argument(
            '-o',
            '--includeOutgoing',
            help=help_text,
            required=False,
            default=False,
            action='store_true'
    )

def add_argument_includeTeamsWithoutMembers(subparser):
    subparser.add_argument(
            '-i', 
            '--includeTeamsWithoutMembers', 
            help='Include teams without members',
            required=False,
            default=False,
            action='store_true'
    )

def add_argument_key(subparser, help_text='Key to retrieve.'):
    subparser.add_argument(
            '-k',
            '--key',
            help=help_text,
            required=True,
            metavar=''
    )

def add_argument_method(subparser, help_text='The http method type of the dependency.'):
    subparser.add_argument(
            '-m',
            '--method',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_name(subparser, help_text='The name of the thing'):
    subparser.add_argument(
            '-n',
            '--name',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_page(subparser, help_text='Page number of results to retrieve'):
    subparser.add_argument(
            '-p',
            '--page',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_page_size(subparser, help_text='Page size for results, default = 50'):
    subparser.add_argument(
            '-z',
            '--pageSize',
            help=help_text,
            required=False,
            default=50,
            metavar=''
    )

def add_argument_parent(subparser, help_text='The parent group.'):
    subparser.add_argument(
            '-p',
            '--parent',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_path(subparser, help_text='The path of the dependency.'):
    subparser.add_argument(
            '-p',
            '--path',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_replace(subparser, help_text='Flag to indicate if relationships should be replaced.'):
    subparser.add_argument(
            '-r',
            '--replace',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_role(subparser):
    subparser.add_argument(
            '-r', 
            '--role', 
            help='AWS role',
            required=True,
            default=True,
            metavar=''
    )

def add_argument_scorecard_tag(subparser):
    subparser.add_argument(
            '-s',
            '--scorecardTag',
            help='Unique tag for the Scorecard',
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_sha(subparser, help_text='The sha string of the deployment to delete.'):
    subparser.add_argument(
            '-s',
            '--sha',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_start_time(subparser, help_text='Start time for audit log retrieve'):
    subparser.add_argument(
            '-s',
            '--startTime',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_tag(subparser, help_text='The entity tag (x-cortex-tag) that identifies the entity.'):
    subparser.add_argument(
            '-t',
            '--tag',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_teamTag(subparser, help_text='The tag identifing the team.'):
    subparser.add_argument(
            '-t',
            '--teamTag',
            help=help_text,
            required=True,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_timestamp(subparser, help_text='Date-time of events to include.'):
    subparser.add_argument(
            '-i',
            '--timestamp',
            help=help_text,
            required=False,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_type(subparser, option="-t", help_text='The resource type.', required=True):
    subparser.add_argument(
            option,
            '--type',
            help=help_text,
            required=required,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_types(subparser, option="-t", help_text='Comma-separated list of entity types.', required=True):
    subparser.add_argument(
            option,
            '--types',
            help=help_text,
            required=required,
            default=argparse.SUPPRESS,
            metavar=''
    )

def add_argument_uuid(subparser, option="-u", help_text='UUID of custom event.', required=True):
    subparser.add_argument(
            option,
            '--uuid',
            help=help_text,
            required=required,
            default=argparse.SUPPRESS,
            metavar=''
    )

def debug_json(r, method):
    if config['debug']:
        data = {}
        data['method'] = method
        data['status'] = r.status_code
        data['url'] = r.url
        data['history'] = str(r.history)
        data['response_headers'] = dict(r.headers)
        data['request_headers'] = dict(r.request.headers)
        data['json'] = str(r.json)
        if config['noObfuscate'] != True:
            data['request_headers']['Authorization'] = "Bearer <OBFUSCATED>"
        json_data = json.dumps(data)
        print(json_data, file=sys.stderr)

def exit(r, method, expected_rc=200):
    if r.status_code != expected_rc:
        print(r.text)
        debug_json(r, method)
        sys.exit(r.status_code)
    else:
        debug_json(r, method)
        if output_behavior=="print":
            print(r.text)
        else:
            global output
            output = r.text

def api_key(headers):
    headers.update({"Authorization": "Bearer " + config['api_key']})

# There might be a more efficient use of the requests library to combine
# these methods into a single generic method.
def get(url, headers={}):
    api_key(headers)
    r = requests.get(config['url'] + url, headers=headers)
    exit( r, 'GET')

def put(url, headers={}, payload=""):
    api_key(headers)

    r = requests.put(config['url'] + url, headers=headers, data=payload)
    exit(r, 'PUT')

def delete(url, headers={}, payload="", expected_rc=200):
    api_key(headers)

    r = requests.delete(config['url'] + url, headers=headers, data=payload)
    exit(r, 'DELETE', expected_rc)

def post(url, headers={}, payload="", expected_rc=200):
    api_key(headers)

    r = requests.post(config['url'] + url, headers=headers,data=payload)
    exit(r, 'POST', expected_rc)

# Generate HTTP API options.  Everything in the Namespace argparse object is
# added to the URL with the exception of those listed in the array below.
def parse_opts(args):
    opts = ""

    for k, v in dict(vars(args)).items():
        if k in ['tenant', 'cliAlias', 'debug', 'noObfuscate', 'func', 'config']:
            continue
        if len(opts) == 0:
           char="?"
        else:
           char="&"
        opts=opts + char + k + "=" + str(v)

    # convert python args to valid JSON
    return opts.replace("True", "true").replace("False", "false")

# Audit Logs start
def subparser_audit_logs_opts(subparsers):
    p = subparsers.add_parser('audit-logs', help='audit log commands')
    sp = p.add_subparsers(help='audit logs help')

    subparser_audit_logs_get(sp)

def subparser_audit_logs_get(subparser):
    sp = subparser.add_parser('get', help='retrieve audit logs')
    add_argument_end_time(sp)
    add_argument_start_time(sp)
    add_argument_page(sp)
    add_argument_page_size(sp)
    sp.set_defaults(func=audit_logs_get)

def audit_logs_get(args):
    get("/api/v1/audit-logs/" + parse_opts(args))

# Audit Logs end

# Backup start
def subparser_backup_opts(subparsers):
    p = subparsers.add_parser('backup', help='import/export commands')
    sp = p.add_subparsers(help='backup help')

    subparser_backup_export(sp)
    subparser_backup_import(sp)

def subparser_backup_export(subparser):
    sp = subparser.add_parser('export', help='Export tenant')
    add_argument_export_directory(sp)
    sp.set_defaults(func=export)

def export(args):
    global output_behavior
    output_behavior="return"

    catalog_directory=args.directory + "/catalog"
    json_directory=args.directory + "/json"
    scorecard_directory=args.directory + "/scorecards"
    teams_directory=args.directory + "/teams"
    resource_definitions_directory=args.directory + "/resource-definitions"

    directory_list = [catalog_directory, json_directory, resource_definitions_directory, scorecard_directory, teams_directory]

    for directory in directory_list:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    print("Getting resource definitions")
    resource_definitions_json=json_directory + "/resource-definitions.json"
    resource_definitions_list(args)
    with open(resource_definitions_json, 'w') as f:
        f.write(output)
    data = json.loads(output)

    # Can't sort json keys, so need to create a list first so it can be sorted.
    resource_types_list = []
    for t in data['definitions']:
        resource_types_list.append(t['type'])

    resource_types="service,domain"
    for resource_type in sorted(resource_types_list):
        resource_types=resource_types + "," + resource_type
        print("-->  " + resource_type)
        resource_file=resource_definitions_directory + "/" + resource_type + ".json"
        args.type = resource_type
        resource_definitions_retrieve(args)
        with open(resource_file, 'w') as f:
            f.write(output)
        f.close()
    delattr(args, 'type')

    print("Getting catalog entities")
    catalog_json=json_directory + "/catalog.json"
    args.types = resource_types
    catalog_list(args)
    delattr(args, 'types')
    with open(catalog_json, 'w') as f:
        f.write(output)

    data = json.loads(output)

    # Can't sort json keys, so need to create a list first so it can be sorted.
    entity_list = []
    for entity in data['entities']:
        entity_list.append(entity['tag'])

    for tag in sorted(entity_list):
        print("-->  " + tag)
        entity_file=catalog_directory + "/" + tag + ".yaml"
        args.tag = tag
        catalog_descriptor(args)
        with open(entity_file, 'w') as f:
            f.write(output)

    print("Getting IP Allowlist definitions")
    ip_allowlist_json=json_directory + "/ip-allowlist.json"
    ip_allowlist_get(args)
    with open(ip_allowlist_json, 'w') as f:
        f.write(output)

    print("Getting scorecards")
    scorecards_json=json_directory + "/scorecards.json"
    scorecards_list(args)
    with open(scorecards_json, 'w') as f:
        f.write(output)

    data = json.loads(output)

    # Can't sort json keys, so need to create a list first so it can be sorted.
    scorecard_list = []
    for scorecard in data['scorecards']:
        scorecard_list.append(scorecard['tag'])

    for tag in sorted(scorecard_list):
        print("-->  " + tag)
        scorecard_file=scorecard_directory + "/" + tag + ".yaml"
        args.tag=tag
        scorecards_descriptor(args)
        with open(scorecard_file, 'w') as f:
            f.write(output)
    delattr(args, 'tag')

    # CORTEX teams; will not try to import IDP-backed teams.  Those would get re-imported after re-establishing the IDP integration.
    print("Getting teams")
    teams_json=json_directory + "/teams.json"
    teams_list(args)
    with open(teams_json, 'w') as f:
        f.write(output)

    data = json.loads(output)

    # Can't sort json keys, so need to create a list first so it can be sorted.
    # Has to be a dictionary because we also need to know about the type of team.
    team_list = dict()
    for team in data['teams']:
        team_list[team['teamTag']] = team['type']

    for team_tag, type in OrderedDict(sorted(team_list.items())).items():
        if type != "CORTEX":
            continue
        print("-->  " + team_tag)
        team_file=teams_directory + "/" + team_tag + ".json"
        args.teamTag=team_tag
        teams_get(args)
        with open(team_file, 'w') as f:
            f.write(output)

    print("\nExport complete!")
    print("Contents available in " + args.directory)

def subparser_backup_import(subparser):
    sp = subparser.add_parser('import', help='Import contents of an export directory')
    add_argument_import_directory(sp)
    sp.set_defaults(func=import_from_export)

def import_from_export(args):
    global output_behavior
    output_behavior="return"

    catalog_directory = args.directory + "/catalog"
    json_directory = args.directory + "/json"
    scorecard_directory = args.directory + "/scorecards"
    teams_directory = args.directory + "/teams"
    resource_definitions_directory = args.directory + "/resource-definitions"

    print("Importing resource definitions")
    for file in sorted(os.listdir(resource_definitions_directory)):
        print("-->  " + file)
        args.file = resource_definitions_directory + "/" + file
        resource_definitions_create(args)

    print("Importing catalog entities")
    for file in sorted(os.listdir(catalog_directory)):
        print("-->  " + file)
        args.file = catalog_directory + "/" + file
        catalog_create_or_update(args)

    print("Importing IP Allowlist definitions")
    args.file = json_directory + "/ip-allowlist.json"
    ip_allowlist_replace(args)

    print("Importing scorecards")
    for file in sorted(os.listdir(scorecard_directory)):
        print("-->  " + file)
        args.file = scorecard_directory + "/" + file
        scorecards_create_or_update(args)

    print("Importing teams")
    for file in sorted(os.listdir(teams_directory)):
        print("-->  " + file)
        args.file = teams_directory + "/" + file
        teams_create(args)

    print("\nImport complete!")
# Backup end

# Catalog start
def subparser_catalog_opts(subparsers):
    p = subparsers.add_parser('catalog', help='catalog commands')
    sp = p.add_subparsers(help='catalog help')

    subparser_catalog_archive(sp)
    subparser_catalog_create_or_update(sp)
    subparser_catalog_delete(sp)
    subparser_catalog_delete_by_type(sp)
    subparser_catalog_list(sp)
    subparser_catalog_descriptor(sp)
    subparser_catalog_details(sp)
    subparser_catalog_unarchive(sp)

def subparser_catalog_archive(subparser):
    sp = subparser.add_parser('archive', help='archive an entity')
    add_argument_tag(sp)
    sp.set_defaults(func=catalog_archive)

def catalog_archive(args):
    put("/api/v1/catalog/" + args.tag + "/archive")

def subparser_catalog_create_or_update(subparser):
    sp = subparser.add_parser(
            'create',
            help='Create a catalog entity using a descriptor YAML. If the YAML refers to an entity that already exists (as referenced by the x-cortex-tag), this API will update the existing entity.',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Additional documentation
                ------------------------
                https://docs.cortex.io/docs/reference/basics/entities
                https://docs.cortex.io/docs/reference/basics/entities#example-cortexyaml-for-service-entity contains sample entities
                '''))
    add_argument_file(sp, 'File containing openapi descriptor for entity')
    sp.add_argument(
            '-d',
            '--dry-run',
            help='When true, this endpoint only validates the descriptor contents and returns any errors or warnings.',
            action='store_true',
            default='false'
    )
    sp.add_argument(
            '-g',
            '--github-pr',
            help='Add a comment with validation errors on the pull request with the given ID',
            default=argparse.SUPPRESS,
            metavar=''
    )
    sp.set_defaults(func=catalog_create_or_update)

def catalog_create_or_update(args):
    headers = { 'Content-Type': 'application/openapi;charset=UTF-8' }
    post("/api/v1/open-api" + parse_opts(args), headers, read_file(args))

def subparser_catalog_delete(subparser):
    sp = subparser.add_parser('delete', help='delete entity')
    add_argument_tag(sp)
    sp.set_defaults(func=catalog_delete)

def catalog_delete(args):
    delete("/api/v1/catalog/" + args.tag)

def subparser_catalog_delete_by_type(subparser):
    sp = subparser.add_parser('delete-by-type', help='Note: Dangerous operation that will delete all entities that are of the given type')
    add_argument_types(sp)
    sp.set_defaults(func=catalog_delete_by_type)

def catalog_delete_by_type(args):
    delete("/api/v1/catalog" + parse_opts(args))

def subparser_catalog_list(subparser):
    sp = subparser.add_parser(
            'list',
            help='List all entities across the Service, Resource and Domain Catalogs.\n This API returns summary data for each entity, so refer to the retrieve entity method to lookup more details for a single entity.'
    )
    add_argument_groups(sp)
    sp.add_argument(
            '-o',
            '--owners',
            help='Filter based on owner group names, which correspond to the x-cortex-owners field in the Catalog Descriptor. Accepts a comma-delimited list of owner group names',
            default=argparse.SUPPRESS,
            metavar=''
    )
    sp.add_argument(
            '-d',
            '--hierarchy-depth',
            help='Depth of the parent / children hierarchy nodes. Can be \'full\' or a valid integer',
            default='full',
            metavar=''
    )
    sp.add_argument(
            '-r',
            '--gitRepositories',
            help='Supports only GitHub repositories in the org/repo format',
            default=argparse.SUPPRESS,
            metavar=''
    )
    sp.add_argument(
            '-i',
            '--includeHierarchyFields',
            help='List of sub fields to include for hierarchies. Only supports \'groups\'',
            default=False,
            action='store_true',
            required=False
    )
    sp.add_argument(
            '-t',
            '--types',
            help='Filter the response to specific types of entities. By default, this includes services, resources, and domains. Corresponds to the x-cortex-type field in the Entity Descriptor.',
            default=argparse.SUPPRESS,
            metavar=''
    )
    sp.add_argument(
            '-a',
            '--includeArchived',
            help='Whether to include archived entities in the response, default to false',
            default=False,
            action='store_true',
            required=False
    )
    sp.add_argument(
            '-m',
            '--includeMetadata',
            help='Whether to include custom data for each entity in the response',
            default=False,
            action='store_true',
            required=False
    )
    sp.set_defaults(func=catalog_list)

def catalog_list(args):
    get("/api/v1/catalog" + parse_opts(args))

def subparser_catalog_descriptor(subparser):
    sp = subparser.add_parser('descriptor', help='Retrieve entity descriptor')
    add_argument_tag(sp)
    sp.add_argument(
            '-y',
            '--yaml',
            help='When true, returns the YAML representation of the descriptor',
            action='store_true',
            default=False,
            required=False
    )
    sp.set_defaults(func=catalog_descriptor)

def catalog_descriptor(args):
    get("/api/v1/catalog/" + args.tag + "/openapi" + parse_opts(args))

def subparser_catalog_details(subparser):
    sp = subparser.add_parser('details', help='Retrieve entity details')
    sp.add_argument(
            '-i',
            '--includeHierarchyFields',
            help='List of sub fields to include for hierarchies. Only supports \'groups\'',
            default=argparse.SUPPRESS,
            metavar=''
    )
    add_argument_groups(sp)
    add_argument_tag(sp)
    sp.set_defaults(func=catalog_details)

def catalog_details(args):
    get("/api/v1/catalog/" + args.tag + parse_opts(args))

def subparser_catalog_unarchive(subparser):
    sp = subparser.add_parser('unarchive', help='unarchive an entity')
    add_argument_tag(sp)
    sp.set_defaults(func=catalog_unarchive)

def catalog_unarchive(args):
    put("/api/v1/catalog/" + args.tag + "/unarchive")
# Catalog end

# Custom Data start
def subparser_custom_data_opts(subparsers):
    p = subparsers.add_parser('custom-data', help='custom_data actions')
    sp = p.add_subparsers(help='custom_data help')

    subparser_custom_data_add(sp)
    subparser_custom_data_bulk(sp)
    subparser_custom_data_delete(sp)
    subparser_custom_data_get(sp)
    subparser_custom_data_list(sp)

def subparser_custom_data_add(subparser):
    sp = subparser.add_parser('add', help='Add custom data for entity', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "description": "string",
                  "key": "my-key",
                  "value": {
                    "nested": {
                      "objects": "are ok"
                    }
                  }
                }

                Examples:
                ---------
                Single value:
                {
                  "description": "A field to store CI/CD tool",
                  "key": "ci-cd-tool",
                  "value": "Jenkins"
                  }
                }

                Nested values:
                {
                "description": "Custom field to store build metrics",
                  "key": "build-metrics",
                  "value": {
                    "2023-08-01": {
                      "success-rate": "50"
                    },
                    "2023-08-02": {
                      "success-rate": "67"
                    }
                  }
                }
                '''))
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing keys to update')
    add_argument_force(sp)
    sp.set_defaults(func=custom_data_add)

def custom_data_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/" + args.tag + "/custom-data", headers, read_file(args))

def subparser_custom_data_bulk(subparser):
    sp = subparser.add_parser('bulk', help='Add multiple key/values of custom data to multiple entities')
    add_argument_file(sp, 'File containing keys to update')
    add_argument_force(sp)
    sp.set_defaults(func=custom_data_bulk)

def custom_data_bulk(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/custom-data", headers, read_file(args))

def subparser_custom_data_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete custom data for entity')
    add_argument_tag(sp)
    add_argument_key(sp, 'Key to delete')
    sp.set_defaults(func=custom_data_delete)

def custom_data_delete(args):
    delete("/api/v1/catalog/" + args.tag + "/custom-data" + parse_opts(args))

def subparser_custom_data_list(subparser):
    sp = subparser.add_parser('list', help='List custom data for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=custom_data_list)

def custom_data_list(args):
    get("/api/v1/catalog/" + args.tag + "/custom-data")

def subparser_custom_data_get(subparser):
    sp = subparser.add_parser('get', help='Get custom data for entity by key')
    add_argument_tag(sp)
    add_argument_key(sp)
    sp.set_defaults(func=custom_data_get)

def custom_data_get(args):
    get("/api/v1/catalog/" + args.tag + "/custom-data/" + args.key)
# Custom Data end

# Custom Events start
def subparser_custom_events_opts(subparsers):
    p = subparsers.add_parser('custom-events', help='custom events actions')
    sp = p.add_subparsers(help='custom_events help')

    subparser_custom_events_create(sp)
    subparser_custom_events_delete_all(sp)
    subparser_custom_events_list(sp)
    subparser_custom_events_delete_by_uuid(sp)
    subparser_custom_events_get_by_uuid(sp)
    subparser_custom_events_update_by_uuid(sp)

def subparser_custom_events_create(subparser):
    sp = subparser.add_parser('create', help='Create custom event', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "customData": {},
                  "description": "string",
                  "timestamp": "2023-10-13T13:27:51.226Z",
                  "title": "Created K8s pod",
                  "type": "POD_CREATION"
                }

                Example:
                ---------
                {
                  "customData": {},
                  "description": "string",
                  "timestamp": "2023-10-13T13:27:51.226Z",
                  "title": "Created K8s pod",
                  "type": "POD_CREATION"
                }
                '''))
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing custom event to create')
    sp.set_defaults(func=custom_events_create)

def custom_events_create(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/" + args.tag + "/custom-events", headers, read_file(args))

def subparser_custom_events_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all custom events for an entity') 
    add_argument_tag(sp)
    add_argument_type(sp, option='-y', help_text='The custom event type, defaults to all types', required=False)
    add_argument_timestamp(sp)
    sp.set_defaults(func=custom_events_delete_all)

def custom_events_delete_all(args):
    delete("/api/v1/catalog/" + args.tag + "/custom-events" + parse_opts(args), expected_rc=204)

def subparser_custom_events_list(subparser):
    sp = subparser.add_parser('list', help='List custom events for entity') 
    add_argument_tag(sp)
    add_argument_type(sp, option='-y', help_text='The custom event type, defaults to all types', required=False)
    add_argument_timestamp(sp)
    sp.set_defaults(func=custom_events_list)

def custom_events_list(args):
    get("/api/v1/catalog/" + args.tag + "/custom-events" + parse_opts(args))

def subparser_custom_events_delete_by_uuid(subparser):
    sp = subparser.add_parser('delete-by-uuid', help='Delete custom events by UUID') 
    add_argument_tag(sp)
    add_argument_uuid(sp)
    sp.set_defaults(func=custom_events_delete_by_uuid)

def custom_events_delete_by_uuid(args):
    delete("/api/v1/catalog/" + args.tag + "/custom-events/" + args.uuid, expected_rc=204)

def subparser_custom_events_get_by_uuid(subparser):
    sp = subparser.add_parser('get-by-uuid', help='Get custom event by UUID') 
    add_argument_tag(sp)
    add_argument_uuid(sp)
    sp.set_defaults(func=custom_events_get_by_uuid)

def custom_events_get_by_uuid(args):
    get("/api/v1/catalog/" + args.tag + "/custom-events/" + args.uuid)

def subparser_custom_events_update_by_uuid(subparser):
    sp = subparser.add_parser('update-by-uuid', help='Update custom event by UUID') 
    add_argument_tag(sp)
    add_argument_uuid(sp)
    add_argument_file(sp, 'File containing custom event to create')
    sp.set_defaults(func=custom_events_update_by_uuid)

def custom_events_update_by_uuid(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/" + args.tag + "/custom-events/" + args.uuid, headers, read_file(args))
# Custom Events end

# Groups start
def subparser_groups_opts(subparsers):
    p = subparsers.add_parser('groups', help='groups commands')
    sp = p.add_subparsers(help='groups subcommand help')
    subparser_groups_add(sp)
    subparser_groups_delete(sp)
    subparser_groups_get(sp)

def subparser_groups_add(subparser):
    sp = subparser.add_parser('add', help='Add groups to entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing JSON array of groups to add')
    sp.set_defaults(func=groups_add)

def groups_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/"+ args.tag + "/groups", headers, payload=read_file(args))

def subparser_groups_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete group from entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing JSON array of groups to delete')
    sp.set_defaults(func=groups_delete)

def groups_delete(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    delete("/api/v1/catalog/"+ args.tag + "/groups", headers, read_file(args))

def subparser_groups_get(subparser):
    sp = subparser.add_parser('get', help='Get groups for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=groups_get)

def groups_get(args):
    get("/api/v1/catalog/"+ args.tag + "/groups")
# Groups end

# Integrations start
def subparser_integrations_opts(subparsers):
    p = subparsers.add_parser('integrations', help='integrations sub-commands')
    sp = p.add_subparsers(help='integrations subcommand help')

    ssp = sp.add_parser('aws', help='AWS integration')
    subparser_integrations_aws_opts(ssp)
    ssp = sp.add_parser('datadog', help='Datadog integration')
    subparser_integrations_datadog_opts(ssp)
    ssp = sp.add_parser('github', help='GitHub integration')
    subparser_integrations_github_opts(ssp)
    ssp = sp.add_parser('gitlab', help='GitLab integration')
    subparser_integrations_gitlab_opts(ssp)
    ssp = sp.add_parser('newrelic', help='Newrelic integration')
    subparser_integrations_newrelic_opts(ssp)
    ssp = sp.add_parser('prometheus', help='Prometheus integration')
    subparser_integrations_prometheus_opts(ssp)
    ssp = sp.add_parser('sonarqube', help='Sonarqube integration')
    subparser_integrations_sonarqube_opts(ssp)
# Integrations end

# Dependencies start
def subparser_dependencies_opts(subparsers):
    p = subparsers.add_parser('dependencies', help='dependencies commands')
    sp = p.add_subparsers(help='dependencies help')

    subparser_dependencies_add(sp)
    subparser_dependencies_add_in_bulk(sp)
    subparser_dependencies_delete(sp)
    subparser_dependencies_delete_all(sp)
    subparser_dependencies_delete_in_bulk(sp)
    subparser_dependencies_get(sp)
    subparser_dependencies_get_all(sp)
    subparser_dependencies_update(sp)

def subparser_dependencies_add(subparser):
    sp = subparser.add_parser('add',
            help='Create dependency from an entity',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "description": "This is a description of the dependency",
                  "metadata": {
                    "someField": "someField data",
                    "someField1": "someField1 data"
                }
                '''))
    add_argument_caller_tag(sp)
    add_argument_callee_tag(sp)
    add_argument_method(sp)
    add_argument_path(sp)
    add_argument_file(sp, 'File containing JSON-formatted description and metadata')
    sp.set_defaults(func=dependencies_add)

def dependencies_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/" + args.callerTag + "/dependencies/" + args.calleeTag, headers, payload=read_file(args), expected_rc=201)

def subparser_dependencies_add_in_bulk(subparser):
    sp = subparser.add_parser('add-in-bulk',
            help='Create or update dependencies in bulk',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "values": {
                    "dependency-service": [
                       {
                         "description": "dependency description",
                         "metadata": {
                           "someField": "someField data",
                           "someField1": "someField1 data"
                         },
                         "method": "GET",
                         "path": "/2.0/users/{username}",
                         "tag": "test-service"
                       }
                    ]
                  }
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted array of dependencies')
    sp.set_defaults(func=dependencies_add_in_bulk)

def dependencies_add_in_bulk(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/dependencies", headers, payload=read_file(args))

def subparser_dependencies_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a dependency from an entity')
    add_argument_caller_tag(sp)
    add_argument_callee_tag(sp)
    add_argument_method(sp)
    add_argument_path(sp)
    sp.set_defaults(func=dependencies_delete)

def dependencies_delete(args):
    delete("/api/v1/catalog/" + args.callerTag + "/dependencies/" + args.calleeTag, expected_rc=204)

def subparser_dependencies_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Deletes any outgoing dependencies from the entity. Note: this only deletes dependencies that were created via the API.')
    add_argument_caller_tag(sp)
    sp.set_defaults(func=dependencies_delete_all)

def dependencies_delete_all(args):
    delete("/api/v1/catalog/" + args.callerTag + "/dependencies", expected_rc=204)

def subparser_dependencies_delete_in_bulk(subparser):
    sp = subparser.add_parser('delete-in-bulk',
            help='Delete dependencies in bulk',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "values": {
                    "dependency-service": [
                       {
                         "description": "dependency description",
                         "metadata": {
                           "someField": "someField data",
                           "someField1": "someField1 data"
                         },
                         "method": "GET",
                         "path": "/2.0/users/{username}",
                         "tag": "test-service"
                       }
                    ]
                  }
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted array of dependencies')
    sp.set_defaults(func=dependencies_delete_in_bulk)

def dependencies_delete_in_bulk(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    delete("/api/v1/catalog/dependencies", headers, payload=read_file(args), expected_rc=204)

def subparser_dependencies_get(subparser):
    sp = subparser.add_parser('get', help='Retrieve dependency between entities')
    add_argument_caller_tag(sp)
    add_argument_callee_tag(sp)
    add_argument_method(sp)
    add_argument_path(sp)
    sp.set_defaults(func=dependencies_get)

def dependencies_get(args):
    get("/api/v1/catalog/" + args.callerTag + "/dependencies/" + args.calleeTag + parse_opts(args))

def subparser_dependencies_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all dependencies for an entity')
    add_argument_caller_tag(sp)
    add_argument_includeOutgoing(sp)
    add_argument_includeIncoming(sp)
    sp.set_defaults(func=dependencies_get_all)

def dependencies_get_all(args):
    get("/api/v1/catalog/" + args.callerTag + "/dependencies" + parse_opts(args))

def subparser_dependencies_update(subparser):
    sp = subparser.add_parser('update', help='Update dependency between entities')
    add_argument_caller_tag(sp)
    add_argument_callee_tag(sp)
    add_argument_method(sp)
    add_argument_path(sp)
    add_argument_file(sp, 'File containing JSON-formatted description and metadata')
    sp.set_defaults(func=dependencies_update)

def dependencies_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/" + args.callerTag + "/dependencies/" + args.calleeTag + parse_opts(args), headers, payload=read_file(args))
# Dependencies end

# Deploys start
def subparser_deploys_opts(subparsers):
    p = subparsers.add_parser('deploys', help='deploys commands')
    sp = p.add_subparsers(help='deploys help')

    subparser_deploys_add(sp)
    subparser_deploys_list(sp)
    subparser_deploys_delete(sp)
    subparser_deploys_delete_all(sp)
    subparser_deploys_delete_filter(sp)

def subparser_deploys_add(subparser):
    sp = subparser.add_parser('add', help='Add a deployment to an entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing JSON-formatted deployment details')
    sp.set_defaults(func=deploys_add)

def deploys_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/" + args.tag + "/deploys", headers, payload=read_file(args))

def subparser_deploys_list(subparser):
    sp = subparser.add_parser('list', help='List deployments for an entity')
    add_argument_tag(sp)
    sp.set_defaults(func=deploys_list)

def deploys_list(args):
    get("/api/v1/catalog/" + args.tag + "/deploys")

def subparser_deploys_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete deployments for an entity')
    add_argument_tag(sp)
    add_argument_environment(sp)
    add_argument_sha(sp)
    add_argument_type(sp, option="-y", help_text="Deployment type to delete", required=False)
    sp.set_defaults(func=deploys_delete)

def deploys_delete(args):
    delete("/api/v1/catalog/" + args.tag + "/deploys" + parse_opts(args))

def subparser_deploys_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all deployments for all entities')
    sp.set_defaults(func=deploys_delete_all)

def deploys_delete_all(args):
    delete("/api/v1/catalog/deploys/all")

def subparser_deploys_delete_filter(subparser):
    sp = subparser.add_parser('delete-filter', help='Delete deployments for all entities based on a filter')
    add_argument_environment(sp)
    add_argument_sha(sp)
    add_argument_type(sp, option="-y", help_text="Deployment type to delete", required=False)
    sp.set_defaults(func=deploys_delete_filter)

def deploys_delete_filter(args):
    delete("/api/v1/catalog/deploys" + parse_opts(args))
# Deploys end

# Discovery Audit start
def subparser_discovery_audit_opts(subparsers):
    p = subparsers.add_parser('discovery-audit', help='Discovery Audit commands')
    sp = p.add_subparsers(help='discovery audit help')

    subparser_discovery_audit_get(sp)

def subparser_discovery_audit_get(subparser):
    sp = subparser.add_parser('get', 
        help="This report shows you recent changes in your environment that aren't reflected in Cortex, including newly created repositories, services, and resources that we discover from your integrations or which were deleted in the environment but corresponding Cortex entities are still present.Add a deployment to an entity",
         formatter_class=argparse.RawTextHelpFormatter, 
         epilog=textwrap.dedent('''\
                Possible values for source, type:
                ---------------------------------
                source:
                - AWS
                - AZURE_DEVOPS
                - BITBUCKET
                - DATADOG
                - DYNATRACE
                - ECS
                - GCP
                - GITHUB
                - GITLAB
                - INSTANA
                - K8S
                - LIGHTSTEP
                - LAMBDA
                - NEWRELIC
                - SERVICENOW

                type:
                - APM_RESOURCE_NOT_DETECTED 
                - AWS_RESOURCE_NOT_DETECTED 
                - ECS_RESOURCE_NOT_DETECTED 
                - GOOGLE_CLOUD_RESOURCE_NOT_DETECTED
                - NEW_APM_RESOURCE
                - NEW_AWS_RESOURCE 
                - NEW_ECS_RESOURCE 
                - NEW_GOOGLE_CLOUD_RESOURCE 
                - NEW_K8S_RESOURCE
                - NEW_REPOSITORY
                - REPOSITORY_ARCHIVED
                - REPOSITORY_DELETED
                '''))
    add_argument_discovery_audit_source(sp)
    add_argument_discovery_audit_type(sp)
    add_argument_includeIgnored(sp)
    sp.set_defaults(func=discovery_audit_get)

def discovery_audit_get(args):
    get("/api/v1/discovery-audit" + parse_opts(args))
# Discovery Audit end

# Docs Start
def subparser_docs_opts(subparsers):
    p = subparsers.add_parser('docs', help='OpenAPI doc commands')
    sp = p.add_subparsers(help='docs subcommand help')

    subparser_docs_delete(sp)
    subparser_docs_retrieve(sp)
    subparser_docs_update(sp)

def subparser_docs_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete OpenAPI docs for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=docs_delete)

def docs_delete(args):
    delete("/api/v1/catalog/" + args.tag + "/documentation/openapi", expected_rc=204)

def subparser_docs_retrieve(subparser):
    sp = subparser.add_parser('get', help='Retrieve OpenAPI docs for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=docs_retrieve)

def docs_retrieve(args):
    get("/api/v1/catalog/" + args.tag + "/documentation/openapi")

def subparser_docs_update(subparser):
    sp = subparser.add_parser('update', help='Update OpenAPI docs for entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing stringified JSON representation of the OpenAPI spec')
    sp.set_defaults(func=docs_update)

def docs_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/" + args.tag + "/documentation/openapi", headers, payload=read_json_from_yaml(args))
# Docs End

# Groups start
def subparser_groups_opts(subparsers):
    p = subparsers.add_parser('groups', help='groups commands')
    sp = p.add_subparsers(help='groups subcommand help')
    subparser_groups_add(sp)
    subparser_groups_delete(sp)
    subparser_groups_get(sp)

def subparser_groups_add(subparser):
    sp = subparser.add_parser('add', help='Add groups to entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing JSON array of groups to add')
    sp.set_defaults(func=groups_add)

def groups_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/"+ args.tag + "/groups", headers, payload=read_file(args))

def subparser_groups_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete group from entity')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing JSON array of groups to delete')
    sp.set_defaults(func=groups_delete)

def groups_delete(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    delete("/api/v1/catalog/"+ args.tag + "/groups", headers, read_file(args))

def subparser_groups_get(subparser):
    sp = subparser.add_parser('get', help='Get groups for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=groups_get)

def groups_get(args):
    get("/api/v1/catalog/"+ args.tag + "/groups")
# Groups end

# Integrations-AWS start
def subparser_integrations_aws_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - aws help')

    subparser_integrations_aws_get(sp)
    subparser_integrations_aws_get_all(sp)
    subparser_integrations_aws_validate(sp)
    subparser_integrations_aws_validate_all(sp)
    subparser_integrations_aws_add(sp)
    subparser_integrations_aws_update(sp)
    subparser_integrations_aws_delete(sp)
    subparser_integrations_aws_delete_all(sp)

def subparser_integrations_aws_get(subparser):
    sp = subparser.add_parser('get', help='Retrieve a configuration')
    add_argument_accountId(sp)
    sp.set_defaults(func=integrations_aws_get)

def integrations_aws_get(args):
    get("/api/v1/aws/configurations/" + str(args.accountId))

def subparser_integrations_aws_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_aws_get_all)

def integrations_aws_get_all(args):
    get("/api/v1/aws/configurations")

def subparser_integrations_aws_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a configuration')
    add_argument_accountId(sp)
    sp.set_defaults(func=integrations_aws_validate)

def integrations_aws_validate(args):
    post("/api/v1/aws/configurations/validate/" + str(args.accountId))

def subparser_integrations_aws_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_aws_validate_all)

def integrations_aws_validate_all(args):
    post("/api/v1/aws/configurations/all/validate")

def subparser_integrations_aws_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_accountId(sp)
    add_argument_role(sp)
    sp.set_defaults(func=integrations_aws_add)

def integrations_aws_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    payload="{ \"accountId\": \"" + args.accountId + "\", \"role\": \"" + args.role + "\"}"
    post("/api/v1/aws/configurations", headers, payload=payload)

def subparser_integrations_aws_update(subparser):
    sp = subparser.add_parser('update', help='Update configurations')
    add_argument_file(sp, 'File containing JSON-formatted configuration; all configurations will be replaced')
    sp.set_defaults(func=integrations_aws_update)

def integrations_aws_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/aws/configurations", headers, payload=read_file(args))

def subparser_integrations_aws_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a configuration')
    add_argument_accountId(sp)
    sp.set_defaults(func=integrations_aws_delete)

def integrations_aws_delete(args):
    delete("/api/v1/aws/configurations/" + args.accountId)

def subparser_integrations_aws_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_aws_delete_all)

def integrations_aws_delete_all(args):
    delete("/api/v1/aws/configurations")
# Integrations-AWS end

# Integrations-github start
def subparser_integrations_github_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - github help')

    subparser_integrations_github_add(sp)
    subparser_integrations_github_add_personal(sp)
    subparser_integrations_github_delete(sp)
    subparser_integrations_github_delete_all(sp)
    subparser_integrations_github_delete_personal(sp)
    subparser_integrations_github_get(sp)
    subparser_integrations_github_get_all(sp)
    subparser_integrations_github_get_default(sp)
    subparser_integrations_github_get_personal(sp)
    subparser_integrations_github_update(sp)
    subparser_integrations_github_update_personal(sp)
    subparser_integrations_github_validate(sp)
    subparser_integrations_github_validate_all(sp)

def subparser_integrations_github_add(subparser):
    sp = subparser.add_parser('add', 
            help='Add a single configuration', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "alias": "string",
                  "apiHost": "string",
                  "appUrl": "string",
                  "applicationId": "string",
                  "clientId": "string",
                  "clientSecret": "string",
                  "isDefault": true,
                  "privateKey": "string"
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted github configuration')
    sp.set_defaults(func=integrations_github_add)

def integrations_github_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/github/configurations/app", headers, payload=read_file(args))

def subparser_integrations_github_add_personal(subparser):
    sp = subparser.add_parser('add-personal', 
            help='Add a single personal configuration', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "accessToken": "string",
                  "alias": "string",
                  "apiHost": "string",
                  "isDefault": true
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted github configuration')
    sp.set_defaults(func=integrations_github_add_personal)

def integrations_github_add_personal(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/github/configurations/personal", headers, payload=read_file(args))

def subparser_integrations_github_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_delete)

def integrations_github_delete(args):
    delete("/api/v1/github/configurations/app/" + args.alias)

def subparser_integrations_github_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_github_delete_all)

def integrations_github_delete_all(args):
    delete("/api/v1/github/configurations")

def subparser_integrations_github_delete_personal(subparser):
    sp = subparser.add_parser('delete-personal', help='Delete a personal configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_delete_personal)

def integrations_github_delete_personal(args):
    delete("/api/v1/github/configurations/personal/" + args.alias)

def subparser_integrations_github_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_get)

def integrations_github_get(args):
    get("/api/v1/github/configurations/app/" + args.alias)

def subparser_integrations_github_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_github_get_all)

def integrations_github_get_all(args):
    get("/api/v1/github/configurations")

def subparser_integrations_github_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_github_get_default)

def integrations_github_get_default(args):
    get("/api/v1/github/default-configuration")

def subparser_integrations_github_get_personal(subparser):
    sp = subparser.add_parser('get-personal', help='Get a single personal configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_get_personal)

def integrations_github_get_personal(args):
    get("/api/v1/github/configurations/personal/" + args.alias)

def subparser_integrations_github_get_personal(subparser):
    sp = subparser.add_parser('get-personal', help='Get a single personal configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_get_personal)

def integrations_github_get_personal(args):
    get("/api/v1/github/configurations/personal/" + args.alias)

def subparser_integrations_github_update(subparser):
    sp = subparser.add_parser('update', help='Update a single app configuration.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted github configuration')
    sp.set_defaults(func=integrations_github_update)

def integrations_github_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/github/configurations/app/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_github_update_personal(subparser):
    sp = subparser.add_parser('update-personal', help='Update a single personal configuration.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted github configuration')
    sp.set_defaults(func=integrations_github_update_personal)

def integrations_github_update_personal(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/github/configurations/personal/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_github_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_github_validate)

def integrations_github_validate(args):
    post("/api/v1/github/configurations/validate/" + args.alias)

def subparser_integrations_github_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_github_validate_all)

def integrations_github_validate_all(args):
    post("/api/v1/github/configurations/validate")
# Integrations-github end

# Integrations-gitlab start
def subparser_integrations_gitlab_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - gitlab help')

    subparser_integrations_gitlab_add(sp)
    subparser_integrations_gitlab_add_multiple(sp)
    subparser_integrations_gitlab_delete(sp)
    subparser_integrations_gitlab_delete_all(sp)
    subparser_integrations_gitlab_get(sp)
    subparser_integrations_gitlab_get_all(sp)
    subparser_integrations_gitlab_get_default(sp)
    subparser_integrations_gitlab_update(sp)
    subparser_integrations_gitlab_validate(sp)
    subparser_integrations_gitlab_validate_all(sp)

def subparser_integrations_gitlab_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_file(sp, 'File containing JSON-formatted gitlab configuration')
    sp.set_defaults(func=integrations_gitlab_add)

def integrations_gitlab_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/gitlab/configuration/", headers, payload=read_file(args))

def subparser_integrations_gitlab_add_multiple(subparser):
    sp = subparser.add_parser('add-multiple', 
            help='Add multiple configurations', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "configurations": [
                    {
                      "alias": "string",
                      "groupNames": [
                        "string"
                      ],
                      "hidePersonalProjects": true,
                      "host": "string",
                      "isDefault": true,
                      "personalAccessToken": "string"
                    }
                  ]
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted gitlab configurations')
    sp.set_defaults(func=integrations_gitlab_add_multiple)

def integrations_gitlab_add_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/gitlab/configurations", headers, payload=read_file(args))

def subparser_integrations_gitlab_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_gitlab_delete)

def integrations_gitlab_delete(args):
    delete("/api/v1/gitlab/configuration/" + args.alias)

def subparser_integrations_gitlab_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_gitlab_delete_all)

def integrations_gitlab_delete_all(args):
    delete("/api/v1/gitlab/configurations")

def subparser_integrations_gitlab_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_gitlab_get)

def integrations_gitlab_get(args):
    get("/api/v1/gitlab/configuration/" + args.alias)

def subparser_integrations_gitlab_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_gitlab_get_all)

def integrations_gitlab_get_all(args):
    get("/api/v1/gitlab/configurations")

def subparser_integrations_gitlab_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_gitlab_get_default)

def integrations_gitlab_get_default(args):
    get("/api/v1/gitlab/default-configuration")

def subparser_integrations_gitlab_update(subparser):
    sp = subparser.add_parser('update', help='WARNING: Updating aliases for configurations or changing the default configuration could cause entity YAMLs that use this integration to break.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted gitlab configuration')
    sp.set_defaults(func=integrations_gitlab_update)

def integrations_gitlab_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/gitlab/configuration/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_gitlab_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configuration')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_gitlab_validate)

def integrations_gitlab_validate(args):
    post("/api/v1/gitlab/configuration/validate/" + args.alias)

def subparser_integrations_gitlab_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_gitlab_validate_all)

def integrations_gitlab_validate_all(args):
    post("/api/v1/gitlab/configuration/validate")
# Integrations-gitlab end

# Integrations-datadog start
def subparser_integrations_datadog_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - datadog help')

    subparser_integrations_datadog_add(sp)
    subparser_integrations_datadog_add_multiple(sp)
    subparser_integrations_datadog_delete(sp)
    subparser_integrations_datadog_delete_all(sp)
    subparser_integrations_datadog_get(sp)
    subparser_integrations_datadog_get_all(sp)
    subparser_integrations_datadog_get_default(sp)
    subparser_integrations_datadog_update(sp)

def subparser_integrations_datadog_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_file(sp, 'File containing JSON-formatted datadog configuration')
    sp.set_defaults(func=integrations_datadog_add)

def integrations_datadog_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/datadog/configuration/", headers, payload=read_file(args))

def subparser_integrations_datadog_add_multiple(subparser):
    sp = subparser.add_parser('add-multiple', 
            help='Add multiple configurations', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "alias": "string",
                  "apiKey": "string",
                  "appKey": "string",
                  "customSubdomain": "string",
                  "environments": [
                    "string"
                  ],
                  "isDefault": true,
                  "region": "EU1"
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted datadog configurations')
    sp.set_defaults(func=integrations_datadog_add_multiple)

def integrations_datadog_add_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/datadog/configurations", headers, payload=read_file(args))

def subparser_integrations_datadog_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_datadog_delete)

def integrations_datadog_delete(args):
    delete("/api/v1/datadog/configuration/" + args.alias)

def subparser_integrations_datadog_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_datadog_delete_all)

def integrations_datadog_delete_all(args):
    delete("/api/v1/datadog/configurations")

def subparser_integrations_datadog_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_datadog_get)

def integrations_datadog_get(args):
    get("/api/v1/datadog/configuration/" + args.alias)

def subparser_integrations_datadog_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_datadog_get_all)

def integrations_datadog_get_all(args):
    get("/api/v1/datadog/configurations")

def subparser_integrations_datadog_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_datadog_get_default)

def integrations_datadog_get_default(args):
    get("/api/v1/datadog/default-configuration")

def subparser_integrations_datadog_update(subparser):
    sp = subparser.add_parser('update', help='WARNING: Updating aliases for configurations or changing the default configuration could cause entity YAMLs that use this integration to break.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted datadog configuration')
    sp.set_defaults(func=integrations_datadog_update)

def integrations_datadog_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/datadog/configuration/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_datadog_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_datadog_validate)

def integrations_datadog_validate(args):
    post("/api/v1/datadog/configuration/validate/" + args.alias)

def subparser_integrations_datadog_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_datadog_validate_all)

def integrations_datadog_validate_all(args):
    post("/api/v1/datadog/configuration/validate")
# Integrations-datadog end

# Integrations-prometheus start
def subparser_integrations_prometheus_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - prometheus help')

    subparser_integrations_prometheus_add(sp)
    subparser_integrations_prometheus_add_multiple(sp)
    subparser_integrations_prometheus_delete(sp)
    subparser_integrations_prometheus_delete_all(sp)
    subparser_integrations_prometheus_get(sp)
    subparser_integrations_prometheus_get_all(sp)
    subparser_integrations_prometheus_get_default(sp)
    subparser_integrations_prometheus_update(sp)

def subparser_integrations_prometheus_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_file(sp, 'File containing JSON-formatted prometheus configuration')
    sp.set_defaults(func=integrations_prometheus_add)

def integrations_prometheus_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/prometheus/configuration/", headers, payload=read_file(args))

def subparser_integrations_prometheus_add_multiple(subparser):
    sp = subparser.add_parser('add-multiple', 
            help='Add multiple configurations', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "alias": "string",
                  "host": "string",
                  "isDefault": true,
                  "password": "string",
                  "prometheusTenantId": "string",
                  "username": "string"
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted prometheus configurations')
    sp.set_defaults(func=integrations_prometheus_add_multiple)

def integrations_prometheus_add_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/prometheus/configurations", headers, payload=read_file(args))

def subparser_integrations_prometheus_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_prometheus_delete)

def integrations_prometheus_delete(args):
    delete("/api/v1/prometheus/configuration/" + args.alias)

def subparser_integrations_prometheus_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_prometheus_delete_all)

def integrations_prometheus_delete_all(args):
    delete("/api/v1/prometheus/configurations")

def subparser_integrations_prometheus_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_prometheus_get)

def integrations_prometheus_get(args):
    get("/api/v1/prometheus/configuration/" + args.alias)

def subparser_integrations_prometheus_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_prometheus_get_all)

def integrations_prometheus_get_all(args):
    get("/api/v1/prometheus/configurations")

def subparser_integrations_prometheus_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_prometheus_get_default)

def integrations_prometheus_get_default(args):
    get("/api/v1/prometheus/default-configuration")

def subparser_integrations_prometheus_update(subparser):
    sp = subparser.add_parser('update', help='WARNING: Updating aliases for configurations or changing the default configuration could cause entity YAMLs that use this integration to break.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted prometheus configuration')
    sp.set_defaults(func=integrations_prometheus_update)

def integrations_prometheus_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/prometheus/configuration/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_prometheus_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_prometheus_validate)

def integrations_prometheus_validate(args):
    post("/api/v1/prometheus/configuration/validate/" + args.alias)

def subparser_integrations_prometheus_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_prometheus_validate_all)

def integrations_prometheus_validate_all(args):
    post("/api/v1/prometheus/configuration/validate")
# Integrations-prometheus end

# Integrations-newrelic start
def subparser_integrations_newrelic_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - newrelic help')

    subparser_integrations_newrelic_add(sp)
    subparser_integrations_newrelic_add_multiple(sp)
    subparser_integrations_newrelic_delete(sp)
    subparser_integrations_newrelic_delete_all(sp)
    subparser_integrations_newrelic_get(sp)
    subparser_integrations_newrelic_get_all(sp)
    subparser_integrations_newrelic_get_default(sp)
    subparser_integrations_newrelic_update(sp)
    subparser_integrations_newrelic_validate(sp)
    subparser_integrations_newrelic_validate_all(sp)

def subparser_integrations_newrelic_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_file(sp, 'File containing JSON-formatted newrelic configuration')
    sp.set_defaults(func=integrations_newrelic_add)

def integrations_newrelic_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/newrelic/configuration/", headers, payload=read_file(args))

def subparser_integrations_newrelic_add_multiple(subparser):
    sp = subparser.add_parser('add-multiple', 
            help='Add multiple configurations', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "accountId": 0,
                  "alias": "string",
                  "isDefault": true,
                  "personalKey": "string",
                  "region": "US"
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted newrelic configurations')
    sp.set_defaults(func=integrations_newrelic_add_multiple)

def integrations_newrelic_add_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/newrelic/configurations", headers, payload=read_file(args))

def subparser_integrations_newrelic_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_newrelic_delete)

def integrations_newrelic_delete(args):
    delete("/api/v1/newrelic/configuration/" + args.alias)

def subparser_integrations_newrelic_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_newrelic_delete_all)

def integrations_newrelic_delete_all(args):
    delete("/api/v1/newrelic/configurations")

def subparser_integrations_newrelic_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_newrelic_get)

def integrations_newrelic_get(args):
    get("/api/v1/newrelic/configuration/" + args.alias)

def subparser_integrations_newrelic_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_newrelic_get_all)

def integrations_newrelic_get_all(args):
    get("/api/v1/newrelic/configurations")

def subparser_integrations_newrelic_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_newrelic_get_default)

def integrations_newrelic_get_default(args):
    get("/api/v1/newrelic/default-configuration")

def subparser_integrations_newrelic_update(subparser):
    sp = subparser.add_parser('update', help='WARNING: Updating aliases for configurations or changing the default configuration could cause entity YAMLs that use this integration to break.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted newrelic configuration')
    sp.set_defaults(func=integrations_newrelic_update)

def integrations_newrelic_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/newrelic/configuration/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_newrelic_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_newrelic_validate)

def integrations_newrelic_validate(args):
    post("/api/v1/newrelic/configuration/validate/" + args.alias)

def subparser_integrations_newrelic_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_newrelic_validate_all)

def integrations_newrelic_validate_all(args):
    post("/api/v1/newrelic/configuration/validate")
# Integrations-newrelic end

# Integrations-sonarqube start
def subparser_integrations_sonarqube_opts(subparser):
    sp = subparser.add_subparsers(help='integrations - sonarqube help')

    subparser_integrations_sonarqube_add(sp)
    subparser_integrations_sonarqube_add_multiple(sp)
    subparser_integrations_sonarqube_delete(sp)
    subparser_integrations_sonarqube_delete_all(sp)
    subparser_integrations_sonarqube_get(sp)
    subparser_integrations_sonarqube_get_all(sp)
    subparser_integrations_sonarqube_get_default(sp)
    subparser_integrations_sonarqube_update(sp)
    subparser_integrations_sonarqube_validate(sp)
    subparser_integrations_sonarqube_validate_all(sp)

def subparser_integrations_sonarqube_add(subparser):
    sp = subparser.add_parser('add', help='Add a single configuration')
    add_argument_file(sp, 'File containing JSON-formatted sonarqube configuration')
    sp.set_defaults(func=integrations_sonarqube_add)

def integrations_sonarqube_add(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/sonarqube/configuration/", headers, payload=read_file(args))

def subparser_integrations_sonarqube_add_multiple(subparser):
    sp = subparser.add_parser('add-multiple', 
            help='Add multiple configurations', 
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "alias": "string",
                  "host": "string",
                  "isDefault": true,
                  "token": "string"
                }
                '''))
    add_argument_file(sp, 'File containing JSON-formatted sonarqube configurations')
    sp.set_defaults(func=integrations_sonarqube_add_multiple)

def integrations_sonarqube_add_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/sonarqube/configurations", headers, payload=read_file(args))

def subparser_integrations_sonarqube_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_sonarqube_delete)

def integrations_sonarqube_delete(args):
    delete("/api/v1/sonarqube/configuration/" + args.alias)

def subparser_integrations_sonarqube_delete_all(subparser):
    sp = subparser.add_parser('delete-all', help='Delete all configurations')
    sp.set_defaults(func=integrations_sonarqube_delete_all)

def integrations_sonarqube_delete_all(args):
    delete("/api/v1/sonarqube/configurations")

def subparser_integrations_sonarqube_get(subparser):
    sp = subparser.add_parser('get', help='Get a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_sonarqube_get)

def integrations_sonarqube_get(args):
    get("/api/v1/sonarqube/configuration/" + args.alias)

def subparser_integrations_sonarqube_get_all(subparser):
    sp = subparser.add_parser('get-all', help='Get all configurations')
    sp.set_defaults(func=integrations_sonarqube_get_all)

def integrations_sonarqube_get_all(args):
    get("/api/v1/sonarqube/configurations")

def subparser_integrations_sonarqube_get_default(subparser):
    sp = subparser.add_parser('get-default', help='Get default configuration')
    sp.set_defaults(func=integrations_sonarqube_get_default)

def integrations_sonarqube_get_default(args):
    get("/api/v1/sonarqube/default-configuration")

def subparser_integrations_sonarqube_update(subparser):
    sp = subparser.add_parser('update', help='WARNING: Updating aliases for configurations or changing the default configuration could cause entity YAMLs that use this integration to break.')
    add_argument_alias(sp)
    add_argument_file(sp, 'File containing JSON-formatted sonarqube configuration')
    sp.set_defaults(func=integrations_sonarqube_update)

def integrations_sonarqube_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/sonarqube/configuration/" + args.alias, headers, payload=read_file(args))

def subparser_integrations_sonarqube_validate(subparser):
    sp = subparser.add_parser('validate', help='Validate a single configurations')
    add_argument_alias(sp)
    sp.set_defaults(func=integrations_sonarqube_validate)

def integrations_sonarqube_validate(args):
    post("/api/v1/sonarqube/configuration/validate/" + args.alias)

def subparser_integrations_sonarqube_validate_all(subparser):
    sp = subparser.add_parser('validate-all', help='Validate all configurations')
    sp.set_defaults(func=integrations_sonarqube_validate_all)

def integrations_sonarqube_validate_all(args):
    post("/api/v1/sonarqube/configuration/validate")
# Integrations-sonarqube end

# IP Allowlist start
def subparser_ip_allowlist_opts(subparsers):
    p = subparsers.add_parser('ip-allowlist', help='IP Allowlist information')
    sp = p.add_subparsers(help='IP Allowlist help')

    subparser_ip_allowlist_get(sp)
    subparser_ip_allowlist_replace(sp)
    subparser_ip_allowlist_validate(sp)

def subparser_ip_allowlist_get(subparser):
    sp = subparser.add_parser('get', help='Get allowlist of IP addresses and ranges')
    sp.set_defaults(func=ip_allowlist_get)

def ip_allowlist_get(args):
    get("/api/v1/ip-allowlist")

def subparser_ip_allowlist_replace(subparser):
    sp = subparser.add_parser('replace',
            help='Replace allowlist of IP addresses and ranges',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "entries": [
                    {
                      "address": "10.0.0.1",
                      "description": "string"
                    }
                  ]
                }
                '''))
    add_argument_file(sp, 'file containing JSON-formatted content of IP allowlist entries')
    sp.set_defaults(func=ip_allowlist_replace)

def ip_allowlist_replace(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/ip-allowlist", headers, read_file(args))

def subparser_ip_allowlist_validate(subparser):
    sp = subparser.add_parser('validate',
            help='Validate allowlist of IP addresses and ranges',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "entries": [
                    {
                      "address": "10.0.0.1",
                      "description": "string"
                    }
                  ]
                }
                '''))
    add_argument_file(sp, 'file containing JSON-formatted content of IP allowlist entries')
    sp.set_defaults(func=ip_allowlist_get)

def ip_allowlist_validate(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/ip-allowlist/validate", headers, read_file(args))
# IP Allowlist end

# On-Call start
def subparser_on_call_opts(subparsers):
    p = subparsers.add_parser('on-call', help='get on-call information')
    sp = p.add_subparsers(help='on-call help')

    subparser_on_call_get(sp)
    subparser_on_call_get_registration(sp)

def subparser_on_call_get(subparser):
    sp = subparser.add_parser('get', help='Get current on-call for an entity')
    sp.set_defaults(func=on_call_get)

def on_call_get(args):
    get("/api/v1/catalog/" + args.tag + "/integrations/oncall/current")

def subparser_on_call_get_registration(subparser):
    sp = subparser.add_parser('get-registration', help='Retrieve on-call registration for entity')
    add_argument_tag(sp)
    sp.set_defaults(func=on_call_get_registration)

def on_call_get_registration(args):
    get("/api/v1/catalog/" + args.tag + "/integrations/oncall/registration")
# On-Call end

# Packages start
def subparser_packages_opts(subparsers):
    p = subparsers.add_parser('packages', help='commands to create and modify packages')
    sp = p.add_subparsers(help='packages help')

    subparser_packages_list_packages(sp)
    ssp = sp.add_parser('go', help='Go package commands')
    subparser_packages_go_opts(ssp)
    ssp = sp.add_parser('java', help='Java package commands')
    subparser_packages_java_opts(ssp)
    ssp = sp.add_parser('python', help='Python package commands')
    subparser_packages_python_opts(ssp)
    ssp = sp.add_parser('node', help='Node package commands')
    subparser_packages_node_opts(ssp)
    ssp = sp.add_parser('nuget', help='NuGet package commands')
    subparser_packages_nuget_opts(ssp)

def subparser_packages_list_packages(subparser):
    sp = subparser.add_parser('list', help='List packages')
    add_argument_tag(sp)
    sp.set_defaults(func=packages_list_packages)

def packages_list_packages(args):
    get("/api/v1/catalog/"+ args.tag + "/packages")

def subparser_packages_go_opts(subparser):
    sp = subparser.add_subparsers(help='Go package sub-commands.')

    subparser_packages_upload_go(sp)
    subparser_packages_delete_go(sp)

def subparser_packages_upload_go(subparser):
    sp = subparser.add_parser('upload', help='Upload go.sum package.')
    add_argument_tag(sp)
    add_argument_file(sp, 'File containing contents of go.sum')
    sp.set_defaults(func=packages_upload_go)

def packages_upload_go(args):
    headers = { 'Content-Type': 'application/text;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/go/gosum", headers, read_file(args))

def subparser_packages_delete_go(subparser):
    sp = subparser.add_parser('delete', help='Delete go package from entity')
    add_argument_tag(sp)
    add_argument_name(sp, "The name of the package to delete")
    sp.set_defaults(func=packages_delete_go)

def packages_delete_go(args):
    delete("/api/v1/catalog/"+ args.tag + "/packages/go" + parse_opts(args))

def subparser_packages_java_opts(subparser):
    sp = subparser.add_subparsers(help='Java package sub-commands.')

    subparser_packages_upload_java_single(sp)
    subparser_packages_upload_java_multiple(sp)
    subparser_packages_delete_java(sp)

def subparser_packages_upload_java_single(subparser):
    sp = subparser.add_parser('upload-single', help='Upload single java package')
    add_argument_tag(sp)
    add_argument_file(sp, 'JSON file containing contents of single java package')
    sp.set_defaults(func=packages_upload_java_single)

def packages_upload_java_single(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/java", headers, read_file(args))

def subparser_packages_upload_java_multiple(subparser):
    sp = subparser.add_parser('upload-multiple', help='Upload multiple java packages')
    add_argument_tag(sp)
    add_argument_file(sp, 'JSON file containing array of java packages')
    sp.set_defaults(func=packages_upload_java_multiple)

def packages_upload_java_multiple(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/java/bulk", headers, read_file(args))

def subparser_packages_delete_java(subparser):
    sp = subparser.add_parser('delete', help='Delete java package from entity')
    add_argument_tag(sp)
    add_argument_name(sp, "The name of the package to delete")
    sp.set_defaults(func=packages_delete_java)

def packages_delete_java(args):
    delete("/api/v1/catalog/"+ args.tag + "/packages/java" + parse_opts(args))

def subparser_packages_python_opts(subparser):
    sp = subparser.add_subparsers(help='Python package sub-commands.')

    subparser_packages_upload_python_pipfile(sp)
    subparser_packages_upload_python_requirements(sp)
    subparser_packages_delete_python(sp)

def subparser_packages_upload_python_pipfile(subparser):
    sp = subparser.add_parser('upload-pipfile', help='Upload python pipfile.lock file')
    add_argument_tag(sp)
    add_argument_file(sp, 'pipfile.lock file')
    sp.set_defaults(func=packages_upload_python_pipfile)

def packages_upload_python_pipfile(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/python/pipfile", headers, read_file(args))

def subparser_packages_upload_python_requirements(subparser):
    sp = subparser.add_parser('upload-requirements', help='Upload python requirements.txt file')
    add_argument_tag(sp)
    add_argument_file(sp, 'requirements.txt file')
    sp.set_defaults(func=packages_upload_python_requirements)

def packages_upload_python_requirements(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/python/requirements", headers, read_file(args))

def subparser_packages_delete_python(subparser):
    sp = subparser.add_parser('delete', help='Delete python package from entity')
    add_argument_tag(sp)
    add_argument_name(sp, "The name of the package to delete")
    sp.set_defaults(func=packages_delete_python)

def packages_delete_python(args):
    delete("/api/v1/catalog/"+ args.tag + "/packages/python" + parse_opts(args))

def subparser_packages_node_opts(subparser):
    sp = subparser.add_subparsers(help='Node package sub-commands.')

    subparser_packages_upload_node_package(sp)
    subparser_packages_upload_node_package_lock(sp)
    subparser_packages_upload_node_yarn_lock(sp)
    subparser_packages_delete_node(sp)

def subparser_packages_upload_node_package(subparser):
    sp = subparser.add_parser('upload-package', help='Upload node package.json file')
    add_argument_tag(sp)
    add_argument_file(sp, 'package.json file')
    sp.set_defaults(func=packages_upload_node_package)

def packages_upload_node_package(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/node/package-json", headers, read_file(args))

def subparser_packages_upload_node_package_lock(subparser):
    sp = subparser.add_parser('upload-package-lock', help='Upload node package-lock.json file')
    add_argument_tag(sp)
    add_argument_file(sp, 'package-lock.json file')
    sp.set_defaults(func=packages_upload_node_package_lock)

def packages_upload_node_package_lock(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/node/package-lock", headers, read_file(args))

def subparser_packages_upload_node_yarn_lock(subparser):
    sp = subparser.add_parser('upload-yarn-lock', help='Upload yarn.lock file')
    add_argument_tag(sp)
    add_argument_file(sp, 'yarn.lock file')
    sp.set_defaults(func=packages_upload_node_yarn_lock)

def packages_upload_node_yarn_lock(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/node/yarn-lock", headers, read_file(args))

def subparser_packages_delete_node(subparser):
    sp = subparser.add_parser('delete', help='Delete node package from entity')
    add_argument_tag(sp)
    add_argument_name(sp, "The name of the package to delete")
    sp.set_defaults(func=packages_delete_node)

def packages_delete_node(args):
    delete("/api/v1/catalog/"+ args.tag + "/packages/node" + parse_opts(args))

def subparser_packages_nuget_opts(subparser):
    sp = subparser.add_subparsers(help='NuGet package sub-commands.')

    subparser_packages_upload_nuget_csproj(sp)
    subparser_packages_upload_nuget_packages_lock(sp)
    subparser_packages_delete_nuget(sp)

def subparser_packages_upload_nuget_csproj(subparser):
    sp = subparser.add_parser('upload-csproj', help='Upload Nuget csproj')
    add_argument_tag(sp)
    add_argument_file(sp, '*.csproj file')
    sp.set_defaults(func=packages_upload_nuget_csproj)

def packages_upload_nuget_csproj(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/dotnet/nuget/csproj", headers, read_file(args))

def subparser_packages_upload_nuget_packages_lock(subparser):
    sp = subparser.add_parser('upload-packages-lock', help='Upload Nuget packages.lock.json')
    add_argument_tag(sp)
    add_argument_file(sp, 'packages.lock.json file')
    sp.set_defaults(func=packages_upload_nuget_packages_lock)

def packages_upload_nuget_packages_lock(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/"+ args.tag + "/packages/dotnet/nuget/packages-lock", headers, read_file(args))

def subparser_packages_delete_nuget(subparser):
    sp = subparser.add_parser('delete', help='Delete nuget package from entity')
    add_argument_tag(sp)
    add_argument_name(sp, "The name of the package to delete")
    sp.set_defaults(func=packages_delete_nuget)

def packages_delete_nuget(args):
    delete("/api/v1/catalog/"+ args.tag + "/packages/dotnet/nuget" + parse_opts(args))
# Packages end

# Plugins start
def subparser_plugins_opts(subparsers):
    p = subparsers.add_parser('plugins', help='commands to create and access plugins')
    sp = p.add_subparsers(help='plugins help')

    subparser_plugins_create(sp)
    subparser_plugins_delete(sp)
    subparser_plugins_get(sp)
    subparser_plugins_get_by_tag(sp)
    subparser_plugins_update(sp)

def subparser_plugins_create(subparser):
    sp = subparser.add_parser('create',
            help='Create a new plugin',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "blob": "string",
                  "contexts": [
                    {
                      "type": "string"
                    }
                  ],
                  "description": "string",
                  "isDraft": true,
                  "minimumRoleRequired": "VIEWER",
                  "name": "string",
                  "proxyTag": "string",
                  "tag": "string"
                }

                Additional documentation
                ------------------------
                https://docs.cortex.io/docs/api/create-plugin
                '''))
    add_argument_file(sp, 'File containing JSON-formatted body of plugin definition')
    sp.set_defaults(func=plugins_create)

def plugins_create(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/plugins", headers, payload=read_file(args))

def subparser_plugins_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a plugin by tag')
    add_argument_tag(sp, 'The tag of the plugin.')
    sp.set_defaults(func=plugins_delete)

def plugins_delete(args):
    delete("/api/v1/plugins/" + args.tag, expected_rc=204)

def subparser_plugins_get(subparser):
    sp = subparser.add_parser('get', help='Get all plugins, excluding drafts')
    add_argument_includeDrafts(sp)
    sp.set_defaults(func=plugins_get)

def plugins_get(args):
    get("/api/v1/plugins" + parse_opts(args))

def subparser_plugins_get_by_tag(subparser):
    sp = subparser.add_parser('get-by-tag', help='Retrieve the metadata of a plugin by tag')
    add_argument_tag(sp, 'The tag of the plugin.')
    sp.set_defaults(func=plugins_get_by_tag)

def plugins_get_by_tag(args):
    get("/api/v1/plugins/" + args.tag)

def subparser_plugins_update(subparser):
    sp = subparser.add_parser('update',
            help='Create a new plugin',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "blob": "string",
                  "contexts": [
                    {
                      "type": "string"
                    }
                  ],
                  "description": "string",
                  "isDraft": true,
                  "minimumRoleRequired": "VIEWER",
                  "name": "string",
                  "proxyTag": "string",
                }

                Additional documentation
                ------------------------
                https://docs.cortex.io/docs/api/update-plugin
                '''))
    add_argument_file(sp, 'File containing JSON-formatted body of plugin definition')
    add_argument_tag(sp, 'The tag of the plugin.')
    sp.set_defaults(func=plugins_update)

def plugins_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/plugins/" + args.tag, headers, payload=read_file(args))
# Plugins end

# Queries start
def subparser_queries_opts(subparsers):
    p = subparsers.add_parser('queries', help='run CQL queries')
    sp = p.add_subparsers(help='queries help')

    subparser_queries_run(sp)
    subparser_queries_get(sp)

def subparser_queries_run(subparser):
    sp = subparser.add_parser('run', help='Run CQL query')
    add_argument_file(sp, 'File containing JSON-formatted CQL query')
    sp.set_defaults(func=queries_run)

def queries_run(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/queries", headers, payload=read_file(args))

def subparser_queries_get(subparser):
    sp = subparser.add_parser('get', help='Get results of a CQL query')
    add_argument_id(sp)
    sp.set_defaults(func=queries_get)

def queries_get(args):
    get("/api/v1/queries/" + args.id)
# Queries end

# Resource Definitions start
def subparser_resource_definitions_opts(subparsers):
    p = subparsers.add_parser('resource-definitions', help='resource definitions')
    sp = p.add_subparsers(help='resource_definitions help')

    subparser_resource_definitions_create(sp)
    subparser_resource_definitions_list(sp)
    subparser_resource_definitions_delete(sp)
    subparser_resource_definitions_retrieve(sp)
    subparser_resource_definitions_update(sp)

def subparser_resource_definitions_create(subparser):
    sp = subparser.add_parser('create',
            help='Create definition',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "description": "string",
                  "name": "string",
                  "schema": {},
                  "type": "string"
                }

                Examples:
                ---------
                Custom resource without any additional schema:
                {
                  "description": "Open Policy Definitions",
                  "name": "OPA Policy",
                  "schema": {},
                  "type": "opa"
                }

                Custom resource with a defined schema:
                {
                  "description": "Resource to capture and catalog basic attributes of a CI/CD system",
                  "name": "CI/CD Tooling",
                  "schema": {
                  {
                    "required": [
                      "version",
                      "vendor"
                    ],
                    "properties": {
                      "version": {
                        "type": "string"
                      },
                      "vendor": {
                        "type": "string"
                      }
                    }
                  }
                  "type": "ci-cd"
                }


                Additional documentation
                ------------------------
                https://docs.cortex.io/docs/reference/basics/resource-catalog
                https://docs.cortex.io/docs/api/create-definition

                Related commands
                ----------------
                cortex resource
                   CLI command to add, update and delete resources.
                '''))
    add_argument_file(sp, 'File containing JSON-formatted resource definition')
    sp.set_defaults(func=resource_definitions_create)

def resource_definitions_create(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/catalog/definitions", headers, read_file(args))

def subparser_resource_definitions_list(subparser):
    sp = subparser.add_parser('list', help='List definition')
    sp.set_defaults(func=resource_definitions_list)

def resource_definitions_list(args):
    get("/api/v1/catalog/definitions")

def subparser_resource_definitions_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete definition')
    add_argument_type(sp)
    sp.set_defaults(func=resource_definitions_delete)

def resource_definitions_delete(args):
    delete("/api/v1/catalog/definitions/" + args.type)

def subparser_resource_definitions_retrieve(subparser):
    sp = subparser.add_parser('get', help='Get definition')
    add_argument_type(sp)
    sp.set_defaults(func=resource_definitions_retrieve)

def resource_definitions_retrieve(args):
    get("/api/v1/catalog/definitions/" + args.type)

def subparser_resource_definitions_update(subparser):
    sp = subparser.add_parser('update', help='Update definition')
    add_argument_type(sp)
    add_argument_file(sp, 'File containing updated JSON schema for resource definition')
    add_argument_force(sp)
    sp.set_defaults(func=resource_definitions_update)

def resource_definitions_update(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/catalog/definitions/" + args.type + parse_opts(args), headers, payload=read_file(args))
# Resource Definitions end

# Scorecards start
def subparser_scorecards_opts(subparsers):
    p = subparsers.add_parser('scorecards', help='scorecards API requests')
    sp = p.add_subparsers(help='scorecards help')

    subparser_scorecards_create_or_update(sp)
    subparser_scorecards_delete(sp)
    subparser_scorecards_list(sp)
    subparser_scorecards_shields_io_badge(sp)
    subparser_scorecards_get(sp)
    subparser_scorecards_descriptor(sp)
    subparser_scorecards_next_steps(sp)
    subparser_scorecards_scores(sp)

def subparser_scorecards_create_or_update(subparser):
    sp = subparser.add_parser('create', help='Create definition')
    add_argument_file(sp, 'File containing openapi descriptor for scorecard')
    sp.set_defaults(func=scorecards_create_or_update)

def scorecards_create_or_update(args):
    headers = { 'Content-Type': 'application/yaml;charset=UTF-8' }
    post("/api/v1/scorecards/descriptor", headers, read_file(args))

def subparser_scorecards_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete scorecard')
    add_argument_tag(sp)
    sp.set_defaults(func=scorecards_delete)

def scorecards_delete(args):
    delete("/api/v1/scorecards/" + args.tag)

def subparser_scorecards_list(subparser):
    sp = subparser.add_parser('list', help='List scorecards')
    sp.set_defaults(func=scorecards_list)

def scorecards_list(args):
    get("/api/v1/scorecards")

def subparser_scorecards_shields_io_badge(subparser):
    sp = subparser.add_parser('shield', help='Retrieve scorecard shields.io badge')
    add_argument_scorecard_tag(sp)
    add_argument_tag(sp)
    sp.set_defaults(func=scorecards_shields_io_badge)

def scorecards_shields_io_badge(args):
    get("/api/v1/scorecards/" + args.scorecardTag + "/entity/" + args.tag + "/badge")

def subparser_scorecards_get(subparser):
    sp = subparser.add_parser('get', help='Retrieve scorecard')
    add_argument_tag(sp, 'Unique tag for the Scorecard')
    sp.set_defaults(func=scorecards_get)

def scorecards_get(args):
    get("/api/v1/scorecards/" + args.tag)

def subparser_scorecards_descriptor(subparser):
    sp = subparser.add_parser('descriptor', help='Retrieve scorecard descriptor')
    add_argument_tag(sp)
    sp.set_defaults(func=scorecards_descriptor)

def scorecards_descriptor(args):
    get("/api/v1/scorecards/" + args.tag + "/descriptor")

def subparser_scorecards_next_steps(subparser):
    sp = subparser.add_parser('next-steps', help='Retrieve next steps for entity in scorecard')
    add_argument_tag(sp, 'Unique tag for the scorecard')
    add_argument_entity_tag(sp)
    sp.set_defaults(func=scorecards_next_steps)

def scorecards_next_steps(args):
    get("/api/v1/scorecards/" + args.tag + "/next-steps" + parse_opts(args))

def subparser_scorecards_scores(subparser):
    sp = subparser.add_parser('scores', help='Return latest scores fot all entities in the Scorecard')
    add_argument_tag(sp, 'Unique tag for the scorecard')
    add_argument_entity_tag(sp)
    sp.set_defaults(func=scorecards_scores)

def scorecards_scores(args):
    get("/api/v1/scorecards/" + args.tag + "/scores" + parse_opts(args))
# Scorecards end

# Teams Hierarchies start
def subparser_teams_hierarchies_opts(subparsers):
    p = subparsers.add_parser('teams-hierarchies', help='commands to create and modify team hierarchies')
    sp = p.add_subparsers(help='teams hierarchies help')

    subparser_teams_hierarchies_create(sp)
    subparser_teams_hierarchies_get(sp)
    subparser_teams_hierarchies_delete(sp)
    subparser_teams_hierarchies_relationships(sp)

def subparser_teams_hierarchies_create(subparser):
    sp = subparser.add_parser('create', 
            help='Create a department',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Format of JSON-formatted configuration file:
                --------------------------------------------
                {
                  "departmentTag": "string",
                  "description": "string",
                  "members": [
                    {
                      "description": "string",
                      "email": "string",
                      "name": "string"
                    }
                  ],
                  "name": "string"
                }
                '''))
    add_argument_file(sp, 'file containing JSON-formatted content for new department')
    sp.set_defaults(func=teams_hierarchies_create)

def teams_hierarchies_create(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/teams/departments", headers, read_file(args))

def subparser_teams_hierarchies_get(subparser):
    sp = subparser.add_parser('get', help='Get department details')
    add_argument_departmentTag(sp)
    sp.set_defaults(func=teams_hierarchies_get)

def teams_hierarchies_get(args):
    get("/api/v1/teams/departments/" + parse_opts(args))

def subparser_teams_hierarchies_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete a department')
    add_argument_departmentTag(sp)
    sp.set_defaults(func=teams_hierarchies_delete)

def teams_hierarchies_delete(args):
    delete("/api/v1/teams/departments/" + parse_opts(args))

def subparser_teams_hierarchies_relationships(subparser):
    sp = subparser.add_parser('relationships', help='Get team relationships')
    sp.set_defaults(func=teams_hierarchies_relationships)

def teams_hierarchies_relationships(args):
    get("/api/v1/teams/relationships")
# Teams hierarchies end

# Teams start
def subparser_teams_opts(subparsers):
    p = subparsers.add_parser('teams', help='commands to create and modify teams')
    sp = p.add_subparsers(help='team help')

    subparser_teams_create(sp)
    subparser_teams_get(sp)
    subparser_teams_list(sp)
    subparser_teams_delete(sp)
    subparser_teams_archive(sp)
    subparser_teams_unarchive(sp)
    subparser_teams_update_metadata(sp)
    subparser_teams_update_members(sp)

def subparser_teams_create(subparser):
    sp = subparser.add_parser('create', help='Create team')
    add_argument_file(sp, 'file containing team openapi definition')
    sp.set_defaults(func=teams_create)

def teams_create(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/teams", headers, read_file(args))

def subparser_teams_get(subparser):
    sp = subparser.add_parser('get', help='Get team details')
    add_argument_teamTag(sp)
    sp.set_defaults(func=teams_get)

def teams_get(args):
    get("/api/v1/teams/" + args.teamTag)

def subparser_teams_list(subparser):
    sp = subparser.add_parser('list', help='List teams')
    add_argument_includeTeamsWithoutMembers(sp)
    sp.set_defaults(func=teams_list)

def teams_list(args):
    get("/api/v1/teams" + parse_opts(args))

def subparser_teams_delete(subparser):
    sp = subparser.add_parser('delete', help='Delete team')
    add_argument_teamTag(sp, help_text="Name of team")
    sp.set_defaults(func=teams_delete)

def teams_delete(args):
    delete("/api/v1/teams" + parse_opts(args), expected_rc=204)

def subparser_teams_archive(subparser):
    sp = subparser.add_parser('archive', help='Archive team')
    add_argument_tag(sp, help_text="Name of team")
    sp.set_defaults(func=teams_archive)

def teams_archive(args):
    put("/api/v1/teams/" + args.tag + "/archive")

def subparser_teams_unarchive(subparser):
    sp = subparser.add_parser('unarchive', help='Unarchive team')
    add_argument_tag(sp, help_text="Name of team")
    sp.set_defaults(func=teams_unarchive)

def teams_unarchive(args):
    put("/api/v1/teams/" + args.tag + "/unarchive")

def subparser_teams_update_metadata(subparser):
    sp = subparser.add_parser('update-metadata', help='Update team metadata')
    add_argument_teamTag(sp)
    add_argument_file(sp, 'JSON file containing team metadata updates')
    sp.set_defaults(func=teams_update_metadata)

def teams_update_metadata(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    put("/api/v1/teams/" + args.teamTag, headers, read_file(args))

def subparser_teams_update_members(subparser):
    sp = subparser.add_parser('update-members', help='[Cortex-managed teams] Update team members')
    add_argument_teamTag(sp)
    add_argument_file(sp, 'JSON file containing team member updates')
    sp.set_defaults(func=teams_update_members)

def teams_update_members(args):
    headers = { 'Content-Type': 'application/json;charset=UTF-8' }
    post("/api/v1/teams" + parse_opts(args) + "/members", headers, read_file(args))
# Teams end

# The default input to parser.parse_args is sys.argv[1:], but we are passing args
# to cli (to facilitate simpler testing in pytest), so we need to set the default
# if args comes in from sys.argv.
def cli(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
            prog='cortex CLI',
            description='Cortex command line interface',
            formatter_class=argparse.RawTextHelpFormatter, 
            epilog=textwrap.dedent('''\
                Type 'man cortex' for additional details.
                '''))
    parser.add_argument('-a', '--cliAlias', help='get CLI parms from [TENANT.aliases] in config file',metavar='')
    parser.add_argument('-c', '--config', help='Config location, default = ~/.cortex/config', default=os.path.expanduser('~') + '/.cortex/config')
    parser.add_argument('-d', '--debug', help='Writes request debug information as JSON to stderr', action='store_true')
    # Makefile sed command replaces this with the actual version.  Please do not change this line or I will be sad.
    parser.add_argument('-n', '--noObfuscate', help='Do not obfuscate bearer token when debugging', action='store_true')
    parser.add_argument('-t', '--tenant', default='default', help='tenant name defined in ~/.cortex/config, defaults to \'default\'',metavar='')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s DEVELOPMENT')
    sp = parser.add_subparsers(help='sub-command help')

    subparser_audit_logs_opts(sp)
    subparser_backup_opts(sp)
    subparser_catalog_opts(sp)
    subparser_custom_data_opts(sp)
    subparser_custom_events_opts(sp)
    subparser_dependencies_opts(sp)
    subparser_deploys_opts(sp)
    subparser_discovery_audit_opts(sp)
    subparser_docs_opts(sp)
    subparser_groups_opts(sp)
    subparser_integrations_opts(sp)
    subparser_ip_allowlist_opts(sp)
    subparser_on_call_opts(sp)
    subparser_packages_opts(sp)
    subparser_plugins_opts(sp)
    subparser_queries_opts(sp)
    subparser_resource_definitions_opts(sp)
    subparser_scorecards_opts(sp)
    subparser_teams_hierarchies_opts(sp)
    subparser_teams_opts(sp)

    validate_input(argv)
    args = parser.parse_args(argv)
    args = get_config(config, args, argv, parser)
    args.func(args)

if __name__ == '__main__':
    sys.exit(cli())
