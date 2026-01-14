// Parse command-line arguments

class CommandLineOptions
{
    public string DbFile { get; set; } = "";
    public List<string> PdfDirs { get; set; } = new();
    public List<string> PdfDirsOriginal { get; set; } = new();  // $REQ_ERR_008, $REQ_ERR_009: Store original paths for error messages
    public string? SummarizePath { get; set; }
    public string? SummarizePathOriginal { get; set; }  // $REQ_ERR_005: Store original user path for error messages
    public string? LogDir { get; set; }  // $REQ_CLI_027: Log directory for API logging
}

static class CommandLineParser
{
    // Parse arguments into CommandLineOptions
    public static CommandLineOptions Parse(string[] args)
    {
        var options = new CommandLineOptions();

        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--db-file":
                    if (i + 1 >= args.Length)
                    {
                        PrintHelpAndError("--db-file requires a path argument");
                        Environment.Exit(1);
                    }
                    // $REQ_CLI_025: Canonicalize db file path
                    options.DbFile = PathCanonicalizer.Canonicalize(args[++i]);
                    break;

                case "--pdf-dir":  // $REQ_CLI_004: Multiple --pdf-dir Arguments
                    if (i + 1 >= args.Length)
                    {
                        PrintHelpAndError("--pdf-dir requires a path argument");
                        Environment.Exit(1);
                    }
                    var dirPath = args[++i];

                    // $REQ_ERR_008, $REQ_ERR_009: Store original path for error messages
                    options.PdfDirsOriginal.Add(dirPath);
                    // $REQ_CLI_025: Canonicalize pdf-dir path before storing
                    // Note: Directory validation moved to Program.cs to ensure API key is checked first
                    options.PdfDirs.Add(PathCanonicalizer.Canonicalize(dirPath));
                    break;

                case "--summarize":
                    // $REQ_CLI_028: --summarize can have optional path argument
                    if (i + 1 < args.Length && !args[i + 1].StartsWith("--"))
                    {
                        // $REQ_ERR_005: Store original path for error messages
                        options.SummarizePathOriginal = args[++i];
                        // $REQ_CLI_025: Canonicalize summarize path
                        options.SummarizePath = PathCanonicalizer.Canonicalize(options.SummarizePathOriginal);
                    }
                    else
                    {
                        // $REQ_CLI_028, $REQ_SUMRET_001, $REQ_SUMRET_007: No path means corpus root
                        options.SummarizePath = "[corpus]";
                        options.SummarizePathOriginal = "[corpus]";
                    }
                    break;

                case "--log-dir":  // $REQ_CLI_027: Log directory argument
                    if (i + 1 >= args.Length)
                    {
                        PrintHelpAndError("--log-dir requires a path argument");
                        Environment.Exit(1);
                    }
                    options.LogDir = args[++i];
                    break;

                default:
                    // $REQ_CLI_023: Unknown Argument
                    PrintHelpAndError($"Unknown argument: {args[i]}");
                    Environment.Exit(1);
                    break;
            }
        }

        // $REQ_CLI_019: Missing Required Argument
        if (string.IsNullOrEmpty(options.DbFile))
        {
            PrintHelpAndError("--db-file is required");
            Environment.Exit(1);
        }

        return options;
    }

    // $REQ_CLI_016: Error Output Format
    // Print help text and error message
    public static void PrintHelpAndError(string errorMessage)
    {
        // Read help text from embedded resource
        var helpText = @"vecsum - Hierarchical PDF summarization using SQLite Vector

Usage:
  vecsum.exe --db-file <path> [--pdf-dir <path>]... [--summarize <path>]

Environment:
  OPENAI_API_KEY        OpenAI API key (required)

Arguments:
  --db-file <path>      SQLite database file (required)
                        Created if it doesn't exist

  --pdf-dir <path>      Directory containing PDFs to ingest
                        Can be specified multiple times
                        Only used when creating a new database

  --summarize <path>    Directory or PDF file to summarize
                        Prints the summary and exits

Examples:
  Build a new database:
    vecsum.exe --db-file ./data.db --pdf-dir ./reports --pdf-dir ./articles

  Get a directory summary:
    vecsum.exe --db-file ./data.db --summarize ./reports

  Get a document summary:
    vecsum.exe --db-file ./data.db --summarize ./reports/q1.pdf
";
        Console.WriteLine(helpText);
        Console.WriteLine();
        Console.WriteLine($"Error: {errorMessage}");
    }
}
