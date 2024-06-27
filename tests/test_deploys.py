from common import *

def _add_deploy(capsys):
    cli_command(capsys, ["deploys", "add", "-t", "shipping-integrations", "-f", "data/run-time/deploys.json"])

def test_deploys(capsys):
    response = cli_command(capsys, ["deploys", "add", "-t", "shipping-integrations", "-f", "data/run-time/deploys-uuid.json"])
    uuid = response['uuid']

    response = cli_command(capsys, ["deploys", "list", "-t", "shipping-integrations"])
    assert any(deploy['uuid'] == uuid for deploy in response['deployments']), "Should find a deploy with uuid"

    cli_command(capsys, ["deploys", "update-by-uuid", "-t", "shipping-integrations", "-u", uuid, "-f", "data/run-time/deploys-update.json"])
    response = cli_command(capsys, ["deploys", "list", "-t", "shipping-integrations"])
    deploy = [deploy for deploy in response['deployments'] if deploy['uuid'] == uuid]
    assert deploy[0]['sha'] == "SHA-456789", "Should find a deploy with sha"

    cli_command(capsys, ["deploys", "delete-by-uuid", "-t", "shipping-integrations", "-u", uuid])
    response = cli_command(capsys, ["deploys", "list", "-t", "shipping-integrations"])
    assert not any(deploy['uuid'] == uuid for deploy in response['deployments']), "Should not find a deploy with uuid"

    _add_deploy(capsys)
    cli_command(capsys, ["deploys", "delete", "-t", "shipping-integrations", "-s", "SHA-123456"])
    response = cli_command(capsys, ["deploys", "list", "-t", "shipping-integrations"])
    assert not any(deploy['sha'] == "SHA-123456" for deploy in response['deployments']), "Should not find a deploy with sha that was deleted"

    _add_deploy(capsys)
    cli_command(capsys, ["deploys", "delete-filter", "-y", "DEPLOY"])
    assert not any(deploy['type'] == "DEPLOY" for deploy in response['deployments']), "Should not find a deploy type 'DEPLOY' sha that was deleted"

    _add_deploy(capsys)
    cli_command(capsys, ["deploys", "delete-all"])
    response = cli_command(capsys, ["deploys", "list", "-t", "shipping-integrations"])
    assert len(response['deployments']) == 0, "All deployments for entity should be deleted"
