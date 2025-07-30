"""
MCP Server implementation for Cortex CLI - Tiered approach for practical usage
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

import typer
from typer.main import get_command
from click import Command, Group, Option, Argument

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# Command examples and schemas database
COMMAND_EXAMPLES = {
    "teams create": {
        "description": "Create a team with members",
        "examples": [
            {
                "description": "Create basic team (members added separately)",
                "arguments": {"tag": "my-team", "name": "My Team"},
                "note": "Members can be added after creation using teams update"
            },
            {
                "description": "Create team with JSON definition",
                "arguments": {"file": "-"},
                "stdin_format": "JSON",
                "stdin_example": {
                    "name": "My Team",
                    "tag": "my-team",
                    "teamType": "CORTEX",
                    "members": [
                        {"email": "user@example.com", "name": "User Name"}
                    ]
                }
            }
        ]
    },
    "catalog create": {
        "examples": [
            {
                "description": "Create service entity",
                "arguments": {"file": "-"},
                "stdin_format": "YAML",
                "stdin_example": """openapi: "3.0.1"
x-cortex-tag: my-service
x-cortex-type: service
info:
  title: My Service
  description: A sample service
  x-cortex-owners:
    - type: group
      name: my-team"""
            }
        ]
    },
    "catalog list": {
        "csv_column_headers": ["ID", "Tag", "Name", "Type", "Git Repository"],
        "hints": [
            "Use --csv for CSV output",
            "Owners will be null unless you specify --include-owners",
            "You can get the custom data for each entity using --include-metadata",
            "Use --filter to filter results by JSONPath expressions, e.g., --filter 'name=.*my-service.*'",
        ],
        "example_json_list_item": {
            "id": "en30c6bd1d7a42943d",
            "name": "Awesome Repo",
            "tag": "awesome-repo",
            "description": "the best repo",
            "type": "service",
            "hierarchy": {
                "parents": [],
                "children": []
            },
            "groups": [],
            "metadata": [],
            "lastUpdated": "2025-06-10T03:47:10.052689",
            "links": [],
            "isArchived": False,
            "git": {
                "repository": "martindstone-org3/awesome-repo",
                "alias": "gh-relay",
                "basepath": None,
                "provider": "github",
                "repositoryUrl": "https://api.github.com/martindstone-org3/awesome-repo"
            },
            "owners": None,
            "slackChannels": [],
            "members": None
        },
        "description": "List entities in the catalog - services, domains, teams, etc.",
        "examples": [
            {
                "description": "List all services",
                "arguments": {"types": "service"},
                "note": "Default is JSON output, use --csv for CSV output"
            },
            {
                "description": "list services with table output and filtering",
                "arguments": {"csv": True, "types": "service", "filter": "tag=.*pattern.*"},
                "note": "Use CSV output for table format; filtering uses Python regex syntax; example below for some jsonpath items that can be used",
            },
            {
                "description": "list services whose names match a regex",
                "arguments": {"csv": True, "filter": "name=.*my-service.*"},
                "note": "Use Python regex syntax for filtering",
            },
        ]
    },
    "teams update": {
        "description": "Update a team with members, links, and metadata",
        "hints": [
            "Use 'teams get' to retrieve team details, then add your changes to the JSON",
            "When adding members, the REST API does not immediately return the updated object. GET the team again to see changes.",
            {
                "example JSON for stdin": json.dumps({
                    "id": "en37adfc4c00cec865",
                    "teamTag": "martin-gautham",
                    "catalogEntityTag": "martin-gautham",
                    "metadata": {
                        "name": "Martin-Gautham",
                    },
                    "links": [],
                    "slackChannels": [],
                    "cortexTeam": {
                        "members": [
                            {
                                "name": "Martin Stone",
                                "email": "martin.stone@cortex.io"
                            }
                        ]
                    },
                    "type": "CORTEX"
                })
            }
        ],
    }
}

COMMON_PATTERNS = {
    "stdin_usage": {
        "description": "For commands that accept file input via stdin",
        "pattern": 'Use {"file": "-", "_stdin": "your_content"} in arguments',
        "note": "Check 'accepts_stdin' flag in command details"
    },
    "filtering": {
        "description": "For list commands with filtering",
        "pattern": 'Filters require CSV output: {"csv": true, "filter": ["jsonpath=regex"]} - use python re style regex',
        "note": "Filters use Python regex syntax"
    },
    "multiple_values": {
        "description": "For options that accept multiple values",
        "pattern": 'Use arrays: {"option_name": ["value1", "value2"]}',
        "note": "Check 'multiple': true in option details"
    }
}


class FastCommandDiscovery:
    """Extract command information directly from Click/Typer without subprocess calls"""

    paths_to_skip = [
        "mcp",
        "teams update-metadata",
        "teams update-members",
    ]

    def __init__(self, app: typer.Typer):
        self.app = app
        self.commands_cache = self._extract_all_commands()

    def _extract_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Extract all command information from the Typer app"""
        commands = {}
        click_command = get_command(self.app)

        def traverse(cmd: Command, path: List[str] = []):
            current_path = " ".join(path) if path else ""

            if current_path in self.paths_to_skip:
                logger.info(f"Skipping command: {current_path}")
                return

            logger.info(f"Processing command: {current_path}")
            if isinstance(cmd, Group):
                # It's a group with subcommands
                if path:  # Don't add the root
                    try:
                        subcommands_list = [str(name) for name in cmd.commands.keys()]
                        commands[current_path] = {
                            "type": "group",
                            "description": str(cmd.help or cmd.short_help or ""),
                            "has_subcommands": True,
                            "subcommands": subcommands_list
                        }
                    except Exception as e:
                        logger.warning(f"Error processing group {current_path}: {e}")

                for name, subcmd in cmd.commands.items():
                    traverse(subcmd, path + [str(name)])
            else:
                # It's a leaf command
                try:
                    cmd_info = {
                        "type": "command",
                        "description": str(cmd.help or cmd.short_help or ""),
                        "has_subcommands": False,
                        "options": [],
                        "accepts_stdin": False,
                        "option_count": 0
                    }

                    # Extract options
                    for param in cmd.params:
                        if isinstance(param, Option):
                            try:
                                # Ensure JSON serializable default value
                                default_val = param.default
                                if default_val is not None:
                                    try:
                                        json.dumps(default_val)  # Test if serializable
                                    except (TypeError, ValueError):
                                        default_val = str(default_val)  # Convert to string if not

                                # skip table output option because it confuses the llm
                                if param.name.lower().endswith("table"):
                                    continue

                                # Ensure all values are JSON serializable
                                opt_info = {
                                    "name": str(param.name),
                                    "opts": [str(opt) for opt in param.opts],  # e.g., ['-f', '--file']
                                    "type": self._get_param_type(param),
                                    "required": bool(param.required),
                                    "default": default_val,
                                    "help": str(param.help or ""),
                                    "is_flag": bool(param.is_flag),
                                    "multiple": bool(param.multiple)
                                }
                                
                                if param.name.lower().endswith("filters"):
                                    opt_info["help"] = "Filtering uses Python regex syntax; format is {'filter': ['jsonpath=regex']; common patterns include name=.*str.* and tag=.*str.*}; see command examples for more"

                                # Check for stdin support
                                help_lower = (param.help or "").lower()
                                if ("stdin" in help_lower and ("-f-" in help_lower or "- for stdin" in help_lower)) or \
                                   (param.name == "file" and "stdin" in help_lower):
                                    cmd_info["accepts_stdin"] = True
                                    opt_info["accepts_stdin"] = True

                                cmd_info["options"].append(opt_info)
                            except Exception as e:
                                logger.warning(f"Error processing option {param.name} for {current_path}: {e}")

                    # Count meaningful options (exclude help/version)
                    cmd_info["option_count"] = len([opt for opt in cmd_info["options"]
                                                   if opt["name"] not in ["help", "version"]])

                    commands[current_path] = cmd_info
                except Exception as e:
                    logger.warning(f"Error processing command {current_path}: {e}")

        traverse(click_command)
        return commands

    def _get_param_type(self, param) -> str:
        """Extract parameter type information"""
        if param.is_flag:
            return "boolean"
        elif hasattr(param.type, 'name'):
            type_name = param.type.name.lower()
            if 'int' in type_name:
                return "integer"
            elif 'float' in type_name:
                return "float"
            elif 'path' in type_name or 'file' in type_name:
                return "file"
            elif 'choice' in type_name:
                return "choice"
            elif 'datetime' in type_name:
                return "datetime"
            return type_name
        return "string"

    def list_commands_summary(self, filter_str: str = "") -> List[Dict[str, Any]]:
        """List commands with summary information only"""
        results = []
        filter_lower = filter_str.lower() if filter_str else ""

        for cmd_path, info in sorted(self.commands_cache.items()):
            if not cmd_path:  # Skip root
                continue

            # Apply filter
            if filter_str and not (
                filter_lower in cmd_path.lower() or
                filter_lower in info.get("description", "").lower()
            ):
                continue

            # Build summary entry
            entry = {
                "command": cmd_path,
                "description": info.get("description", ""),
                "type": info.get("type", "command")
            }

            # Add key flags for quick reference
            flags = []
            if info.get("has_subcommands"):
                flags.append("has subcommands")
            if info.get("accepts_stdin"):
                flags.append("accepts stdin")
            if info.get("option_count", 0) > 0:
                flags.append(f"{info['option_count']} options")

            if flags:
                entry["flags"] = flags

            # For groups, show subcommands
            if info.get("subcommands"):
                entry["subcommands"] = info["subcommands"]

            results.append(entry)

        return results

    def get_command_details(self, command: str) -> Dict[str, Any]:
        """Get detailed information about a specific command"""
        cmd_info = self.commands_cache.get(command)
        if not cmd_info:
            return {"error": f"Command '{command}' not found"}

        # Return full details for the specific command
        return {
            "command": command,
            "details": cmd_info,
            "has_examples": command in COMMAND_EXAMPLES
        }

    def get_command_examples(self, command: str) -> Dict[str, Any]:
        """Get examples for a specific command"""
        if command not in COMMAND_EXAMPLES:
            return {
                "command": command,
                "error": f"No examples available for '{command}'",
                "available_examples": list(COMMAND_EXAMPLES.keys())
            }

        return {
            "command": command,
            "examples": COMMAND_EXAMPLES[command],
            "common_patterns": COMMON_PATTERNS
        }


