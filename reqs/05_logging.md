# API Logging

Documents the optional logging of OpenAI API requests and responses via the `--log-dir` argument.

## $REQ_LOG_001: No Logging Without --log-dir
**Source:** ./specs/LOGGING.md (Section: "Command-Line / --log-dir")

If `--log-dir` is not specified, no API logging occurs.

## $REQ_LOG_002: Log Directory Creation
**Source:** ./specs/LOGGING.md (Section: "Command-Line / --log-dir")

If `--log-dir` is specified and the directory does not exist, it is created.

## $REQ_LOG_003: Log File Naming Convention
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Filename Convention")

Log files must be named `{timestamp}_{operation}_{REQUEST|RESPONSE}.md` where timestamp is `YYYY-MM-DD-HH-MM-SS-mmm` (millisecond precision, local time).

## $REQ_LOG_004: Logged Operations
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Operations")

Three operation types are logged: EMBED (embedding generation), SUMMARIZE (content summarization), and BOUNDARY (topic boundary detection).

## $REQ_LOG_005: Request and Response File Pairs
**Source:** ./specs/LOGGING.md (Section: "Log File Format")

Each API call writes two files: a request file and a response file with matching timestamps.

## $REQ_LOG_006: Request File Header Format
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Request File Content")

Request files must include a header with the operation name, timestamp, and model name.

## $REQ_LOG_007: Request File Messages Section
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Request File Content")

Request files must include a "Messages" section containing the JSON array of messages sent to the API.

## $REQ_LOG_008: Response File Header Format
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Response File Content")

Response files must include a header with the operation name, timestamp, model name, elapsed time in seconds, and token counts (prompt and completion).

## $REQ_LOG_009: Response File Content Section
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Response File Content")

Response files must include a "Content" section with the response text or embedding summary.

## $REQ_LOG_010: Response File Raw JSON Section
**Source:** ./specs/LOGGING.md (Section: "Log File Format / Response File Content")

Response files must include a "Raw JSON" section containing the full API response.

## $REQ_LOG_011: Embedding Response Logging
**Source:** ./specs/LOGGING.md (Section: "Notes")

Embedding responses log vector dimensions and first few values, not full 1536-float arrays.
