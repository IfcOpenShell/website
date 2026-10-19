#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main() {
    ifcopenshell::file model("model.ifc");
    if (!model.good()) return 1;
    auto walls = model.instances_by_type<Ifc4::IfcWall>();
    std::cout << walls.size() << " walls found\n";
    for (auto wall : walls)
        std::cout << wall.Name().value_or("<unnamed>") << "\n";
}
