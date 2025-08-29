#!/bin/bash

# Relaxed error checking for early writing phase
OUTDIR=".output"
MAIN="main"

echo "🔍 Checking LaTeX compilation (RELAXED MODE - early writing phase)..."

if [ -f "$OUTDIR/$MAIN.log" ]; then
    echo "=== RELAXED LOG ANALYSIS ==="
    echo "File: $OUTDIR/$MAIN.log"
    echo ""
    
    # Check for CRITICAL errors only (ignore common early writing issues)
    if grep -q "! " "$OUTDIR/$MAIN.log"; then
        echo "❌ CRITICAL ERRORS (must fix):"
        grep "! " "$OUTDIR/$MAIN.log" | head -5
        echo ""
    else
        echo "✅ No critical errors found"
    fi
    
    # Check for undefined references (common in early writing)
    if grep -q "LaTeX Warning: Reference.*undefined" "$OUTDIR/$MAIN.log"; then
        echo "📝 UNDEFINED REFERENCES (normal in early writing):"
        grep "LaTeX Warning: Reference.*undefined" "$OUTDIR/$MAIN.log" | head -3
        echo "   → These will resolve as you add more content"
        echo ""
    fi
    
    # Check for undefined citations (common in early writing)
    if grep -q "LaTeX Warning: Citation.*undefined" "$OUTDIR/$MAIN.log"; then
        echo "📚 UNDEFINED CITATIONS (normal in early writing):"
        grep "LaTeX Warning: Citation.*undefined" "$OUTDIR/$MAIN.log" | head -3
        echo "   → These will resolve as you add bibliography entries"
        echo ""
    fi
    
    # Check for overfull/underfull boxes (ignore in early writing)
    if grep -q "Overfull\|Underfull" "$OUTDIR/$MAIN.log"; then
        echo "📏 LAYOUT ISSUES (ignore for now):"
        grep "Overfull\|Underfull" "$OUTDIR/$MAIN.log" | head -3
        echo "   → Focus on content first, fix layout later"
        echo ""
    fi
    
    # Check for warnings (show but don't worry too much)
    if grep -q "Warning:" "$OUTDIR/$MAIN.log"; then
        echo "⚠️  WARNINGS (review when convenient):"
        grep "Warning:" "$OUTDIR/$MAIN.log" | head -3
        echo ""
    fi
    
    # Show compilation status
    if grep -q "Output written on" "$OUTDIR/$MAIN.log"; then
        echo "✅ COMPILATION SUCCESSFUL"
        echo "   → PDF was generated despite warnings"
    else
        echo "❌ COMPILATION FAILED"
        echo "   → Check critical errors above"
    fi
    
else
    echo "❌ Log file not found: $OUTDIR/$MAIN.log"
    echo "Run compilation first to generate log file."
fi

# Check if PDF exists and show info
if [ -f "$OUTDIR/$MAIN.pdf" ]; then
    echo ""
    echo "📄 PDF STATUS:"
    echo "   File: $OUTDIR/$MAIN.pdf"
    echo "   Size: $(ls -lh "$OUTDIR/$MAIN.pdf" | awk '{print $5}')"
    echo "   Modified: $(ls -lh "$OUTDIR/$MAIN.pdf" | awk '{print $6, $7, $8}')"
else
    echo ""
    echo "❌ PDF file not found: $OUTDIR/$MAIN.pdf"
fi

echo ""
echo "💡 EARLY WRITING PHASE GUIDELINES:"
echo "   ✅ Focus on: Content, structure, ideas"
echo "   ⏳ Ignore for now: Perfect formatting, layout issues"
echo "   🔧 Fix later: Undefined references, citations, warnings"
echo "   🚨 Fix now: Critical errors that prevent compilation" 