# Audit a model against an IDS specification
python -m ifctester specs.ids model.ifc --no-color

# Produce a shareable HTML report
python -m ifctester specs.ids model.ifc -r Html -o report.html
