from tests.helpers.utils import *

BASE_URL = "https://api.getcortexapp.com"

MOCK_K8S_RESPONSE = {
    "resources": [
        {
            "namespace": "production",
            "name": "my-service",
            "cluster": "prod-cluster",
            "type": "Deployment",
            "lastUpdated": "2024-01-15T10:30:00Z",
        },
        {
            "namespace": "production",
            "name": "my-service-worker",
            "cluster": "prod-cluster",
            "type": "StatefulSet",
            "lastUpdated": "2024-01-15T10:30:00Z",
        },
    ]
}

TAG = "my-service"


@responses.activate
def test_catalog_k8s_json():
    responses.add(
        responses.GET,
        BASE_URL + f"/api/v1/catalog/{TAG}/k8s",
        json=MOCK_K8S_RESPONSE,
        status=200,
    )
    response = cli(["catalog", "k8s", "--tag", TAG])
    assert response == MOCK_K8S_RESPONSE


@responses.activate
def test_catalog_k8s_table():
    responses.add(
        responses.GET,
        BASE_URL + f"/api/v1/catalog/{TAG}/k8s",
        json=MOCK_K8S_RESPONSE,
        status=200,
    )
    response = cli(["catalog", "k8s", "--tag", TAG, "--table"], ReturnType.STDOUT)
    assert "production" in response
    assert "prod-cluster" in response


@responses.activate
def test_catalog_k8s_csv():
    responses.add(
        responses.GET,
        BASE_URL + f"/api/v1/catalog/{TAG}/k8s",
        json=MOCK_K8S_RESPONSE,
        status=200,
    )
    response = cli(["catalog", "k8s", "--tag", TAG, "--csv"], ReturnType.STDOUT)
    assert "production" in response
    assert "prod-cluster" in response


@responses.activate
def test_catalog_k8s_table_and_csv_raises_error():
    responses.add(
        responses.GET,
        BASE_URL + f"/api/v1/catalog/{TAG}/k8s",
        json=MOCK_K8S_RESPONSE,
        status=200,
    )
    result = cli(["catalog", "k8s", "--tag", TAG, "--table", "--csv"], ReturnType.RAW)
    assert result.exit_code != 0


@responses.activate
def test_catalog_k8s_empty_response():
    responses.add(
        responses.GET,
        BASE_URL + f"/api/v1/catalog/{TAG}/k8s",
        json={},
        status=200,
    )
    response = cli(["catalog", "k8s", "--tag", TAG])
    assert response == {}
