# Convert an IFC model to glTF for the web
IfcConvert -y model.ifc model.glb

# Or to Collada, shifting the project origin
IfcConvert -y --model-offset "10000;10000;0" model.ifc model.dae
