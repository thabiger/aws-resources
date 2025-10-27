"""Markdown report renderer for aws_resources discover output.

This module provides a single entrypoint `render_markdown_report(output)` which
accepts the same output dict produced by the discover command and returns a
string with a pretty Markdown representation.

The implementation is deliberately small and dependency-free so it can be used
in CI or shipped as part of the package without adding dependencies.
"""
from typing import Any, Dict


def _fmt_num(v):
    try:
        if isinstance(v, int):
            return f"{v:,}"
        if isinstance(v, float):
            return f"{v:,.2f}"
    except Exception:
        pass
    return str(v)


def _render_md_list(lst: list, indent: int = 0) -> list:
    lines = []
    prefix = "  " * indent
    for item in lst[:20]:
        if isinstance(item, dict):
            # render mapping inline
            for k, v in item.items():
                lines.append(f"{prefix}- {k}: {v}")
        else:
            lines.append(f"{prefix}- {item}")
    if len(lst) > 20:
        lines.append(f"{prefix}- ... and {len(lst)-20} more items")
    return lines


def _render_md_mapping(m: Dict[str, Any], indent: int = 0) -> list:
    lines = []
    prefix = "  " * indent
    for k, v in m.items():
        if isinstance(v, dict):
            # if inner dict has primitive values, render as bullets
            if all(not isinstance(x, (dict, list)) for x in v.values()):
                lines.append(f"{prefix}- **{k}**:")
                for subk, subv in v.items():
                    lines.append(
                        f"{prefix}  - {subk}: {_fmt_num(subv) if isinstance(subv, (int, float)) else subv}"
                    )
            else:
                lines.append(f"{prefix}- **{k}**:")
                for subk, subv in v.items():
                    # if subv is primitive, render inline
                    if not isinstance(subv, (dict, list)):
                        lines.append(
                            f"{prefix}  - {subk}: {_fmt_num(subv) if isinstance(subv, (int, float)) else subv}"
                        )
                    else:
                        lines.append(f"{prefix}  - {subk}:")
                        if isinstance(subv, dict):
                            lines.extend(_render_md_mapping(subv, indent + 2))
                        elif isinstance(subv, list):
                            lines.extend(_render_md_list(subv, indent + 2))
        elif isinstance(v, list):
            lines.append(f"{prefix}- **{k}**: {len(v)} items")
            lines.extend(_render_md_list(v, indent + 1))
        else:
            lines.append(
                f"{prefix}- **{k}**: {_fmt_num(v) if isinstance(v, (int, float)) else v}"
            )
    return lines


def render_markdown_report(output: Dict[str, Any]) -> str:
    """Render the discovery output as a human-friendly Markdown report."""
    lines = []
    period = output.get("period", {})
    start = period.get("start")
    end = period.get("end")
    lines.append("# AWS Resources Report")
    if start or end:
        lines.append(f"**Period:** {start or 'N/A'} — {end or 'N/A'}")
    lines.append("")

    services = list(output.get("services", []))
    # sort by cost descending if present
    try:
        services.sort(key=lambda s: float(s.get("cost") or 0), reverse=True)
    except Exception:
        pass

    for svc in services:
        name = svc.get("name") or "<unknown>"
        cost = svc.get("cost")
        supported = bool(svc.get("supported", False))
        note = svc.get("note")

        # header for service
        cost_str = _fmt_num(cost) if cost is not None else "N/A"
        lines.append(f"## {name} — ${cost_str}")
        if note:
            lines.append(f"- Note: {note}")

        # render summary if available
        detail = svc.get("detail") or {}
        summary = detail.get("summary") if isinstance(detail, dict) else None
        if summary:
            lines.append("")
            lines.append("### Summary")
            lines.extend(_render_md_mapping(summary, indent=0))

        lines.append("")

    return "\n".join(lines)
