# API Logging

## Overview

Optional logging of OpenAI API requests and responses for debugging and analysis.

## Command-Line

```
vecsum.exe --db-file <path> --pdf-dir <path> [--log-dir <path>]
```

### --log-dir (optional)

Path to a directory for API log files.

- If not specified, no logging occurs
- Directory is created if it does not exist
- Each API call writes two files: a request file and a response file

## Log File Format

### Filename Convention

```
{timestamp}_{operation}_{REQUEST|RESPONSE}.md
```

- **timestamp**: `YYYY-MM-DD-HH-MM-SS-mmm` (millisecond precision, local time)
- **operation**: Type of API call (see below)
- **REQUEST/RESPONSE**: Indicates which half of the exchange

### Operations

| Operation | Description                                  |
| --------- | -------------------------------------------- |
| EMBED     | Embedding generation call to embedding model |
| SUMMARIZE | Content summarization call to LLM            |
| BOUNDARY  | Topic boundary detection call to LLM         |

### Example Filenames

```
2025-12-14-23-03-16-461_SUMMARIZE_REQUEST.md
2025-12-14-23-03-16-461_SUMMARIZE_RESPONSE.md
2025-12-14-23-03-17-892_BOUNDARY_REQUEST.md
2025-12-14-23-03-17-892_BOUNDARY_RESPONSE.md
2025-12-14-23-03-18-104_EMBED_REQUEST.md
2025-12-14-23-03-18-104_EMBED_RESPONSE.md
```

### Request File Content

```markdown
# {Operation} [REQUEST]
**Timestamp:** {timestamp}
**Model:** {model name}

---

## Messages

{JSON array of messages sent to the API}
```

### Response File Content

```markdown
# {Operation} [RESPONSE]
**Timestamp:** {timestamp}
**Model:** {model name}
**Elapsed:** {N.NNN} seconds
**Tokens:** {prompt tokens} prompt, {completion tokens} completion

---

## Content

{response text or embedding summary}

---

## Raw JSON

```json
{full API response}
```
```

## Notes

- Directory is created if it does not yet exist
- Log files can grow large during full corpus builds
- Embedding responses log vector dimensions and first few values, not full 1536-float arrays
