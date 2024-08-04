from muagent.base_configs.prompts.simple_prompts import *


def replacePrompt(prompt: str, keys: list[str] = []):
    prompt = prompt.replace("{", "{{").replace("}", "}}")
    for key in keys:
        prompt = prompt.replace(f"{{{{{key}}}}}", f"{{{key}}}")
    return prompt

def cleanPrompt(prompt):
    while "\n " in prompt:
        prompt = prompt.replace("\n ", "\n")
    return prompt


def createAgentSelectorPrompt(agents, agent_names, language="en", **kwargs) -> str:
    prompt = agent_prompt_zh if language == "zh" else agent_prompt_en
    prompt = replacePrompt(prompt, keys=["agents", "agent_names"])
    prompt = prompt.format(**{"agents": agents, "agent_names": agent_names})
    # if language == "zh":
    #     prompt = agent_prompt_zh.format(**{"agents": agents, "agent_names": agent_names})
    # else:
    #     prompt = agent_prompt_en.format(**{"agents": agents, "agent_names": agent_names})
    return cleanPrompt(prompt)


def createSummaryPrompt(conversation, language="en", **kwargs) -> str:
    prompt = summary_prompt_zh if language == "zh" else summary_prompt_en
    prompt = replacePrompt(prompt, keys=["conversation"])
    prompt = prompt.format(**{"conversation": conversation,})
    # if language == "zh":
    #     prompt = summary_prompt_zh.format(**{"conversation": conversation})
    # else:
    #     prompt = summary_prompt_en.format(**{"conversation": conversation})
    return cleanPrompt(prompt)


def createMKGSchemaPrompt(conversation, language="en", **kwargs) -> str:
    prompt = memory_auto_schema_prompt_zh if language == "zh" else memory_auto_schema_prompt_en
    prompt = replacePrompt(prompt, keys=["conversation"])
    prompt = prompt.format(**{"conversation": conversation,})
    # if language == "zh":
    #     prompt = memory_auto_schema_prompt_zh.format(**{"conversation": conversation})
    # else:
    #     prompt = memory_auto_schema_prompt_en.format(**{"conversation": conversation})
    return cleanPrompt(prompt)


def createMKGPrompt(conversation, schemas, language="en", **kwargs) -> str:
    prompt = memory_extract_prompt_zh if language == "zh" else memory_extract_prompt_en
    prompt = replacePrompt(prompt, keys=["conversation", "schemas"])
    prompt = prompt.format(**{"conversation": conversation, "schemas": schemas})
    # if language == "zh":
    #     prompt = memory_extract_prompt_zh.format(**{"conversation": conversation, "schemas": schemas})
    # else:
    #     prompt = memory_extract_prompt_en.format(**{"conversation": conversation, "schemas": schemas})
    return cleanPrompt(prompt)


def createText2EKGPrompt(text, language="en", **kwargs) -> str:
    prompt = text2EKG_prompt_zh if language == "zh" else text2EKG_prompt_en
    prompt = replacePrompt(prompt, keys=["text"])
    from loguru import logger
    logger.debug(f"{prompt}")
    prompt = prompt.format(**{"text": text,})
    return cleanPrompt(prompt)