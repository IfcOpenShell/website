# Runnable homepage examples

The homepage snippets come from these source files. `manifest.json` controls their
order. Optional `begin-example` / `end-example` comments select the portion shown
on the homepage; the source file in this repository contains the complete program.
Multiple marked regions are joined in order, so the Pyodide listings include
the runtime import and installation setup while omitting the HTML output harness.

`fixtures/model.ifc` is a small IFC4 model with three named walls (including solid
geometry), a door, its type, storey and fire rating. `new.ifc` changes one wall's
name. The IDS and clash configuration use this same model. Regenerate the IFC
fixtures with `uv run --with ifcopenshell==0.9.0 examples/create_fixture.py`.

## Build the website

From the `website` directory:

```sh
uv run website.py
```

This embeds every listing and its real captured output directly in the homepage's
inline JavaScript, as before the examples were extracted. The playground needs no
separate example files or runtime fetches. The runnable sources stay in this
repository. The build fails if a source or
fixture changed without refreshing its captured output. The “Show output” button
displays that capture. Standalone Pyodide HTML files execute in the browser.

## Refresh the captures

Install Node.js, CMake, a C++17 compiler, and an installed IfcOpenShell CMake
package with IFC4, OpenCASCADE and IfcConvert. The native package's dependencies
must also be discoverable by CMake (set `CMAKE_PREFIX_PATH` if necessary).

```sh
uv run --with playwright==1.61.0 python -m playwright install chromium
uv run examples/run.py --prefix /path/to/installed-ifcopenshell
uv run website.py
```

Alternatively, refresh and assemble together:

```sh
uv run website.py --refresh-examples --ifcopenshell-prefix /path/to/installed-ifcopenshell
```

`IFCOPENSHELL_PREFIX` also sets the native prefix. On this Windows checkout it is
`C:/Users/tkrij/Documents/AECgeeks/projects/ifcopenshell/v0.9/_installed-vs2022-x64`.
That installation currently identifies itself as **0.9.1**; captures record its
actual version. Python tools and the published NPM packages are pinned to **0.9.0**.

Pyodide uses modular **0.9.1+e050d20** wheels and Pyodide **0.29.5**. Builds fetch
the pinned S3 archive linked from builds.ifcopenshell.org and verify its SHA-256.
The wheels and archive cache are ignored by Git. The published archive predates
the automatic plugin path fix, so preparation applies that Python-only change
without rebuilding binaries. See `pyodide/wheels/README.md` for provenance.

Refresh selected languages with repeated `--language` options, for example:

```sh
uv run examples/run.py --language python --language javascript
```

The runner installs the locked NPM dependencies, builds C++ against the supplied
prefix, runs every selected example in an isolated directory, and checks the
written artifacts. Pyodide runs in Chromium, including selecting the fixture
through the real file input. A failed program or artifact check leaves the
captures unchanged. Only successful runs update `captures.json`.

Extra CMake options use `--cmake-arg=-DName=value` (or
`--examples-cmake-arg=-DName=value` on `website.py`). The default build configuration
is `RelWithDebInfo`.

## Run an individual example

Use a scratch working directory containing copies of the fixtures. Programs read
`model.ifc` relative to the working directory and may overwrite it. With the NPM
dependencies installed using `npm ci` in this folder, run a JavaScript source
with `node /path/to/examples/javascript/Edit_a_wall.mjs`. Run Python with
`uv run --with ifcopenshell==0.9.0 /path/to/examples/python/Edit_a_wall.py`.

C++ sources are independent executables:

```sh
cmake -S examples/cpp -B examples/build/cpp -DCMAKE_PREFIX_PATH=/path/to/installed-ifcopenshell
cmake --build examples/build/cpp --config RelWithDebInfo --target run_examples
```

For Pyodide, first run `uv run examples/prepare_pyodide.py` from `website`,
then serve this folder with `python -m http.server 8000` and open
`http://localhost:8000/pyodide/Edit_a_wall.html`. Each HTML file includes its own
runtime setup and loads the shared fixture over HTTP. Models are parsed directly
with `ifcopenshell.file.from_string()`, using fetched text or `file.text()` from
the file input. No input file is staged in Pyodide's filesystem. The prepared parser
wheel includes the Emscripten-only initializer change from the v0.9 worktree:
importing IfcOpenShell automatically sets its package directory as the plugin
search path when no explicit paths have been configured. Neither the examples
nor the demo app need to configure that path themselves.

## SDK in GitHub Actions

Both `ifcopenshell-docs.yml` and `publish-websites.yml` use the shared
`capture-cpp-examples` action. It downloads `ifcopenshell-cpp-linux64` from
[SDK run 39129013616](https://github.com/IfcOpenShell/IfcOpenShell/actions/runs/39129013616),
checks the archive's SHA-256, extracts the complete SDK, and compiles/runs the
C++ examples in Release mode. It also refreshes the CLI examples using the SDK's
IfcConvert. Captures record the SDK source commit, architecture and configuration.

The docs workflow uploads `website-examples`, containing the captured output and
the assembled homepage HTML. The publishing workflow refreshes those same
examples immediately before building and publishing the homepage. The
`cpp_sdk_run_id` workflow input selects a newer successful SDK run when needed;
the artifact is currently retained upstream for 30 days.

For a separate Linux build alongside the Windows build directory, pass
`--build-dir /path/to/linux-build` to `examples/run.py`.
