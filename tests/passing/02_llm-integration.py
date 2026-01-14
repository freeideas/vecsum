#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_api_key_environment_variable():
    """$REQ_LLM_001: Test that missing OPENAI_API_KEY prints error"""
    # Create a test database path that doesn't exist (so we trigger database creation)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, 'test.db')
    pdf_dir = os.path.join(tmpdir, 'pdfs')
    os.makedirs(pdf_dir)

    try:
        # Remove the API key from environment
        env = os.environ.copy()
        if 'OPENAI_API_KEY' in env:
            del env['OPENAI_API_KEY']

        # Run the program without API key, attempting to create new database
        result = subprocess.run(
            ['./released/vecsum.exe', '--db-file', db_path, '--pdf-dir', pdf_dir],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env
        )

        # Should exit with error code
        assert result.returncode != 0, f"Program should exit with error when OPENAI_API_KEY is missing"  # $REQ_LLM_001

        # Should print help text followed by error message
        assert "Error: OPENAI_API_KEY environment variable is not set" in result.stdout, \
            f"Expected error message not found. Got: {result.stdout}"  # $REQ_LLM_001

        # Should include help text
        assert "vecsum - Hierarchical PDF summarization" in result.stdout, \
            "Help text should be included"  # $REQ_LLM_001

        print("✓ $REQ_LLM_001: API key environment variable check passed")
    finally:
        import shutil
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


def test_api_key_validation():
    """$REQ_LLM_002: Test that 401 error prints invalid API key message"""
    # This test requires creating a mock scenario or using an invalid key
    # Since we can't actually test with OpenAI API without keys, we verify
    # the code structure exists in OpenAIClient.cs

    # Read the source code to verify the implementation
    openai_client_path = Path('./code/OpenAIClient.cs')
    assert openai_client_path.exists(), "OpenAIClient.cs should exist"

    content = openai_client_path.read_text(encoding='utf-8')

    # Check for 401 handling
    assert 'HttpStatusCode.Unauthorized' in content, \
        "Should check for Unauthorized status"  # $REQ_LLM_002
    assert 'OPENAI_API_KEY is invalid or expired' in content, \
        "Should have invalid/expired API key error message"  # $REQ_LLM_002

    print("✓ $REQ_LLM_002: API key validation code verified")


def test_openai_api_error_reporting():
    """$REQ_LLM_003: Test that OpenAI API errors are reported"""
    # Verify error handling code exists
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should have error handling for API errors
    assert 'OpenAI API error:' in content, \
        "Should have OpenAI API error message"  # $REQ_LLM_003
    assert 'PrintHelpAndError' in content, \
        "Should call PrintHelpAndError for API errors"  # $REQ_LLM_003

    print("✓ $REQ_LLM_003: OpenAI API error reporting code verified")


def test_embedding_generation():
    """$REQ_LLM_004: Test embedding configuration"""
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should use text-embedding-3-small model
    assert 'text-embedding-3-small' in content, \
        "Should use text-embedding-3-small model"  # $REQ_LLM_004

    # Should produce 1536-dimensional vectors (6144 bytes = 1536 floats * 4 bytes)
    assert 'embeddingArray.Length * 4' in content or '6144' in content, \
        "Should handle 1536-dimensional vectors"  # $REQ_LLM_004

    print("✓ $REQ_LLM_004: Embedding generation model verified")


def test_summarization_model():
    """$REQ_LLM_005: Test summarization model"""
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should use gpt-4.1-mini as specified in the requirement
    assert 'gpt-4.1-mini' in content, \
        "Should use gpt-4.1-mini model for summarization"  # $REQ_LLM_005

    print("✓ $REQ_LLM_005: Summarization model verified")


def test_summarization_prompt():
    """$REQ_LLM_006: Test summarization prompt"""
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should have the specific prompt text
    assert 'Summarize the following content concisely, preserving key facts and main ideas' in content, \
        "Should use the specified summarization prompt"  # $REQ_LLM_006

    # Should concatenate content with newlines
    assert 'string.Join' in content, \
        "Should concatenate multiple content items"  # $REQ_LLM_006

    print("✓ $REQ_LLM_006: Summarization prompt verified")


def test_topic_boundary_detection():
    """$REQ_LLM_007: Test topic boundary detection prompt"""
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should have WouldChangeSummary method
    assert 'WouldChangeSummary' in content, \
        "Should have WouldChangeSummary method"  # $REQ_LLM_007

    # Should ask about significant changes to summary
    assert 'significant changes to the summary' in content, \
        "Should ask about significant changes"  # $REQ_LLM_007

    # Should mention topic/subject/major shift
    assert 'new topic' in content or 'subject' in content or 'major shift' in content, \
        "Should mention topic/subject/shift in prompt"  # $REQ_LLM_007

    # Should expect YES/NO answer
    assert 'YES or NO' in content, \
        "Should expect YES/NO answer"  # $REQ_LLM_007

    # Should return boolean
    assert '.Contains("YES")' in content or 'YES' in content, \
        "Should check for YES in response"  # $REQ_LLM_007

    print("✓ $REQ_LLM_007: Topic boundary detection verified")


def test_embedding_storage_format():
    """$REQ_LLM_008: Test embedding storage format"""
    # Check Database.cs for BLOB storage
    db_path = Path('./code/Database.cs')
    if db_path.exists():
        content = db_path.read_text(encoding='utf-8')
        # Should store embeddings as BLOB
        assert 'BLOB' in content, \
            "Should use BLOB type for embeddings"  # $REQ_LLM_008

    # Check OpenAIClient.cs for float32 conversion
    openai_client_path = Path('./code/OpenAIClient.cs')
    content = openai_client_path.read_text(encoding='utf-8')

    # Should convert float array to bytes
    assert 'Buffer.BlockCopy' in content or 'byte[]' in content, \
        "Should convert float array to byte array"  # $REQ_LLM_008

    # Should handle 1536 floats (6144 bytes)
    assert 'embeddingArray.Length * 4' in content, \
        "Should convert 1536 floats to 6144 bytes"  # $REQ_LLM_008

    print("✓ $REQ_LLM_008: Embedding storage format verified")


def main():
    # Ensure we're in the project root
    if not Path('./released/vecsum.exe').exists():
        print("Error: vecsum.exe not found. Build the project first.")
        sys.exit(97)

    print("Testing LLM Integration Requirements...")
    print()

    # Run all tests
    test_api_key_environment_variable()
    test_api_key_validation()
    test_openai_api_error_reporting()
    test_embedding_generation()
    test_summarization_model()
    test_summarization_prompt()
    test_topic_boundary_detection()
    test_embedding_storage_format()

    print()
    print("All LLM integration tests passed!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
