# Test Report: 02_error-handling
**Timestamp:** 2026-01-14-14-22-57-850
**Status:** FAIL
**Test File:** tests\passing\02_error-handling.py

---

## Output

```
Testing error handling...

Traceback (most recent call last):
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_error-handling.py", line 380, in <module>
    test_missing_api_key()
    ~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_error-handling.py", line 72, in test_missing_api_key
    assert "OPENAI_API_KEY environment variable is not set" in output, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected missing API key error message, got: vecsum - Hierarchical PDF summarization using SQLite Vector

Usage:
  vecsum.exe --db-file <path> [--pdf-dir <path>]... [--summarize <path>]

Environment:
  OPENAI_API_KEY        OpenAI API key (required)

Arguments:
  --db-file <path>      SQLite database file (required)
                        Created if it doesn't exist

  --pdf-dir <path>      Directory containing PDFs to ingest
                        Can be specified multiple times
                        Only used when creating a new database

  --summarize <path>    Directory or PDF file to summarize
                        Prints the summary and exits

Examples:
  Build a new database:
    vecsum.exe --db-file ./data.db --pdf-dir ./reports --pdf-dir ./articles

  Get a directory summary:
    vecsum.exe --db-file ./data.db --summarize ./reports

  Get a document summary:
    vecsum.exe --db-file ./data.db --summarize ./reports/q1.pdf


Error: --pdf-dir is required when creating a new database


```

---

**Result:** ✗ FAIL
