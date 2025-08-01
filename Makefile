# Makefile for LaTeX compilation
# Set output directory
OUTDIR = .output

# Main document
MAIN = main

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Create output directory if it doesn't exist
$(OUTDIR):
	mkdir -p $(OUTDIR)

# Compile LaTeX document
$(MAIN).pdf: $(MAIN).tex $(OUTDIR)
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN)
	$(BIBTEX) $(OUTDIR)/$(MAIN)
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN)
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN)
	cp $(OUTDIR)/$(MAIN).pdf .
	find $(OUTDIR) -type f -size 0 -delete

# Clean auxiliary files
clean:
	rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.synctex.gz *.toc
	rm -rf $(OUTDIR)

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf

# Show help
help:
	@echo "Available targets:"
	@echo "  all      - Compile the document (default)"
	@echo "  clean    - Remove auxiliary files"
	@echo "  cleanall - Remove auxiliary files and PDF"
	@echo "  help     - Show this help message"

.PHONY: clean cleanall help 