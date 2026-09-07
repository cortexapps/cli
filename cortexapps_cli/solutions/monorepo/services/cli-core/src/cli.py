"""
cli-core — main entry point and HTTP client for the Cortex CLI.
"""
import typer

app = typer.Typer()


@app.command()
def hello(name: str = "world"):
    """Say hello from the core CLI package."""
    print(f"Hello, {name}! This is cli-core.")


if __name__ == "__main__":
    app()
