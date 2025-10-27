import sys
import unittest
from unittest.mock import MagicMock, patch


class TestLambdaAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_lambda_analyze(self):
        import boto3

        mock_client = MagicMock()

        # paginator for list_functions
        mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "Functions": [
                    {"FunctionName": "fn1", "MemorySize": 128, "Runtime": "python3.11", "Handler": "app.handler"},
                    {"FunctionName": "fn2", "MemorySize": 256, "Runtime": "nodejs18.x", "Handler": "index.handler"},
                ]
            }
        ]

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.lambda import LambdaAnalyzer

        a = LambdaAnalyzer()
        out = a.analyze()

        self.assertEqual(out["summary"]["total_functions"], 2)
        self.assertEqual(out["summary"]["total_memory_mb"], 128 + 256)
        self.assertEqual(out["summary"]["by_runtime"]["python3.11"], 1)


if __name__ == "__main__":
    unittest.main()
