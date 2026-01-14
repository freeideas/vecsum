# PDF Chunking

Documents how PDF text is extracted and split into overlapping chunks for processing.

## $REQ_PDFCHUNK_001: Text Extraction from PDF
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 1: Document Chunking (Level 0)")

For each PDF file, text must be extracted from the PDF.

## $REQ_PDFCHUNK_002: Chunk Size
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

PDF text must be split into chunks of 1000 characters.

## $REQ_PDFCHUNK_003: Chunk Overlap
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

Chunks must have 100 character overlap between consecutive chunks.

## $REQ_PDFCHUNK_004: Chunk Embedding
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 1: Document Chunking (Level 0)")

An embedding must be generated for each chunk.

## $REQ_PDFCHUNK_005: Chunk Node Storage
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 1: Document Chunking (Level 0)")

Each chunk must be inserted as a node with `node_type = 'chunk'` and `doc_path` set to the PDF file path.
