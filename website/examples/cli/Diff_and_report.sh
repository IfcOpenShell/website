# See what changed between two revisions
python -m ifcdiff model.ifc new.ifc -o diff.json

# Export a door schedule to a spreadsheet
python -m ifccsv -i model.ifc -s doors.csv --export -q "IfcDoor" -a Name
cat doors.csv

# Run clash detection between two sets
python -m ifcclash -o results.json clashsets.json
