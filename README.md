# kicad-mcp-tools

Standalone KiCad automation toolkit extracted from the
[MycoMIDI](https://github.com/rjmendez/MycoMIDI) project.

It packages a small set of stdlib-only utilities that are useful outside
MycoMIDI:

- `kicad_mcp_tools.sexpr_cst` — lossless KiCad S-expression CST parser and serializer
- `kicad_mcp_tools.atomic_write` — same-directory atomic file replacement helper
- `kicad_mcp_tools.drc_classify` — DRC/ERC JSON classifier for clean/findings/malformed states
- `kicad_mcp_tools.pin_header_footprint_gen` — simple through-hole pin-header footprint generator
- `scripts/kicad-cli.sh` — pinned Docker wrapper for `kicad-cli`
- `demo/` — tiny sample schematic and PCB inputs for CLI experiments

## Origin and attribution

These files were extracted from MycoMIDI without removing MycoMIDI's own copy.
The implementation and attribution headers were preserved from that origin.

The toolkit also preserves attribution to the upstream MIT-licensed projects
whose patterns were adapted in MycoMIDI:

- [ProductOfAmerica/mcp-server-kicad](https://github.com/ProductOfAmerica/mcp-server-kicad)
- [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro)

See `THIRD_PARTY_LICENSES.md` for the preserved third-party license text and
provenance notes.

## Install

```bash
pip install .
```

## Run tests

```bash
python3 -m unittest discover tests
```

## Example

```python
from kicad_mcp_tools import classify_kicad_report, generate_pin_header_footprint

result = classify_kicad_report({"violations": [], "unconnected_items": []})
footprint = generate_pin_header_footprint(4)
```
