"""Assemble runnable sources and verified execution output for the homepage."""
import hashlib
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).parent / "examples"


def fingerprint(language, filename):
    paths = [ROOT / language / filename, ROOT / "manifest.json"]
    paths += sorted((ROOT / "fixtures").glob("*"))
    if language == "cpp":
        paths.append(ROOT / "cpp/CMakeLists.txt")
    if language == "javascript":
        paths += [ROOT / "package.json", ROOT / "package-lock.json"]
    if language == "pyodide":
        paths += [ROOT / "pyodide/wheels.json", ROOT / "prepare_pyodide.py"]
    digest = hashlib.sha256()
    for path in paths:
        # Captures must survive Git checkouts with either LF or CRLF endings.
        data = path.read_bytes()
        if path.suffix != ".whl":
            data = data.replace(b"\r\n", b"\n")
        digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
        digest.update(data + b"\0")
    return digest.hexdigest()


def listing(source):
    if "begin-example" not in source:
        return source.rstrip()
    lines = source.splitlines()
    fragments = []
    current = None
    for line in lines:
        if "begin-example" in line:
            if current is not None:
                raise ValueError("Nested begin-example marker")
            current = []
        elif "end-example" in line:
            if current is None:
                raise ValueError("end-example without begin-example")
            fragments.append(textwrap.dedent("\n".join(current)).strip())
            current = None
        elif current is not None:
            current.append(line)
    if current is not None:
        raise ValueError("Missing end-example marker")
    return "\n\n".join(fragments)


def load_examples():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    captures = json.loads((ROOT / "captures.json").read_text())
    result = {}
    for language, filenames in manifest.items():
        result[language] = []
        for filename in filenames:
            path = ROOT / language / filename
            capture = captures[f"{language}/{filename}"]
            if capture["sha256"] != fingerprint(language, filename):
                raise RuntimeError(f"Stale example output: {path}. Refresh with uv run examples/run.py.")
            result[language].append({
                "name": path.stem.replace("_", " ").replace("IDS", "(IDS)"),
                "file": filename,
                "code": listing(path.read_text(encoding="utf-8")),
                "out": capture["output"],
                "command": capture["command"],
            })
    return result
