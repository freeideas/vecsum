# Test Report: 02_error-handling

**Status:** FAIL
**Exit Code:** 1
**Timestamp:** 2026-01-14-14-47-01-641
**Test File:** tests/failing/02_error-handling.py

## Output

```
Testing error handling...

✓ Test missing API key passed
✓ Test missing --db-file passed
✓ Test missing --pdf-dir for new database passed
✓ Test missing --summarize for existing database passed
[stderr] Traceback (most recent call last):
[stderr]   File "C:\Users\Human\Desktop\prjx\vecsum\tests\failing\02_error-handling.py", line 384, in <module>
[stderr]     test_directory_does_not_exist()
[stderr]     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
[stderr]   File "C:\Users\Human\Desktop\prjx\vecsum\tests\failing\02_error-handling.py", line 190, in test_directory_does_not_exist
[stderr]     assert str(nonexistent_dir) in output, \
[stderr]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr] AssertionError: Expected path 'C:\Users\Human\Desktop\prjx\vecsum\tmp\nonexistent_directory_12345' in error message, got: vecsum - Hierarchical PDF summarization using SQLite Vector
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
[stderr] Error: Directory does not exist: c:/users/human/desktop/prjx/vecsum/tmp/nonexistent_directory_12345
[stderr] 

```
