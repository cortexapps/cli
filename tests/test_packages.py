"""
Tests for packages commands.
"""
from cortexapps_cli.cortex import cli

def test_packages_go_sum():
    cli(["packages", "go", "upload", "-t", "test-service", "-f", "tests/test_packages_go.sum"])

def test_packages_java_single():
    cli(["packages", "java", "upload-single", "-t", "test-service", "-f", "tests/test_packages_java_single.json"])

def test_packages_java_multiple():
    cli(["packages", "java", "upload-multiple", "-t", "test-service", "-f", "tests/test_packages_java_multiple.json"])

def test_packages_python_pipfile():
    cli(["packages", "python", "upload-pipfile", "-t", "test-service", "-f", "tests/test_packages_python_pipfile.lock"])

def test_packages_python_requirements():
    cli(["packages", "python", "upload-requirements", "-t", "test-service", "-f", "tests/test_packages_python_requirements.txt"])

def test_packages_node_package():
    cli(["packages", "node", "upload-package", "-t", "test-service", "-f", "tests/test_packages_node_package.json"])

def test_packages_node_package_lock():
    cli(["packages", "node", "upload-package-lock", "-t", "test-service", "-f", "tests/test_packages_node_package_lock.json"])

def test_packages_node_yarn_lock():
    cli(["packages", "node", "upload-yarn-lock", "-t", "test-service", "-f", "tests/test_packages_node_yarn.lock"])

def test_packages_list():
    cli(["packages", "list", "-t", "test-service"])

def test_packages_python_delete():
    cli(["packages", "python", "delete", "-t", "test-service", "-n", "cycler"])

def test_packages_node_delete():
    cli(["packages", "node", "delete", "-t", "test-service", "-n", "inter-angular"])

def test_packages():
    cli(["packages", "list", "-t", "test-service"])

def test_packages_nuget_packages_lock():
    cli(["packages", "nuget", "upload-packages-lock", "-t", "test-service", "-f", "tests/test_packages_nuget_packages_lock.json"])

def test_packages_nuget_csproj():
    cli(["packages", "nuget", "upload-csproj", "-t", "test-service", "-f", "tests/test_packages_nuget.csproj"])
