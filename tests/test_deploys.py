from tests.helpers.utils import *

def _add_deploy():
    cli(["deploys", "add", "-t", "shipping-integrations", "-f", "data/run-time/deploys.json"])

def _delete_all():
    cli(["deploys", "delete-all"])
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    assert len(response['deployments']) == 0, "All deployments for entity should be deleted"

def test_deploys():
    _delete_all()

    response = json_response(["deploys", "add", "-t", "shipping-integrations", "-f", "data/run-time/deploys-uuid.json"])
    uuid = response['uuid']

    _add_deploy()
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    assert any(deploy['uuid'] == uuid for deploy in response['deployments']), "Should find a deploy with uuid"
    assert response['total'] == 2, "Two deploys should be returned for entity"

    cli(["deploys", "update-by-uuid", "-t", "shipping-integrations", "-uu", uuid, "-f", "data/run-time/deploys-update.json"])
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    deploy = [deploy for deploy in response['deployments'] if deploy['uuid'] == uuid]
    assert deploy[0]['sha'] == "SHA-456789", "Should find a deploy with sha"
 
    cli(["deploys", "delete-by-uuid", "-t", "shipping-integrations", "-uu", uuid])
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    assert not any(deploy['uuid'] == uuid for deploy in response['deployments']), "Should not find a deploy with uuid"
    assert response['total'] == 1, "Following delete-by-uuid, only one deploy should be returned for entity"

    _add_deploy()
    cli(["deploys", "delete", "-t", "shipping-integrations", "-s", "SHA-123456"])
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    assert not any(deploy['sha'] == "SHA-123456" for deploy in response['deployments']), "Should not find a deploy with sha that was deleted"

    _add_deploy()
    cli(["deploys", "delete-by-filter", "-ty", "DEPLOY"])
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    assert not any(deploy['type'] == "DEPLOY" for deploy in response['deployments']), "Should not find a deploy type 'DEPLOY' that was deleted"

    response = json_response(["deploys", "add",
                              "-t", "shipping-integrations",
                              "--email", "julien@tpb.com",
                              "--name", "Julien", 
                              "--environment", "PYPI.org",
                              "--sha", "SHA-123456",
                              "--title", "my title",
                              "--type", "DEPLOY",
                              "--url", "https://tpb.com",
                              "-c", "abc=123",
                              "-c", "def=456"])
    uuid = response['uuid']
    response = json_response(["deploys", "list", "-t", "shipping-integrations"])
    deploy = [deploy for deploy in response['deployments'] if deploy['uuid'] == uuid]
    assert deploy[0]['sha'] == "SHA-123456", "Should find a deploy with sha"
    assert deploy[0]['deployer']['email'] == "julien@tpb.com", "Email should be set for deploy"
    assert deploy[0]['deployer']['name'] == "Julien", "Name should be set for deploy"
    assert deploy[0]['environment'] == "PYPI.org", "environment should be set for deploy"
    assert deploy[0]['title'] == "my title", "title should be set for deploy"
    assert deploy[0]['type'] == "DEPLOY", "type should be set for deploy"
    assert deploy[0]['customData']['abc'] == "123", "Custom data field should be populated"
    assert deploy[0]['customData']['def'] == "456", "Custom data field should be populated"

    _add_deploy()
    _delete_all()
