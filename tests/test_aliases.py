"""
Tests for CLI aliases.
"""
from cortexapps_cli.cortex import cli
from string import Template
import os

def test_aliases_get(tmp_path):
    cortex_api_key = os.getenv('CORTEX_API_KEY')
    f = tmp_path / "cortex_config"
    template = Template("""
        [default]
        api_key = ${cortex_api_key}

        [default.aliases]
        test = catalog descriptor -t test-service
        """)
    content = template.substitute(cortex_api_key=cortex_api_key)
    f.write_text(content)
    cli(["-c", str(f), "-a", "test"])
