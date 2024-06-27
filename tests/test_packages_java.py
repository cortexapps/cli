from common import *

def test(capsys):
    cli_command(capsys, ["packages", "java", "upload-single", "-t", "sso-integration", "-f", "data/run-time/packages_java_single.json"])
    cli_command(capsys, ["packages", "java", "upload-multiple", "-t", "sso-integration", "-f", "data/run-time/packages_java_multiple.json"])
    packages(capsys, "java", "JAVA", "3.3.3", "io.cortex.teams", "sso-integration")
