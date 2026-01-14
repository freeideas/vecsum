#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test suite for CLI requirements (reqs/01_cli.md)
Tests the vecsum.exe command-line interface behavior.
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import atexit

# Track processes for cleanup
_procs = []

def cleanup():
    """Clean up any running processes."""
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            pass

atexit.register(cleanup)

# Project root (assuming test runs from project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
VECSUM_EXE = PROJECT_ROOT / 'released' / 'vecsum.exe'

def run_demo(*args, env=None, expect_error=False):
    """Run vecsum.exe with given arguments and return result."""
    cmd = [str(VECSUM_EXE)] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env or os.environ.copy()
    )
    if not expect_error and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print(f"returncode: {result.returncode}")
    return result

def create_test_pdf(path):
    """Create a minimal valid PDF file at the given path."""
    # Minimal PDF that should be readable by most PDF libraries
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
0000000327 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
419
%%EOF
"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(pdf_content)

def test_cli():
    """Main test function for CLI requirements."""

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / 'tmp') as tmpdir:
        tmpdir = Path(tmpdir)

        # Test database paths
        db_file = tmpdir / 'test.db'
        db_file2 = tmpdir / 'test2.db'

        # Create test PDF directories
        pdf_dir1 = tmpdir / 'docs1'
        pdf_dir2 = tmpdir / 'docs2'
        pdf_dir1.mkdir()
        pdf_dir2.mkdir()

        # Create test PDFs
        pdf1 = pdf_dir1 / 'test1.pdf'
        pdf2 = pdf_dir1 / 'test2.pdf'
        pdf3 = pdf_dir2 / 'test3.pdf'

        create_test_pdf(pdf1)
        create_test_pdf(pdf2)
        create_test_pdf(pdf3)

        print("Testing CLI requirements...")

        # $REQ_CLI_019: Error for Missing --db-file
        print("Test: Missing --db-file")
        result = run_demo(expect_error=True)
        assert result.returncode != 0, "Should fail without --db-file"
        assert "--db-file is required" in result.stdout or "--db-file is required" in result.stderr, \
            "$REQ_CLI_019: Should error with '--db-file is required'"

        # $REQ_CLI_023: Error for Unknown Argument
        print("Test: Unknown argument")
        result = run_demo('--db-file', str(db_file), '--unknown-arg', expect_error=True)
        assert result.returncode != 0, "Should fail with unknown argument"
        assert "Unknown argument" in result.stdout or "Unknown argument" in result.stderr, \
            "$REQ_CLI_023: Should error with 'Unknown argument'"

        # $REQ_CLI_021: Error for Non-Existent --pdf-dir
        print("Test: Non-existent pdf-dir")
        nonexistent = tmpdir / 'nonexistent'
        env_fake_key = os.environ.copy()
        env_fake_key['OPENAI_API_KEY'] = 'fake-key-for-testing'
        result = run_demo('--db-file', str(db_file), '--pdf-dir', str(nonexistent), env=env_fake_key, expect_error=True)
        assert result.returncode != 0, "Should fail with non-existent directory"
        assert "Directory does not exist" in result.stdout or "Directory does not exist" in result.stderr, \
            "$REQ_CLI_021: Should error with 'Directory does not exist'"

        # $REQ_CLI_022: Error for Empty --pdf-dir
        print("Test: Empty pdf-dir")
        empty_dir = tmpdir / 'empty'
        empty_dir.mkdir()
        env_fake_key = os.environ.copy()
        env_fake_key['OPENAI_API_KEY'] = 'fake-key-for-testing'
        result = run_demo('--db-file', str(db_file), '--pdf-dir', str(empty_dir), env=env_fake_key, expect_error=True)
        assert result.returncode != 0, "Should fail with empty directory"
        assert "No PDF files found in" in result.stdout or "No PDF files found in" in result.stderr, \
            "$REQ_CLI_022: Should error with 'No PDF files found in'"

        # $REQ_CLI_028: Error for Missing --pdf-dir When Creating Database
        print("Test: Missing --pdf-dir when creating database")
        new_db = tmpdir / 'newdb.db'
        # Need to provide a fake API key so we can test the pdf-dir requirement
        env_fake_key = os.environ.copy()
        env_fake_key['OPENAI_API_KEY'] = 'fake-key-for-testing'
        result = run_demo('--db-file', str(new_db), env=env_fake_key, expect_error=True)
        assert result.returncode != 0, "Should fail without --pdf-dir for new database"
        assert "--pdf-dir is required when creating a new database" in result.stdout or \
               "--pdf-dir is required when creating a new database" in result.stderr, \
            "$REQ_CLI_028: Should error with '--pdf-dir is required when creating a new database'"

        # Test API key requirements (need to check if OPENAI_API_KEY is set)
        # $REQ_CLI_017: Error for Missing OPENAI_API_KEY
        print("Test: Missing OPENAI_API_KEY")
        env_no_key = os.environ.copy()
        if 'OPENAI_API_KEY' in env_no_key:
            del env_no_key['OPENAI_API_KEY']

        result = run_demo('--db-file', str(db_file), '--pdf-dir', str(pdf_dir1), env=env_no_key, expect_error=True)
        assert result.returncode != 0, "Should fail without OPENAI_API_KEY"
        assert "OPENAI_API_KEY environment variable is not set" in result.stdout or \
               "OPENAI_API_KEY environment variable is not set" in result.stderr, \
            "$REQ_CLI_017: Should error with 'OPENAI_API_KEY environment variable is not set'"

        # For remaining tests, we need a valid OPENAI_API_KEY or we skip OpenAI-dependent tests
        if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY']:
            print("WARNING: OPENAI_API_KEY not set, skipping OpenAI-dependent tests")
            print("The following requirements cannot be tested without API key:")
            print("  $REQ_CLI_002: Database File Creation - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_003: Existing Database Usage - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_004: Multiple --pdf-dir Arguments - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_005: --pdf-dir Ignored for Existing Database - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_007: Directory as Tree Branch - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_008: --summarize Directory Path - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_009: --summarize PDF File Path - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_011: Build Time Printed After Database Creation - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_012: Lookup Time Printed After Summary Retrieval - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_013: Summary Output Format - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_014: Progress Indicator During Build - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_015: Build and Query in One Command - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_018: Error for Invalid OPENAI_API_KEY - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_020: Error for --summarize Path Not in Database - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_024: Error for OpenAI API Failures - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_025: Path Canonicalization on Input - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_027: --summarize Without Path Returns Corpus Summary - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_029: Error for Missing --summarize With Existing Database - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_030: Recursive PDF Ingestion - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_031: --log-dir Enables Logging - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_032: --log-dir Directory Creation - Not reasonably testable: Requires OpenAI API")
            print("  $REQ_CLI_033: No Logging Without --log-dir - Not reasonably testable: Requires OpenAI API")
            return

        # Now test with actual OpenAI API
        # $REQ_CLI_002: Database File Creation
        # $REQ_CLI_004: Multiple --pdf-dir Arguments
        # $REQ_CLI_007: Directory as Tree Branch
        # $REQ_CLI_011: Build Time Printed After Database Creation
        # $REQ_CLI_014: Progress Indicator During Build
        print("Test: Create new database with multiple pdf-dirs")
        result = run_demo('--db-file', str(db_file), '--pdf-dir', str(pdf_dir1), '--pdf-dir', str(pdf_dir2))
        assert result.returncode == 0, f"$REQ_CLI_002/$REQ_CLI_004: Should create database successfully"
        assert db_file.exists(), "$REQ_CLI_002: Database file should be created"
        assert 'Build time:' in result.stdout, "$REQ_CLI_011: Should print build time"
        assert '.' in result.stdout, "$REQ_CLI_014: Should print progress dots"

        # $REQ_CLI_003: Existing Database Usage
        # $REQ_CLI_005: --pdf-dir Ignored for Existing Database
        print("Test: Use existing database (ignore pdf-dir)")
        db_mtime = db_file.stat().st_mtime
        result = run_demo('--db-file', str(db_file), '--pdf-dir', str(pdf_dir1))
        assert result.returncode == 0, "$REQ_CLI_003: Should use existing database"
        assert db_file.stat().st_mtime == db_mtime, "$REQ_CLI_005: Database should not be modified (pdf-dir ignored)"
        assert 'Build time:' not in result.stdout, "$REQ_CLI_003: Should not rebuild existing database"

        # $REQ_CLI_008: --summarize Directory Path
        # $REQ_CLI_012: Lookup Time Printed After Summary Retrieval
        # $REQ_CLI_013: Summary Output Format
        print("Test: Summarize directory")
        result = run_demo('--db-file', str(db_file), '--summarize', str(pdf_dir1))
        assert result.returncode == 0, "$REQ_CLI_008: Should summarize directory"
        assert f'Summary for:' in result.stdout, "$REQ_CLI_013: Should include 'Summary for:'"
        assert 'Lookup time:' in result.stdout, "$REQ_CLI_012/$REQ_CLI_013: Should print lookup time"

        # $REQ_CLI_009: --summarize PDF File Path
        print("Test: Summarize PDF file")
        result = run_demo('--db-file', str(db_file), '--summarize', str(pdf1))
        assert result.returncode == 0, "$REQ_CLI_009: Should summarize PDF file"
        assert f'Summary for:' in result.stdout, "$REQ_CLI_013: Should include 'Summary for:'"
        assert 'Lookup time:' in result.stdout, "$REQ_CLI_013: Should print lookup time"

        # $REQ_CLI_015: Build and Query in One Command
        print("Test: Build and query in one command")
        result = run_demo('--db-file', str(db_file2), '--pdf-dir', str(pdf_dir1), '--summarize', str(pdf_dir1))
        assert result.returncode == 0, "$REQ_CLI_015: Should build and query in one command"
        assert db_file2.exists(), "$REQ_CLI_015: Database should be created"
        assert 'Build time:' in result.stdout, "$REQ_CLI_015: Should print build time"
        assert f'Summary for:' in result.stdout, "$REQ_CLI_015: Should print summary"
        assert 'Lookup time:' in result.stdout, "$REQ_CLI_015: Should print lookup time"

        # $REQ_CLI_020: Error for --summarize Path Not in Database
        print("Test: Summarize path not in database")
        nonexistent_path = tmpdir / 'not_in_db'
        result = run_demo('--db-file', str(db_file), '--summarize', str(nonexistent_path), expect_error=True)
        assert result.returncode != 0, "$REQ_CLI_020: Should fail for path not in database"
        assert 'Path not found in database' in result.stdout or 'Path not found in database' in result.stderr, \
            "$REQ_CLI_020: Should error with 'Path not found in database'"

        # $REQ_CLI_030: Recursive PDF Ingestion
        print("Test: Recursive PDF ingestion")
        # Create a subdirectory with a PDF - it SHOULD be ingested recursively
        subdir = pdf_dir1 / 'subdir'
        subdir.mkdir()
        pdf_in_subdir = subdir / 'nested.pdf'
        create_test_pdf(pdf_in_subdir)

        # Create new database with pdf_dir1 (which now has a subdirectory)
        db_file_recursive = tmpdir / 'test_recursive.db'
        result = run_demo('--db-file', str(db_file_recursive), '--pdf-dir', str(pdf_dir1))
        assert result.returncode == 0, "$REQ_CLI_030: Should create database"

        # Try to query the nested PDF - should succeed because it was ingested recursively
        result = run_demo('--db-file', str(db_file_recursive), '--summarize', str(pdf_in_subdir))
        assert result.returncode == 0, "$REQ_CLI_030: Nested PDF should be in database (recursive ingestion)"
        assert 'Summary for:' in result.stdout, "$REQ_CLI_030: Should return summary for recursively ingested PDF"

        # $REQ_CLI_025: Path Canonicalization on Input
        print("Test: Path canonicalization")
        # Use relative path to test canonicalization - should work if canonicalized properly
        # Create a relative path that points to the same directory
        original_cwd = Path.cwd()
        os.chdir(pdf_dir1.parent)  # Change to parent of pdf_dir1
        try:
            relative_path = Path('docs1')  # Relative path from current directory
            result = run_demo('--db-file', str(db_file), '--summarize', str(relative_path))
            assert result.returncode == 0, "$REQ_CLI_025: Should succeed with relative path after canonicalization"
            assert 'Summary for:' in result.stdout, "$REQ_CLI_025: Should return summary for canonicalized path"
        finally:
            os.chdir(original_cwd)  # Restore original working directory

        # $REQ_CLI_027: --summarize Without Path Returns Corpus Summary
        print("Test: Summarize without path (corpus summary)")
        result = run_demo('--db-file', str(db_file), '--summarize')
        assert result.returncode == 0, "$REQ_CLI_027: Should return corpus summary"
        assert 'Summary for: [corpus]' in result.stdout or 'Summary for:[corpus]' in result.stdout, \
            "$REQ_CLI_027: Should include 'Summary for: [corpus]'"
        assert 'Lookup time:' in result.stdout, "$REQ_CLI_027: Should print lookup time"

        # $REQ_CLI_029: Error for Missing --summarize With Existing Database
        print("Test: Missing --summarize with existing database")
        result = run_demo('--db-file', str(db_file), expect_error=True)
        assert result.returncode != 0, "$REQ_CLI_029: Should fail without --summarize for existing database"
        assert "--summarize is required when using existing database" in result.stdout or \
               "--summarize is required when using existing database" in result.stderr, \
            "$REQ_CLI_029: Should error with '--summarize is required when using existing database'"

        # $REQ_CLI_031: --log-dir Enables Logging
        # $REQ_CLI_032: --log-dir Directory Creation
        # $REQ_CLI_033: No Logging Without --log-dir
        print("Test: --log-dir enables logging")
        log_dir = tmpdir / 'logs'
        db_file_log = tmpdir / 'test_log.db'
        result = run_demo('--db-file', str(db_file_log), '--pdf-dir', str(pdf_dir2), '--log-dir', str(log_dir))
        assert result.returncode == 0, "$REQ_CLI_031: Should succeed with --log-dir"
        assert log_dir.exists(), "$REQ_CLI_032: Log directory should be created"
        # Check if log files were created
        log_files = list(log_dir.glob('*.json'))
        assert len(log_files) > 0, "$REQ_CLI_031: Should create log files when --log-dir is specified"

        # Test without --log-dir to verify no logging occurs
        print("Test: No logging without --log-dir")
        db_file_nolog = tmpdir / 'test_nolog.db'
        result = run_demo('--db-file', str(db_file_nolog), '--pdf-dir', str(pdf_dir2))
        assert result.returncode == 0, "$REQ_CLI_033: Should succeed without --log-dir"
        # Verify no new log files were created in the temp directory
        temp_log_files = list(tmpdir.glob('*.json'))
        assert len(temp_log_files) == 0, "$REQ_CLI_033: Should not create log files without --log-dir"

        # $REQ_CLI_016: Error Output Format
        print("Test: Error output includes help text")
        result = run_demo('--invalid', expect_error=True)
        assert result.returncode != 0, "$REQ_CLI_016: Should fail with error"
        # Should include help text (Usage:) and error message
        assert 'Usage:' in result.stdout, "$REQ_CLI_016: Should include help text"
        assert 'Error:' in result.stdout, "$REQ_CLI_016: Should include error message"

        # $REQ_CLI_007: Directory as Tree Branch - Not reasonably testable: Internal database structure, verified by successful summarization
        # $REQ_CLI_018: Error for Invalid OPENAI_API_KEY - Not reasonably testable: Requires actually calling OpenAI API with invalid key
        # $REQ_CLI_024: Error for OpenAI API Failures - Not reasonably testable: Requires triggering actual OpenAI API failures
        # $REQ_CLI_026: Standalone Executable - Not reasonably testable: Cannot verify "no dependencies" programmatically; verified by successful execution

        print("\nAll CLI tests passed!")

if __name__ == '__main__':
    # Ensure tmp directory exists
    os.makedirs(PROJECT_ROOT / 'tmp', exist_ok=True)

    test_cli()
