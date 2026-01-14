# Summary Tree Building

Documents the bottom-up algorithm for building the hierarchical summary tree from chunks to document tops to directory tops to corpus root.

## $REQ_TREE_001: Chunk Creation from PDFs
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 1: Document Chunking (Level 0)")

For each PDF file, text must be extracted and split into chunks of 1000 characters with 100 character overlap. Each chunk must have an embedding generated and be stored as a node with `node_type = 'chunk'` and `doc_path` set to the PDF path.

## $REQ_TREE_002: Adaptive Boundary Detection Algorithm
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Core Algorithm: Adaptive Boundary Detection")

The tree building algorithm must start with two items and create an initial summary, then attempt to extend by adding additional items. Before adding each item, the system must ask the LLM whether incorporating the content would require significant changes to the summary (topic boundary detection). If yes, a new summary group starts.

## $REQ_TREE_003: Lone Item Promotion
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Core Algorithm: Adaptive Boundary Detection")

When only one item remains at the end of a level during tree building, that lone item must be promoted without summarization.

## $REQ_TREE_004: Single Item Level Handling
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Core Algorithm: Adaptive Boundary Detection")

When `buildLevel` receives exactly one item, it must return that item directly (promoted as the top).

## $REQ_TREE_005: Document Tree Building
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 2: Build Document Trees")

For each document, the core algorithm must be applied to its chunks, recursing until one node remains. That final node must be marked as `node_type = 'doc_top'`.

## $REQ_TREE_006: Directory Tree Building
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 3: Build Directory Trees")

After all documents in a directory have their doc_top nodes, the core algorithm must be applied to those doc_tops. The final node must be marked as `node_type = 'dir_top'` with `dir_path` set to the directory path.

## $REQ_TREE_007: Corpus Root Building
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Step 4: Build Corpus Root")

After all directories have their dir_top nodes, the core algorithm must be applied to those dir_tops. The final node must be marked as `node_type = 'root'`.

## $REQ_TREE_008: Summarization Prompt
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Summarization Prompt")

When summarizing items, the LLM must be prompted to summarize the concatenated content concisely, preserving key facts and main ideas.

## $REQ_TREE_009: Topic Boundary Detection Prompt
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "The 'Would This Change the Summary?' Check")

The topic boundary detection must prompt the LLM with the current summary and next content, asking whether incorporating the content would require significant changes or introduce a new topic/subject/major shift in focus, expecting a YES or NO answer.

## $REQ_TREE_010: Unbalanced Tree Structure
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Tree Structure (Unbalanced)")

The resulting tree must be unbalanced -- simple documents (uniform topic) produce shallow branches while complex documents (many topic shifts) produce deeper branches.

## $REQ_TREE_011: Summary Nodes Link to Covered Items
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Core Algorithm: Adaptive Boundary Detection")

Each summary node must store links to the items it covers.

## $REQ_TREE_012: Default Embedding Model
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

The default embedding model must be text-embedding-3-small producing 1536-dimension vectors.

## $REQ_TREE_013: Default Summary Model
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

The default summarization and boundary detection model must be gpt-4.1-mini.

## $REQ_TREE_014: Default Chunk Size
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

The default chunk size must be 1000 characters.

## $REQ_TREE_015: Default Chunk Overlap
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

The default chunk overlap must be 100 characters.
