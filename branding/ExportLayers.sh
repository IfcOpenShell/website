#!/bin/bash

export SRC_FILE=IfcOpenShellLogos.svg

ICONNAMES=$(inkscape -S ${SRC_FILE} 2>/dev/null | grep "Final" | grep -v "^bm_" | awk 'BEGIN{FS=","}{print $1}')

for ICONNAME in ${ICONNAMES[@]}; do
    ICONNAME=${ICONNAME//"Final"/}
    echo "Exporting plain and cleaned ${ICONNAME}Final to SVGs/${ICONNAME}_plain.svg"
    inkscape -j -l --vacuum-defs -i ${ICONNAME}Final -o SVGs/${ICONNAME}_plain.svg ${SRC_FILE} 2>/dev/null
    echo "...now scouring (optimizing) it..."
    # Scour the svg to reduce it's size
    scour --renderer-workaround --enable-comment-stripping --indent=none --no-line-breaks --enable-id-stripping --shorten-ids SVGs/${ICONNAME}_plain.svg SVGs/${ICONNAME}.svg
    # Create a compressed version - work in Linux, not sure about Win/Mac.
    #echo "...now create a compressed version..."
    #scour SVGs/${ICONNAME}.svg SVGs/${ICONNAME}.svgz
    # Cleanup
    echo "...clean up..."
    rm SVGs/${ICONNAME}_plain.svg
    #rm SVGs/${ICONNAME}.svg
    echo "...and done!"
done
