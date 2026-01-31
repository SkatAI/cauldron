from langchain_core.prompts import ChatPromptTemplate

MODERATION_SYSTEM = """\
You are a content moderation assistant. Analyze the following text and determine \
if it contains any toxic, hateful, or NSFW content.

Respond ONLY with a JSON object (no markdown fences) with this exact structure:
{{
  "is_toxic": true/false,
  "is_nsfw": true/false,
  "issues": [
    {{"type": "toxic_content" | "nsfw_content", "description": "brief explanation"}}
  ]
}}

If no issues are found, return:
{{
  "is_toxic": false,
  "is_nsfw": false,
  "issues": []
}}
"""

MODERATION_HUMAN = "Analyze this content for moderation:\n\n{content}"

moderation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MODERATION_SYSTEM),
        ("human", MODERATION_HUMAN),
    ]
)
