import * as ifcopenshell from "ifcopenshell";
import { readFile, writeFile } from "node:fs/promises";

const runtime = await ifcopenshell.init();
await runtime.loadPlugin("schema", "ifc4");

const model = ifcopenshell.open(await readFile("model.ifc"));
const walls = model.byType("IfcWall");
walls[0].set("Name", "My wall");
await writeFile("updated-model.ifc", model.toString());
console.log(`Renamed 1 of ${walls.length} walls`);
model.destroy();
