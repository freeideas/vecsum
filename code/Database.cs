// $REQ_DB_001: Database management and queries

using Microsoft.Data.Sqlite;

class Database
{
    private readonly string _connectionString;

    public Database(string dbFile)
    {
        _connectionString = $"Data Source={dbFile};";
    }

    // $REQ_DB_002: Create new database with schema
    public static Database CreateDatabase(string dbFile)
    {
        var connStr = $"Data Source={dbFile};";

        using var conn = new SqliteConnection(connStr);
        conn.Open();

        using var cmd = conn.CreateCommand();

        // $REQ_DB_003: Create tables
        cmd.CommandText = @"
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER REFERENCES nodes(id),
                node_type TEXT NOT NULL,
                doc_path TEXT,
                dir_path TEXT,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL
            );

            CREATE TABLE directories (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE
            );

            CREATE TABLE documents (
                id INTEGER PRIMARY KEY,
                directory_id INTEGER REFERENCES directories(id),
                path TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL
            );
        ";
        cmd.ExecuteNonQuery();

        // $REQ_DB_004: Create indexes
        cmd.CommandText = @"
            CREATE INDEX idx_nodes_doc_path ON nodes(doc_path, node_type);
            CREATE INDEX idx_nodes_dir_path ON nodes(dir_path, node_type);
            CREATE INDEX idx_nodes_type ON nodes(node_type);
            CREATE INDEX idx_nodes_parent ON nodes(parent_id);
        ";
        cmd.ExecuteNonQuery();

        return new Database(dbFile);
    }

    // $REQ_DB_005: Insert a node and return its ID
    public long InsertNode(long? parentId, string nodeType, string? docPath, string? dirPath, string content, byte[] embedding)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT INTO nodes (parent_id, node_type, doc_path, dir_path, content, embedding)
            VALUES (@parent_id, @node_type, @doc_path, @dir_path, @content, @embedding);
            SELECT last_insert_rowid();
        ";

        cmd.Parameters.AddWithValue("@parent_id", parentId.HasValue ? parentId.Value : DBNull.Value);
        cmd.Parameters.AddWithValue("@node_type", nodeType);
        cmd.Parameters.AddWithValue("@doc_path", docPath ?? (object)DBNull.Value);
        cmd.Parameters.AddWithValue("@dir_path", dirPath ?? (object)DBNull.Value);
        cmd.Parameters.AddWithValue("@content", content);
        cmd.Parameters.AddWithValue("@embedding", embedding);

        // $REQ_CLI_014: Print progress indicator
        Console.Write(".");

        return (long)cmd.ExecuteScalar()!;
    }

    // Update a node's parent_id
    public void UpdateNodeParent(long nodeId, long parentId)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = "UPDATE nodes SET parent_id = @parent_id WHERE id = @node_id";
        cmd.Parameters.AddWithValue("@parent_id", parentId);
        cmd.Parameters.AddWithValue("@node_id", nodeId);

        cmd.ExecuteNonQuery();
    }

    // $REQ_DB_007: Insert a directory and return its ID
    public long InsertDirectory(string path)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT OR IGNORE INTO directories (path) VALUES (@path);
            SELECT id FROM directories WHERE path = @path;
        ";
        cmd.Parameters.AddWithValue("@path", path);

        return (long)cmd.ExecuteScalar()!;
    }

    // $REQ_DB_008: Insert a document
    public void InsertDocument(long directoryId, string path, string filename)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT OR IGNORE INTO documents (directory_id, path, filename)
            VALUES (@directory_id, @path, @filename);
        ";
        cmd.Parameters.AddWithValue("@directory_id", directoryId);
        cmd.Parameters.AddWithValue("@path", path);
        cmd.Parameters.AddWithValue("@filename", filename);

        cmd.ExecuteNonQuery();
    }

    // $REQ_CLI_008, $REQ_CLI_009: Get summary by path
    public string? GetSummary(string userPath)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        // $REQ_CLI_028, $REQ_SUMRET_001: Check if requesting corpus root
        if (userPath == "[corpus]")
        {
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT content FROM nodes WHERE node_type = 'root'";
            var result = cmd.ExecuteScalar();
            return result?.ToString();
        }

        // $REQ_CLI_025, $REQ_SUMRET_005: Query paths must be canonicalized to match stored paths
        var canonicalPath = PathCanonicalizer.Canonicalize(userPath);

        // $REQ_DB_010, $REQ_SUMRET_002: Check if path is a document
        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = "SELECT 1 FROM documents WHERE path = @path";
            cmd.Parameters.AddWithValue("@path", canonicalPath);

            if (cmd.ExecuteScalar() != null)
            {
                // It's a document, get doc_top
                cmd.CommandText = "SELECT content FROM nodes WHERE doc_path = @path AND node_type = 'doc_top'";
                cmd.Parameters.Clear();
                cmd.Parameters.AddWithValue("@path", canonicalPath);

                var result = cmd.ExecuteScalar();
                return result?.ToString();
            }
        }

        // $REQ_DB_011, $REQ_SUMRET_003: Check if path is a directory
        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = "SELECT 1 FROM directories WHERE path = @path";
            cmd.Parameters.AddWithValue("@path", canonicalPath);

            if (cmd.ExecuteScalar() != null)
            {
                // It's a directory, get dir_top
                cmd.CommandText = "SELECT content FROM nodes WHERE dir_path = @path AND node_type = 'dir_top'";
                cmd.Parameters.Clear();
                cmd.Parameters.AddWithValue("@path", canonicalPath);

                var result = cmd.ExecuteScalar();
                return result?.ToString();
            }
        }

        return null;
    }

    // $REQ_DB_012: Get all doc_top nodes for a directory
    public List<(long id, string content)> GetDocTopsForDirectory(string dirPath)
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT id, content FROM nodes
            WHERE doc_path IN (
                SELECT path FROM documents WHERE directory_id = (
                    SELECT id FROM directories WHERE path = @dir_path
                )
            ) AND node_type = 'doc_top'
        ";
        cmd.Parameters.AddWithValue("@dir_path", dirPath);

        var results = new List<(long, string)>();
        using var reader = cmd.ExecuteReader();
        while (reader.Read())
        {
            results.Add((reader.GetInt64(0), reader.GetString(1)));
        }

        return results;
    }

    // $REQ_DB_013: Get all dir_top nodes
    public List<(long id, string content)> GetAllDirTops()
    {
        using var conn = new SqliteConnection(_connectionString);
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT id, content FROM nodes WHERE node_type = 'dir_top'";

        var results = new List<(long, string)>();
        using var reader = cmd.ExecuteReader();
        while (reader.Read())
        {
            results.Add((reader.GetInt64(0), reader.GetString(1)));
        }

        return results;
    }
}
