# Build Output Requirements

Requirements for the delivered executable in `./released/`.

## $REQ_BUILD_001: Single Executable Output
**Source:** ./README.md (Section: "Output")

The build must produce `./released/vecsum.exe` as a single standalone executable.

## $REQ_BUILD_002: No External Runtime Dependencies
**Source:** ./README.md (Section: "Output")

The executable must not require a .NET runtime to be installed on the target system.

## $REQ_BUILD_003: No External DLLs
**Source:** ./README.md (Section: "Output")

The executable must not require any external DLL files.

## $REQ_BUILD_004: No Separate SQLite Files
**Source:** ./README.md (Section: "Output")

The executable must not require separate SQLite extension files -- SQLite and SQLite Vector must be bundled inside the executable.
