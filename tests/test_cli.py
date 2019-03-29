import json
import unittest
import subprocess

CLI = "cli.py"
PYI = "python3"


class TestCli(unittest.TestCase):
    """Basic cli tests"""

    def test_logs(self):
        result = subprocess.run(
            [PYI, CLI, "logs", "--jira-only", "--tempo-format"],
            stdout=subprocess.PIPE,
            encoding="utf8",
        )
        out = json.loads(result.stdout)
        self.assertIsInstance(out, list)

    def test_tempo(self):
        result = subprocess.run(
            [PYI, CLI, "tempo", "--issue", "AP-217"], stdout=subprocess.PIPE
        )
        out = json.loads(result.stdout)
        self.assertIsInstance(out, list)
