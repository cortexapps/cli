import typer
from typing import List, Optional
from typing_extensions import Annotated

class ListCommandOptions:
    table_output = Annotated[
        Optional[bool],
        typer.Option("--table", help="Output the response as a table", show_default=False)  # , callback=table_output_cb)
    ]
    csv_output = Annotated[
        Optional[bool],
        typer.Option("--csv", help="Output the response as CSV", show_default=False)  # , callback=csv_output_cb)
    ]
    columns = Annotated[
        Optional[List[str]],
        typer.Option("--columns", "-C", help="Columns to include in the table, in the format HeaderName=jsonpath", show_default=False)
    ]
    filters = Annotated[
        Optional[List[str]],
        typer.Option("--filter", "-F", help="Filters to apply on rows, in the format jsonpath=regex", show_default=False)
    ]
    no_headers = Annotated[
        Optional[bool],
        typer.Option("--no-headers", help="For csv output type only: don't print header columns.", show_default=False)
    ]
    sort = Annotated[
        Optional[List[str]],
        typer.Option("--sort", "-S", help="Sort order to apply on rows, in the format jsonpath:asc or jsonpath:desc", show_default=False)
    ]
    page = Annotated[
        Optional[int],
        typer.Option("--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages", show_default=False)
    ]
    page_size = Annotated[
        Optional[int],
        typer.Option("--page-size", "-z", help="Page size for results", show_default=False)
    ]

class CommandOptions:
    _print = Annotated[
        Optional[bool],
        typer.Option("--print", help="If result should be printed to the terminal", hidden=True)
    ]
