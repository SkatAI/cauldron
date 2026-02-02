from langchain_core.prompts import ChatPromptTemplate

MODERATION_SYSTEM = """\
Tu es un assistant de modération de contenu. Analyse le texte suivant et détermine \
s'il contient du contenu toxique, haineux ou NSFW (inapproprié).

Le texte à analyser est en français. Réponds uniquement en français.

Réponds UNIQUEMENT avec un objet JSON (sans balises markdown) avec cette structure exacte :
{{
  "is_toxic": true/false,
  "is_nsfw": true/false,
  "issues": [
    {{"type": "toxic_content" | "nsfw_content", "description": "brève explication en français"}}
  ]
}}

Si aucun problème n'est détecté, retourne :
{{
  "is_toxic": false,
  "is_nsfw": false,
  "issues": []
}}
"""

MODERATION_HUMAN = "Analyse ce contenu pour modération :\n\n{content}"

moderation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MODERATION_SYSTEM),
        ("human", MODERATION_HUMAN),
    ]
)
