# CLI commands style guide (WIP)

Here are some guidelines on developing commands for Cortex CLI

## Flags and arguments

* Prefer flags over arguments, so that command actions are clearer and future additions are less likely to break existing scripts.
* Flags should have a long two-dash version and a short single-dash version: `--long-version`, `-l`.
* Try to use the same short version flag everywhere. We want to avoud having a single letter flag that means different things in different commands.
* Flags that are multiple words should be in `kebab-case`.

## General forms

Commands should be readable and easy to understand. In general, the parts of a command may be:

* Executable name e.g., `cortex`
* Global flags that affect the behavior of the executable as a whole, like `--tenant` or `--config`
* Top-level object type or topic e.g., `team`, `catalog`
* Top level verb e.g., `create`, `list`, `add`
* Verb objects, if applicable, e.g., `links`, `description`
* Command-specific arguments and flags, e.g., `--description`, `--file`

Examples:
```
# list catalog entries of type 'service' and include ownership info
cortex catalog list --include-owners --types service

# create a team from a file
cortex teams create --file input.json

# add a link to a team
cortex teams add link --url https://www.catster.com --type documentation --name Catster
```

## Standard verbs

Recommendations for verbs to use in the CLI, and their meanings:

* **list** - List out a resource of which there may be many. If the endpoing is paginated, retrieve all pages by default. Optionally provide `--page` and `--page-size` to allow the user to get a single page. This should map to either a get or a fetch in the client. Provide options to the user for table and CSV output.

* **get** - Get the full details of a specific object. This would usually map to a HTTPS GET. The user would expect to see detailed information about a single object.

* **create** - Create an object. If your command is not creating an object but rather adding information to an existing object, it should be called **add** rather than create. Create should fail if the object already exists. Consider adding `--replace-existing` and `--update-existing` flags if you want to allow this behavior for users. Original create commands required the full definition of the object in JSON or YAML; all new create commands should have this as default behavior as well. Consider adding flags to also allow creation of objects without a full JSON/YAML object definition.

* **delete** - Delete an object. If the the terminal is interactive, prompt the user to make sure they really want to delete. Provide a `--force` flag that skips the prompt, but when the terminal is interactive says what it's going to do and waits ten seconds in case the user changes their mind; instruct the user to hit Ctrl+C to abort. When the terminal is not interactive (when the delete command is happening as part of a script of batch process) delete with `--force` should succeed immediately and delete without `--force` should fail immediately.

* **update** - Make changes to an existing object. Accept a full object definition in JSON or YAML as appropriate. Ideally, also accept a partial object definition. If the object definition is valid, retrieve the existing object, merge the changes in the provided definition, and apply the update.

* **archive/unarchive** - In some cases, these operations could be accomplished via **update** but they should be provided as separate verbs as well.

* **add/remove** - Add items to or remove items from object attributes that are lists. In many cases this could be accomplished by **get/update** above, but in the case of commonly used attributes like *links* they should be provided as separate verbs as well. Unlike **delete**, it's not necessary to prompt or warn the user before executing **remove**. Consider also providing a **list** subcommand to list existing values in the attribute.

* **set/unset** - Set or unset object attributes that are not lists. In many cases this could be accomplished by **get/update** above, but in the case of commonly used attributes like *description* they should be provided as separate verbs as well. Unlike **delete**, it's not necessary to prompt or warn the user before executing **unset**. Consider also providing a **show** command to show the existing value of the attribute.

* **open** - Open the specified object(s) in the user's browser. Fail immediately if the terminal is not active or a browser is not available. Consider warning the user if this would result in opening more than 3 browser tabs.
