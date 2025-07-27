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

    # Use awk to:
    # - Insert subfile documentclass at the top
    # - Strip preamble (everything before \begin{document})
    # - Remove lines with unwanted LaTeX commands
    # - Replace abstract environment with a simple italic paragraph

    awk '
    BEGIN {
        print "\\documentclass[../nutr630-notes.tex]{subfiles}\n"
        in_document = 0
    }
    /\\begin{document}/ {
        print; in_document = 1; next
    }
    {
        if (in_document) {
            # Remove unwanted lines
            if ($0 ~ /\\tableofcontents/ || $0 ~ /\\maketitle/ || $0 ~ /\\bibliography{.*}/ || $0 ~ /\\bibliographystyle{.*}/) next

            # Replace abstract environment with italic text block
            gsub(/\\begin{abstract}/, "\\\\noindent\\\\textit{")
            gsub(/\\end{abstract}/, "}")

            print
        }
    }
    ' "$file" > "$output_file"
done

# Copy figures folder
cp -r tex/figures "$OUTPUT_DIR/figures"
