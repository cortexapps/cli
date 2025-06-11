import csv
import json
import re
import sys
import typer

from typing import overload

from rich import print_json
from rich.table import Table
from rich.console import Console

def guess_data_key(response: list | dict):
    """
    Guess the key of the data list in a paginated response.

    Args:
    response (list or dict): The response to guess the data key from.

    Returns:
    The key of the data list in the response.
    """
    if isinstance(response, list):
        # if the response is a list, there is no data key
        return ''
    if isinstance(response, dict):
        # if the response is a dict, it should have exactly one key whose value is a list
        data_keys = [k for k, v in response.items() if isinstance(v, list)]
        if len(data_keys) == 0:
            # if no such key is found, raise an error
            raise ValueError(f"Response dict does not contain a list: {response}")
        if len(data_keys) > 1:
            # if more than one such key is found, raise an error
            raise ValueError(f"Response dict contains multiple lists: {response}")
        return data_keys[0]

    # if the response is neither a list nor a dict, raise an error
    raise ValueError(f"Response is not a list or dict: {response}")

def get_value_at_path(data, path):
    """
        Get the value at a specified path in a nested dictionary.

        Args:
        data (dict): The input dictionary.
        path (str): The path to the desired value, separated by dots.

        Returns:
        The value at the specified path or None if the path doesn't exist.
        """
    keys = path.split(".")
    current = data

    try:
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                key = int(key)
                current = current[key]
            else:
                return None
        return current
    except:
        return None

def matches_filters(data, filters):
    """
    Check if a dictionary matches a list of filters.

    Args:
    data (dict): The dictionary to check.
    filters (list): A list of filters in the format jsonpath=regex.

    Returns:
    True if the dictionary matches all filters, False otherwise.
    """
    if not filters:
        return True
    for filter in filters:
        jsonpath, regex = filter.split("=")
        value = get_value_at_path(data, jsonpath)
        if value is None:
            return False
        if not re.match(regex, str(value)):
            return False
    return True

def humanize_value(value):
    """
    Convert a value to a human-readable string.

    Args:
    value: The value to convert.

    Returns:
    A human-readable string representation of the value.
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return ', '.join([str(x) for x in value])
    if isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)

def print_output(data, columns=None, filters=None, sort=None, output_format='json', no_headers=False):
    """
    Print output in the specified format.

    Args:
    data: The data to print.
    columns: A list of columns to include in the output.
    filters: A list of filters to apply to the data.
    output_format: The format to print the data in.
    no_headers: if column headers should not be shown
    """

    if output_format is None:
        output_format = 'json'
    elif not output_format in ['json', 'table', 'csv']:
        raise ValueError("Invalid output format. Must be one of: json, table, csv")

    if output_format == 'json':
        if columns:
            raise typer.BadParameter("Columns can only be specified when using --table or --csv")
        if filters:
            raise typer.BadParameter("Filters can only be specified when using --table or --csv")
        print_json(data=data)
        return

    data_key = guess_data_key(data)
    table_data = data.get(data_key) if data_key else data

    if not isinstance(table_data, list):
        raise ValueError(f"Data is not a list: {table_data}")

    if not columns:
        raise typer.BadParameter("Columns must be specified when using --table or --csv")

    columns = list(columns)
    for idx, column in enumerate(columns):
        if not re.match(r"^[a-zA-Z0-9_. ]+=[a-zA-Z0-9_.]+$", column):
            if re.match(r"^[a-zA-Z0-9_.]+$", column):
                # if no column name is specified and it's a valid jsonpath, use the jsonpath as the column name
                columns[idx] = f"{column}={column}"
            else:
                raise typer.BadParameter("Columns must be in the format HeaderName=jsonpath")

    if filters:
        for filter in filters:
            if not re.match(r"^[a-zA-Z0-9_.]+=.+$", filter):
                raise typer.BadParameter("Filters must be in the format jsonpath=regex")

    column_headers = [x.split('=')[0] for x in columns]
    column_accessors = [x.split('=')[1] for x in columns]
    rows = []

    if sort:
        for sort_item in sort:
            if not re.match(r"^[a-zA-Z0-9_.]+:(asc|ASC|desc|DESC)$", sort_item):
                raise typer.BadParameter("Sort must be in the format jsonpath:asc or jsonpath:desc")
            (jsonpath, order) = sort_item.split(':')
            if order.lower() == 'asc':
                table_data = sorted(table_data, key=lambda x: get_value_at_path(x, jsonpath))
            elif order.lower() == 'desc':
                table_data = sorted(table_data, key=lambda x: get_value_at_path(x, jsonpath), reverse=True)

    for item in table_data:
        if matches_filters(item, filters):
            rows.append([humanize_value(get_value_at_path(item, accessor)) for accessor in column_accessors])

    if output_format == 'table':
        table = Table()
        for header in column_headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        console = Console()
        console.print(table)
    elif output_format == 'csv':
        csv_writer = csv.writer(sys.stdout, lineterminator='\n')
        if not no_headers:
            csv_writer.writerow(column_headers)
        csv_writer.writerows(rows)

def print_output_with_context(ctx: typer.Context, data):
    columns = ctx.params.get('columns', None)
    filters = ctx.params.get('filters', None)
    sort = ctx.params.get('sort', None)
    table_output = ctx.params.get('table_output', None)
    csv_output = ctx.params.get('csv_output', None)
    no_headers = ctx.params.get('no_headers', None)
    if table_output and csv_output:
        raise typer.BadParameter("Only one of --table and --csv can be specified")
    if table_output:
        output_format = 'table'
    elif csv_output:
        output_format = 'csv'
    else:
        output_format = 'json'
    print_output(data, columns=columns, filters=filters, sort=sort, output_format=output_format, no_headers=no_headers)
