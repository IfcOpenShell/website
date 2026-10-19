# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ifcopenshell==0.9.0", "ifctester==0.9.0", "ifcdiff==0.9.0",
#   "ifccsv==0.9.0", "ifcclash==0.9.0", "playwright==1.61.0",
#   "requests",
# ]
# ///
"""Execute the website examples and capture their actual stdout/stderr."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from example_catalog import ROOT, fingerprint


def execute(command, cwd, env=None):
    if env and not Path(command[0]).is_absolute():
        command = [shutil.which(command[0], path=env["PATH"]) or command[0], *command[1:]]
    result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=300)
    encoding = "utf-16-le" if os.name == "nt" and Path(command[0]).stem.lower() == "ifcconvert" else "utf-8"
    output = result.stdout.decode(encoding, errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {command}\n{output}")
    return output


def verify_artifacts(filename, directory, output):
    import ifcopenshell
    if filename.startswith("Edit_a_wall"):
        model = ifcopenshell.open(str(directory / "updated-model.ifc"))
        assert model.by_type("IfcWall")[0].Name == "My wall"
        assert len(model.by_type("IfcWall")) == 3
    if filename.startswith("Author_"):
        model = ifcopenshell.open(str(directory / "model.ifc"))
        assert len(model.by_type("IfcWall")) == 1 and model.schema == "IFC4"
    if filename == "Convert.sh":
        assert (directory / "model.glb").read_bytes()[:4] == b"glTF"
        assert b"COLLADA" in (directory / "model.dae").read_bytes()
    if filename == "Validate_IDS.sh":
        assert "[PASS] (1/1)" in output and "[FAIL]" not in output
        assert "Doors have a fire rating" in (directory / "report.html").read_text(encoding="utf-8")
    if filename == "Diff_and_report.sh":
        diff = json.loads((directory / "diff.json").read_text())
        assert len(diff["changed"]) == 1
        assert "Door - 01" in (directory / "doors.csv").read_text()
        clashes = json.loads((directory / "results.json").read_text())
        assert clashes[0]["clashes"] == {}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", action="append", choices=["python", "cpp", "javascript", "pyodide", "cli"])
    parser.add_argument("--prefix", default=os.getenv("IFCOPENSHELL_PREFIX"), help="Installed native IfcOpenShell prefix")
    parser.add_argument("--cmake-arg", action="append", default=[])
    parser.add_argument("--config", default="RelWithDebInfo")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/cpp", help="CMake build directory")
    args = parser.parse_args()
    for package in ("ifcopenshell", "ifctester", "ifcdiff", "ifccsv", "ifcclash"):
        assert importlib.metadata.version(package) == "0.9.0", f"Expected {package}==0.9.0"
    manifest = json.loads((ROOT / "manifest.json").read_text())
    captures_path = ROOT / "captures.json"
    captures = {}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # CLI subprocesses must use the same pinned uv environment as this runner.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    if args.prefix:
        args.prefix = str(Path(args.prefix).resolve())
        env["PATH"] = str(Path(args.prefix) / "bin") + os.pathsep + env["PATH"]
    languages = args.language or list(manifest)
    native_version = None
    sdk_build = None
    if any(lang in languages for lang in ("cpp", "cli")):
        if not args.prefix:
            parser.error("--prefix (or IFCOPENSHELL_PREFIX) is required for C++ and CLI examples")
        config = Path(args.prefix) / "lib/cmake/IfcOpenShell/IfcOpenShellConfigVersion.cmake"
        import re
        native_version = re.search(r'set\(PACKAGE_VERSION "([^"]+)"\)', config.read_text()).group(1)
        build_info = Path(args.prefix) / "build-info.json"
        if build_info.exists():
            info = json.loads(build_info.read_text())
            sdk_build = {key: info[key] for key in ("commit", "architecture", "configuration")}
    build = args.build_dir.resolve()
    if "cpp" in languages:
        print(execute(["cmake", "-S", str(ROOT / "cpp"), "-B", str(build),
                       f"-DIfcOpenShell_DIR={args.prefix}/lib/cmake/IfcOpenShell",
                       f"-DCMAKE_BUILD_TYPE={args.config}", *args.cmake_arg], ROOT))
        print(execute(["cmake", "--build", str(build), "--config", args.config, "--parallel", "2"], ROOT))
    if "javascript" in languages:
        print(execute(["npm.cmd" if os.name == "nt" else "npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], ROOT))
    server = browser = playwright = None
    try:
        if "pyodide" in languages:
            from examples.prepare_pyodide import prepare_wheels
            from playwright.sync_api import sync_playwright
            prepare_wheels()
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
            Thread(target=server.serve_forever, daemon=True).start()
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch()
        for language in languages:
            for filename in manifest[language]:
                print(f"Running {language}/{filename}", flush=True)
                with tempfile.TemporaryDirectory(prefix="ifcos-example-") as temporary:
                    directory = Path(temporary)
                    for fixture in (ROOT / "fixtures").iterdir():
                        shutil.copy2(fixture, directory)
                    source = ROOT / language / filename
                    version = native_version if language == "cpp" else "0.9.0"
                    if language == "pyodide":
                        page = browser.new_page()
                        try:
                            page.goto(f"http://127.0.0.1:{server.server_port}/pyodide/{filename}")
                            page.wait_for_function("window.exampleReady || window.exampleError", timeout=300000)
                            assert not page.evaluate("window.exampleError"), page.locator("#output").inner_text()
                            if filename == "From_a_file_input.html":
                                page.set_input_files("input", str(ROOT / "fixtures/model.ifc"))
                                page.wait_for_function("document.querySelector('#output').textContent.includes('Schema:')")
                            output = page.locator("#output").inner_text()
                            if filename == "Edit_a_wall.html":
                                data = page.evaluate("Array.from(document.defaultView.examplePyodide.FS.readFile('updated-model.ifc'))")
                                (directory / "updated-model.ifc").write_bytes(bytes(data))
                            version = page.evaluate("window.examplePyodide.pyimport('importlib.metadata').version('ifcopenshell')")
                        finally:
                            page.close()
                        command = f"Open examples/pyodide/{filename} over HTTP"
                    elif language == "cli":
                        output = ""
                        for line in source.read_text().splitlines():
                            if not line.strip() or line.startswith("#"):
                                continue
                            output += f"$ {line}\n"
                            argv = shlex.split(line)
                            if argv[0] == "cat":
                                output += (directory / argv[1]).read_text()
                            else:
                                if argv[0] == "python":
                                    argv[0] = sys.executable
                                output += execute(argv, directory, env)
                        command = f"$ sh {filename}"
                    else:
                        if language == "cpp":
                            executable = build / args.config / (source.stem + ".exe") if os.name == "nt" else build / source.stem
                            argv = [str(executable)]
                            command = f"$ ./{source.stem}"
                        else:
                            argv = [sys.executable if language == "python" else "node", str(source)]
                            command = f"$ {'python' if language == 'python' else 'node'} {filename}"
                        output = execute(argv, directory, env)
                    verify_artifacts(filename, directory, output)
                    captures[f"{language}/{filename}"] = {
                        "sha256": fingerprint(language, filename), "command": command,
                        "output": output.rstrip(), "version": version,
                        **({"native_version": native_version} if language in ("cpp", "cli") else {}),
                        **({"sdk": sdk_build} if sdk_build and language in ("cpp", "cli") else {}),
                    }
        previous = json.loads(captures_path.read_text()) if captures_path.exists() else {}
        previous.update(captures)
        captures_path.write_text(json.dumps(previous, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
