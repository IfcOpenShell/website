#include <ifcparse/file.h>
#include <ifcparse/global_id.h>
#include <ifcparse/parse.h>
#include <ifcparse/schemas/Ifc4.h>
#include <fstream>
#include <iostream>

int main() {
    ifcopenshell::file model(&Ifc4::get_schema());
    auto wall = model.create<Ifc4::IfcWall>();
    wall.setGlobalId(ifcopenshell::global_id());
    wall.setName("My wall");
    std::ofstream output("model.ifc");
    output << model;
    if (!output) return 1;
    std::cout << "Wrote model.ifc - "
              << model.instances_by_type<Ifc4::IfcWall>().size()
              << " wall in schema " << model.schema()->name() << "\n";
}
