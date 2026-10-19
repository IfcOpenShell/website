#include <ifcparse/file.h>
#include <ifcparse/parse.h>
#include <ifcparse/schemas/Ifc4.h>
#include <fstream>
#include <iostream>

int main() {
    ifcopenshell::file model("model.ifc");
    if (!model.good()) return 1;
    auto walls = model.instances_by_type<Ifc4::IfcWall>();
    if (walls.empty()) return 1;
    walls.front().setName("My wall");
    std::ofstream output("updated-model.ifc");
    output << model;
    if (!output) return 1;
    std::cout << "Renamed 1 of " << walls.size() << " walls\n";
}
