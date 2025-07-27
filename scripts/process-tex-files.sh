#!/bin/bash

# Directory containing the original .tex files
TEX_DIR="tex"
# Directory to store processed -book.tex files
OUTPUT_DIR="tex-processed"
# Main LaTeX file
MAIN_FILE="nutr630-notes.tex"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Process each .tex file in the tex directory
for file in "$TEX_DIR"/*.tex; do
    # Get the base filename without extension
    base_name=$(basename "$file" .tex)
    # Define the output file name
    output_file="$OUTPUT_DIR/$base_name-book.tex"

    echo "Processing $file to $output_file"

    # Read the original file and modify it
    # 1. Extract content after \begin{document}
    # 2. Prepend \documentclass[../nutr630-notes.tex]{subfiles}
    # 3. Remove everything before \begin{document} (i.e., the preamble)
    awk '
    BEGIN { print "\\documentclass[../nutr630-notes.tex]{subfiles}\n" }
    /\\begin{document}/ { print; in_document=1; next }
    in_document { print }
    ' "$file" > "$output_file"
done

# Compile the main LaTeX document using latexmk
latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" "$MAIN_FILE"