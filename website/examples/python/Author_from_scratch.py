import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate

# Create a blank model
model = ifcopenshell.api.project.create_file()

# All projects must have one IFC Project element
project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="My Project")

# Geometry is optional in IFC, but here we want it, so let's define units
ifcopenshell.api.unit.assign_unit(model)

# Let's create a modeling geometry context, so we can store 3D geometry
context = ifcopenshell.api.context.add_context(model, context_type="Model")
body = ifcopenshell.api.context.add_context(model, context_type="Model",
    context_identifier="Body", target_view="MODEL_VIEW", parent=context)

# Create a site, building, and storey. Many hierarchies are possible.
site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="My Site")
building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Building A")
storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Ground Floor")

# Place the building on the site, and the storey in the building
ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])
ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])

# Create a wall with a local origin at (0, 0, 0)
wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

# Add a body geometry: 5m long, 3m high, and 200mm thick
representation = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=5, height=3, thickness=0.2)
ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)

# Place our wall in the ground floor, then write to a file
ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[wall])
model.write("model.ifc")
print(f"Wrote model.ifc ({model.schema}) - {len(model.by_type('IfcWall'))} wall")
