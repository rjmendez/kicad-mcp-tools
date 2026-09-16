# kicad-mcp-tools

[![CI](https://github.com/rjmendez/kicad-mcp-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/rjmendez/kicad-mcp-tools/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-coming_soon-lightgrey)](https://pypi.org/project/kicad-mcp-tools/)

Standalone KiCad automation toolkit extracted from the
[MycoMIDI](https://github.com/rjmendez/MycoMIDI) project.

## What is this?

`kicad-mcp-tools` is a small, stdlib-only Python toolkit for automating common
KiCad-adjacent tasks without depending on a running KiCad instance. It packages
reusable helpers that started life inside MycoMIDI and proved useful enough to
stand alone.

It currently includes:

- `kicad_mcp_tools.sexpr_cst` — lossless KiCad S-expression CST parser and serializer
- `kicad_mcp_tools.atomic_write` — same-directory atomic file replacement helper
- `kicad_mcp_tools.drc_classify` — DRC/ERC JSON classifier for clean/findings/malformed states
- `kicad_mcp_tools.pin_header_footprint_gen` — simple through-hole pin-header footprint generator
- `scripts/kicad-cli.sh` — pinned Docker wrapper for `kicad-cli`
- `demo/` — tiny sample schematic and PCB inputs for CLI experiments

## Why does it exist?

This repository was split out from the hardware-design automation work behind
MycoMIDI, a bioelectric-signal-to-MIDI project that needed lightweight,
scriptable KiCad tooling during schematic, PCB, and validation workflows.

The extraction keeps that tooling reusable for other projects while preserving
credit to the open-source KiCad MCP server work that informed the approach:

- [MycoMIDI](https://github.com/rjmendez/MycoMIDI)
- [ProductOfAmerica/mcp-server-kicad](https://github.com/ProductOfAmerica/mcp-server-kicad)
- [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro)

## Origin and attribution

These files were extracted from MycoMIDI without removing MycoMIDI's own copy.
The implementation and attribution headers were preserved from that origin.

The toolkit also preserves attribution to the upstream MIT-licensed projects
whose patterns were adapted in MycoMIDI:

- [ProductOfAmerica/mcp-server-kicad](https://github.com/ProductOfAmerica/mcp-server-kicad)
- [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro)

See `THIRD_PARTY_LICENSES.md` for the preserved third-party license text and
provenance notes.

## Installation

Once the package is published:

```bash
pip install kicad-mcp-tools
```

From source today:

```bash
git clone https://github.com/rjmendez/kicad-mcp-tools.git
cd kicad-mcp-tools
pip install -e .
```

## Run tests

```bash
python3 -m unittest discover tests
```

## Quickstart

```python
from kicad_mcp_tools import generate_electrode_connector_footprint, parse

footprint = generate_electrode_connector_footprint(4)
tree = parse(footprint.encode("utf-8"))

print(tree.lists[0].head)          # footprint
print(len(tree.lists[0].find_all("pad")))  # 4
```
