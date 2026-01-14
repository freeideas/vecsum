// $REQ_TREE_001: Build hierarchical summary tree

class TreeNode
{
    public long Id { get; set; }
    public string Content { get; set; } = "";
}

class TreeBuilder
{
    private readonly Database _db;
    private readonly OpenAIClient _openAI;

    public TreeBuilder(Database db, OpenAIClient openAI)
    {
        _db = db;
        _openAI = openAI;
    }

    // Update a node's parent_id to link it to its summary
    void UpdateNodeParent(long nodeId, long parentId)
    {
        _db.UpdateNodeParent(nodeId, parentId);
    }

    // $REQ_TREE_002: Process a directory of PDF files
    public void ProcessDirectory(string dirPath)
    {
        // $REQ_PATHCANON_005: Paths during ingestion must be canonicalized before storage
        var canonicalDirPath = PathCanonicalizer.Canonicalize(dirPath);
        var directoryId = _db.InsertDirectory(canonicalDirPath);

        // $REQ_CLI_029: Get all PDF files in directory (recursive)
        var pdfFiles = Directory.GetFiles(dirPath, "*.pdf", SearchOption.AllDirectories);

        foreach (var pdfFile in pdfFiles)
        {
            ProcessDocument(pdfFile, directoryId, canonicalDirPath);
        }

        // $REQ_TREE_004: Build directory summary from doc_tops
        BuildDirectorySummary(canonicalDirPath);
    }

    // $REQ_TREE_005: Process a single PDF document
    void ProcessDocument(string pdfPath, long directoryId, string dirPath)
    {
        // $REQ_PATHCANON_005: Paths during ingestion must be canonicalized before storage
        var canonicalPath = PathCanonicalizer.Canonicalize(pdfPath);
        var filename = Path.GetFileName(pdfPath);

        _db.InsertDocument(directoryId, canonicalPath, filename);

        // $REQ_TREE_001, $REQ_TREE_006: Extract text and create chunks
        var text = PDFExtractor.ExtractText(pdfPath);
        var chunks = PDFExtractor.ChunkText(text);

        // $REQ_TREE_001, $REQ_TREE_007: Create chunk nodes
        var chunkNodes = new List<TreeNode>();
        foreach (var chunk in chunks)
        {
            var embedding = _openAI.GetEmbedding(chunk);
            var id = _db.InsertNode(null, "chunk", canonicalPath, null, chunk, embedding);
            chunkNodes.Add(new TreeNode { Id = id, Content = chunk });
        }

        // $REQ_TREE_005, $REQ_TREE_008: Build document tree from chunks
        BuildLevel(chunkNodes, canonicalPath, null, "doc_top");
    }

    // $REQ_TREE_002, $REQ_TREE_010: Build a single level of the tree using adaptive boundary detection
    TreeNode BuildLevel(List<TreeNode> items, string? docPath, string? dirPath, string finalNodeType = "summary")
    {
        // $REQ_TREE_011: Base case - single item
        if (items.Count == 0)
        {
            throw new InvalidOperationException("Cannot build level from empty list");
        }

        // $REQ_TREE_004: Single item level handling
        if (items.Count == 1)
        {
            // If this is the final node and needs special type, create it
            if (finalNodeType != "summary")
            {
                var embedding = _openAI.GetEmbedding(items[0].Content);
                var id = _db.InsertNode(null, finalNodeType, docPath, dirPath, items[0].Content, embedding);
                return new TreeNode { Id = id, Content = items[0].Content };
            }
            return items[0];
        }

        var results = new List<TreeNode>();
        int i = 0;

        while (i < items.Count)
        {
            // $REQ_TREE_003, $REQ_TREE_012: Edge case - lone item at end (promotion without summarization)
            if (i == items.Count - 1)
            {
                results.Add(items[i]);
                break;
            }

            // $REQ_TREE_002, $REQ_TREE_013: Start with two items
            var covered = new List<TreeNode> { items[i], items[i + 1] };
            i += 2;

            // $REQ_TREE_002, $REQ_TREE_014: Create initial summary
            var summaryText = _openAI.Summarize(covered.Select(n => n.Content).ToList());

            // $REQ_TREE_002, $REQ_TREE_015: Try to extend the summary with boundary detection
            while (i < items.Count)
            {
                if (_openAI.WouldChangeSummary(summaryText, items[i].Content))
                {
                    break; // Topic boundary detected
                }
                covered.Add(items[i]);
                i++;
            }

            // If we added more items, regenerate summary
            if (covered.Count > 2)
            {
                summaryText = _openAI.Summarize(covered.Select(n => n.Content).ToList());
            }

            // $REQ_TREE_011: Create summary node with parent links
            var embedding = _openAI.GetEmbedding(summaryText);
            var summaryId = _db.InsertNode(null, "summary", docPath, dirPath, summaryText, embedding);

            // Store parent_id references to link summary to covered items
            foreach (var coveredNode in covered)
            {
                UpdateNodeParent(coveredNode.Id, summaryId);
            }

            results.Add(new TreeNode { Id = summaryId, Content = summaryText });
        }

        // Recurse until one node remains
        if (results.Count == 1 && finalNodeType != "summary")
        {
            // This is the final result, create it with the proper type
            var embedding = _openAI.GetEmbedding(results[0].Content);
            var id = _db.InsertNode(null, finalNodeType, docPath, dirPath, results[0].Content, embedding);
            return new TreeNode { Id = id, Content = results[0].Content };
        }
        return BuildLevel(results, docPath, dirPath, finalNodeType);
    }

    // $REQ_TREE_006: Build directory summary from doc_tops
    void BuildDirectorySummary(string dirPath)
    {
        var docTops = _db.GetDocTopsForDirectory(dirPath);

        if (docTops.Count == 0)
            return;

        var nodes = docTops.Select(dt => new TreeNode { Id = dt.id, Content = dt.content }).ToList();
        BuildLevel(nodes, null, dirPath, "dir_top");
    }

    // $REQ_TREE_007: Build corpus root from all dir_tops
    public void BuildCorpusRoot()
    {
        var dirTops = _db.GetAllDirTops();

        if (dirTops.Count == 0)
            return;

        var nodes = dirTops.Select(dt => new TreeNode { Id = dt.id, Content = dt.content }).ToList();
        BuildLevel(nodes, null, null, "root");
    }
}
