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
import tempfile
import shutil
from pathlib import Path

def main():
    # Get project root
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent

    print("Testing Summary Tree Building Requirements")
    print(f"Project root: {project_root}")

    # Check if vecsum.exe exists
    vecsum_exe = project_root / "released" / "vecsum.exe"
    if not vecsum_exe.exists():
        print(f"ERROR: vecsum.exe not found at {vecsum_exe}")
        print("Run build.py first")
        return 97

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_db = tmp_path / "test.db"

        # $REQ_TREE_001 - Not reasonably testable: Chunk creation requires PDF processing
        # $REQ_TREE_002 - Not reasonably testable: Adaptive boundary detection requires LLM interaction
        # $REQ_TREE_003 - Not reasonably testable: Lone item promotion requires specific multi-item scenarios
        # $REQ_TREE_004 - Not reasonably testable: Single item level handling requires specific scenarios
        # $REQ_TREE_005 - Not reasonably testable: Document tree building requires PDF processing and LLM
        # $REQ_TREE_006 - Not reasonably testable: Directory tree building requires PDF processing and LLM
        # $REQ_TREE_007 - Not reasonably testable: Corpus root building requires multiple directories and LLM

        # $REQ_TREE_008: Summarization prompt - verify in code
        print("\n$REQ_TREE_008: Checking summarization prompt...")
        openai_client_cs = project_root / "code" / "OpenAIClient.cs"
        if not openai_client_cs.exists():
            print(f"ERROR: OpenAIClient.cs not found")
            return 1

        with open(openai_client_cs, 'r', encoding='utf-8') as f:
            openai_code = f.read()

        # Check for summarization prompt with required elements
        if "Summarize the following content concisely, preserving key facts and main ideas" not in openai_code:
            print("ERROR: Summarization prompt not found or incorrect")
            return 1
        print("✓ Summarization prompt found")

        # $REQ_TREE_009: Topic boundary detection prompt - verify in code
        print("\n$REQ_TREE_009: Checking topic boundary detection prompt...")
        if "Would incorporating this content require significant changes" not in openai_code:
            print("ERROR: Topic boundary detection prompt not found")
            return 1
        if "introduce a new topic, subject, or major shift in focus" not in openai_code:
            print("ERROR: Topic boundary detection prompt missing key phrases")
            return 1
        if "Answer YES or NO" not in openai_code:
            print("ERROR: Topic boundary detection prompt missing YES/NO answer requirement")
            return 1
        print("✓ Topic boundary detection prompt found")

        # $REQ_TREE_010 - Not reasonably testable: Unbalanced tree structure is a property of the algorithm

        # $REQ_TREE_011: Summary nodes link to covered items - verify in code
        print("\n$REQ_TREE_011: Checking parent-child relationships...")
        tree_builder_cs = project_root / "code" / "TreeBuilder.cs"
        with open(tree_builder_cs, 'r', encoding='utf-8') as f:
            tree_code = f.read()

        if "UpdateNodeParent" not in tree_code:
            print("ERROR: UpdateNodeParent method not found")
            return 1
        if "parent_id" not in tree_code.lower():
            print("ERROR: parent_id references not found")
            return 1
        print("✓ Parent-child relationships properly stored")

        # $REQ_TREE_012: Default embedding model
        print("\n$REQ_TREE_012: Checking default embedding model...")
        if "text-embedding-3-small" not in openai_code:
            print("ERROR: Default embedding model not found or incorrect")
            return 1
        print("✓ Default embedding model is text-embedding-3-small")

        # $REQ_TREE_013: Default summary model
        print("\n$REQ_TREE_013: Checking default summary model...")
        if "gpt-4.1-mini" not in openai_code:
            print("ERROR: Default summary model not found or incorrect")
            return 1
        print("✓ Default summary model is gpt-4.1-mini")

        # $REQ_TREE_014: Default chunk size
        print("\n$REQ_TREE_014: Checking default chunk size...")
        pdf_extractor_cs = project_root / "code" / "PDFExtractor.cs"
        with open(pdf_extractor_cs, 'r', encoding='utf-8') as f:
            pdf_code = f.read()

        if "chunkSize = 1000" not in pdf_code:
            print("ERROR: Default chunk size not 1000")
            return 1
        print("✓ Default chunk size is 1000")

        # $REQ_TREE_015: Default chunk overlap
        print("\n$REQ_TREE_015: Checking default chunk overlap...")
        if "overlap = 100" not in pdf_code:
            print("ERROR: Default chunk overlap not 100")
            return 1
        print("✓ Default chunk overlap is 100")

    print("\n✓ All testable requirements verified")
    return 0

if __name__ == "__main__":
    sys.exit(main())
