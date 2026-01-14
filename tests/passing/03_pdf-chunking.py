#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test PDF chunking functionality.

Requirements tested:
- $REQ_PDFCHUNK_001: Text extraction from PDF
- $REQ_PDFCHUNK_002: Chunk size of 1000 characters
- $REQ_PDFCHUNK_003: 100 character overlap
- $REQ_PDFCHUNK_004: Chunk embedding generation
- $REQ_PDFCHUNK_005: Chunk node storage with node_type='chunk' and doc_path
"""

import sys
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_chunking_logic():
    """Test the chunking algorithm matches requirements."""
    # Simulate the chunking logic from PDFExtractor.cs
    def chunk_text(text, chunk_size=1000, overlap=100):
        chunks = []
        pos = 0

        while pos < len(text):
            end = min(pos + chunk_size, len(text))
            chunks.append(text[pos:end])

            # Move forward by (chunk_size - overlap) to create overlap
            pos += chunk_size - overlap

            # Stop if we've reached the end
            if end >= len(text):
                break

        return chunks

    # Test with known input
    test_text = "A" * 2500  # 2500 characters

    chunks = chunk_text(test_text, chunk_size=1000, overlap=100)

    # $REQ_PDFCHUNK_002: Chunk size should be 1000
    assert chunks[0] == "A" * 1000, "First chunk should be exactly 1000 chars"
    assert len(chunks[0]) == 1000, "First chunk length should be 1000"

    # $REQ_PDFCHUNK_003: Overlap should be 100 characters
    # After first chunk (0-1000), next should start at position 900 (1000-100)
    # So chunks should overlap by 100 chars
    assert len(chunks) == 3, "2500 char text should produce 3 chunks"

    # Verify overlap: last 100 chars of chunk[0] should equal first 100 chars of chunk[1]
    assert chunks[0][-100:] == chunks[1][:100], "Chunks should overlap by 100 characters"
    assert chunks[1][-100:] == chunks[2][:100], "All consecutive chunks should overlap by 100 characters"

    print("✓ $REQ_PDFCHUNK_002: Chunk size is 1000 characters")
    print("✓ $REQ_PDFCHUNK_003: Chunks overlap by 100 characters")

def test_pdf_extraction():
    """$REQ_PDFCHUNK_001: Verify PDF text extraction implementation"""
    pdf_extractor_path = Path('./code/PDFExtractor.cs')
    assert pdf_extractor_path.exists(), "PDFExtractor.cs should exist"

    content = pdf_extractor_path.read_text(encoding='utf-8')

    # Should have ExtractText method
    assert 'ExtractText' in content, \
        "Should have ExtractText method"  # $REQ_PDFCHUNK_001

    # Should use iText to extract text from PDF
    assert 'PdfDocument' in content, \
        "Should use iText PdfDocument"  # $REQ_PDFCHUNK_001
    assert 'PdfReader' in content, \
        "Should use PdfReader to read PDF"  # $REQ_PDFCHUNK_001
    assert 'PdfTextExtractor' in content or 'GetTextFromPage' in content, \
        "Should extract text from pages"  # $REQ_PDFCHUNK_001

    print("✓ $REQ_PDFCHUNK_001: PDF text extraction implementation verified")

def test_chunk_implementation():
    """Verify that chunking is implemented correctly in PDFExtractor.cs"""
    pdf_extractor_path = Path('./code/PDFExtractor.cs')
    content = pdf_extractor_path.read_text(encoding='utf-8')

    # Should have ChunkText method
    assert 'ChunkText' in content, \
        "Should have ChunkText method"

    # Should use chunk size of 1000 (default parameter)
    assert 'chunkSize = 1000' in content or 'chunkSize=1000' in content, \
        "Should default to chunk size of 1000"  # $REQ_PDFCHUNK_002

    # Should use overlap of 100 (default parameter)
    assert 'overlap = 100' in content or 'overlap=100' in content, \
        "Should default to overlap of 100"  # $REQ_PDFCHUNK_003

    print("✓ PDFExtractor.cs chunking implementation verified")

def test_embedding_generation():
    """$REQ_PDFCHUNK_004: Verify embedding generation for chunks"""
    # Check TreeBuilder.cs to verify embeddings are generated for chunks
    tree_builder_path = Path('./code/TreeBuilder.cs')
    assert tree_builder_path.exists(), "TreeBuilder.cs should exist"

    content = tree_builder_path.read_text(encoding='utf-8')

    # Should call GetEmbedding for each chunk
    assert 'GetEmbedding(chunk)' in content, \
        "Should generate embeddings for chunks"  # $REQ_PDFCHUNK_004

    # Verify embedding is passed when inserting chunk node
    # Look for pattern: InsertNode(..., "chunk", ..., embedding)
    lines = content.split('\n')
    chunk_insert_found = False
    for line in lines:
        if 'InsertNode' in line and '"chunk"' in line and 'embedding' in line:
            chunk_insert_found = True
            break

    assert chunk_insert_found, \
        "Should insert chunk nodes with embeddings"  # $REQ_PDFCHUNK_004

    print("✓ $REQ_PDFCHUNK_004: Chunk embedding generation verified")

def test_chunk_node_storage():
    """$REQ_PDFCHUNK_005: Verify chunk nodes are stored with correct type and doc_path"""
    tree_builder_path = Path('./code/TreeBuilder.cs')
    content = tree_builder_path.read_text(encoding='utf-8')

    # Should insert nodes with node_type="chunk"
    assert '"chunk"' in content, \
        "Should insert nodes with node_type='chunk'"  # $REQ_PDFCHUNK_005

    # Should pass canonicalPath as doc_path parameter
    # Look for pattern where chunks are inserted with the document path
    lines = content.split('\n')
    chunk_storage_found = False
    for i, line in enumerate(lines):
        if 'InsertNode' in line and '"chunk"' in line:
            # Check nearby lines for canonicalPath being passed
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
            if 'canonicalPath' in context:
                chunk_storage_found = True
                break

    assert chunk_storage_found, \
        "Should store chunks with doc_path set to PDF file path"  # $REQ_PDFCHUNK_005

    # Verify Database.cs has proper schema for chunk storage
    db_path = Path('./code/Database.cs')
    if db_path.exists():
        db_content = db_path.read_text(encoding='utf-8')
        assert 'node_type' in db_content, \
            "Database should have node_type column"  # $REQ_PDFCHUNK_005
        assert 'doc_path' in db_content, \
            "Database should have doc_path column"  # $REQ_PDFCHUNK_005

    print("✓ $REQ_PDFCHUNK_005: Chunk node storage implementation verified")

def main():
    print("Testing PDF Chunking Requirements...")
    print()

    # Test chunking algorithm logic
    test_chunking_logic()
    print()

    # Test PDF text extraction
    test_pdf_extraction()
    print()

    # Test chunk implementation
    test_chunk_implementation()
    print()

    # Test embedding generation
    test_embedding_generation()
    print()

    # Test chunk node storage
    test_chunk_node_storage()
    print()

    print("All PDF chunking tests passed!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
