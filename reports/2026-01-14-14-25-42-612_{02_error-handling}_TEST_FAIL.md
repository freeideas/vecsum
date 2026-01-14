# Test Report: 02_error-handling

**Status:** FAIL
**Exit Code:** 1
**Timestamp:** 2026-01-14-14-25-42-612
**Test File:** tests/failing/02_error-handling.py

## Output

```
Testing error handling...

[stderr] Traceback (most recent call last):
[stderr]   File "C:\Users\Human\Desktop\prjx\vecsum\tests\failing\02_error-handling.py", line 380, in <module>
[stderr]     test_missing_api_key()
[stderr]     ~~~~~~~~~~~~~~~~~~~~^^
[stderr]   File "C:\Users\Human\Desktop\prjx\vecsum\tests\failing\02_error-handling.py", line 72, in test_missing_api_key
[stderr]     assert "OPENAI_API_KEY environment variable is not set" in output, \
[stderr]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr] AssertionError: Expected missing API key error message, got: vecsum - Hierarchical PDF summarization using SQLite Vector
[stderr] 
[stderr] Usage:
[stderr]   vecsum.exe --db-file <path> [--pdf-dir <path>]... [--summarize <path>]
[stderr] 
[stderr] Environment:
[stderr]   OPENAI_API_KEY        OpenAI API key (required)
[stderr] 
[stderr] Arguments:
[stderr]   --db-file <path>      SQLite database file (required)
[stderr]                         Created if it doesn't exist
[stderr] 
[stderr]   --pdf-dir <path>      Directory containing PDFs to ingest
[stderr]                         Can be specified multiple times
[stderr]                         Only used when creating a new database
[stderr] 
[stderr]   --summarize <path>    Directory or PDF file to summarize
[stderr]                         Prints the summary and exits
[stderr] 
[stderr] Examples:
[stderr]   Build a new database:
[stderr]     vecsum.exe --db-file ./data.db --pdf-dir ./reports --pdf-dir ./articles
[stderr] 
[stderr]   Get a directory summary:
[stderr]     vecsum.exe --db-file ./data.db --summarize ./reports
[stderr] 
[stderr]   Get a document summary:
[stderr]     vecsum.exe --db-file ./data.db --summarize ./reports/q1.pdf
[stderr] 
[stderr] 
[stderr] Error: --pdf-dir is required when creating a new database
[stderr] 

```
