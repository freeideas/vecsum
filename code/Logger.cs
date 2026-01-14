// $REQ_LOG_001: API request/response logging
using System.Text;

static class Logger
{
    private static string? _logDir;

    // $REQ_LOG_002: Initialize logger with log directory
    public static void Initialize(string? logDir)
    {
        _logDir = logDir;

        // $REQ_LOG_003, $REQ_CLI_032: Create log directory if it doesn't exist
        if (_logDir != null && !Directory.Exists(_logDir))
        {
            Directory.CreateDirectory(_logDir);
        }
    }

    // $REQ_LOG_004: Log API request
    public static void LogRequest(string operation, string model, string requestBody)
    {
        if (_logDir == null) return;  // $REQ_CLI_031, $REQ_CLI_033

        var timestamp = GetTimestamp();
        var filename = $"{timestamp}_{operation}_REQUEST.md";
        var path = Path.Combine(_logDir, filename);

        var content = new StringBuilder();
        content.AppendLine($"# {operation} [REQUEST]");
        content.AppendLine($"**Timestamp:** {timestamp}");
        content.AppendLine($"**Model:** {model}");
        content.AppendLine();
        content.AppendLine("---");
        content.AppendLine();
        content.AppendLine("## Messages");
        content.AppendLine();
        content.AppendLine(requestBody);

        File.WriteAllText(path, content.ToString());
    }

    // $REQ_LOG_005: Log API response
    public static void LogResponse(string operation, string model, double elapsedSeconds, int promptTokens, int completionTokens, string responseContent, string rawJson)
    {
        if (_logDir == null) return;  // $REQ_CLI_031, $REQ_CLI_033

        var timestamp = GetTimestamp();
        var filename = $"{timestamp}_{operation}_RESPONSE.md";
        var path = Path.Combine(_logDir, filename);

        var content = new StringBuilder();
        content.AppendLine($"# {operation} [RESPONSE]");
        content.AppendLine($"**Timestamp:** {timestamp}");
        content.AppendLine($"**Model:** {model}");
        content.AppendLine($"**Elapsed:** {elapsedSeconds:F3} seconds");
        content.AppendLine($"**Tokens:** {promptTokens} prompt, {completionTokens} completion");
        content.AppendLine();
        content.AppendLine("---");
        content.AppendLine();
        content.AppendLine("## Content");
        content.AppendLine();
        content.AppendLine(responseContent);
        content.AppendLine();
        content.AppendLine("---");
        content.AppendLine();
        content.AppendLine("## Raw JSON");
        content.AppendLine();
        content.AppendLine("```json");
        content.AppendLine(rawJson);
        content.AppendLine("```");

        File.WriteAllText(path, content.ToString());
    }

    // $REQ_LOG_006: Get timestamp in format YYYY-MM-DD-HH-MM-SS-mmm
    private static string GetTimestamp()
    {
        var now = DateTime.Now;
        return $"{now:yyyy-MM-dd-HH-mm-ss-fff}";
    }
}
