# Path Canonicalization

Documents how file and directory paths are normalized for consistent storage and retrieval across different path formats.

## $REQ_PATHCANON_001: Resolve Relative Paths to Absolute
**Source:** ./specs/DB-SCHEMA.md (Section: "Canonicalization Rules")

Paths must be resolved to absolute paths, expanding `.`, `..`, and relative path components.

## $REQ_PATHCANON_002: Convert Backslashes to Forward Slashes
**Source:** ./specs/DB-SCHEMA.md (Section: "Canonicalization Rules")

All backslashes in paths must be converted to forward slashes.

## $REQ_PATHCANON_003: Remove Trailing Slashes from Directories
**Source:** ./specs/DB-SCHEMA.md (Section: "Canonicalization Rules")

Trailing slashes must be removed from directory paths.

## $REQ_PATHCANON_004: Lowercase Paths on Windows
**Source:** ./specs/DB-SCHEMA.md (Section: "Canonicalization Rules")

On Windows, paths must be converted to lowercase for case-insensitive matching. On Linux, case must be preserved.

## $REQ_PATHCANON_005: Ingestion Path Matching
**Source:** ./specs/DB-SCHEMA.md (Section: "Path Canonicalization")

Paths specified in different formats during ingestion (relative, absolute, with `..`, with backslashes) that resolve to the same location must store the same canonical path in the database.

## $REQ_PATHCANON_006: Query Path Matching
**Source:** ./specs/DB-SCHEMA.md (Section: "Path Canonicalization")

When querying with `--summarize`, paths specified in different formats (relative, absolute, with backslashes) must be canonicalized and match the stored canonical path to find the summary.
