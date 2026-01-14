#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import subprocess
import sys
import tempfile
from pathlib import Path
import os
import sqlite3

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def run_vecsum(args):
    """Helper to run vecsum.exe with proper encoding."""
    # Try multiple possible locations for the executable
    possible_paths = [
        Path('released/vecsum.exe'),
        Path(__file__).resolve().parent.parent.parent / 'released' / 'vecsum.exe',
    ]

    exe_path = None
    for path in possible_paths:
        if path.exists():
            exe_path = path
            break

    if exe_path is None:
        print(f"Error: vecsum.exe not found in any expected location. Run build first.", file=sys.stderr)
        sys.exit(97)

    cmd = [str(exe_path)] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result

def create_mock_database(db_path, canonical_dir_path, canonical_doc_path):
    """Create a mock database with test data to avoid needing OpenAI API."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES nodes(id),
            node_type TEXT NOT NULL,
            doc_path TEXT,
            dir_path TEXT,
            content TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE directories (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            directory_id INTEGER REFERENCES directories(id),
            path TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL
        )
    """)

    # Insert test data with canonical paths
    # $REQ_PATHCANON_001, $REQ_PATHCANON_002, $REQ_PATHCANON_003, $REQ_PATHCANON_004:
    # Paths stored should be: absolute, forward slashes, no trailing slash, lowercase on Windows
    cursor.execute("INSERT INTO directories (id, path) VALUES (1, ?)", (canonical_dir_path,))
    cursor.execute(
        "INSERT INTO documents (id, directory_id, path, filename) VALUES (1, 1, ?, 'test.pdf')",
        (canonical_doc_path,)
    )

    # Create dummy embeddings (zeros)
    dummy_embedding = b'\x00' * (1536 * 4)  # 1536 floats * 4 bytes

    # Insert nodes for directory and document summaries
    cursor.execute(
        "INSERT INTO nodes (id, parent_id, node_type, doc_path, dir_path, content, embedding) VALUES (1, NULL, 'doc_top', ?, NULL, 'Test document summary', ?)",
        (canonical_doc_path, dummy_embedding)
    )
    cursor.execute(
        "INSERT INTO nodes (id, parent_id, node_type, doc_path, dir_path, content, embedding) VALUES (2, NULL, 'dir_top', NULL, ?, 'Test directory summary', ?)",
        (canonical_dir_path, dummy_embedding)
    )

    conn.commit()
    conn.close()


def test_canonicalization():
    """Test path canonicalization requirements."""

    # Create a temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        # Create a test directory structure
        test_docs = Path(tmpdir) / 'testdocs' / 'subdir'
        test_docs.mkdir(parents=True, exist_ok=True)

        # Create a minimal valid PDF file (for path existence checks)
        test_pdf = test_docs / 'test.pdf'
        test_pdf.write_bytes(b'dummy pdf content')  # Minimal content

        # Get the canonical form that should be stored in DB
        # $REQ_PATHCANON_001: Absolute path
        # $REQ_PATHCANON_002: Forward slashes
        # $REQ_PATHCANON_003: No trailing slash
        # $REQ_PATHCANON_004: Lowercase on Windows
        canonical_dir = str(test_docs.resolve()).replace('\\', '/')
        canonical_doc = str(test_pdf.resolve()).replace('\\', '/')
        if sys.platform == 'win32':
            canonical_dir = canonical_dir.lower()
            canonical_doc = canonical_doc.lower()

        # Create mock database with canonical paths
        create_mock_database(db_path, canonical_dir, canonical_doc)

        # Test querying with different path formats
        # Format 1: Absolute path
        abs_path = str(test_docs.resolve())

        result = run_vecsum([
            '--db-file', str(db_path),
            '--summarize', abs_path
        ])

        # $REQ_PATHCANON_006: Query paths in different formats must be canonicalized and match stored paths
        assert result.returncode == 0, f"Query with absolute path failed: {result.stderr}"
        assert "Test directory summary" in result.stdout, f"Expected to find directory summary, got: {result.stdout}"

        # Format 2: Relative path with .. components
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            result = run_vecsum([
                '--db-file', str(db_path),
                '--summarize', './testdocs/../testdocs/subdir'
            ])

            # $REQ_PATHCANON_001: Resolve relative paths to absolute, expanding . and ..
            assert result.returncode == 0, f"Query with .. path failed: {result.stderr}"
            assert "Test directory summary" in result.stdout, f"Expected to find directory summary with .. path"

            # Format 3: Backslashes (Windows only)
            if sys.platform == 'win32':
                result = run_vecsum([
                    '--db-file', str(db_path),
                    '--summarize', '.\\testdocs\\subdir'
                ])

                # $REQ_PATHCANON_002: Convert backslashes to forward slashes
                assert result.returncode == 0, f"Query with backslash path failed: {result.stderr}"
                assert "Test directory summary" in result.stdout, f"Expected to find directory summary with backslash path"

        finally:
            os.chdir(orig_cwd)

    print("✓ All path canonicalization tests passed")

