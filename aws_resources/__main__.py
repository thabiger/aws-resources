import argparse
import json
import logging
from typing import Any, Dict
from datetime import date, timedelta

from aws_resources.collectors.cost_explorer import CostExplorerCollector
from aws_resources.analyzers.registry import get_analyzer_for_service
import aws_resources.analyzers  # register built-in analyzers
from aws_resources.output.markdown import render_markdown_report

logger = logging.getLogger(__name__)


def discover_command(args):
    # Use Cost Explorer to find which services have cost activity in the given period
    # Default to the current month's first and last day if not provided.
    today = date.today()
    first_of_month = today.replace(day=1)
    # get first day of next month by pushing to a safe day then replacing day=1
    next_month = (first_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_of_month = next_month - timedelta(days=1)

    start = args.start or first_of_month.isoformat()
    end = args.end or last_of_month.isoformat()

    try:
        collector = CostExplorerCollector(profile=args.profile, region_name=args.region)
        services = collector.get_service_costs(start, end)
    except Exception as e:
        # Fall back to a clear error message rather than crashing
        logger.exception("Failed to query Cost Explorer")
        print(json.dumps({"error": str(e)}))
        return

    output: Dict[str, Any] = {"period": {"start": start, "end": end}, "services": []}

    # built-in blacklist: fragments of service names (lowercase) that should
    # always be excluded from analysis. Common example: tax-related charges.
    BUILT_IN_BLACKLIST = {"tax", "taxes"}

    # parse optional service filter (comma-separated list)
    services_filter = None
    if getattr(args, "services", None):
        raw_tokens = [s.strip().lower() for s in args.services.split(",") if s.strip()]

        # common short-name aliases mapping (lowercase) -> list of possible full service name fragments
        ALIASES = {
            "efs": ["amazon elastic file system", "amazon efs"],
            "s3": ["amazon simple storage service", "amazon s3"],
            "dynamodb": ["amazon dynamodb"],
            "ec2": ["amazon elastic compute cloud", "amazon ec2"],
            "ecr": ["amazon elastic container registry", "amazon ecr"],
            "ecs": ["amazon elastic container service", "amazon ecs"],
            "eks": ["amazon elastic kubernetes service", "amazon eks"],
            "rds": ["amazon relational database service", "amazon rds"],
            "opensearch": ["amazon opensearch service", "amazon elasticsearch"],
            "elasticache": ["amazon elasticache"],
            "cloudfront": ["amazon cloudfront"],
            "route53": ["amazon route 53", "amazon route53"],
            "ses": ["amazon simple email service", "aws ses"],
            "sns": ["amazon simple notification service"],
            "sqs": ["amazon simple queue service"],
            "lambda": ["aws lambda", "amazon lambda"],
            "docdb": ["amazon documentdb", "amazon documentdb (with mongodb compatibility)"],
        }

        # build a set of acceptable service name fragments (lowercase) from tokens and aliases
        services_filter = set()
        for t in raw_tokens:
            services_filter.add(t)
            if t in ALIASES:
                for a in ALIASES[t]:
                    services_filter.add(a)

    for svc in services:
        svc_name = svc.get("service")
        svc_cost = svc.get("amount")
        svc_name_lower = (svc_name or "").lower()

        # skip built-in blacklisted services first
        if any(fragment in svc_name_lower for fragment in BUILT_IN_BLACKLIST):
            logger.debug("Skipping service '%s' due to built-in blacklist", svc_name)
            continue

        # apply optional service filter: if provided, only process services
        # whose name contains one of the filter fragments (case-insensitive)
        if services_filter:
            if not any(fragment in svc_name_lower for fragment in services_filter):
                logger.debug("Skipping service '%s' due to --services filter", svc_name)
                continue

        analyzer_factory = get_analyzer_for_service(svc_name)
        if analyzer_factory:
            try:
                # Create analyzer instance passing through profile/region if the
                # factory accepts them. Factories for built-in analyzers accept
                # (profile, region_name) as optional keyword args.
                try:
                    analyzer = analyzer_factory(profile=args.profile, region_name=args.region)
                except TypeError:
                    # backward-compat: factory may not accept args
                    analyzer = analyzer_factory()

                detail = analyzer.analyze(include_details=bool(getattr(args, "resources_details", False)))
                output["services"].append({"name": svc_name, "cost": svc_cost, "supported": True, "detail": detail})
            except Exception as e:
                logger.exception("Analyzer failed for %s", svc_name)
                output["services"].append({"name": svc_name, "cost": svc_cost, "supported": False, "note": f"analyzer error: {e}"})
        else:
            output["services"].append({"name": svc_name, "cost": svc_cost, "supported": False, "note": "In-depth analysis not supported yet"})

    # final output: either JSON (default) or a pretty Markdown report
    out_format = getattr(args, "out_format", "json")
    if out_format == "json":
        print(json.dumps(output, indent=2))
    else:
        print(render_markdown_report(output))

    # markdown renderer moved to `aws_resources.output.markdown`


def main():
    parser = argparse.ArgumentParser(prog="aws_resources")
    subparsers = parser.add_subparsers(dest="command")

    discover = subparsers.add_parser("discover", help="Discover AWS resources")
    discover.add_argument("--start", required=False, help="Start date (YYYY-MM-DD)")
    discover.add_argument("--end", required=False, help="End date (YYYY-MM-DD)")
    discover.add_argument("--profile", required=False, help="AWS profile to use")
    discover.add_argument("--region", required=False, help="AWS region to use (optional)")
    discover.add_argument("--resources-details", action="store_true", dest="resources_details",
                          help="Include per-resource details for supported services (default: summary only)")
    discover.add_argument("--services", required=False,
                          help="Comma-separated list of service names to analyze (only these will be processed)")
    discover.add_argument("--format", "--output-format", dest="out_format",
                          choices=["json", "md"], default="json",
                          help="Output format: 'json' (default) or 'md' for a pretty Markdown report")

    args = parser.parse_args()

    if args.command == "discover":
        discover_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