class CortexMCPServer:
    """MCP Server with tiered command discovery"""

    def __init__(
        self,
        app: typer.Typer,
        cli_command: Optional[List[str]] = None
    ):
        self.app = app
        self.server = Server("cortex-cli")

        # Default CLI command
        if cli_command is None:
            cli_command = [sys.argv[0]]
        self.cli_command = cli_command

        # Initialize fast discovery
        logger.info("Initializing fast command discovery...")
        self.discovery = FastCommandDiscovery(app)
        logger.info(f"Discovered {len(self.discovery.commands_cache)} commands: {', '.join(self.discovery.commands_cache.keys())}")

        self._setup_tools()
        self._setup_handlers()

    def _setup_tools(self):
        """Create the tiered tools"""
        # Tool 1: Quick command discovery
        list_commands_tool = Tool(
            name="list_commands",
            description="List all available Cortex CLI commands with summary information",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "Optional filter for command names or descriptions"
                    }
                }
            }
        )

        # Tool 2: Detailed command information
        command_details_tool = Tool(
            name="get_command_details",
            description="Get detailed information about a specific command including all options",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Full command path, e.g., 'catalog list' or 'teams create'"
                    }
                },
                "required": ["command"]
            }
        )

        # Tool 3: Command examples and usage patterns
        command_examples_tool = Tool(
            name="get_command_examples",
            description="Get examples and usage patterns for a specific command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Full command path, e.g., 'catalog list' or 'teams create'"
                    }
                },
                "required": ["command"]
            }
        )

        # Tool 4: Execute commands (unchanged)
        cortex_cli_tool = Tool(
            name="cortex_cli",
            description="Execute any Cortex CLI command. Use other tools first to discover commands and options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Full command path, e.g., 'catalog list' or 'teams create'"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Command arguments as key-value pairs. Use '_stdin' for stdin input.",
                        "additionalProperties": True
                    }
                },
                "required": ["command"]
            }
        )

        self.tools = {
            "list_commands": list_commands_tool,
            "get_command_details": command_details_tool,
            "get_command_examples": command_examples_tool,
            "cortex_cli": cortex_cli_tool
        }

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return list(self.tools.values())

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "list_commands":
                return await self._handle_list_commands(arguments.get("filter", ""))
            elif name == "get_command_details":
                return await self._handle_command_details(arguments.get("command", ""))
            elif name == "get_command_examples":
                return await self._handle_command_examples(arguments.get("command", ""))
            elif name == "cortex_cli":
                return await self._handle_cli_execution(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]

    async def _handle_list_commands(self, filter_str: str) -> List[TextContent]:
        """Handle list_commands - return summary information only"""
        commands = self.discovery.list_commands_summary(filter_str)

        if not commands:
            return [TextContent(type="text", text=json.dumps({
                "message": "No commands found matching filter",
                "filter": filter_str
            }, indent=2))]

        result = {
            "commands": commands,
            "total_count": len(commands),
            "filter_applied": filter_str if filter_str else None,
            "note": "Use 'get_command_details' for detailed option information or 'get_command_examples' for usage examples"
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_command_details(self, command: str) -> List[TextContent]:
        """Handle get_command_details - return full details for one command"""
        if not command:
            return [TextContent(type="text", text=json.dumps({
                "error": "No command specified"
            }, indent=2))]

        details = self.discovery.get_command_details(command)
        return [TextContent(type="text", text=json.dumps(details, indent=2))]

    async def _handle_command_examples(self, command: str) -> List[TextContent]:
        """Handle get_command_examples - return examples and patterns"""
        if not command:
            return [TextContent(type="text", text=json.dumps({
                "error": "No command specified",
                "available_examples": list(COMMAND_EXAMPLES.keys())
            }, indent=2))]

        examples = self.discovery.get_command_examples(command)
        return [TextContent(type="text", text=json.dumps(examples, indent=2))]

    async def _handle_cli_execution(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle CLI command execution (unchanged from previous version)"""
        command = arguments.get("command", "")
        args = arguments.get("arguments", {})

        if not command:
            return [TextContent(type="text", text="Error: No command specified")]

        # Build command line
        cmd_parts = self.cli_command.copy() + command.split()

        # Handle stdin data
        stdin_data = None
        if "_stdin" in args:
            stdin_data = args.pop("_stdin")

        # Add arguments
        for key, value in args.items():
            if value is None or key.startswith("_"):
                continue

            if isinstance(value, bool):
                if value:
                    cmd_parts.append(f"--{key.replace('_', '-')}")
            elif isinstance(value, (list, tuple)):
                for item in value:
                    cmd_parts.append(f"--{key.replace('_', '-')}")
                    cmd_parts.append(str(item))
            else:
                cmd_parts.append(f"--{key.replace('_', '-')}")
                cmd_parts.append(str(value))

        try:
            # Execute command
            if stdin_data:
                process = await asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(stdin_data.encode()),
                    timeout=30
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30
                )

            result = {
                "command": " ".join(cmd_parts),
                "success": process.returncode == 0,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "returncode": process.returncode
            }

            # Try to parse JSON output
            if result["success"] and result["stdout"].strip():
                try:
                    result["parsed_output"] = json.loads(result["stdout"])
                    return [TextContent(type="text", text=json.dumps(result["parsed_output"], indent=2))]
                except json.JSONDecodeError:
                    pass

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except asyncio.TimeoutError:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Command timed out after 30 seconds",
                    "command": " ".join(cmd_parts)
                }, indent=2)
            )]
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "command": " ".join(cmd_parts)
                }, indent=2)
            )]

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting tiered MCP server")
        logger.info(f"CLI command: {' '.join(self.cli_command)}")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_mcp_command(app: typer.Typer) -> typer.Typer:
    """Create MCP command with tiered discovery"""

    @app.command()
    def mcp(
        ctx: typer.Context,
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
        cli_command: Optional[str] = typer.Option(
            None,
            "--cli-command",
            help="Override CLI command (defaults to current command)"
        )
    ):
        """Start MCP server exposing all CLI commands as tools"""
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        cli_cmd_list = None
        if cli_command:
            cli_cmd_list = cli_command.split()

        server = CortexMCPServer(app, cli_command=cli_cmd_list)
        asyncio.run(server.run())

    return app
