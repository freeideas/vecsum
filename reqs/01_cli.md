# Command-Line Interface

Documents the command-line arguments, their behavior, and usage patterns for the vecsum.exe executable.

## $REQ_CLI_002: Database File Creation
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --db-file")

If the file specified by `--db-file` does not exist, the program creates it and builds the summary tree from all `--pdf-dir` directories.

## $REQ_CLI_003: Existing Database Usage
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --db-file")

If the file specified by `--db-file` exists, the program opens and uses it as-is without rebuilding.

## $REQ_CLI_004: Multiple --pdf-dir Arguments
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --pdf-dir")

The `--pdf-dir` argument can be specified zero or more times to specify directories containing PDF files.

## $REQ_CLI_005: --pdf-dir Ignored for Existing Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --pdf-dir")

When `--db-file` already exists, any `--pdf-dir` arguments are ignored.

## $REQ_CLI_007: Subdirectories as Tree Branches
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --pdf-dir")

Each subdirectory containing PDFs becomes a branch in the summary tree.

## $REQ_CLI_008: --summarize Directory Path
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --summarize")

When `--summarize` specifies a directory path, the program prints the directory summary (dir_top node).

## $REQ_CLI_009: --summarize PDF File Path
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --summarize")

When `--summarize` specifies a PDF file path, the program prints the document summary (doc_top node).

## $REQ_CLI_011: Build Time Printed After Database Creation
**Source:** ./specs/COMMAND-LINE.md (Section: "Output / Timing")

After database creation, the program prints the build time.

## $REQ_CLI_012: Lookup Time Printed After Summary Retrieval
**Source:** ./specs/COMMAND-LINE.md (Section: "Output / Timing")

After `--summarize` retrieval, the program prints the lookup time.

## $REQ_CLI_013: Summary Output Format
**Source:** ./specs/COMMAND-LINE.md (Section: "Output / Summary Output")

When `--summarize` is provided, output includes "Summary for: <path>" (or "Summary for: [corpus]" when no path is given), optionally "Build time: <N ms>" if the database was just created, "Lookup time: <N ms>", and the summary text.

## $REQ_CLI_014: Progress Indicator During Build
**Source:** ./specs/COMMAND-LINE.md (Section: "Examples / Build a new database")

During database build, the program prints a dot per database row written as a progress indicator.

## $REQ_CLI_015: Build and Query in One Command
**Source:** ./specs/COMMAND-LINE.md (Section: "Examples / Build and query in one command")

The program supports building a new database and querying it in a single command by specifying both `--pdf-dir` and `--summarize` arguments together.

## $REQ_CLI_016: Error Output Format
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

On any error, the program prints help text followed by the specific error message, then exits.

## $REQ_CLI_017: Error for Missing OPENAI_API_KEY
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `OPENAI_API_KEY` environment variable is not set, the program prints error "OPENAI_API_KEY environment variable is not set".

## $REQ_CLI_018: Error for Invalid OPENAI_API_KEY
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `OPENAI_API_KEY` is invalid (API returns 401), the program prints error "OPENAI_API_KEY is invalid or expired".

## $REQ_CLI_019: Error for Missing --db-file
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `--db-file` is not provided, the program prints error "--db-file is required".

## $REQ_CLI_020: Error for --summarize Path Not in Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `--summarize` path is not found in the database, the program prints error "Path not found in database: <path>".

## $REQ_CLI_021: Error for Non-Existent --pdf-dir
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If a `--pdf-dir` directory does not exist, the program prints error "Directory does not exist: <path>".

## $REQ_CLI_022: Error for Empty --pdf-dir
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If a `--pdf-dir` directory contains no PDF files, the program prints error "No PDF files found in: <path>".

## $REQ_CLI_023: Error for Unknown Argument
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If an unknown argument is provided, the program prints error "Unknown argument: <arg>".

## $REQ_CLI_024: Error for OpenAI API Failures
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If an OpenAI API error occurs during processing, the program prints error "OpenAI API error: <message>".

## $REQ_CLI_025: Path Canonicalization on Input
**Source:** ./specs/DB-SCHEMA.md (Section: "Path Canonicalization")

All paths provided to the CLI (via `--pdf-dir` and `--summarize`) are canonicalized before use, allowing users to specify paths in any form (relative, absolute, with `..`, etc.) and still match stored paths.

## $REQ_CLI_026: Standalone Executable
**Source:** ./README.md (Section: "Output")

`./released/vecsum.exe` is a single standalone executable with no external dependencies -- no .NET runtime, no DLLs, no separate SQLite extension files.

## $REQ_CLI_027: --summarize Without Path Returns Corpus Summary
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --summarize")

When `--summarize` is provided without a path argument, the program prints the corpus summary (root node).

## $REQ_CLI_028: Error for Missing --pdf-dir When Creating Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `--db-file` does not exist and no `--pdf-dir` is provided, the program prints error "--pdf-dir is required when creating a new database".

## $REQ_CLI_029: Error for Missing --summarize With Existing Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If `--db-file` exists and `--summarize` is not provided, the program prints error "--summarize is required when using existing database".

## $REQ_CLI_030: Recursive PDF Ingestion
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --pdf-dir")

All PDFs in a `--pdf-dir` directory and its subdirectories are ingested recursively.

## $REQ_CLI_031: --log-dir Enables Logging
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --log-dir")

When `--log-dir` is specified, API request/response logging occurs to the specified directory.

## $REQ_CLI_032: --log-dir Directory Creation
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --log-dir")

If the directory specified by `--log-dir` does not exist, the program creates it.

## $REQ_CLI_033: No Logging Without --log-dir
**Source:** ./specs/COMMAND-LINE.md (Section: "Arguments / --log-dir")

If `--log-dir` is not specified, no API logging occurs.
