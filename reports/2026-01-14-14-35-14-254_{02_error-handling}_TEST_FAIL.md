# Test Report: 02_error-handling
**Timestamp:** 2026-01-14-14-35-14-254
**Status:** FAIL
**Test File:** tests\passing\02_error-handling.py

---

## Output

```
Testing error handling...

✓ Test missing API key passed
✓ Test missing --db-file passed
✓ Test missing --pdf-dir for new database passed
✓ Test missing --summarize for existing database passed
Traceback (most recent call last):
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_error-handling.py", line 384, in <module>
    test_directory_does_not_exist()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_error-handling.py", line 190, in test_directory_does_not_exist
    assert str(nonexistent_dir) in output, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected path 'C:\Users\Human\Desktop\prjx\vecsum\tmp\nonexistent_directory_12345' in error message, got: vecsum - Hierarchical PDF summarization using SQLite Vector

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


Error: Directory does not exist: c:/users/human/desktop/prjx/vecsum/tmp/nonexistent_directory_12345


```

---

**Result:** ✗ FAIL
