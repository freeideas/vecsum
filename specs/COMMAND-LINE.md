# Command-Line Interface

## Usage

```
vecsum.exe --db-file <path> [--pdf-dir <path>]... [--summarize [<path>]] [--log-dir <path>]
```

## Arguments

### --db-file (required)

Path to the SQLite database file.

- If the file does not exist, it will be created and the summary tree will be built from all `--pdf-dir` directories
- At least one `--pdf-dir` is required when creating a new database
- If the file exists, it will be opened and used as-is (no rebuild)

```
vecsum.exe --db-file ./vecsum.db
```

### --pdf-dir (zero or more)

Path to a directory containing PDF files to process.

- Can be specified multiple times
- Only used when `--db-file` does not exist (during initial build)
- All PDFs in the directory and subdirectories (recursive) will be ingested
- Each subdirectory containing PDFs becomes a branch in the summary tree

```
vecsum.exe --db-file ./vecsum.db --pdf-dir ./cooking --pdf-dir ./programming
```

### --summarize (optional)

Request a summary. Path argument is optional.

- If no path given: prints the corpus summary (root node)
- If a directory path: prints the directory summary (dir_top node)
- If a PDF file path: prints the document summary (doc_top node)
- Path must match a path that was ingested into the database

```
vecsum.exe --db-file ./vecsum.db --summarize
vecsum.exe --db-file ./vecsum.db --summarize ./cooking
vecsum.exe --db-file ./vecsum.db --summarize ./cooking/recipe1.pdf
```

### --log-dir (optional)

Path to a directory for API request/response logs.

- If not specified, no logging occurs
- Directory is created if it does not exist
- See [LOGGING.md](LOGGING.md) for log file format details

```
vecsum.exe --db-file ./vecsum.db --pdf-dir ./docs --log-dir ./logs
```

## Output

### Timing

The program prints timing information for operations performed:

- **Build time**: Printed after database creation (if `--db-file` was created)
- **Summary lookup time**: Printed after `--summarize` retrieval

### Summary Output

When `--summarize` is provided, output format:

```
Summary for: <path or [corpus]>
Build time: <N ms> (only if database was just created)
Lookup time: <N ms>

<summary text>
```

The label shows `[corpus]` when no path is given, otherwise the provided path.

## Examples

### Build a new database

```
vecsum.exe --db-file ./mydata.db --pdf-dir ./reports --pdf-dir ./articles
```

Output (dot per database row written):
```
..........................................
Build time: 12345 ms
```

### Query an existing database

```
vecsum.exe --db-file ./mydata.db --summarize ./reports
```

Output:
```
Summary for: ./reports
Lookup time: 2 ms

This directory contains quarterly financial reports covering Q1-Q4 2025...
```

### Query corpus summary

```
vecsum.exe --db-file ./mydata.db --summarize
```

Output:
```
Summary for: [corpus]
Lookup time: 1 ms

This corpus contains financial reports and technical articles covering...
```

### Build and query in one command

```
vecsum.exe --db-file ./new.db --pdf-dir ./docs --summarize ./docs
```

Output:
```
....................
Build time: 8000 ms

Summary for: ./docs
Lookup time: 1 ms

This directory contains technical documentation for...
```

## Error Handling

Any error prints help text (see [HELP-TEXT.txt](HELP-TEXT.txt)) followed by the specific error message, then exits.

Example output:
```
vecsum - Hierarchical PDF summarization using SQLite Vector
...
[help text]
...

Error: OPENAI_API_KEY environment variable is not set
```

| Condition                                   | Error message                                      |
| ------------------------------------------- | -------------------------------------------------- |
| `OPENAI_API_KEY` not set                    | OPENAI_API_KEY environment variable is not set     |
| `OPENAI_API_KEY` invalid (API returns 401)  | OPENAI_API_KEY is invalid or expired               |
| `--db-file` missing                         | --db-file is required                              |
| `--db-file` not found and no `--pdf-dir`    | --pdf-dir is required when creating a new database |
| `--db-file` exists and no `--summarize`     | --summarize is required when using existing database |
| `--db-file` exists but `--pdf-dir` provided | (no error, ignore `--pdf-dir`, use existing db)    |
| `--summarize` path not in database          | Path not found in database: <path>                 |
| `--pdf-dir` directory does not exist        | Directory does not exist: <path>                   |
| `--pdf-dir` contains no PDFs (recursive)    | No PDF files found in: <path>                      |
| Unknown argument                            | Unknown argument: <arg>                            |
| OpenAI API error during processing          | OpenAI API error: <message>                        |
