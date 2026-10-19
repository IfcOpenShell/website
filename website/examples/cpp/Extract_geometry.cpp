#include <ifcgeom/converter.h>
#include <ifcgeom/element.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <memory>

int main() {
    ifcopenshell::file model("model.ifc");
    if (!model.good()) return 1;
    // begin-example
    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&model, "opencascade", settings),
        &model, settings);

    for (auto wall : model.instances_by_type<Ifc4::IfcWall>()) {
        std::unique_ptr<ifcopenshell::geom::native_element> brep(
            converter.create_brep_for_representation_and_product(
                converter.mapping()->representation_of(wall), wall));
        if (!brep) return 1;
        ifcopenshell::geom::triangulation_element mesh(*brep);
        std::cout << wall.Name().value_or("<unnamed>") << ": "
                  << mesh.geometry().verts().size() / 3 << " vertices\n";
    }
    // end-example
}
