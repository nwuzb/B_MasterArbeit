#!/bin/bash

# Safe LaTeX compilation script with error handling (macOS compatible)
# Set output directory
OUTDIR=".output"

# Create output directory if it doesn't exist
mkdir -p "$OUTDIR"

# Main document
MAIN="main"

echo "Compiling LaTeX document (SAFE MODE - macOS compatible)..."

# Function to run pdflatex with non-interactive mode
run_pdflatex_safe() {
    echo "Running pdflatex (pass $1)..."
    
    # Run pdflatex with non-interactive mode (no timeout on macOS)
    pdflatex -interaction=nonstopmode -output-directory="$OUTDIR" "$MAIN.tex"
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: pdflatex exited with code $exit_code"
        echo "Check the log file for errors: $OUTDIR/$MAIN.log"
        return $exit_code
    else
        echo "pdflatex completed successfully"
        return 0
    fi
}

# Function to run bibtex with non-interactive mode
run_bibtex_safe() {
    echo "Running BibTeX..."
    
    bash -c "cd '$OUTDIR' && bibtex '$MAIN'"
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: BibTeX exited with code $exit_code"
        return $exit_code
    else
        echo "BibTeX completed successfully"
        return 0
    fi
}

# First pass
if ! run_pdflatex_safe 1; then
    echo "First pass failed. Stopping compilation."
    exit 1
fi

# Run bibtex if bibliography exists
if [ -f "library/citations.bib" ]; then
    if ! run_bibtex_safe; then
        echo "BibTeX failed, but continuing with compilation..."
    fi
fi

# Second pass
if ! run_pdflatex_safe 2; then
    echo "Second pass failed. Stopping compilation."
    exit 1
fi

# Third pass (for cross-references)
if ! run_pdflatex_safe 3; then
    echo "Third pass failed. Stopping compilation."
    exit 1
fi

# Copy PDF to main directory if it exists
if [ -f "$OUTDIR/$MAIN.pdf" ]; then
    cp "$OUTDIR/$MAIN.pdf" .
    echo "PDF copied to main directory"
    echo "Compilation successful! PDF saved as $MAIN.pdf"
else
    echo "ERROR: PDF file not found. Compilation failed."
    echo "Check the log file for errors: $OUTDIR/$MAIN.log"
    exit 1
fi

# Clean up empty files and directories
find "$OUTDIR" -type f -size 0 -delete
find "$OUTDIR" -type d -empty -delete
# Force remove chapters directory if it exists and is empty
if [ -d "$OUTDIR/chapters" ] && [ -z "$(ls -A "$OUTDIR/chapters")" ]; then
    rmdir "$OUTDIR/chapters"
fi

echo "Auxiliary files are in $OUTDIR/"
echo "Auxiliary files in $OUTDIR/:"
ls -la "$OUTDIR/" 