# aws-resources

A small CLI and analyzer framework that starts from Cost Explorer and runs per-service analyzers to produce a compact, shareable report about which AWS resources are in use and how much they cost.

This repository contains:
- A CLI entrypoint (module-style) at `aws_resources/__main__.py`.
- Per-service analyzers under `aws_resources/analyzers/`.
- Output renderers (JSON + Markdown) in `aws_resources/output/`.
- An example anonymized report in `example-report.json` and `example-report.md`.

Goals
- Produce a cost-first inventory report (summary by default, optional resource-level details).
- Make it easy to add service analyzers.
- Allow exporting pretty Markdown reports for sharing or JSON for programmatic consumption.

Quickstart
----------

Prerequisites
- Python 3.10+ (project uses modern typing features)
- A virtualenv or your preferred environment manager

Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the CLI (basic)

The package exposes a module-style CLI. The simplest invocation prints a JSON report to stdout:

```bash
python -m aws_resources
# -> JSON document printed to stdout (default)
```

Common usage examples
---------------------

- Generate a Markdown report for all services and save it to a file:

```bash
python -m aws_resources --output-format md > report.md
```

- Run only a subset of services (short-name aliases are supported) and include resource-level details:

```bash
python -m aws_resources --services ec2,rds,s3 --resources-details --output-format md > compute-and-storage.md
```

- Produce machine-friendly JSON (default) and filter to just S3 and CloudFront:

```bash
python -m aws_resources --services s3,cloudfront > summary.json
```

Flags you can use
- --services    Comma-separated short-names (e.g. ec2,rds,s3). Partial/alias matching supported.
- --resources-details  Include per-resource detail output where the analyzer supports it.
- --output-format / --out-format  Choose output format: json (default) or md (markdown).

Examples of expected outputs
- JSON: a structured document (see `example-report.json`) describing period, services, costs, and details when asked.
- Markdown: a human-friendly summary produced by `aws_resources/output/markdown.py` (see `example-report.md`).

How it works (brief)
- A Cost Explorer collector provides the starting cost information per service.
- An analyzer registry discovers and runs per-service analyzers (one analyzer per service).
- Each analyzer implements an analyze(include_details: bool) -> dict method and returns a normalized summary structure used by the renderers.

Extending the project — adding a new analyzer
--------------------------------------------

If you want to add support for a new AWS service, follow these steps.

1) Add a new analyzer file

Create a new file under `aws_resources/analyzers/`, for example `aws_resources/analyzers/myservice.py`.

Here's a minimal analyzer skeleton to copy and adapt:

```python
from typing import Dict, Any

class MyServiceAnalyzer:
	"""Analyzer interface used by the analyzer registry.

	Contract (informal):
	- inputs: access to boto3 (or mocks in tests), current account/region context
	- method: analyze(include_details: bool) -> Dict[str, Any]
	- output: a dict with at least `summary` and optional `resources`/`detail` keys
	"""

	def __init__(self, boto3_session=None):
		self.session = boto3_session

	def analyze(self, include_details: bool = False) -> Dict[str, Any]:
		# collect and return a normalized dict, e.g.:
		return {
			"name": "My Service",
			"cost": 0.0,
			"supported": True,
			"detail": {
				"summary": {
					"total_resources": 0,
				}
			}
		}

```

2) Register the analyzer

Open `aws_resources/analyzers/__init__.py` and add your analyzer to the registry or import list used by the CLI. The project discovers analyzers through that module.

3) Implement tests

Create unit tests under `tests/` using `unittest` (the project uses stdlib unittest with mocks). Example pattern:

```python
import unittest
from unittest.mock import MagicMock
from aws_resources.analyzers.myservice import MyServiceAnalyzer

class TestMyServiceAnalyzer(unittest.TestCase):
	def test_analyze_summary(self):
		fake_session = MagicMock()
		# configure fake_session clients/responses
		analyzer = MyServiceAnalyzer(boto3_session=fake_session)
		out = analyzer.analyze(include_details=False)
		self.assertIn('detail', out)

if __name__ == '__main__':
	unittest.main()
```

4) Run tests

```bash
python -m unittest discover -v
```

5) Documentation & examples

- Add any notes required for your analyzer to the project README or `docs/` (if present).
- Include example JSON snippets in tests to clarify expected shapes.

Renderer notes
--------------

The Markdown renderer lives in `aws_resources/output/markdown.py`. It accepts the normalized report produced by the main runner and emits readable sections. If you change the output shape of analyzers, update the renderer accordingly.

Contribution guidelines (short)
-----------------------------

- Fork the repo and create a topic branch for your feature.
- Keep analyzer implementations small and focused; prefer composition over large monolithic files.
- Add unit tests that mock AWS responses rather than calling the real AWS APIs.
- Keep output shapes backward compatible where possible. If you need breaking changes, document them.
- Submit a PR with a clear title, description, and tests. Add example output if the analyzer is non-trivial.

Developer workflow & tips
------------------------

- Iterative development: implement analyzer -> unit tests -> run CLI with `--services` to smoke test.
- Use the example files `example-report.json` and `example-report.md` as fixtures for UI/renderer changes.
- To quickly render the Markdown from an existing JSON (if you want a small helper):

```python
import json
from aws_resources.output.markdown import render_markdown_report

with open('example-report.json') as f:
	report = json.load(f)

print(render_markdown_report(report))
```

Packaging / project commands
---------------------------

- Run unit tests: `python -m unittest discover -v`
- Run the CLI: `python -m aws_resources --output-format md > report.md`

License & contact
-----------------

This project is provided as-is. If you contribute, add a short description in the PR and mention whether you want your contribution to be licensed under the project license.

Acknowledgements
----------------
Thanks for using and contributing — small, well-scoped analyzers make this project easy to extend and maintain.

