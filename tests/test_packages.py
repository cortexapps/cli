from common import *

# When trying to put python and node tests in separate tests running in parallel, got 409 Conflict HTTP errors,
# even when using different entity tag.
def test(capsys):
    cli_command(capsys, ["packages", "go", "upload", "-t", "sso-integration", "-f", "data/run-time/packages_go.sum"])
    packages(capsys, "go", "GO", "3.3.0", "github.com/gofrs/uuid", "sso-integration")

    cli_command(capsys, ["packages", "python", "upload-pipfile", "-t", "sso-integration", "-f", "data/run-time/packages_python_pipfile.lock"])
    packages(capsys, "python", "PYTHON", "2022.12.7", "certifi", "sso-integration")

    cli_command(capsys, ["packages", "python", "upload-requirements", "-t", "sso-integration", "-f", "data/run-time/packages_python_requirements.txt"])
    packages(capsys, "python", "PYTHON", "1.0.6", "contourpy", "sso-integration")

    cli_command(capsys, ["packages", "node", "upload-package", "-t", "sso-integration", "-f", "data/run-time/packages_node_package.json"])
    packages(capsys, "node", "NODE", "^4.1.11", "clean-css", "sso-integration")

    cli_command(capsys, ["packages", "node", "upload-package-lock", "-t", "sso-integration", "-f", "data/run-time/packages_node_package_lock.json"])
    packages(capsys, "node", "NODE", "4.2.6", "@angular/common", "sso-integration")

    cli_command(capsys, ["packages", "node", "upload-yarn-lock", "-t", "sso-integration", "-f", "data/run-time/packages_node_yarn.lock"])
    packages(capsys, "node", "NODE", "6.16.5", "@types/babylon", "sso-integration")

    cli_command(capsys, ["packages", "nuget", "upload-packages-lock", "-t", "sso-integration", "-f", "data/run-time/packages_nuget_packages_lock.json"])
    packages(capsys, "nuget", "NUGET", "1.0.0", "Microsoft.NETFramework.ReferenceAssemblies", "sso-integration")

    cli_command(capsys, ["packages", "nuget", "upload-csproj", "-t", "sso-integration", "-f", "data/run-time/packages_nuget.csproj"])
    packages(capsys, "nuget", "NUGET", "7.1.1", "CsvHelper", "sso-integration")
