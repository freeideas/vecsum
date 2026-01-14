# Strategy Overview

## What This Project Does

vecsum builds a hierarchical summary tree from PDF documents. Each document, directory, and the entire corpus gets a summary that can be retrieved instantly via database lookup.

## Key Concepts

### Summary Tree

An unbalanced tree built bottom-up:
- **Chunks**: Raw text extracted from PDFs
- **Summaries**: Groups of chunks or summaries combined
- **doc_top**: The single summary representing an entire document
- **dir_top**: The single summary representing an entire directory
- **root**: The single summary representing the entire corpus

### Adaptive Topic Boundaries

Instead of fixed-size grouping, the system detects natural topic shifts. Two chunks start a summary, then additional chunks are added until the LLM detects a topic change. This produces summaries that align with the document's actual structure.

## Implementation

- **Language**: C# on .NET 10
- **Output**: Single standalone executable `./released/vecsum.exe`
  - No .NET runtime required
  - No DLLs or external files
  - SQLite and SQLite Vector bundled inside
  - Publish as single-file, self-contained, trimmed
- **PDF extraction**: iText7 (bundled)
- **LLM**: HTTP API calls for summarization and embeddings

## Detailed Specs

- [COMMAND-LINE.md](COMMAND-LINE.md) -- CLI arguments and usage
- [DB-SCHEMA.md](DB-SCHEMA.md) -- Database tables, indexes, and queries
- [HOW-TO-BUILD-TREE.md](HOW-TO-BUILD-TREE.md) -- Tree building algorithm
- [LOGGING.md](LOGGING.md) -- Optional API request/response logging
