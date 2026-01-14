#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import subprocess
import sqlite3
import sys
import struct
from pathlib import Path

# Ensure proper encoding on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Test for Summary Retrieval (reqs/04_summary-retrieval.md)

def canonicalize_path(path_str):
    """Canonicalize path using same logic as C# code"""
    p = Path(path_str).resolve()
    path_canon = str(p).replace('\\', '/')

    # Remove trailing slash (except root like "C:/")
    if len(path_canon) > 3 and path_canon.endswith('/'):
        path_canon = path_canon.rstrip('/')

    # Lowercase on Windows
    if sys.platform == 'win32':
        path_canon = path_canon.lower()

    return path_canon

def create_test_database():
    """Create a test database with mock data"""
    tmp_dir = Path('tmp')
    tmp_dir.mkdir(exist_ok=True)

    db_file = tmp_dir / 'test_summary_retrieval.db'
    if db_file.exists():
        db_file.unlink()

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Create schema
    cursor.execute('''
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES nodes(id),
            node_type TEXT NOT NULL,
            doc_path TEXT,
            dir_path TEXT,
            content TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE directories (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            directory_id INTEGER REFERENCES directories(id),
            path TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX idx_nodes_doc_path ON nodes(doc_path, node_type)')
    cursor.execute('CREATE INDEX idx_nodes_dir_path ON nodes(dir_path, node_type)')
    cursor.execute('CREATE INDEX idx_nodes_type ON nodes(node_type)')
    cursor.execute('CREATE INDEX idx_nodes_parent ON nodes(parent_id)')

    # Create dummy embedding (1536 float32 values = 6144 bytes)
    dummy_embedding = struct.pack('f' * 1536, *([0.1] * 1536))

    # Insert test data
    # Use paths relative to current working directory
    cooking_dir = Path('extart/example-pdfs/cooking')
    pdf_path = cooking_dir / 'test.pdf'

    # Canonicalize paths
    cooking_dir_canon = canonicalize_path(str(cooking_dir))
    pdf_path_canon = canonicalize_path(str(pdf_path))

    # Insert directory
    cursor.execute('INSERT INTO directories (id, path) VALUES (?, ?)',
                   (1, cooking_dir_canon))

    # Insert document
    cursor.execute('INSERT INTO documents (id, directory_id, path, filename) VALUES (?, ?, ?, ?)',
                   (1, 1, pdf_path_canon, 'test.pdf'))

    # Insert doc_top node for the PDF
    cursor.execute('''
        INSERT INTO nodes (id, parent_id, node_type, doc_path, dir_path, content, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (1, None, 'doc_top', pdf_path_canon, None,
          'This is a test document summary about cooking recipes.', dummy_embedding))

    # Insert dir_top node for the directory
    cursor.execute('''
        INSERT INTO nodes (id, parent_id, node_type, doc_path, dir_path, content, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (2, None, 'dir_top', None, cooking_dir_canon,
          'This directory contains cooking-related documents and recipes.', dummy_embedding))

    # Insert root node (corpus summary)
    cursor.execute('''
        INSERT INTO nodes (id, parent_id, node_type, doc_path, dir_path, content, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (3, None, 'root', None, None,
          'This corpus contains various documents and directories for testing.', dummy_embedding))

    conn.commit()
    conn.close()

    return db_file

def run_demo(*args):
    """Run vecsum.exe with given arguments, return (exit_code, stdout, stderr)"""
    exe = Path('released/vecsum.exe').resolve()
    cmd = [str(exe)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result.returncode, result.stdout, result.stderr

def main():
    print("Creating test database...")
    db_file = create_test_database()
    print(f"Test database created: {db_file}")

    # Test paths
    cooking_dir = Path('extart/example-pdfs/cooking')
    pdf_path = cooking_dir / 'test.pdf'

    # $REQ_SUMRET_001: Retrieve corpus summary (no path)
    print("\n$REQ_SUMRET_001: Testing corpus summary retrieval (no path)...")
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize')

    if exit_code != 0:
        print(f"Corpus summary failed with exit code {exit_code}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    # $REQ_SUMRET_001, $REQ_SUMRET_004, $REQ_SUMRET_007: Output format
    assert 'Summary for:' in stdout, "Should show 'Summary for:' label"  # $REQ_SUMRET_001, $REQ_SUMRET_004
    assert '[corpus]' in stdout, "Should show '[corpus]' instead of path"  # $REQ_SUMRET_007
    assert 'Lookup time:' in stdout, "Should show 'Lookup time: <N ms>'"  # $REQ_SUMRET_004
    assert 'This corpus contains various documents and directories for testing.' in stdout, "Should show corpus summary"  # $REQ_SUMRET_001

    print("✓ Corpus summary retrieved successfully")

    # $REQ_SUMRET_003: Retrieve directory summary
    print("\n$REQ_SUMRET_003: Testing directory summary retrieval...")
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize', str(cooking_dir))

    if exit_code != 0:
        print(f"Directory summary failed with exit code {exit_code}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    # $REQ_SUMRET_003, $REQ_SUMRET_004: Output format includes "Summary for:", "Lookup time:", and summary text
    assert 'Summary for:' in stdout, "Should show 'Summary for: <path>'"  # $REQ_SUMRET_003, $REQ_SUMRET_004
    assert 'cooking' in stdout.lower(), "Should include directory name in summary path"  # $REQ_SUMRET_003
    assert 'Lookup time:' in stdout, "Should show 'Lookup time: <N ms>'"  # $REQ_SUMRET_004
    assert 'This directory contains cooking-related documents and recipes.' in stdout, "Should show directory summary"  # $REQ_SUMRET_003

    print("✓ Directory summary retrieved successfully")

    # $REQ_SUMRET_002: Retrieve document summary by PDF path
    print("\n$REQ_SUMRET_002: Testing document summary retrieval...")
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize', str(pdf_path))

    if exit_code != 0:
        print(f"Document summary failed with exit code {exit_code}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    # $REQ_SUMRET_002, $REQ_SUMRET_004: Output format
    assert 'Summary for:' in stdout, "Should show 'Summary for: <path>'"  # $REQ_SUMRET_002, $REQ_SUMRET_004
    assert 'test.pdf' in stdout.lower(), "Should include PDF filename in summary path"  # $REQ_SUMRET_002
    assert 'Lookup time:' in stdout, "Should show 'Lookup time: <N ms>'"  # $REQ_SUMRET_004
    assert 'This is a test document summary about cooking recipes.' in stdout, "Should show document summary"  # $REQ_SUMRET_002

    print("✓ Document summary retrieved successfully")

    # $REQ_SUMRET_005: Path canonicalization - test with different path formats
    print("\n$REQ_SUMRET_005: Testing path canonicalization...")

    # Test with absolute path for directory
    abs_cooking = cooking_dir.resolve()
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize', str(abs_cooking))

    if exit_code != 0:
        print(f"Absolute path summary failed with exit code {exit_code}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    assert 'Lookup time:' in stdout, "Should find summary with absolute path"  # $REQ_SUMRET_005
    assert 'This directory contains cooking-related documents and recipes.' in stdout  # $REQ_SUMRET_005
    print("✓ Path canonicalization working (absolute directory path)")

    # Test with absolute path for document
    abs_pdf = pdf_path.resolve()
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize', str(abs_pdf))

    if exit_code != 0:
        print(f"Absolute PDF path summary failed with exit code {exit_code}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    assert 'Lookup time:' in stdout, "Should find summary with absolute PDF path"  # $REQ_SUMRET_005
    assert 'This is a test document summary about cooking recipes.' in stdout  # $REQ_SUMRET_005
    print("✓ Path canonicalization working (absolute document path)")

    # $REQ_SUMRET_006: Path not found error
    print("\n$REQ_SUMRET_006: Testing path not found error...")
    fake_path = Path('tmp/nonexistent/path')
    exit_code, stdout, stderr = run_demo('--db-file', str(db_file), '--summarize', str(fake_path))

    # Should exit with error
    assert exit_code != 0, "Should fail for nonexistent path"  # $REQ_SUMRET_006

    # Check error message (could be in stdout or stderr based on how help/error is printed)
    output = stdout + stderr
    assert 'Path not found in database:' in output, "Should show 'Path not found in database: <path>'"  # $REQ_SUMRET_006
    assert 'nonexistent' in output.lower(), "Should mention the nonexistent path"  # $REQ_SUMRET_006

    print("✓ Path not found error working correctly")

    print("\n✓ All summary retrieval tests passed!")

if __name__ == '__main__':
    main()
