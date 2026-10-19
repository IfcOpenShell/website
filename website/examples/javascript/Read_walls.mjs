import * as ifcopenshell from "ifcopenshell";
import { readFile } from "node:fs/promises";

const runtime = await ifcopenshell.init();
await runtime.loadPlugin("schema", "ifc4");

const model = ifcopenshell.open(await readFile("model.ifc"));
const walls = model.byType("IfcWall");
console.log(`${walls.length} walls found`);
for (const wall of walls) console.log(wall.get("Name"));
model.destroy();
