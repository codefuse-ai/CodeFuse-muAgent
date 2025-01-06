
FUNCTION_CALL_PROMPT_en = """You have access to the following functions: 

{tool_desc}

To call a function, please respond with JSON for a function call.

Respond in the format [{"name": function name, "arguments": dictionary of argument name and its value}].
"""

FC_AUTO_PROMPT_en = """
The function can be called zero or multiple according to your needs.
"""


FC_REQUIRED_PROMPT_en = """
You must call a function as least.
"""

FC_PARALLEL_PROMPT_en = """
The function can be called in parallel.
"""


FC_RESPONSE_PROMPT_en = """## Response Ouput
Response the function calls by formatting the in JSON. The format should be:

```json
[
{
  "name": function name,
  "arguments": dictionary of argument name and its value
}
]
```
"""