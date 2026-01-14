# How to Build the Summary Tree

## Overview

The summary tree is built bottom-up: chunks -> document summaries -> directory summaries -> corpus root. The same algorithm applies at every level.

## Tree Structure (Unbalanced)

```
                      [corpus root]
                      /            \
              [dir A top]       [dir B top]
              /    |    \            |
        [doc1]  [doc2]  [doc3]    [doc4 top]
          |       |       |        /   |   \
         L1      L1      L1      L2   L2   L2
          |     / | \     |       |    |    |
         L0   L0 L0 L0   L0      L1   L1   L1
                                 /|\  /|\  /|\
                                L0s  L0s  L0s
```

- Simple documents (uniform topic) have shallow branches
- Complex documents (many topic shifts) have deeper branches
- The tree is unbalanced -- this is fine (see below)

## Core Algorithm: Adaptive Boundary Detection

The same function builds every level of the tree.

```
function buildLevel(items[]):
    if items.length == 0:
        return []
    if items.length == 1:
        return items  # already at top, promote directly

    results = []
    i = 0

    while i < items.length:
        # Edge case: only one item left at end of list
        if i == items.length - 1:
            # Lone item gets promoted without summarization
            results.append(items[i])
            break

        # Start with two items, create initial summary
        summary = summarize(items[i], items[i+1])
        covered = [items[i], items[i+1]]
        i = i + 2

        # Try to extend the summary
        while i < items.length:
            if wouldChangeSummary(summary, items[i]):
                break  # topic boundary detected
            covered.append(items[i])
            i = i + 1

        # Store summary node with links to covered items
        node = createNode(summary, parent_of=covered)
        results.append(node)

    # Recurse until one node remains
    return buildLevel(results)
```

## Step 1: Document Chunking (Level 0)

For each PDF file:

1. Extract text from PDF
2. Split into chunks of 1000 characters with 100 character overlap
3. Generate embedding for each chunk
4. Insert each chunk as a node with `node_type = 'chunk'` and `doc_path` set

## Step 2: Build Document Trees

For each document, apply the core algorithm to its chunks:

```
for each document:
    chunks = getChunks(document.path)
    top = buildLevel(chunks)
    # mark the final node as node_type = 'doc_top'
```

The `buildLevel` function recurses until one node remains. That node becomes the document's top.

### Summarization Prompt

```
function summarize(items[]):
    prompt = """
    Summarize the following content concisely, preserving key facts and main ideas:

    {concatenated content of all items}
    """
    return LLM(prompt)
```

### The "Would This Change the Summary?" Check

```
function wouldChangeSummary(currentSummary, nextItem):
    prompt = """
    Current summary: {currentSummary}

    Next content: {nextItem.content}

    Would incorporating this content require significant changes
    to the summary? Does it introduce a new topic, subject, or
    major shift in focus?

    Answer YES or NO.
    """
    return LLM(prompt) == "YES"
```

This detects natural topic boundaries rather than using fixed batch sizes.

## Step 3: Build Directory Trees

After all documents in a directory have their doc_top nodes:

```
for each directory:
    doc_tops = getDocTops(directory.path)
    top = buildLevel(doc_tops)
    # mark the final node as node_type = 'dir_top'
    # set dir_path = directory.path
```

## Step 4: Build Corpus Root

After all directories have their dir_top nodes:

```
dir_tops = getAllDirTops()
root = buildLevel(dir_tops)
# mark the final node as node_type = 'root'
```

## Why Unbalanced is Fine

1. **Every node has a top.** Query "summarize doc X" -> find node where `doc_path = X AND node_type = 'doc_top'`. Path length doesn't matter.

2. **Compression depth reflects complexity.** A document needing 5 levels is more complex than one needing 2. The structure encodes this information.

3. **LLM sees text, not structure.** When building a directory summary, the LLM sees document summaries as text. It doesn't know how many compression steps produced them.

## Configuration

| Parameter       | Default                  | Description                                           |
| --------------- | ------------------------ | ----------------------------------------------------- |
| chunk_size      | 1000                     | Characters per raw chunk (smaller = finer boundaries) |
| chunk_overlap   | 100                      | Overlap between chunks (in characters)                |
| embedding_model | text-embedding-3-small   | OpenAI model for vector embeddings (1536 dimensions)  |
| summary_model   | gpt-4.1-mini             | OpenAI model for summarization and boundary detection |
