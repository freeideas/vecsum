# Test Report: 04_summary-retrieval
**Timestamp:** 2026-01-14-13-27-22-720
**Status:** FAIL
**Test File:** tests\passing\04_summary-retrieval.py

---

## Output

```
Creating test database...
Test database created: tmp\test_summary_retrieval.db

$REQ_SUMRET_002: Testing directory summary retrieval...
Directory summary failed with exit code 1
STDOUT: vecsum - Hierarchical PDF summarization using SQLite Vector

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


Error: OPENAI_API_KEY environment variable is not set

STDERR: 

```

---

**Result:** ✗ FAIL
