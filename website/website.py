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
  GH_APIKEY  GitHub personal access token (required).
  OSC_APIKEY OpenCollective API key (required).
  COMMIT     Commit SHA to use as the source for VERSION.
             By default the latest commit on the default branch is used.
"""

import itertools
import operator
import os
import shutil

import requests
from github import Auth, Github
from jinja2 import Environment, FileSystemLoader

gh = Github(auth=Auth.Token(os.environ["GH_APIKEY"]))
ifcopenshell_repo = gh.get_repo("IfcOpenShell/IfcOpenShell")


def get_contributors():
    osc_apikey = os.environ["OSC_APIKEY"]

    tier1 = []
    tier2 = []
    tier3 = []

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

    dicts = {}
    for slug in ["opensourcebim", "apple-m1-build-server", "full-infra-geom-implementation"]:
        results = requests.post(
            endpoint, json={"query": query, "variables": {"slug": slug}}, headers={"Api-Key": osc_apikey}
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

_version_kwargs = {"ref": commit} if (commit := os.getenv("COMMIT")) else {}
VERSION = ifcopenshell_repo.get_contents("VERSION", **_version_kwargs).decoded_content.decode().strip()

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
