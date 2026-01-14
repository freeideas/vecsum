# vecsum

Fast hierarchical summarization of PDF documents using vector tree

## Overview

Builds an unbalanced summary tree from PDF documents. Documents are chunked and embedded, then recursively summarized upward until a single vector represents each document. Directory-level summaries group related documents. Finding any summary is a single database lookup.

## Demonstration

Example PDFs are in `./extart/example-pdfs/`:

```
extart/example-pdfs/
  cooking/        <- PDFs about cooking/recipes
  programming/    <- PDFs about programming/tutorials
```

Build the database:
```
./released/vecsum.exe --db-file ./vecsum.db --pdf-dir ./extart/example-pdfs/cooking --pdf-dir ./extart/example-pdfs/programming
```

Query a summary:
```
./released/vecsum.exe --db-file ./vecsum.db --summarize
./released/vecsum.exe --db-file ./vecsum.db --summarize ./extart/example-pdfs/cooking
./released/vecsum.exe --db-file ./vecsum.db --summarize ./extart/example-pdfs/cooking/recipe1.pdf
```

See [specs/COMMAND-LINE.md](specs/COMMAND-LINE.md) for full CLI documentation.

## Output

`./released/vecsum.exe` is a single standalone executable with no external dependencies. No .NET runtime, no DLLs, no separate SQLite extension files -- everything is bundled into one file.

## How It Works

1. PDF documents are chunked by character count and embedded into vectors
2. Chunks are grouped by topic boundaries (detected by LLM) and summarized
3. Summaries are recursively grouped and summarized until one remains per document
4. Document summaries are grouped by directory and summarized upward
5. Querying any node's top retrieves its instant summary

See [specs/STRATEGY.md](specs/STRATEGY.md) for implementation details.
