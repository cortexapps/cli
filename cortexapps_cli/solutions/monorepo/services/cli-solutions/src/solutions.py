"""
cli-solutions — framework for installable Cortex solution bundles.
"""


def install(solution_name: str) -> None:
    """Install a named solution bundle."""
    print(f"Installing solution: {solution_name}")


def list_solutions() -> list:
    """Return available solution names."""
    return ["monorepo", "backstage-migration", "team-health"]


if __name__ == "__main__":
    for s in list_solutions():
        print(f"  - {s}")
