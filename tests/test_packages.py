"""
Tests for packages commands.
"""
from cortexapps_cli.cortex import cli

def test_packages_go_sum():
    cli(["packages", "go", "upload", "-t", "test-service", "-f", "tests/test_packages_go.sum"])

    cli(["packages", "java", "upload-single", "-t", "test-service", "-f", "tests/test_packages_java_single.json"])

    cli(["packages", "java", "upload-multiple", "-t", "test-service", "-f", "tests/test_packages_java_multiple.json"])

    cli(["packages", "python", "upload-pipfile", "-t", "test-service", "-f", "tests/test_packages_python_pipfile.lock"])

    cli(["packages", "python", "upload-requirements", "-t", "test-service", "-f", "tests/test_packages_python_requirements.txt"])

    cli(["packages", "node", "upload-package", "-t", "test-service", "-f", "tests/test_packages_node_package.json"])

    cli(["packages", "node", "upload-package-lock", "-t", "test-service", "-f", "tests/test_packages_node_package_lock.json"])

    cli(["packages", "node", "upload-yarn-lock", "-t", "test-service", "-f", "tests/test_packages_node_yarn.lock"])

    cli(["packages", "list", "-t", "test-service"])

    cli(["packages", "java", "delete", "-t", "test-service", "-n", "io.cortex.teams"])

    cli(["packages", "python", "delete", "-t", "test-service", "-n", "cycler"])

    cli(["packages", "node", "delete", "-t", "test-service", "-n", "inter-angular"])

    cli(["packages", "list", "-t", "test-service"])

    cli(["packages", "nuget", "upload-packages-lock", "-t", "test-service", "-f", "tests/test_packages_nuget_packages_lock.json"])

    cli(["packages", "nuget", "upload-csproj", "-t", "test-service", "-f", "tests/test_packages_nuget.csproj"])
