"""
cli-commands — command implementations per Cortex resource.
"""
import typer

app = typer.Typer()


@app.command()
def list_entities():
    """List all catalog entities."""
    print("Listing entities from cli-commands...")


@app.command()
def get_entity(tag: str):
    """Get a single entity by tag."""
    print(f"Fetching entity: {tag}")


if __name__ == "__main__":
    app()
