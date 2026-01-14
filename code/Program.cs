// Main entry point for command-line interface
using System.Diagnostics;
using System.Reflection;

class Program
{
    static void Main(string[] args)
    {
        // $REQ_CLI_026: Initialize SQLite for standalone executable
        // Use winsqlite3 provider (Windows built-in SQLite)
        SQLitePCL.raw.SetProvider(new SQLitePCL.SQLite3Provider_winsqlite3());

        // Initialize iText DI container for single-file executable
        InitializeiTextDI();

        // $REQ_CLI_002: Parse command-line arguments
        var options = CommandLineParser.Parse(args);

        // $REQ_CLI_031, $REQ_CLI_032, $REQ_CLI_033, $REQ_LOG_002: Initialize logger
        Logger.Initialize(options.LogDir);

        // $REQ_CLI_002, $REQ_CLI_003: Check if database file exists
        bool dbExists = File.Exists(options.DbFile);

        long buildTimeMs = 0;
        OpenAIClient? openAI = null;

        if (!dbExists)
        {
            // $REQ_ERR_002: Validate OPENAI_API_KEY environment variable first
            var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
            if (string.IsNullOrEmpty(apiKey))
            {
                CommandLineParser.PrintHelpAndError("OPENAI_API_KEY environment variable is not set");
                Environment.Exit(1);
            }

            // $REQ_CLI_028, $REQ_ERR_005: Error if no --pdf-dir when creating database
            if (options.PdfDirs.Count == 0)
            {
                CommandLineParser.PrintHelpAndError("--pdf-dir is required when creating a new database");
                Environment.Exit(1);
            }

            // $REQ_CLI_021, $REQ_CLI_022: Validate PDF directories
            for (int i = 0; i < options.PdfDirs.Count; i++)
            {
                var dirPath = options.PdfDirs[i];
                var originalPath = options.PdfDirsOriginal[i];

                // $REQ_ERR_008: Directory Does Not Exist - use original path in error
                if (!Directory.Exists(dirPath))
                {
                    CommandLineParser.PrintHelpAndError($"Directory does not exist: {originalPath}");
                    Environment.Exit(1);
                }

                // $REQ_ERR_009: No PDFs in Directory (check recursively) - use original path in error
                var pdfFiles = Directory.GetFiles(dirPath, "*.pdf", SearchOption.AllDirectories);
                if (pdfFiles.Length == 0)
                {
                    CommandLineParser.PrintHelpAndError($"No PDF files found in: {originalPath}");
                    Environment.Exit(1);
                }
            }

            openAI = new OpenAIClient(apiKey);

            // $REQ_CLI_002: Create new database and build tree
            var sw = Stopwatch.StartNew();
            BuildTree(options.DbFile, options.PdfDirs, openAI);  // $REQ_CLI_007, $REQ_CLI_014, $REQ_CLI_015
            sw.Stop();
            buildTimeMs = sw.ElapsedMilliseconds;
            Console.WriteLine();
            Console.WriteLine($"Build time: {buildTimeMs} ms");  // $REQ_CLI_011, $REQ_TIMING_001
        }
        else
        {
            // $REQ_CLI_003: Use existing database, $REQ_CLI_005: ignore pdf-dirs
            // $REQ_CLI_029: Error if no --summarize when using existing database
            if (options.SummarizePath == null)
            {
                CommandLineParser.PrintHelpAndError("--summarize is required when using existing database");
                Environment.Exit(1);
            }
        }

        // $REQ_CLI_008, $REQ_CLI_009: Handle --summarize option
        // $REQ_SUMRET_001, $REQ_SUMRET_002, $REQ_SUMRET_003: Retrieve summaries
        if (options.SummarizePath != null)
        {
            var db = new Database(options.DbFile);
            var sw = Stopwatch.StartNew();
            var summary = db.GetSummary(options.SummarizePath);  // $REQ_SUMRET_005: Path canonicalization in GetSummary
            sw.Stop();

            // $REQ_ERR_005, $REQ_SUMRET_006: Summarize Path Not Found
            if (summary == null)
            {
                CommandLineParser.PrintHelpAndError($"Path not found in database: {options.SummarizePathOriginal}");
                Environment.Exit(1);
            }

            Console.WriteLine();
            Console.WriteLine($"Summary for: {options.SummarizePath}");  // $REQ_CLI_013, $REQ_SUMRET_004, $REQ_SUMRET_007
            if (buildTimeMs > 0)
            {
                Console.WriteLine($"Build time: {buildTimeMs} ms");  // $REQ_CLI_011, $REQ_CLI_015, $REQ_TIMING_003
            }
            Console.WriteLine($"Lookup time: {sw.ElapsedMilliseconds} ms");  // $REQ_CLI_012, $REQ_CLI_013, $REQ_TIMING_002, $REQ_TIMING_004, $REQ_SUMRET_004
            Console.WriteLine();
            Console.WriteLine(summary);  // $REQ_CLI_013, $REQ_SUMRET_004
        }
    }

    static void InitializeiTextDI()
    {
        try
        {
            // Create a new DI container
            var container = new iText.Commons.Utils.DIContainer();
            
            // Use reflection to set the static instance field
            var containerType = typeof(iText.Commons.Utils.DIContainer);
            var instanceField = containerType.GetField("instance", 
                BindingFlags.Static | BindingFlags.NonPublic);
            
            if (instanceField != null)
            {
                instanceField.SetValue(null, container);
            }
        }
        catch
        {
            // If reflection fails, try to continue anyway
            // iText might have already initialized
        }
    }

    // $REQ_BUILD_001: Build the summary tree from PDF directories
    static void BuildTree(string dbFile, List<string> pdfDirs, OpenAIClient openAI)
    {
        var db = Database.CreateDatabase(dbFile);
        var treeBuilder = new TreeBuilder(db, openAI);

        // $REQ_BUILD_002: Process each PDF directory
        foreach (var dirPath in pdfDirs)
        {
            treeBuilder.ProcessDirectory(dirPath);
        }

        // $REQ_BUILD_003: Build corpus root
        treeBuilder.BuildCorpusRoot();
    }
}
