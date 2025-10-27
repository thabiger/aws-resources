import subprocess
import sys
import json


def test_discover_scaffold_runs():
    proc = subprocess.run([sys.executable, "-m", "aws_resources", "discover"], capture_output=True, text=True)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data.get("status") == "scaffold"
