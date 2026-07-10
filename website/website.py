#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "jinja2",
#     "PyGithub",
#     "requests",
# ]
# ///

"""
Generate static HTML for ifcopenshell.org and bonsaibim.org.

Environment variables:
  GH_APIKEY  GitHub personal access token. Used to fetch VERSION and the list
             of code contributors. When unset, placeholder data is used.
  OSC_APIKEY OpenCollective API key. Used to fetch financial donors. When unset,
             donors are skipped (and placeholder data is used if no other
             contributors are available).
  COMMIT     Commit SHA to use as the source for VERSION.
             By default the latest commit on the default branch is used.

If neither GH_APIKEY nor OSC_APIKEY is set the site still builds end to end
using placeholder data, which is handy for local previews.
"""

import itertools
import operator
import os
import shutil

import requests
from github import Auth, Github
from jinja2 import Environment, FileSystemLoader

GH_APIKEY = os.getenv("GH_APIKEY")
OSC_APIKEY = os.getenv("OSC_APIKEY")

if GH_APIKEY:
    gh = Github(auth=Auth.Token(GH_APIKEY))
    ifcopenshell_repo = gh.get_repo("IfcOpenShell/IfcOpenShell")
else:
    print("warning: GH_APIKEY is not set; using a placeholder VERSION and no code contributors.")
    ifcopenshell_repo = None


def placeholder_contributors():
    """Fake contributor data so the site renders without any API keys."""
    avatar = "assets/images/partner/partner-11.png"

    def make(name, type_):
        return {"name": name, "avatar": avatar, "url": "#", "type": type_, "amount": 0}

    return {
        "tier1": [make(f"Placeholder Sponsor {i}", "donor") for i in range(1, 5)],
        "tier2": [make(f"Placeholder Backer {i}", "donor") for i in range(1, 9)],
        "tier3": [make(f"Placeholder Contributor {i}", "developer") for i in range(1, 25)],
    }


def get_contributors():
    tier1 = []
    tier2 = []
    tier3 = []

    if not OSC_APIKEY:
        print("warning: OSC_APIKEY is not set; skipping OpenCollective donors.")

    endpoint = "https://api.opencollective.com/graphql/v2"
    query = """
    query account($slug: String) {
      account(slug: $slug) {
        name
        slug
        members(limit: 1000) {
          totalCount
          nodes {
            totalDonations {
              value
              currency
            }
            account {
              name
              website
              imageUrl(height: 100, format: png)
              slug
            }
          }
        }
      }
    }
    """

    # @todo We can get the github contribution link from the opencollective profile
    # to sum financial and code contributions.

    # @todo Add a little tag on the avator to indicate [$] or [</>] and maybe a tooltip
    # to provide a textual summary of the provided contribution.

    if OSC_APIKEY:
        dicts = {}
        for slug in ["opensourcebim", "apple-m1-build-server", "full-infra-geom-implementation"]:
            results = requests.post(
                endpoint, json={"query": query, "variables": {"slug": slug}}, headers={"Api-Key": OSC_APIKEY}
            ).json()

            nodes = results["data"]["account"]["members"]["nodes"]

            def make_dict(result):
                slug = result["account"]["slug"]
                di = {
                    "name": result["account"]["name"],
                    "avatar": result["account"]["imageUrl"],
                    "url": "https://opencollective.com/" + result["account"]["slug"],
                    "type": "donor",
                    "amount": result["totalDonations"]["value"],
                }
                return slug, di

            # Seems like some members are mentioned multiple times, with indentical
            # data, folding data based on slug eliminates these duplicates.
            for slug, di in dict(map(make_dict, nodes)).items():
                if slug in dicts:
                    dicts[slug]["amount"] += di["amount"]
                else:
                    dicts[slug] = di

        for data in sorted(dicts.values(), key=operator.itemgetter("amount"), reverse=True):
            if data["amount"] >= 500:
                tier1.append(data)
            elif data["amount"] >= 250:
                tier2.append(data)
            else:
                tier3.append(data)

    # Devs are contributors too!
    if ifcopenshell_repo is not None:
        for member in itertools.islice(ifcopenshell_repo.get_contributors(), 1000):
            data = {
                "name": member.login,
                "avatar": member.avatar_url,
                "url": member.html_url,
                "type": "developer",
                "amount": member.contributions,
            }
            if data["amount"] >= 500:
                tier1.append(data)
            elif data["amount"] >= 50:
                tier2.append(data)
            else:
                tier3.append(data)

    if not (tier1 or tier2 or tier3):
        print("warning: no contributor data available; using placeholder contributors.")
        return placeholder_contributors()

    return {"tier1": tier1, "tier2": tier2, "tier3": tier3}


pages = {
    "ifcopenshell": {
        "index": "IfcOpenShell - The open source IFC toolkit and geometry engine",
        "downloads": "Downloads - IfcOpenShell C++, Python, and utilities",
        "upload": "Upload - Private filesharing for issues",
    },
    "bonsaibim": {
        "blender": "Bonsai - beautiful, detailed, and data-rich OpenBIM",
        "download": "Download - install Bonsai for Windows, Mac, and Linux",
        "community": "Community - provide support, share your work, and learn together",
        "search-ifc-class": "Search IFC class - find the correct IFC class to use in your BIM model",
    },
}

if ifcopenshell_repo is not None:
    _version_kwargs = {"ref": commit} if (commit := os.getenv("COMMIT")) else {}
    VERSION = ifcopenshell_repo.get_contents("VERSION", **_version_kwargs).decoded_content.decode().strip()
else:
    VERSION = "0.0.0-dev"

environment = Environment(loader=FileSystemLoader("templates/"))

for brand, content in pages.items():
    os.makedirs(f"{brand}_org_static_html", exist_ok=True)
    shutil.copytree("assets", f"{brand}_org_static_html/assets", dirs_exist_ok=True)
    for page, title in content.items():
        template = environment.get_template(f"{page}.html")
        filename = f"{page}.html"
        extra = {}
        if brand == "ifcopenshell" and page == "index":
            extra = get_contributors()
        elif brand == "bonsaibim" and page == "blender":
            filename = "index.html"
        content = template.render(brand=brand, page=page, title=title, version=VERSION, **extra)
        with open(f"{brand}_org_static_html/{filename}", mode="w", encoding="utf-8") as f:
            f.write(content)
