"""Redirect the old Bonsai docs URLs to their new home under /studio/.

Until 2026-09 the Bonsai (Studio) docs were published at the root of
docs.bonsaibim.org. Shipped versions of Bonsai, bonsaibim.org, forum posts and
search engines still link to those paths, so for every page under studio/ this
writes a stub at the old path that forwards to the new one.

TODO: delete this script, its call in bonsai-docs.yml and the stubs it writes
after 2027-09-20.

Usage: redirects.py <root of the docs.bonsaibim.org checkout>
"""

import sys
from pathlib import Path

STUB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting</title>
<link rel="canonical" href="https://docs.bonsaibim.org/studio/{page}">
<meta http-equiv="refresh" content="0; url=/studio/{page}">
<script>location.replace("/studio/{page}" + location.hash);</script>
</head>
<body>
<p>This page moved to <a href="/studio/{page}">/studio/{page}</a>.</p>
</body>
</html>
"""

root = Path(sys.argv[1])
for page in (root / "studio").rglob("*.html"):
    relative = page.relative_to(root / "studio")
    # The root index is the landing page for all the Bonsai docs.
    if relative == Path("index.html"):
        continue
    stub = root / relative
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(STUB.format(page=relative.as_posix()))