def test_backslash_conversion():
    """Test that backslashes are converted to forward slashes."""
    # This is tested implicitly in the main test
    # $REQ_PATHCANON_002: Convert backslashes to forward slashes
    # (Verified by successful matching of Windows-style paths with backslashes)
    pass

def test_trailing_slash_removal():
    """Test that trailing slashes are removed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        test_docs = Path(tmpdir) / 'testdocs'
        test_docs.mkdir(parents=True, exist_ok=True)

        test_pdf = test_docs / 'test.pdf'
        test_pdf.write_bytes(b'dummy pdf content')

        # Get canonical path (without trailing slash)
        canonical_dir = str(test_docs.resolve()).replace('\\', '/')
        canonical_doc = str(test_pdf.resolve()).replace('\\', '/')
        if sys.platform == 'win32':
            canonical_dir = canonical_dir.lower()
            canonical_doc = canonical_doc.lower()

        # Create mock database
        create_mock_database(db_path, canonical_dir, canonical_doc)

        # Query with trailing slash
        result = run_vecsum([
            '--db-file', str(db_path),
            '--summarize', str(test_docs) + '/'
        ])

        # $REQ_PATHCANON_003: Remove trailing slashes from directories
        assert result.returncode == 0, f"Query with trailing slash failed: {result.stderr}"
        assert "Test directory summary" in result.stdout, "Summary should be found when querying with trailing slash"

        # Query without trailing slash (should also work)
        result = run_vecsum([
            '--db-file', str(db_path),
            '--summarize', str(test_docs)
        ])

        assert result.returncode == 0, f"Query without trailing slash failed: {result.stderr}"
        assert "Test directory summary" in result.stdout, "Summary should be found when querying without trailing slash"

    print("✓ Trailing slash removal test passed")

def test_case_handling():
    """Test case handling: lowercase on Windows, preserve on Linux."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        test_docs = Path(tmpdir) / 'TestDocs'
        test_docs.mkdir(parents=True, exist_ok=True)

        test_pdf = test_docs / 'test.pdf'
        test_pdf.write_bytes(b'dummy pdf content')

        # Get canonical path (lowercase on Windows, preserve case on Linux)
        canonical_dir = str(test_docs.resolve()).replace('\\', '/')
        canonical_doc = str(test_pdf.resolve()).replace('\\', '/')
        if sys.platform == 'win32':
            canonical_dir = canonical_dir.lower()
            canonical_doc = canonical_doc.lower()

        # Create mock database
        create_mock_database(db_path, canonical_dir, canonical_doc)

        if sys.platform == 'win32':
            # On Windows, query with different case should work
            # Query with uppercase version
            uppercase_path = str(test_docs).upper()
            result = run_vecsum([
                '--db-file', str(db_path),
                '--summarize', uppercase_path
            ])

            # $REQ_PATHCANON_004: Lowercase paths on Windows
            assert result.returncode == 0, f"Query with uppercase path failed on Windows: {result.stderr}"
            assert "Test directory summary" in result.stdout, "Summary should be found with different case on Windows"

            # Query with lowercase version
            lowercase_path = str(test_docs).lower()
            result = run_vecsum([
                '--db-file', str(db_path),
                '--summarize', lowercase_path
            ])

            assert result.returncode == 0, f"Query with lowercase path failed on Windows: {result.stderr}"
            assert "Test directory summary" in result.stdout, "Summary should be found with lowercase on Windows"
        else:
            # On Linux, case is preserved
            # $REQ_PATHCANON_004: On Linux, case must be preserved
            # Query with exact case should work
            result = run_vecsum([
                '--db-file', str(db_path),
                '--summarize', str(test_docs)
            ])

            assert result.returncode == 0, f"Query with exact case failed on Linux: {result.stderr}"
            assert "Test directory summary" in result.stdout, "Summary should be found with exact case on Linux"

    print("✓ Case handling test passed")

def test_ingestion_path_matching():
    """Test that different path formats during ingestion result in same canonical path."""
    # $REQ_PATHCANON_005: Not reasonably testable - would require running actual ingestion with OpenAI API
    # Ingestion involves file processing and embedding generation, which is complex and API-dependent
    # The canonicalization logic is verified through query matching tests instead
    pass

if __name__ == '__main__':
    try:
        test_canonicalization()
        test_trailing_slash_removal()
        test_case_handling()
        test_ingestion_path_matching()
        print("\n✓ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
