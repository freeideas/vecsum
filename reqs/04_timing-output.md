# Timing Output

Documents the timing information printed for database build operations and summary lookup operations.

## $REQ_TIMING_001: Build Time Printed After Database Creation
**Source:** ./specs/COMMAND-LINE.md (Section: "Timing")

When the database is created (because `--db-file` did not exist), the program prints the build time in milliseconds in the format `Build time: <N ms>`.

## $REQ_TIMING_002: Lookup Time Printed After Summary Retrieval
**Source:** ./specs/COMMAND-LINE.md (Section: "Timing")

When `--summarize` retrieves a summary, the program prints the lookup time in milliseconds in the format `Lookup time: <N ms>`.

## $REQ_TIMING_003: Build Time Included in Summary Output When Database Was Just Created
**Source:** ./specs/COMMAND-LINE.md (Section: "Summary Output")

When `--summarize` is provided and the database was just created in the same invocation, the output includes `Build time: <N ms>` before the lookup time.

## $REQ_TIMING_004: Build Time Omitted When Using Existing Database
**Source:** ./specs/COMMAND-LINE.md (Section: "Summary Output")

When `--summarize` queries an existing database (not created in this invocation), only `Lookup time: <N ms>` is printed, without build time.
