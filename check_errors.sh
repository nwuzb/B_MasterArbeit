#!/bin/bash

# Script to check LaTeX compilation errors
OUTDIR=".output"
MAIN="main"

echo "Checking for LaTeX compilation errors..."

if [ -f "$OUTDIR/$MAIN.log" ]; then
    echo "=== LaTeX Log File Analysis ==="
    echo "File: $OUTDIR/$MAIN.log"
    echo ""
    
    # Check for errors
    if grep -q "! " "$OUTDIR/$MAIN.log"; then
        echo "❌ ERRORS FOUND:"
        grep "! " "$OUTDIR/$MAIN.log" | head -10
        echo ""
    else
        echo "✅ No errors found in log file"
    fi
    
    # Check for warnings
    if grep -q "Warning:" "$OUTDIR/$MAIN.log"; then
        echo "⚠️  WARNINGS FOUND:"
        grep "Warning:" "$OUTDIR/$MAIN.log" | head -10
        echo ""
    else
        echo "✅ No warnings found in log file"
    fi
    
    # Check for overfull/underfull boxes
    if grep -q "Overfull\|Underfull" "$OUTDIR/$MAIN.log"; then
        echo "📏 LAYOUT ISSUES:"
        grep "Overfull\|Underfull" "$OUTDIR/$MAIN.log" | head -5
        echo ""
    fi
    
    # Show last few lines of log
    echo "=== Last 10 lines of log file ==="
    tail -10 "$OUTDIR/$MAIN.log"
    
else
    echo "❌ Log file not found: $OUTDIR/$MAIN.log"
    echo "Run compilation first to generate log file."
fi

# Check if PDF exists
if [ -f "$OUTDIR/$MAIN.pdf" ]; then
    echo ""
    echo "✅ PDF file exists: $OUTDIR/$MAIN.pdf"
    ls -lh "$OUTDIR/$MAIN.pdf"
else
    echo ""
    echo "❌ PDF file not found: $OUTDIR/$MAIN.pdf"
fi 