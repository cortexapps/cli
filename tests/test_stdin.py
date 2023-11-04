"""
Tests for stdin input.
"""
import subprocess

def test_stdin_input(capsys):
    cat_process = subprocess.Popen(['cat', 'tests/test_catalog_service.yaml'], stdout=subprocess.PIPE)
    cortex_process = subprocess.Popen(['cortexapps_cli/cortex.py', 'catalog', 'create','-f-'],stdin=cat_process.stdout, stdout=subprocess.PIPE)
    out, err = cortex_process.communicate()
    rc=cortex_process.wait()
    assert rc == 0,  "catalog test with stdin should succeed"
