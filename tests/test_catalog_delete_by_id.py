from tests.helpers.utils import *
import tempfile
import os

def _create_entity(tag):
    content = f"""openapi: 3.0.1
info:
  title: Delete By ID Test Entity
  x-cortex-tag: {tag}
  x-cortex-type: service
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        return f.name

def test_delete_by_id_flag():
    tag = "cli-test-delete-by-id-flag"
    path = _create_entity(tag)
    try:
        cli(["catalog", "create", "-f", path])

        response = cli(["catalog", "details", "-t", tag])
        cid = response['id']
        assert cid.startswith("en"), f"Expected a CID starting with 'en', got: {cid}"

        cli(["catalog", "delete-by-id", "--id", cid])

        response = cli(["catalog", "details", "-t", tag], ReturnType.RAW)
        assert "HTTP Error 404:" in response.stdout, "Entity should be deleted (404 expected)"
    finally:
        os.unlink(path)

def test_delete_by_id_file():
    tag1 = "cli-test-delete-by-id-file-1"
    tag2 = "cli-test-delete-by-id-file-2"
    path1 = _create_entity(tag1)
    path2 = _create_entity(tag2)
    try:
        cli(["catalog", "create", "-f", path1])
        cli(["catalog", "create", "-f", path2])

        cid1 = cli(["catalog", "details", "-t", tag1])['id']
        cid2 = cli(["catalog", "details", "-t", tag2])['id']

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"{cid1}\n{cid2}\n")
            ids_file = f.name

        try:
            cli(["catalog", "delete-by-id", "--file", ids_file])

            for tag in [tag1, tag2]:
                response = cli(["catalog", "details", "-t", tag], ReturnType.RAW)
                assert "HTTP Error 404:" in response.stdout, f"Entity {tag} should be deleted (404 expected)"
        finally:
            os.unlink(ids_file)
    finally:
        os.unlink(path1)
        os.unlink(path2)
