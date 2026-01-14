# Test Report: 02_llm-integration
**Timestamp:** 2026-01-14-14-22-58-976
**Status:** FAIL
**Test File:** tests\passing\02_llm-integration.py

---

## Output

```
Testing LLM Integration Requirements...

Traceback (most recent call last):
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_llm-integration.py", line 214, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_llm-integration.py", line 199, in main
    test_api_key_environment_variable()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Human\Desktop\prjx\vecsum\tests\passing\02_llm-integration.py", line 43, in test_api_key_environment_variable
    assert "Error: OPENAI_API_KEY environment variable is not set" in result.stdout, \
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected error message not found. Got: vecsum - Hierarchical PDF summarization using SQLite Vector

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


Error: --summarize is required when using existing database


```

---

**Result:** ✗ FAIL
