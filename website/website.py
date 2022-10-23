import os
import shutil
import requests
from jinja2 import Environment, FileSystemLoader

osc_apikey = os.environ["OSC_APIKEY"]
gh_apikey = os.environ["GH_APIKEY"]

def get_contributors():

    tier1 = []
    tier2 = []
    tier3 = []

    endpoint = "https://api.opencollective.com/graphql/v2"
    query = """
    query account($slug: String) {
      account(slug: $slug) {
        name
        slug
        members(limit: 100) {
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

    results = requests.post(
        endpoint, json={"query": query, "variables": {"slug": "opensourcebim"}}, headers={"Api-Key": osc_apikey}
    ).json()
    totalContributors = results["data"]["account"]["members"]["totalCount"]
    names = set()
    for result in sorted(results["data"]["account"]["members"]["nodes"], key=lambda m: m["totalDonations"]["value"])[::-1]:
        data = {
            "name": result["account"]["name"],
            "avatar": result["account"]["imageUrl"],
            "url": "https://opencollective.com/" + result["account"]["slug"],
            "type": "donor",
            "amount": result["totalDonations"]["value"],
        }
        if data["name"] in names:
            continue  # Seems like some members are mentioned multiple times
        if data["amount"] >= 500:
            tier1.append(data)
        elif data["amount"] >= 250:
            tier2.append(data)
        else:
            tier3.append(data)
        names.add(data["name"])

    # Devs are contributors too!
    page = 1
    while True:
        results = requests.get(
            f"https://api.github.com/repos/ifcopenshell/ifcopenshell/contributors?page={page}&per_page=100",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {gh_apikey}",
            },
        ).json()
        page += 1
        if not results or page > 10:
            break
        for member in results:
            data = {
                "name": member["login"],
                "avatar": member["avatar_url"],
                "url": member["html_url"],
                "type": "developer",
                "amount": member["contributions"],
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
    },
    "blenderbim": {
        "blender": "BlenderBIM Add-on - beautiful, detailed, and data-rich OpenBIM",
        "download": "Download - install the BlenderBIM Add-on for Windows, Mac, and Linux",
        "community": "Community - provide support, share your work, and learn together",
    },
}

environment = Environment(loader=FileSystemLoader("templates/"))

for brand, content in pages.items():
    os.makedirs(f"{brand}_org_static_html", exist_ok=True)
    shutil.copytree("assets", f"{brand}_org_static_html/assets",dirs_exist_ok=True)
    for page, title in content.items():
        template = environment.get_template(f"{page}.html")
        filename = f"{page}.html"
        extra = {}
        if brand == "ifcopenshell" and page == "index":
            extra = get_contributors()
        elif brand == "blenderbim" and page == "blender":
            filename = "index.html"
        content = template.render(brand=brand, page=page, title=title, **extra)
        with open(f"{brand}_org_static_html/{filename}", mode="w", encoding="utf-8") as f:
            f.write(content)