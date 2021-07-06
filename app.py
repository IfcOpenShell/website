from flask import Flask, render_template, url_for

import builds

app = Flask(__name__, static_folder="static")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ifcmax")
def max():
    return render_template("ifcmax.html")


@app.route("/bimserver")
def bimserver():
    dico_master = builds.get("IfcGeomServer", "master")
    return render_template("bimserver.html", builds_master=dico_master)


@app.route("/ifcblender")
def blender():
    dico_master = builds.get("IfcBlender", "master")
    dico_v6 = builds.get("IfcBlender", "v0.6.0")
    return render_template(
        "ifcblender.html", builds_master=dico_master, builds_v06=dico_v6
    )


@app.route("/ifcconvert")
def convert():
    dico_master = builds.get("IfcConvert", "master")
    dico_v6 = builds.get("IfcConvert", "v0.6.0")
    return render_template(
        "ifcconvert.html", builds_master=dico_master, builds_v06=dico_v6
    )


@app.route("/python")
def python():
    dico_master = builds.get("ifcopenshell-python", "master")
    dico_v6 = builds.get("ifcopenshell-python", "v0.6.0")
    return render_template("python.html", builds_master=dico_master, builds_v06=dico_v6)


@app.route("/code")
def code():
    return render_template("code.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
