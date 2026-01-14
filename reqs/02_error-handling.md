# Error Handling

Documents the specific error conditions and their corresponding error messages as defined in the CLI specification.

## $REQ_ERR_001: Error Output Format
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

Any error must print help text followed by the specific error message, then exit.

## $REQ_ERR_002: Missing API Key
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `OPENAI_API_KEY` environment variable is not set, the error message must be: "OPENAI_API_KEY environment variable is not set"

## $REQ_ERR_003: Invalid API Key
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `OPENAI_API_KEY` is invalid (API returns 401), the error message must be: "OPENAI_API_KEY is invalid or expired"

## $REQ_ERR_004: Missing Required Argument
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--db-file` argument is not provided, the error message must be: "--db-file is required"

## $REQ_ERR_005: Missing PDF Dir for New Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--db-file` does not exist and no `--pdf-dir` is provided, the error message must be: "--pdf-dir is required when creating a new database"

## $REQ_ERR_006: Missing Summarize for Existing Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--db-file` exists and no `--summarize` is provided, the error message must be: "--summarize is required when using existing database"

## $REQ_ERR_007: Summarize Path Not Found
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--summarize` path is not in the database, the error message must be: "Path not found in database: <path>"

## $REQ_ERR_008: Directory Does Not Exist
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--pdf-dir` specifies a directory that does not exist, the error message must be: "Directory does not exist: <path>"

## $REQ_ERR_009: No PDFs in Directory
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When `--pdf-dir` specifies a directory that contains no PDF files, the error message must be: "No PDF files found in: <path>"

## $REQ_ERR_010: Unknown Argument
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When an unknown argument is provided, the error message must be: "Unknown argument: <arg>"

## $REQ_ERR_011: OpenAI API Error
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

When an OpenAI API error occurs during processing, the error message must be: "OpenAI API error: <message>"
