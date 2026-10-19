import ifcopenshell

# Open an IFC model from disk
model = ifcopenshell.open("model.ifc")

# Find every wall and rename the first one
walls = model.by_type("IfcWall")
walls[0].Name = "My wall"

model.write("updated-model.ifc")
print(f"Renamed 1 of {len(walls)} walls")
