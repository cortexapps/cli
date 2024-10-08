import csv
import json
import re
import sys
import typer

from rich import print_json
from rich.table import Table
from rich.console import Console

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

def print_output(data, columns=None, filters=None, output_format='json'):
    """
    Print output in the specified format.

    Args:
    data: The data to print.
    columns: A list of columns to include in the output.
    filters: A list of filters to apply to the data.
    output_format: The format to print the data in.
    """
    
    if not output_format in ['json', 'table', 'csv']:
        raise ValueError("Invalid output format. Must be one of: json, table, csv")
    
    if output_format == 'json':
        if columns:
            raise typer.BadParameter("Columns can only be specified when using --table or --csv")
        if filters:
            raise typer.BadParameter("Filters can only be specified when using --table or --csv")
        print_json(data=data)
        return
    
    if not columns:
        raise typer.BadParameter("Columns must be specified when using --table or --csv")
    
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
    
    for item in data:
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
        csv_writer = csv.writer(sys.stdout)
        csv_writer.writerow(column_headers)
        csv_writer.writerows(rows)
