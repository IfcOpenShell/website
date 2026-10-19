"""Generate the small shared IFC4 model used by all website examples."""
from pathlib import Path

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import numpy as np


def create_fixture(directory: Path):
    model = ifcopenshell.api.project.create_file()
    def entity(cls, name):
        return ifcopenshell.api.root.create_entity(model, ifc_class=cls, name=name)

    project = entity("IfcProject", "Website examples")
    ifcopenshell.api.unit.assign_unit(model)
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(model, context_type="Model",
        context_identifier="Body", target_view="MODEL_VIEW", parent=context)
    site = entity("IfcSite", "My Site")
    building = entity("IfcBuilding", "Building A")
    storey = entity("IfcBuildingStorey", "Level 1")
    for parent, child in [(project, site), (site, building), (building, storey)]:
        ifcopenshell.api.aggregate.assign_object(model, relating_object=parent, products=[child])
    for i, name in enumerate(["Exterior - Brick", "Interior - Partition", "Core - Concrete"]):
        wall = entity("IfcWall", name)
        matrix = np.eye(4)
        matrix[1, 3] = i * 2
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall, matrix=matrix)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            model, context=body, length=5, height=3, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[wall])
    door = entity("IfcDoor", "Door - 01")
    door_type = entity("IfcDoorType", "DBL-1200x2100")
    ifcopenshell.api.type.assign_type(model, related_objects=[door], relating_type=door_type)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[door])
    pset = ifcopenshell.api.pset.add_pset(model, product=door, name="Pset_DoorCommon")
    ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"FireRating": "60min"})
    # Stable identifiers and header keep regeneration reviewable.
    for i, root in enumerate(model.by_type("IfcRoot"), 1):
        root.GlobalId = ifcopenshell.guid.compress(f"{i:032x}")
    model.header.file_name.time_stamp = "2026-01-01T00:00:00"
    model.write(str(directory / "model.ifc"))
    model.by_type("IfcWall")[0].Name = "My wall"
    model.write(str(directory / "new.ifc"))


if __name__ == "__main__":
    create_fixture(Path(__file__).parent / "fixtures")
