from tests.helpers.utils import *

def test_packages():
    cli(["packages", "go", "upload", "-t", "test-service", "-f", "tests/test_packages_go.sum"])

    cli(["packages", "java", "upload-single", "-t", "test-service", "-f", "tests/test_packages_java_single.json"])

    cli(["packages", "java", "upload-multiple", "-t", "test-service", "-f", "tests/test_packages_java_multiple.json"])

    # upload-pipfile will replace any existing PYTHON package entries for an entity.  It's assumed you will use either
    # pipfile.lock or requirements.txt, but not both.
    # So we need to test here because these packages will be overwritten by the upload-requirements command.
    cli(["packages", "python", "upload-pipfile", "-t", "test-service", "-f", "tests/test_packages_python_pipfile.lock"])
    response = cli(["packages", "list", "-t", "test-service"])
    assert any(package['name'] == 'certifi' and package['packageType'] == "PYTHON" for package in response), "Should find Python pipfile package"

    cli(["packages", "python", "upload-requirements", "-t", "test-service", "-f", "tests/test_packages_python_requirements.txt"])

    # Similar store for Node as Python.  Only one file type is supported.
    cli(["packages", "node", "upload-package-json", "-t", "test-service", "-f", "tests/test_packages_node_package.json"])
    response = cli(["packages", "list", "-t", "test-service"])
    assert any(package['name'] == 'clean-css' and package['packageType'] == "NODE" for package in response), "Should find Node package.json package"

    cli(["packages", "node", "upload-package-lock", "-t", "test-service", "-f", "tests/test_packages_node_package_lock.json"])
    response = cli(["packages", "list", "-t", "test-service"])
    assert any(package['name'] == '@angular/common' and package['packageType'] == "NODE" for package in response), "Should find Node package.lock package"

    cli(["packages", "node", "upload-yarn-lock", "-t", "test-service", "-f", "tests/test_packages_node_yarn.lock"])

    cli(["packages", "nuget", "upload-packages-lock", "-t", "test-service", "-f", "tests/test_packages_nuget_packages_lock.json"])

    cli(["packages", "nuget", "upload-csproj", "-t", "test-service", "-f", "tests/test_packages_nuget.csproj"])

    response = cli(["packages", "list", "-t", "test-service"])
    assert any(package['name'] == 'github.com/cortex.io/catalog' and package['packageType'] == "GO" for package in response), "Should find GO package"
    assert any(package['name'] == 'io.cortex.scorecards' and package['packageType'] == "JAVA" for package in response), "Should find single-updated Java package"
    assert any(package['name'] == 'io.cortex.teams' and package['packageType'] == "JAVA" for package in response), "Should find multiple-update Java package"
    assert any(package['name'] == 'cycler' and package['packageType'] == "PYTHON" for package in response), "Should find Python requirement.txt package"
    assert any(package['name'] == '@types/babylon' and package['packageType'] == "NODE" for package in response), "Should find Node yarn.lock package"
    assert any(package['name'] == 'MicroBuild.Core' and package['packageType'] == "NUGET" for package in response), "Should find NuGet package"

    cli(["packages", "go", "delete", "-t", "test-service", "-n", "github.com/cortex.io/catalog"])

    cli(["packages", "java", "delete", "-t", "test-service", "-n", "io.cortex.scorecards"])
    cli(["packages", "java", "delete", "-t", "test-service", "-n", "io.cortex.teams"])

    cli(["packages", "python", "delete", "-t", "test-service", "-n", "cycler"])

    cli(["packages", "node", "delete", "-t", "test-service", "-n", "@types/babylon"])

    cli(["packages", "nuget", "delete", "-t", "test-service", "-n", "MicroBuild.Core"])

    response = cli(["packages", "list", "-t", "test-service"])

    assert not any(package['name'] == 'github.com/cortex.io/catalog' and package['packageType'] == "GO" for package in response), "Should not find deleted GO package"

    assert not any(package['name'] == 'io.cortex.scorecards' and package['packageType'] == "JAVA" for package in response), "Should not find deleted single-updated Java package"
    assert not any(package['name'] == 'io.cortex.teams' and package['packageType'] == "JAVA" for package in response), "Should not find deleted multiple-update Java package"

    assert not any(package['name'] == 'cycler' and package['packageType'] == "PYTHON" for package in response), "Should not find deleted Python requirement.txt package"

    assert not any(package['name'] == '@types/babylon' and package['packageType'] == "NODE" for package in response), "Should not find deleted Node yarn.lock package"

    assert not any(package['name'] == 'MicroBuild.Core' and package['packageType'] == "NUGET" for package in response), "Should not find deleted NuGet package"

    cli(["packages", "delete-all", "-t", "test-service"])
    response = cli(["packages", "list", "-t", "test-service"])
    assert len(response) == 0, "Should not find any packages after delete-all"
