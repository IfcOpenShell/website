# Pyodide runtime assets

The wheel files in this directory are downloaded build assets, ignored by Git.
`uv run website.py` and the Pyodide example runner automatically prepare them.
For standalone use, run `uv run examples/prepare_pyodide.py` first.

The pinned **0.9.1+e050d20** modular archive is linked from
[builds.ifcopenshell.org](https://builds.ifcopenshell.org/) and downloaded from
[S3](https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-modular-v0.9.1-e050d20-pyodide.zip).
`../wheels.json` records its URL, SHA-256, and the three wheel filenames needed by
the examples: parser, IFC4 schema, and Python utilities. The verified archive is
cached under the ignored `examples/build/pyodide` directory.

This published build predates the Emscripten-only automatic plugin path fix.
`prepare_pyodide.py` applies that small `ifcopenshell/__init__.py` change and
regenerates `RECORD` after extraction. Every other wheel payload, including all
binaries, is preserved. Switch the manifest to a rebuilt archive and remove the
compatibility patch when the fix is published.

The example fingerprints include the pinned manifest, preparation script, and
HTML source. IfcOpenShell is distributed under LGPL-3.0-or-later.
