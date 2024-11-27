from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_newrelic_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_aws_add():
    """
    Test adding a single configuration
    """
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations", json=[{'accountId': 123, 'role:': 'test'}], status=200)
    response = cli(["integrations", "aws", "add", "-a", "123", "-r", "test"])
    assert response[0]['accountId'] == 123, "accountId should be returned in response"

@responses.activate
def test_integrations_aws_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations/123456", status=200)
    cli(["integrations", "aws", "delete", "-a", "123456"])

@responses.activate
def test_integrations_aws_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations", status=200)
    cli(["integrations", "aws", "delete-all"])

@responses.activate
def test_integrations_aws_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations/123456", status=200)
    cli(["integrations", "aws", "get", "-a", "123456"])

@responses.activate
def test_integrations_aws_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations", status=200)
    cli(["integrations", "aws", "get-all"])

@responses.activate
def test_integrations_aws_update():
    #f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations", status=200)
    cli(["integrations", "aws", "update", "-c", "123=test", "-c", "456=test1"])

@responses.activate
def test_integrations_aws_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations/validate/123456", status=200)
    cli(["integrations", "aws", "validate", "-a", "123456"])

@responses.activate
def test_integrations_aws_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/configurations/all/validate", status=200)
    cli(["integrations", "aws", "validate-all"])

@responses.activate
def test_integrations_list_types():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/types", json=[{'total': 1, 'types': [{'type': 'AWS::EC2::Instance'}]}], status=200)
    cli(["integrations", "aws", "list-types"])

@responses.activate
def test_integrations_aws_update_types():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/aws/types", json=[{'types': [{'type': 'AWS::EC2::Instance'}]}], status=200)
    cli(["integrations", "aws", "update-types", "-t", "AWS::EC2::Instance=true", "-t", "AWS::ECS::VPC=false"], ReturnType.RAW)
