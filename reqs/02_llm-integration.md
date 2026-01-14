# LLM Integration

Documents the OpenAI API usage for summarization, topic boundary detection, and embedding generation.

## $REQ_LLM_001: API Key Environment Variable
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

The program requires the OPENAI_API_KEY environment variable to be set. If not set, the program prints help text followed by "Error: OPENAI_API_KEY environment variable is not set" and exits.

## $REQ_LLM_002: API Key Validation
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If the OpenAI API returns a 401 error, the program prints help text followed by "Error: OPENAI_API_KEY is invalid or expired" and exits.

## $REQ_LLM_003: OpenAI API Error Reporting
**Source:** ./specs/COMMAND-LINE.md (Section: "Error Handling")

If an OpenAI API error occurs during processing, the program prints help text followed by "Error: OpenAI API error: <message>" and exits.

## $REQ_LLM_004: Embedding Generation
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

Embeddings are generated using the text-embedding-3-small model, producing 1536-dimensional vectors.

## $REQ_LLM_005: Summarization Model
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Configuration")

Summarization and boundary detection use the gpt-4.1-mini model.

## $REQ_LLM_006: Summarization Prompt
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "Summarization Prompt")

When summarizing content, the LLM is prompted to "Summarize the following content concisely, preserving key facts and main ideas" with the concatenated content of all items being summarized.

## $REQ_LLM_007: Topic Boundary Detection
**Source:** ./specs/HOW-TO-BUILD-TREE.md (Section: "The 'Would This Change the Summary?' Check")

Topic boundary detection prompts the LLM with the current summary and next content, asking whether incorporating the content would require significant changes to the summary or introduce a new topic/subject/major shift in focus. The LLM responds YES or NO, where YES indicates a topic boundary.

## $REQ_LLM_008: Embedding Storage Format
**Source:** ./specs/DB-SCHEMA.md (Section: "Tables")

Embeddings are stored as BLOB data containing 1536 float32 values (6144 bytes) from text-embedding-3-small.
