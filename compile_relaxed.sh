#!/bin/bash

# Relaxed LaTeX compilation script for early writing phase (macOS compatible)
# Focus on content rather than strict syntax
OUTDIR=".output"

# Create output directory if it doesn't exist
mkdir -p "$OUTDIR"

# Main document
MAIN="main"

echo "Compiling LaTeX document (RELAXED MODE - focusing on content)..."

# Function to run pdflatex with relaxed settings
run_pdflatex_relaxed() {
    echo "Running pdflatex (pass $1) - RELAXED MODE..."
    
    # Run pdflatex with relaxed settings (no timeout on macOS)
    pdflatex \
        -interaction=nonstopmode \
        -output-directory="$OUTDIR" \
        "$MAIN.tex"
    
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "⚠️  pdflatex exited with code $exit_code (but continuing in relaxed mode)"
        echo "This is normal in early writing phase - check log for details"
        return 0  # Continue anyway in relaxed mode
    else
        echo "pdflatex completed successfully"
        return 0
    fi
}

# Function to run bibtex with relaxed settings
run_bibtex_relaxed() {
    echo "Running BibTeX (RELAXED MODE)..."
    
    # Ensure BibTeX can find .bib files located in the project root (parent of .output)
    # BIBINPUTS controls the search path for .bib files (kpathsea). The trailing colon
    # preserves the default search path after the custom entries.
    bash -c "cd '$OUTDIR' && BIBINPUTS=..: bibtex '$MAIN'"
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "⚠️  BibTeX exited with code $exit_code (but continuing in relaxed mode)"
        echo "Bibliography issues are common in early writing - will fix later"
        return 0  # Continue anyway in relaxed mode
    else
        echo "BibTeX completed successfully"
        return 0
    fi
}

# First pass - always continue
echo "=== PASS 1: Initial compilation ==="
run_pdflatex_relaxed 1

# Run bibtex if bibliography exists - don't stop on errors
if [ -f "library/citations.bib" ]; then
    echo "=== BIBLIOGRAPHY PROCESSING ==="
    run_bibtex_relaxed
else
    echo "No bibliography file found - skipping BibTeX"
fi

# Second pass - always continue
echo "=== PASS 2: Bibliography integration ==="
run_pdflatex_relaxed 2

# Third pass - always continue
echo "=== PASS 3: Cross-references ==="
run_pdflatex_relaxed 3

# Copy PDF to main directory if it exists (even with errors)
if [ -f "$OUTDIR/$MAIN.pdf" ]; then
    cp "$OUTDIR/$MAIN.pdf" .
    echo ""
    echo "✅ PDF generated successfully!"
    echo "📄 PDF saved as: $MAIN.pdf"
    echo "📊 File size: $(ls -lh "$MAIN.pdf" | awk '{print $5}')"
else
    echo ""
    echo "❌ PDF file not found - compilation may have failed completely"
    echo "Check the log file for critical errors: $OUTDIR/$MAIN.log"
fi

# Clean up empty files and directories
find "$OUTDIR" -type f -size 0 -delete
find "$OUTDIR" -type d -empty -delete
if [ -d "$OUTDIR/chapters" ] && [ -z "$(ls -A "$OUTDIR/chapters")" ]; then
    rmdir "$OUTDIR/chapters"
fi

echo ""
echo "=== RELAXED COMPILATION COMPLETE ==="
echo "📁 Auxiliary files in: $OUTDIR/"
echo "📋 Log file: $OUTDIR/$MAIN.log"
echo ""
echo "💡 TIPS FOR EARLY WRITING PHASE:"
echo "   - Focus on content, not perfect formatting"
echo "   - Common issues to ignore: overfull boxes, undefined references"
echo "   - Use './check_relaxed.sh' to see what can be improved later"
echo "   - Use './compile_safe.sh' when ready for strict compilation" 