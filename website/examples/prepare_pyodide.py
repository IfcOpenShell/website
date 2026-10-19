# /// script
# dependencies = ["requests"]
# ///
"""Fetch the pinned Pyodide wheels from the archive listed on builds.ifcopenshell.org."""

import base64
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
INITIALIZER = """if sys.platform == "emscripten" and not ifcopenshell_wrapper.get_plugin_search_paths():
    # Pyodide installs optional plugin wheels alongside the Python package.
    ifcopenshell_wrapper.set_plugin_search_paths([os.path.dirname(os.path.abspath(__file__))])

"""


def patch_initializer(wheel):
    """Carry the Python-only v0.9 initializer fix until a rebuilt wheel is published."""
    with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
        entries = archive.infolist()
        payload = {entry.filename: archive.read(entry.filename) for entry in entries}
    source = payload["ifcopenshell/__init__.py"].decode().replace("\r\n", "\n")
    if INITIALIZER.strip() in source:
        return wheel
    marker = "from . import file as file_module"
    if source.count(marker) != 1:
        raise RuntimeError("Unexpected IfcOpenShell initializer; review the pinned Pyodide build")
    payload["ifcopenshell/__init__.py"] = source.replace(marker, INITIALIZER + "\n" + marker, 1).encode()

    record = next(name for name in payload if name.endswith(".dist-info/RECORD"))
    rows = []
    for name, data in payload.items():
        digest = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        rows.append([name, "", ""] if name == record else [name, digest, str(len(data))])
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerows(rows)
    payload[record] = output.getvalue().encode()
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as archive:
        for entry in entries:
            archive.writestr(entry, payload[entry.filename])
    return result.getvalue()


def prepare_wheels():
    manifest = json.loads((ROOT / "pyodide/wheels.json").read_text())
    cache = ROOT / "build/pyodide" / (manifest["sha256"] + ".zip")
    cache.parent.mkdir(parents=True, exist_ok=True)
    data = cache.read_bytes() if cache.exists() else b""
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        print(f"Downloading Pyodide wheels: {manifest['url']}", flush=True)
        with requests.get(manifest["url"], timeout=60) as response:
            response.raise_for_status()
            data = response.content
        if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
            raise RuntimeError("Pyodide archive SHA-256 does not match wheels.json")
        cache.write_bytes(data)

    destination = ROOT / "pyodide/wheels"
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in manifest["files"]:
            wheel = archive.read(name)
            if name.startswith("ifcopenshell-"):
                wheel = patch_initializer(wheel)
            path = destination / name
            if not path.exists() or path.read_bytes() != wheel:
                path.write_bytes(wheel)
    return destination


if __name__ == "__main__":
    prepare_wheels()
