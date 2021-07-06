import re

from github import Github
from werkzeug.contrib.cache import SimpleCache


def get_commit_comment(branch):
    def has_comments(commit):
        comments = commit.get_comments()
        for comment in comments:
            if comment.user.login == "IfcOpenBot":
                if "v0.6.0" in comment.body:
                    return True

    def get_commit_with_comment(commit):
        if has_comments(commit):
            return commit

        for acommit in commit.parents:
            return get_commit_with_comment(acommit)

    g = Github()
    repo = g.get_repo("IfcOpenBot/IfcOpenShell")

    # commits on the website are currently hardcoded
    if branch == "master":
        commit = repo.get_commit("8625aab5f0c2c4752eb10ad20daee744547b377e")
    else:
        commit = repo.get_commit("517b81950478e2eb580b24cd03c5a9907f23979c")

    head_commit = repo.get_branch(branch).commit
    commit = get_commit_with_comment(head_commit)

    return list(commit.get_comments())[0].body


cache = SimpleCache()


def get_commit_comment_cached(branch):
    rv = cache.get(branch)
    if rv is None:
        rv = get_commit_comment(branch)
        cache.set(branch, rv, timeout=60 * 60 * 8)
    return rv


def build_dict(first_comment_body):
    d = {
        "IfcBlender": [],
        "IfcGeomServer": [],
        "IfcConvert": [],
        "ifcopenshell-python": [],
    }
    m = re.findall(r"\((.*?)\)", first_comment_body)
    for e in m:
        if "ifcblender" in e:
            d["IfcBlender"].append(e)

        if "IfcConvert" in e:
            d["IfcConvert"].append(e)

        if "IfcGeomServer" in e:
            d["IfcGeomServer"].append(e)

        if "ifcopenshell-python" in e:
            d["ifcopenshell-python"].append(e)

    return d


def os_version(nbits):
    return " %sbit" % nbits


def get_os(s, nm):
    if "linux" in s:
        return " " + "Linux"
    if "os" in s:
        return " " + "OSX"
    if "win" in s:
        return " " + "Windows"


def get(product, branch):
    try:
        first_comment_body = get_commit_comment_cached(branch)
        urls = build_dict(first_comment_body)[product]
        names = []

        for i in range(len(urls)):
            final_dict = {"Linux": [], "OSX": [], "Windows": []}

            if product == "IfcGeomServer":
                idx = urls[i].index(".zip")
                nbits = urls[i][idx - 2 : idx]
                nm = os_version(nbits)
                nm += get_os(urls[i])
                names.append("IfcGeomServer" + " " + nm)

            if product == "IfcBlender":

                if branch == "v0.6.0":
                    nb = re.search(r"(blender-(.*)-v0\.6\.0)", urls[i])
                    nb = nb.group()
                if branch == "master":
                    nb = re.search(r"(blender-(.*)-master)", urls[i])
                    nb = nb.group()

                m2 = re.search(r"-([^-]*)", nb)
                m2 = m2.group()
                m2 = str(m2)
                subs = m2.split("-")[1]
                idx0 = urls[i].index("python")
                nm = urls[i][idx0 + 7 : idx0 + 9]
                nm = nm[0] + "." + nm[1]
                idx = urls[i].index(".zip")
                nbits = urls[i][idx - 2 : idx]

                if branch == "v0.6.0":
                    result = re.search("python(.*)-v0.6.0", urls[i])
                if branch == "master":
                    result = re.search("python(.*)-master", urls[i])

                other = result.group(1)
                nm = nm + " "
                nm = os_version(nbits)
                nm = nm
                nm += get_os(urls[i], nm)
                names.append(
                    "IfcBlender for python" + " " + other[1] + "." + other[2] + " " + nm
                )

            if product == "IfcConvert":
                nm = ""
                idx = urls[i].index(".zip")
                nbits = urls[i][idx - 2 : idx]
                nm = os_version(nbits)
                nm += get_os(urls[i], nm)
                names.append("IfcConvert" + " " + nm)

            if product == "ifcopenshell-python":

                if branch == "v0.6.0":
                    nb = re.search(r"(python-(.*)-v0\.6\.0)", urls[i])
                    nb = nb.group()
                if branch == "master":
                    nb = re.search(r"(python-(.*)-master)", urls[i])
                    nb = nb.group()

                m2 = re.search(r"-([^-]*)", nb)
                m2 = m2.group()
                m2 = str(m2)
                subs = m2.split("-")[1]
                nm = subs[0] + "." + subs[1]
                idx = urls[i].index(".zip")
                nbits = urls[i][idx - 2 : idx]

                if branch == "v0.6.0":
                    result = re.search("python(.*)-v0.6.0", urls[i])
                if branch == "master":
                    result = re.search("python(.*)-master", urls[i])

                other = result.group(1)
                nm = nm + " "
                nm = os_version(nbits)
                nm += get_os(urls[i], nm)

                if urls[i][67] == "u":
                    # handle the python X.Yu case.
                    names.append(
                        "IfcOpenShell-python for python"
                        + " "
                        + other[1]
                        + "."
                        + other[2]
                        + "u"
                        + nm
                    )
                else:
                    names.append(
                        "IfcOpenShell-python for python"
                        + " "
                        + other[1]
                        + "."
                        + other[2]
                        + nm
                    )

        for i in range(len(urls)):
            t = (urls[i], names[i])
            if "linux" in urls[i]:
                final_dict["Linux"].append(t)
            if "os" in urls[i]:
                final_dict["OSX"].append(t)
            if "win" in urls[i]:
                final_dict["Windows"].append(t)

        for k, v in final_dict.items():
            final_dict[k] = [t for t in (set(tuple(i) for i in v))]
            final_dict[k] = sorted(final_dict[k], key=lambda x: x[1])

        return final_dict
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"Windows": [], "OSX": [], "Linux": []}


if __name__ == "__main__":
    print("Use this module to construct the IfcOpenShell builds")
