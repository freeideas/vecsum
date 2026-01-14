// OpenAI API client for embeddings and summarization

using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

class OpenAIClient
{
    private readonly string _apiKey;
    private readonly HttpClient _http;

    public OpenAIClient(string apiKey)
    {
        _apiKey = apiKey;
        _http = new HttpClient();
        _http.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
    }

    // Generate embedding for text  // $REQ_LLM_004, $REQ_TREE_012
    public byte[] GetEmbedding(string text)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        const string model = "text-embedding-3-small";  // $REQ_LLM_004, $REQ_TREE_012

        var requestBody = new
        {
            model = model,
            input = text
        };

        var json = JsonConvert.SerializeObject(requestBody);

        // $REQ_LOG_004: Log request
        Logger.LogRequest("EMBED", model, json);

        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = _http.PostAsync("https://api.openai.com/v1/embeddings", content).Result;
        sw.Stop();

        // Handle API errors  // $REQ_LLM_002, $REQ_LLM_003
        if (!response.IsSuccessStatusCode)
        {
            // $REQ_LLM_002: Invalid API Key (401 Unauthorized)
            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                CommandLineParser.PrintHelpAndError("OPENAI_API_KEY is invalid or expired");
                Environment.Exit(1);
            }

            // $REQ_LLM_003: OpenAI API Error
            var errorBody = response.Content.ReadAsStringAsync().Result;
            CommandLineParser.PrintHelpAndError($"OpenAI API error: {response.StatusCode} - {errorBody}");
            Environment.Exit(1);
        }

        var responseBody = response.Content.ReadAsStringAsync().Result;
        var jsonResponse = JObject.Parse(responseBody);

        // Extract embedding array and convert to byte array  // $REQ_LLM_004, $REQ_LLM_008
        var embeddingArray = jsonResponse["data"]![0]!["embedding"]!.ToObject<float[]>()!;

        // $REQ_LOG_005: Log response
        var promptTokens = jsonResponse["usage"]?["prompt_tokens"]?.ToObject<int>() ?? 0;
        var totalTokens = jsonResponse["usage"]?["total_tokens"]?.ToObject<int>() ?? 0;
        var completionTokens = totalTokens - promptTokens;
        var embeddingSummary = $"Vector dimensions: {embeddingArray.Length}, First 5 values: [{string.Join(", ", embeddingArray.Take(5).Select(f => f.ToString("F6")))}]";
        Logger.LogResponse("EMBED", model, sw.Elapsed.TotalSeconds, promptTokens, completionTokens, embeddingSummary, responseBody);

        // Convert float[] to byte[] (1536 floats * 4 bytes = 6144 bytes)  // $REQ_LLM_008
        var bytes = new byte[embeddingArray.Length * 4];
        Buffer.BlockCopy(embeddingArray, 0, bytes, 0, bytes.Length);

        return bytes;
    }

    // Summarize text content  // $REQ_LLM_005, $REQ_LLM_006, $REQ_TREE_008, $REQ_TREE_013
    public string Summarize(List<string> contents)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        const string model = "gpt-4.1-mini";  // $REQ_LLM_005, $REQ_TREE_013
        var combinedContent = string.Join("\n\n", contents);

        var requestBody = new
        {
            model = model,
            messages = new[]
            {
                new { role = "user", content = $"Summarize the following content concisely, preserving key facts and main ideas:\n\n{combinedContent}" }  // $REQ_LLM_006, $REQ_TREE_008
            }
        };

        var json = JsonConvert.SerializeObject(requestBody);

        // $REQ_LOG_004: Log request
        Logger.LogRequest("SUMMARIZE", model, json);

        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = _http.PostAsync("https://api.openai.com/v1/chat/completions", content).Result;
        sw.Stop();

        // $REQ_LLM_003: OpenAI API Error
        if (!response.IsSuccessStatusCode)
        {
            var errorBody = response.Content.ReadAsStringAsync().Result;
            CommandLineParser.PrintHelpAndError($"OpenAI API error: {response.StatusCode} - {errorBody}");
            Environment.Exit(1);
        }

        var responseBody = response.Content.ReadAsStringAsync().Result;
        var jsonResponse = JObject.Parse(responseBody);

        var result = jsonResponse["choices"]![0]!["message"]!["content"]!.ToString();

        // $REQ_LOG_005: Log response
        var promptTokens = jsonResponse["usage"]?["prompt_tokens"]?.ToObject<int>() ?? 0;
        var completionTokens = jsonResponse["usage"]?["completion_tokens"]?.ToObject<int>() ?? 0;
        Logger.LogResponse("SUMMARIZE", model, sw.Elapsed.TotalSeconds, promptTokens, completionTokens, result, responseBody);

        return result;
    }

    // Check if adding content would change summary  // $REQ_LLM_007, $REQ_TREE_009, $REQ_TREE_013
    public bool WouldChangeSummary(string currentSummary, string nextContent)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        const string model = "gpt-4.1-mini";  // $REQ_LLM_005, $REQ_TREE_013

        var requestBody = new
        {
            model = model,
            messages = new[]
            {
                new { role = "user", content = $@"Current summary: {currentSummary}

Next content: {nextContent}

Would incorporating this content require significant changes to the summary? Does it introduce a new topic, subject, or major shift in focus?

Answer YES or NO." }  // $REQ_LLM_007, $REQ_TREE_009
            }
        };

        var json = JsonConvert.SerializeObject(requestBody);

        // $REQ_LOG_004: Log request
        Logger.LogRequest("BOUNDARY", model, json);

        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = _http.PostAsync("https://api.openai.com/v1/chat/completions", content).Result;
        sw.Stop();

        // $REQ_LLM_003: OpenAI API Error
        if (!response.IsSuccessStatusCode)
        {
            var errorBody = response.Content.ReadAsStringAsync().Result;
            CommandLineParser.PrintHelpAndError($"OpenAI API error: {response.StatusCode} - {errorBody}");
            Environment.Exit(1);
        }

        var responseBody = response.Content.ReadAsStringAsync().Result;
        var jsonResponse = JObject.Parse(responseBody);

        var answer = jsonResponse["choices"]![0]!["message"]!["content"]!.ToString().Trim().ToUpper();

        // $REQ_LOG_005: Log response
        var promptTokens = jsonResponse["usage"]?["prompt_tokens"]?.ToObject<int>() ?? 0;
        var completionTokens = jsonResponse["usage"]?["completion_tokens"]?.ToObject<int>() ?? 0;
        Logger.LogResponse("BOUNDARY", model, sw.Elapsed.TotalSeconds, promptTokens, completionTokens, answer, responseBody);

        return answer.Contains("YES");  // $REQ_LLM_007
    }
}
