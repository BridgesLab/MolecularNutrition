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
    # - Insert subfile documentclass and document environment
    # - Strip preamble (everything before \begin{document})
    # - Remove unwanted LaTeX commands
    # - Replace abstract environment with a tufte-friendly italic paragraph
    # - Update \includegraphics paths to tex-processed/figures/
    awk '
    BEGIN {
        print "\\documentclass[../nutr630-notes.tex]{subfiles}\n"
        print "\\begin{document}\n"
        in_document = 0
    }
    /\\begin{document}/ {
        in_document = 1; next
    }
    {
        if (in_document) {
            # Remove unwanted lines
            if ($0 ~ /\\tableofcontents/ || $0 ~ /\\maketitle/ || $0 ~ /\\bibliography{.*}/ || $0 ~ /\\bibliographystyle{.*}/) next

            # Replace abstract environment with italic text block, avoiding line break errors
            if (/\\begin{abstract}/) {
                print "\\noindent\\textit{"
                next
            }
            if (/\\end{abstract}/) {
                print "}"
                next
            }

            # Update \includegraphics paths to match the correct directory
            if ($0 ~ /\\includegraphics/) {
                gsub(/\\includegraphics{figures/, "\\includegraphics{tex-processed/figures")
            }

            # Preserve other content
            print
        }
    }
    END {
        print "\\end{document}\n"
    }
    ' "$file" > "$output_file"
done

# Copy contents of figures folder into tex-processed/figures without nesting
rm -rf "$OUTPUT_DIR/figures"
mkdir -p "$OUTPUT_DIR/figures"
cp -r "$TEX_DIR/figures/"* "$OUTPUT_DIR/figures/"