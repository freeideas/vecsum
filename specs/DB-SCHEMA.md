# Database Schema

## Overview

The database stores the summary tree as nodes with parent-child relationships. All paths are canonicalized (converted to absolute paths) before storage and query, so users can specify paths in any form (relative, absolute, with `..`, etc.).

## Tables

### nodes

The main table storing all tree nodes.

```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES nodes(id),
    node_type TEXT NOT NULL,          -- 'chunk', 'summary', 'doc_top', 'dir_top', 'root'
    doc_path TEXT,                    -- PDF file path (for chunk/summary/doc_top nodes)
    dir_path TEXT,                    -- directory path (for dir_top nodes)
    content TEXT NOT NULL,            -- text content (chunk text or summary text)
    embedding BLOB NOT NULL           -- 1536 float32 values (6144 bytes) from text-embedding-3-small
);
```

### Path Storage Rules

| node_type | doc_path           | dir_path           | Example                                                   |
| --------- | ------------------ | ------------------ | --------------------------------------------------------- |
| chunk     | canonical PDF path | NULL               | `c:/users/human/prjx/vecsum/testdocs/cooking/recipe1.pdf` |
| summary   | canonical PDF path | NULL               | `c:/users/human/prjx/vecsum/testdocs/cooking/recipe1.pdf` |
| doc_top   | canonical PDF path | NULL               | `c:/users/human/prjx/vecsum/testdocs/cooking/recipe1.pdf` |
| dir_top   | NULL               | canonical dir path | `c:/users/human/prjx/vecsum/testdocs/cooking`             |
| root      | NULL               | NULL               | (corpus root)                                             |

**Important:** All paths are canonicalized before storage. See [Path Canonicalization](#path-canonicalization).

### directories

Tracks which directories were ingested.

```sql
CREATE TABLE directories (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE         -- canonical directory path
);
```

### documents

Tracks which PDF files were ingested.

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    directory_id INTEGER REFERENCES directories(id),
    path TEXT NOT NULL UNIQUE,        -- canonical PDF file path
    filename TEXT NOT NULL            -- just the filename for display
);
```

## Indexes

```sql
CREATE INDEX idx_nodes_doc_path ON nodes(doc_path, node_type);
CREATE INDEX idx_nodes_dir_path ON nodes(dir_path, node_type);
CREATE INDEX idx_nodes_type ON nodes(node_type);
CREATE INDEX idx_nodes_parent ON nodes(parent_id);
```

## Query Patterns

### Get Document Summary (by PDF path)

```sql
SELECT content FROM nodes
WHERE doc_path = :pdf_path AND node_type = 'doc_top';
```

Example (path is canonicalized before query):
```sql
SELECT content FROM nodes
WHERE doc_path = 'c:/users/human/prjx/vecsum/testdocs/cooking/recipe1.pdf' AND node_type = 'doc_top';
```

### Get Directory Summary (by directory path)

```sql
SELECT content FROM nodes
WHERE dir_path = :dir_path AND node_type = 'dir_top';
```

Example (path is canonicalized before query):
```sql
SELECT content FROM nodes
WHERE dir_path = 'c:/users/human/prjx/vecsum/testdocs/cooking' AND node_type = 'dir_top';
```

### Get Corpus Summary

```sql
SELECT content FROM nodes
WHERE node_type = 'root';
```

### Check if Path Exists

To determine if a user-provided path is a document or directory (canonicalize the path first):

```sql
-- Check if it's a document
SELECT 1 FROM documents WHERE path = :canonical_path;

-- Check if it's a directory
SELECT 1 FROM directories WHERE path = :canonical_path;
```

### K-NN Search Across Raw Chunks

```sql
SELECT id, content, vec_distance(embedding, :query_vec) as distance
FROM nodes
WHERE node_type = 'chunk'
ORDER BY distance
LIMIT :k;
```

### K-NN Within Document

```sql
SELECT id, content, node_type, vec_distance(embedding, :query_vec) as distance
FROM nodes
WHERE doc_path = :pdf_path
ORDER BY distance
LIMIT :k;
```

## SQLite Vector

SQLite and the SQLite Vector extension are bundled into the executable. No external downloads or setup required.

The vector extension provides `vec_distance()` for k-NN queries. See https://www.sqlite.ai/sqlite-vector for documentation on vector operations.

## Path Canonicalization

All paths are canonicalized before storing or querying. This ensures matches regardless of how the user specifies the path.

### Canonicalization Rules

1. Resolve to absolute path (expand `.`, `..`, relative paths)
2. Convert backslashes to forward slashes
3. Remove trailing slashes from directories
4. Use consistent casing (lowercase on Windows, preserve on Linux)

### Example

User runs:
```
vecsum.exe --db-file ./db.sqlite --pdf-dir ./testdocs/cooking
vecsum.exe --db-file ./db.sqlite --pdf-dir ../vecsum/testdocs/cooking
vecsum.exe --db-file ./db.sqlite --pdf-dir C:\Users\Human\Desktop\prjx\vecsum\testdocs\cooking
```

All three store the same canonical path:
```
C:/Users/Human/Desktop/prjx/vecsum/testdocs/cooking
```

User queries:
```
vecsum.exe --db-file ./db.sqlite --summarize ./testdocs/cooking
vecsum.exe --db-file ./db.sqlite --summarize testdocs/cooking
vecsum.exe --db-file ./db.sqlite --summarize C:\Users\Human\Desktop\prjx\vecsum\testdocs\cooking
```

All three canonicalize to the same path and find the summary.

### C# Implementation

```csharp
string CanonicalizePath(string path)
{
    // Resolve to absolute, normalize separators
    string full = Path.GetFullPath(path);

    // Convert to forward slashes
    full = full.Replace('\\', '/');

    // Remove trailing slash (except root like "C:/")
    if (full.Length > 3 && full.EndsWith('/'))
        full = full.TrimEnd('/');

    // Lowercase on Windows for case-insensitive matching
    if (OperatingSystem.IsWindows())
        full = full.ToLowerInvariant();

    return full;
}
```
