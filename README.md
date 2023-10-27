# Cortex CLI

# Testing
pytest

# Build
python -m build

# check for vulns
python -m pip install pip-audit
pip-audit .

# Upload
python3 -m twine upload --repository testpypi dist/*

# Install
python3 -m venv /tmp/<DIR>
source <DIR>/bin/activate
python3 -m venv /tmp/c1
source <DIR>/bin/c1
pip install --index-url https://test.pypi.org/simple/ cortexapps-cli
pip install --index-url https://test.pypi.org/simple/ cortexapps-cli=0.0.3

pip install --extra-index-url https://pypi.org/simple --no-cache-dir --index-url https://test.pypi.org/simple/ cortexapps-cli

