import os, sys
from loguru import logger
import json

os.environ["do_create_dir"] = "1"

try:
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")


# test local code
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)


from muagent.schemas import Message, Memory
from muagent.prompt_manager import CommonPromptManager


system_prompt = """#### Agent Profile
As an agent specializing in software quality assurance, 
your mission is to craft comprehensive test cases that bolster the functionality, reliability, and robustness of a specified Code Snippet. 
This task is to be carried out with a keen understanding of the snippet's interactions with its dependent classes and methods—collectively referred to as Retrieval Code Snippets. 
Analyze the details given below to grasp the code's intended purpose, its inherent complexity, and the context within which it operates. 
Your constructed test cases must thoroughly examine the various factors influencing the code's quality and performance.

ATTENTION: response carefully referenced "Response Output Format" in format.

Each test case should include:
1. clear description of the test purpose.
2. The input values or conditions for the test.
3. The expected outcome or assertion for the test.
4. Appropriate tags (e.g., 'functional', 'integration', 'regression') that classify the type of test case.
5. these test code should have package and import

#### Input Format

**Code Snippet:** the initial Code or objective that the user wanted to achieve

**Retrieval Code Snippets:** These are the interrelated pieces of code sourced from the codebase, which support or influence the primary Code Snippet.

#### Response Output Format
**SaveFileName:** construct a local file name based on Question and Context, such as

```java
package/class.java
```

**Test Code:** generate the test code for the current Code Snippet.
```java
...
```

"""

intput_template = ""
output_template = ""
prompt = ""

agent_names = ["agent1", "agent2"]
agent_descs = [f"hello {agent}" for agent in agent_names]
tools = ["Multiplier", "WeatherInfo"]

bpm = CommonPromptManager(
    system_prompt=system_prompt,
    input_template=intput_template,
    output_template=output_template,
    prompt=prompt,
)

# 
message1 = Message(
    role_name="test",
    role_type="user",
    content="hello"
)
message2 = Message(
    role_name="test",
    role_type="assistant",
    content="hi! can i help you!"
)
query = Message(
    role_name="test",
    role_type="user",
    input_text="i want to know the weather of beijing",
    content="i want to know the weather of beijing",
    spec_parsed_content={
        "Retrieval Code Snippets": "hi"
    },
    global_kwargs={
        "Code Snippet": "hello",
        "Test Code": "nice to meet you."
    }
)
memory = Memory(messages=[message1, message2])

# prompt = bpm.pre_print(
#     query=query, memory=memory, tools=tools, 
#     agent_names=agent_names, agent_descs=agent_descs
# )
# print(prompt)

prompt = bpm.generate_prompt(
    query=query, memory=memory, tools=tools,
    agent_names=agent_names, agent_descs=agent_descs
)
print(prompt)