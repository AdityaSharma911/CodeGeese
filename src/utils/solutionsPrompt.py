from src.model.problemDetails import CodeSnippet
from typing import List

def build_prompt(title: str, content: str, code_snippets: List[CodeSnippet]) -> str:
    code_context = "\n\n".join([
        f"---\nLanguage: {snip.lang}\n```{snip.lang}\n{snip.code}\n```"
        for snip in code_snippets
    ])

    return f"""\
You are an expert in classifying LeetCode problems by algorithmic patterns and topic tags.

### Problem Title:
{title}

### Problem Description:
{content}

### Code Snippets:
{code_context or "No code snippets available."}

---

### Your task:
1. Identify the high-level **algorithmic pattern** used (e.g., "binary search + prefix sum", "self join + aggregation").
2. Extract **concise** and **relevant** topic **tags** (e.g., "dfs", "greedy", "group by", "sql").

### Return Format:
```json
{{
  "pattern": "<algorithmic pattern>",
  "tags": ["tag1", "tag2", ...]
}}
"""
