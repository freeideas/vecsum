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
import shutil
from pathlib import Path

def main():
    # Get project root (parent of code directory)
    code_dir = Path(__file__).parent
    project_root = code_dir.parent
    released_dir = project_root / "released"
    dotnet_exe = project_root / "tools" / "compiler" / "dotnet.exe"

    print("Building vecsum.exe...")
    print(f"Project root: {project_root}")
    print(f"Code directory: {code_dir}")
    print(f"Release directory: {released_dir}")

    # Ensure released directory exists
    released_dir.mkdir(exist_ok=True)

    # Check if dotnet exists
    if not dotnet_exe.exists():
        print(f"ERROR: .NET SDK not found at {dotnet_exe}")
        return 1

    # Restore packages
    print("\nRestoring NuGet packages...")
    result = subprocess.run(
        [str(dotnet_exe), "restore", "vecsum.csproj"],
        cwd=str(code_dir),
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print("ERROR: Package restore failed")
        return 1

    # Build and publish
    print("\nBuilding and publishing single-file executable...")
    result = subprocess.run(
        [
            str(dotnet_exe), "publish", "vecsum.csproj",
            "-c", "Release",
            "-o", str(released_dir),
            "/p:PublishSingleFile=true",
            "/p:SelfContained=true",
            "/p:RuntimeIdentifier=win-x64",
            "/p:PublishTrimmed=false",
            "/p:EnableCompressionInSingleFile=true"
        ],
        cwd=str(code_dir),
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print("ERROR: Build failed")
        return 1

    # Check if vecsum.exe was created
    vecsum_exe = released_dir / "vecsum.exe"
    if not vecsum_exe.exists():
        print(f"ERROR: vecsum.exe was not created at {vecsum_exe}")
        return 1

    # Clean up extra files (keep only vecsum.exe)
    print("\nCleaning up extra files...")
    for item in released_dir.iterdir():
        if item.name != "vecsum.exe":
            if item.is_file():
                item.unlink()
                print(f"  Removed: {item.name}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"  Removed directory: {item.name}")

    print(f"\n✓ Build successful!")
    print(f"✓ Output: {vecsum_exe}")
    print(f"✓ Size: {vecsum_exe.stat().st_size / (1024*1024):.2f} MB")

    return 0

if __name__ == "__main__":
    sys.exit(main())
