import * as ifcopenshell from "ifcopenshell";
import { writeFile } from "node:fs/promises";

const runtime = await ifcopenshell.init();
await runtime.loadPlugin("schema", "ifc4");

const model = new ifcopenshell.File("IFC4");
model.create("IfcWall", {
    GlobalId: "0EI0MSHbX9gg8Fxwar7lL8",
    Name: "My wall",
});
await writeFile("model.ifc", model.toString());
console.log(`Wrote model.ifc - ${model.byType("IfcWall").length} wall in schema ${model.schema()}`);
model.destroy();
