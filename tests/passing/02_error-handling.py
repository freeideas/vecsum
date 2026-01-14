#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test error handling for the vecsum CLI application.

This test validates all error conditions and their corresponding error messages
as specified in reqs/02_error-handling.md.
"""

import subprocess
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Use repo-relative paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VECSUM_EXE = REPO_ROOT / "released" / "vecsum.exe"
TMP_DIR = REPO_ROOT / "tmp"

# Ensure tmp directory exists
TMP_DIR.mkdir(exist_ok=True)


def run_demo(args, env=None):
    """Run vecsum.exe with given arguments and capture output."""
    cmd = [str(VECSUM_EXE)] + args
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=full_env
    )
    return result


def test_error_output_format(output):
    """Verify error output contains help text followed by error message."""
    # $REQ_ERR_001: Error Output Format
    assert "vecsum - Hierarchical PDF summarization using SQLite Vector" in output, \
        "Error output must start with help text"
    assert "Usage:" in output, "Error output must contain usage info"
    assert "Error:" in output, "Error output must contain 'Error:' prefix"


def test_missing_api_key():
    """Test missing OPENAI_API_KEY environment variable."""
    # $REQ_ERR_002: Missing API Key
    result = run_demo(
        ["--db-file", str(TMP_DIR / "test.db")],
        env={"OPENAI_API_KEY": ""}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "OPENAI_API_KEY environment variable is not set" in output, \
        f"Expected missing API key error message, got: {output}"

    print("✓ Test missing API key passed")


def test_missing_db_file():
    """Test missing --db-file argument."""
    # $REQ_ERR_004: Missing Required Argument
    result = run_demo([], env={"OPENAI_API_KEY": "test-key"})

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "--db-file is required" in output, \
        f"Expected --db-file required error message, got: {output}"

    print("✓ Test missing --db-file passed")


def test_missing_pdf_dir_for_new_db():
    """Test missing --pdf-dir when creating a new database."""
    # $REQ_ERR_005: Missing PDF Dir for New Database
    db_file = TMP_DIR / "test_new.db"
    if db_file.exists():
        db_file.unlink()

    result = run_demo(
        ["--db-file", str(db_file)],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "--pdf-dir is required when creating a new database" in output, \
        f"Expected --pdf-dir required error message, got: {output}"

    print("✓ Test missing --pdf-dir for new database passed")


def test_missing_summarize_for_existing_db():
    """Test missing --summarize when using existing database."""
    # $REQ_ERR_006: Missing Summarize for Existing Database

    # Create a minimal SQLite database
    import sqlite3

    db_file = TMP_DIR / "test_existing.db"
    if db_file.exists():
        db_file.unlink()

    # Create database with proper schema (mimicking what vecsum creates)
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES nodes(id),
            node_type TEXT NOT NULL,
            doc_path TEXT,
            dir_path TEXT,
            content TEXT NOT NULL,
            embedding BLOB NOT NULL
        );
        CREATE TABLE directories (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE
        );
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            directory_id INTEGER REFERENCES directories(id),
            path TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

    # Try to use existing database without --summarize
    result = run_demo(
        ["--db-file", str(db_file)],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "--summarize is required when using existing database" in output, \
        f"Expected --summarize required error message, got: {output}"

    print("✓ Test missing --summarize for existing database passed")


def test_directory_does_not_exist():
    """Test --pdf-dir with non-existent directory."""
    # $REQ_ERR_008: Directory Does Not Exist
    nonexistent_dir = TMP_DIR / "nonexistent_directory_12345"

    result = run_demo(
        ["--db-file", str(TMP_DIR / "test.db"), "--pdf-dir", str(nonexistent_dir)],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "Directory does not exist:" in output, \
        f"Expected directory not exist error message, got: {output}"
    assert str(nonexistent_dir) in output, \
        f"Expected path '{nonexistent_dir}' in error message, got: {output}"

    print("✓ Test directory does not exist passed")


def test_no_pdfs_in_directory():
    """Test --pdf-dir with directory containing no PDFs."""
    # $REQ_ERR_009: No PDFs in Directory
    empty_dir = TMP_DIR / "empty_pdf_dir"
    empty_dir.mkdir(exist_ok=True)

    # Create a non-PDF file to ensure it's not empty
    (empty_dir / "test.txt").write_text("not a pdf")

    result = run_demo(
        ["--db-file", str(TMP_DIR / "test.db"), "--pdf-dir", str(empty_dir)],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "No PDF files found in:" in output, \
        f"Expected no PDFs error message, got: {output}"
    assert str(empty_dir) in output, \
        f"Expected path '{empty_dir}' in error message, got: {output}"

    print("✓ Test no PDFs in directory passed")


def test_unknown_argument():
    """Test unknown command-line argument."""
    # $REQ_ERR_010: Unknown Argument
    result = run_demo(
        ["--db-file", str(TMP_DIR / "test.db"), "--invalid-arg"],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "Unknown argument:" in output, \
        f"Expected unknown argument error message, got: {output}"
    assert "--invalid-arg" in output, \
        f"Expected '--invalid-arg' in error message, got: {output}"

    print("✓ Test unknown argument passed")


def test_summarize_path_not_found():
    """Test --summarize with path not in database."""
    # $REQ_ERR_007: Summarize Path Not Found

    # Create a minimal SQLite database with proper schema but no data
    import sqlite3

    db_file = TMP_DIR / "test_summarize.db"
    if db_file.exists():
        db_file.unlink()

    # Create database with proper schema (mimicking what vecsum creates)
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES nodes(id),
            node_type TEXT NOT NULL,
            doc_path TEXT,
            dir_path TEXT,
            content TEXT NOT NULL,
            embedding BLOB NOT NULL
        );
        CREATE TABLE directories (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE
        );
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            directory_id INTEGER REFERENCES directories(id),
            path TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

    # Try to summarize a path that doesn't exist in the (empty) database
    result = run_demo(
        ["--db-file", str(db_file), "--summarize", "./nonexistent/path"],
        env={"OPENAI_API_KEY": "test-key"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "Path not found in database:" in output, \
        f"Expected path not found error message, got: {output}"
    assert "./nonexistent/path" in output, \
        f"Expected './nonexistent/path' in error message, got: {output}"

    print("✓ Test summarize path not found passed")


def test_invalid_api_key():
    """Test invalid OPENAI_API_KEY (API returns 401)."""
    # $REQ_ERR_003: Invalid API Key
    # Note: This test requires actually calling the OpenAI API with an invalid key.
    # We'll create a test PDF directory and try to build, which will trigger API call.

    # Create a test directory with a dummy PDF
    test_pdf_dir = TMP_DIR / "test_pdfs_invalid_key"
    test_pdf_dir.mkdir(exist_ok=True)

    # Create a minimal PDF file (this is a valid minimal PDF)
    pdf_content = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
409
%%EOF
"""
    (test_pdf_dir / "test.pdf").write_text(pdf_content)

    db_file = TMP_DIR / "test_invalid_key.db"
    if db_file.exists():
        db_file.unlink()

    # Use an obviously invalid API key
    result = run_demo(
        ["--db-file", str(db_file), "--pdf-dir", str(test_pdf_dir)],
        env={"OPENAI_API_KEY": "invalid-key-12345"}
    )

    assert result.returncode != 0, "Should exit with non-zero code"

    output = result.stdout + result.stderr
    test_error_output_format(output)

    assert "OPENAI_API_KEY is invalid or expired" in output, \
        f"Expected invalid API key error message, got: {output}"

    print("✓ Test invalid API key passed")


def test_openai_api_error():
    """Test OpenAI API error during processing."""
    # $REQ_ERR_011: OpenAI API Error - Not reasonably testable: Would require triggering
    # specific non-401 OpenAI API errors (rate limits, service errors, etc.) which would
    # require either mocking internal implementation details or unreliably depending on
    # real API failures. The error message format is distinct from the 401 invalid key
    # error ($REQ_ERR_003) and cannot be reliably triggered in a fast, deterministic test.
    print("✓ Test OpenAI API error marked as not reasonably testable")


if __name__ == "__main__":
    print("Testing error handling...")
    print()

    # Run tests
    test_missing_api_key()
    test_missing_db_file()
    test_missing_pdf_dir_for_new_db()
    test_missing_summarize_for_existing_db()
    test_directory_does_not_exist()
    test_no_pdfs_in_directory()
    test_unknown_argument()
    test_summarize_path_not_found()
    test_invalid_api_key()
    test_openai_api_error()

    print()
    print("All error handling tests passed!")
    sys.exit(0)
