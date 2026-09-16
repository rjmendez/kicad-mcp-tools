"""MCP server exposing the standalone KiCad helper functions."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from .drc_classify import classify_kicad_report
from .pin_header_footprint_gen import generate_pin_header_footprint as _generate_pin_header_footprint
from .sexpr_cst import Atom, Doc, List, Node, parse, serialize

mcp = MCPServer(
    "kicad-tools",
    title="KiCad MCP Tools",
    description="Standalone KiCad S-expression, DRC/ERC, and footprint helpers.",
)


def _node_to_data(node: Node) -> dict[str, Any]:
    if isinstance(node, Atom):
        return {
            "kind": node.kind,
            "text": node.text,
        }

    children = [_node_to_data(child) for child in node.children or ()]
    data: dict[str, Any] = {
        "kind": node.kind,
        "children": children,
    }
    if isinstance(node, (Doc, List)):
        data["head"] = node.head
    return data


@mcp.tool(structured_output=True)
def parse_kicad_sexpr(text: str) -> dict[str, Any]:
    """Parse KiCad S-expression text into a structured CST-like representation."""
    document = parse(text.encode("utf-8"))
    return _node_to_data(document)


@mcp.tool(structured_output=True)
def roundtrip_kicad_sexpr(text: str) -> dict[str, Any]:
    """Parse and re-serialize KiCad S-expression text to validate byte-preserving round-trips."""
    document = parse(text.encode("utf-8"))
    serialized_text = serialize(document).decode("utf-8", "surrogateescape")
    return {
        "round_trip_equal": serialized_text == text,
        "serialized_text": serialized_text,
    }


@mcp.tool(structured_output=True)
def classify_drc_report(json_text: str) -> dict[str, Any]:
    """Classify KiCad DRC/ERC JSON as clean, findings, malformed, or unavailable."""
    return asdict(classify_kicad_report(json_text))


@mcp.tool()
def generate_pin_header_footprint(
    pin_count: int,
    pitch_mm: float = 2.54,
    rows: int = 1,
    name: str | None = None,
    description: str | None = None,
) -> str:
    """Generate a through-hole pin-header footprint as KiCad .kicad_mod S-expression text."""
    return _generate_pin_header_footprint(
        pin_count,
        rows=rows,
        pitch_mm=pitch_mm,
        name=name,
        description=description,
    )


def main() -> None:
    """Run the KiCad MCP server over stdio."""
    mcp.run()


__all__ = [
    "classify_drc_report",
    "generate_pin_header_footprint",
    "main",
    "mcp",
    "parse_kicad_sexpr",
    "roundtrip_kicad_sexpr",
]
