// Canonicalize paths for consistent storage and querying

static class PathCanonicalizer
{
    // Convert path to canonical form
    public static string Canonicalize(string path)
    {
        // $REQ_PATHCANON_001: Resolve to absolute path
        string full = Path.GetFullPath(path);

        // $REQ_PATHCANON_002: Convert backslashes to forward slashes
        full = full.Replace('\\', '/');

        // $REQ_PATHCANON_003: Remove trailing slash (except for root like "C:/")
        if (full.Length > 3 && full.EndsWith('/'))
        {
            full = full.TrimEnd('/');
        }

        // $REQ_PATHCANON_004: Lowercase on Windows for case-insensitive matching
        if (OperatingSystem.IsWindows())
        {
            full = full.ToLowerInvariant();
        }

        return full;
    }
}
