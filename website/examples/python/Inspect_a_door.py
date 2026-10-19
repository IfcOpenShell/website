import ifcopenshell
import ifcopenshell.util.element

model = ifcopenshell.open("model.ifc")
door = model.by_type("IfcDoor")[0]

# Pull the properties, type and storey of a door
psets = ifcopenshell.util.element.get_psets(door)
door_type = ifcopenshell.util.element.get_type(door)
storey = ifcopenshell.util.element.get_container(door, ifc_class="IfcBuildingStorey")

print(door_type.Name, "on", storey.Name)
print("Fire rating:", psets["Pset_DoorCommon"]["FireRating"])
