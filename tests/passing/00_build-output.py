#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import subprocess
from pathlib import Path

def main():
    # Get project root (assume CWD is project root)
    project_root = Path.cwd()
    released_dir = project_root / "released"
    vecsum_exe = released_dir / "vecsum.exe"

    print("Testing build output requirements...")
    print(f"Project root: {project_root}")
    print(f"Released directory: {released_dir}")

    # $REQ_BUILD_001: Single Executable Output
    print("\n[Test] $REQ_BUILD_001: Single executable output")
    assert released_dir.exists(), f"Released directory does not exist: {released_dir}"
    assert vecsum_exe.exists(), f"vecsum.exe does not exist: {vecsum_exe}"
    assert vecsum_exe.is_file(), f"vecsum.exe is not a file: {vecsum_exe}"
    print("✓ vecsum.exe exists as a file")

    # $REQ_BUILD_002: No External Runtime Dependencies
    print("\n[Test] $REQ_BUILD_002: No external runtime dependencies")
    # Verify this is a native executable, not a .NET assembly
    # .NET assemblies would show "Mono/.Net assembly" in file output
    file_result = subprocess.run(
        ['file', str(vecsum_exe)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    file_output = file_result.stdout
    print(f"File type: {file_output.strip()}")

    is_dotnet_assembly = '.Net assembly' in file_output or 'Mono/.Net assembly' in file_output
    assert not is_dotnet_assembly, \
        f"vecsum.exe is a .NET assembly (requires .NET runtime): {file_output}"
    print("✓ vecsum.exe is a native executable (no .NET runtime required)")

    # $REQ_BUILD_003: No External DLLs
    # $REQ_BUILD_004: No Separate SQLite Files
    # These requirements mean only vecsum.exe should exist in released/
    print("\n[Test] $REQ_BUILD_003, $REQ_BUILD_004: No external dependencies")
    released_contents = list(released_dir.iterdir())
    print(f"Contents of released/: {[item.name for item in released_contents]}")

    # Check that only vecsum.exe exists
    assert len(released_contents) == 1, \
        f"Expected only vecsum.exe in released/, found: {[item.name for item in released_contents]}"
    assert released_contents[0].name == "vecsum.exe", \
        f"Expected only vecsum.exe, found: {released_contents[0].name}"

    # Verify no DLLs
    dll_files = list(released_dir.glob("*.dll"))
    assert len(dll_files) == 0, f"Found DLL files (violates $REQ_BUILD_003): {[f.name for f in dll_files]}"
    print("✓ No external DLL files found")

    # Verify no SQLite files
    sqlite_files = list(released_dir.glob("*sqlite*"))
    # Filter out vecsum.exe from the search (it might contain "sqlite" internally)
    sqlite_files = [f for f in sqlite_files if f.name != "vecsum.exe"]
    assert len(sqlite_files) == 0, \
        f"Found SQLite files (violates $REQ_BUILD_004): {[f.name for f in sqlite_files]}"
    print("✓ No separate SQLite files found")

    # Verify executable is self-contained
    print(f"✓ Single standalone executable: {vecsum_exe}")
    print(f"✓ Size: {vecsum_exe.stat().st_size / (1024*1024):.2f} MB")

    print("\n✓ All build output requirements passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
