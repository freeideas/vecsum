# Summary Retrieval

Documents querying summaries from the database for documents, directories, and the corpus root.

## $REQ_SUMRET_001: Retrieve Corpus Summary (No Path)
**Source:** ./specs/COMMAND-LINE.md (Section: "--summarize")

When `--summarize` is provided without a path argument, the program prints the corpus summary (root node).

## $REQ_SUMRET_002: Retrieve Document Summary by PDF Path
**Source:** ./specs/COMMAND-LINE.md (Section: "--summarize")

When `--summarize` is provided with a PDF file path, the program prints the document summary (doc_top node) for that PDF.

## $REQ_SUMRET_003: Retrieve Directory Summary by Directory Path
**Source:** ./specs/COMMAND-LINE.md (Section: "--summarize")

When `--summarize` is provided with a directory path, the program prints the directory summary (dir_top node) for that directory.

## $REQ_SUMRET_004: Summary Output Format
**Source:** ./specs/COMMAND-LINE.md (Section: "Summary Output")

When `--summarize` is provided, output includes: "Summary for: <path>", "Lookup time: <N ms>", and the summary text.

## $REQ_SUMRET_005: Path Canonicalization for Queries
**Source:** ./specs/DB-SCHEMA.md (Section: "Path Canonicalization")

User-provided paths are canonicalized before querying, so the same summary is found regardless of path format (relative, absolute, with `..`, backslashes, different casing on Windows).

## $REQ_SUMRET_006: Path Not Found Error
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--summarize` is provided with a path not in the database, the program prints: "Path not found in database: <path>".

## $REQ_SUMRET_007: Corpus Summary Label
**Source:** ./specs/COMMAND-LINE.md (Section: "Summary Output")

When `--summarize` is provided without a path argument, the output label shows `[corpus]` instead of a path.
