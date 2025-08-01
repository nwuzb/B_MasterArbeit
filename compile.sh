#!/bin/bash

# LaTeX compilation script
# Set output directory
OUTDIR=".output"

# Create output directory if it doesn't exist
mkdir -p "$OUTDIR"

# Main document
MAIN="main"

echo "Compiling LaTeX document..."

# First pass
pdflatex -output-directory="$OUTDIR" "$MAIN.tex"

# Run bibtex if bibliography exists
if [ -f "library/citations.bib" ]; then
    echo "Running BibTeX..."
    (cd "$OUTDIR" && bibtex "$MAIN")
fi

# Second pass
pdflatex -output-directory="$OUTDIR" "$MAIN.tex"

# Third pass (for cross-references)
pdflatex -output-directory="$OUTDIR" "$MAIN.tex"

# Copy PDF to main directory
cp "$OUTDIR/$MAIN.pdf" .

# Clean up empty files and directories
find "$OUTDIR" -type f -size 0 -delete
find "$OUTDIR" -type d -empty -delete

echo "Compilation complete! PDF saved as $MAIN.pdf"
echo "Auxiliary files are in $OUTDIR/"

# Optional: show auxiliary files
echo "Auxiliary files in $OUTDIR/:"
ls -la "$OUTDIR/" 