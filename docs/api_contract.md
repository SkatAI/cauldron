# Cauldron API Contract

Validation service for AI persona system prompts. Evaluates quality across 8 criteria and checks for toxic/NSFW content.

**Base URL:** `http://<host>:8088`

---

## POST /v1/validate

Validates and evaluates a markdown system prompt.

**Request:**
```json
{ "content": "# Persona\n\n## Contexte de l'entretien\n..." }
```

**Response:**
```json
{
  "status": "valid" | "invalid",
  "errors": [
    { "code": "<error_code>", "message": "...", "detail": "..." | null }
  ],
  "quality": {
    "criteria": [
      { "name": "Clarté du rôle", "justification": "..." },
      { "name": "Traits de comportement et attitude", "justification": "..." },
      { "name": "Style de communication", "justification": "..." },
      { "name": "Motivations et objectifs", "justification": "..." },
      { "name": "Contraintes et limitations", "justification": "..." },
      { "name": "Instructions de cohérence", "justification": "..." },
      { "name": "Pertinence contextuelle", "justification": "..." },
      { "name": "Clarté et concision", "justification": "..." }
    ],
    "advice": "Suggestions d'amélioration en français..."
  } | null
}
```

**Status logic:**
- `valid` — No toxic/NSFW content detected (quality evaluation is informational only)
- `invalid` — Toxic or NSFW content detected

**Error codes:**

| Code | Description | BFF Action |
|------|-------------|------------|
| `toxic_content` | Toxic content detected | Show moderation warning |
| `nsfw_content` | NSFW content detected | Show moderation warning |
| `parse_error` | Request parsing failed | Show generic error |
| `internal_error` | Service error | Retry or show unavailable |

**Example — valid response with quality evaluation:**
```json
{
  "status": "valid",
  "errors": [],
  "quality": {
    "criteria": [
      { "name": "Clarté du rôle", "justification": "L'identité du persona est bien définie avec profession et contexte." },
      { "name": "Traits de comportement et attitude", "justification": "Les traits de personnalité sont présents mais pourraient être plus détaillés." },
      { "name": "Style de communication", "justification": "Le ton et le niveau de formalité sont clairement spécifiés." },
      { "name": "Motivations et objectifs", "justification": "Les objectifs du persona ne sont pas explicitement définis." },
      { "name": "Contraintes et limitations", "justification": "Quelques limites sont indiquées." },
      { "name": "Instructions de cohérence", "justification": "L'instruction demande explicitement de maintenir le persona." },
      { "name": "Pertinence contextuelle", "justification": "Le persona est parfaitement adapté au contexte d'entretien." },
      { "name": "Clarté et concision", "justification": "L'instruction est claire sans être trop longue." }
    ],
    "advice": "Améliorer la définition des motivations et objectifs du persona dans la conversation."
  }
}
```

**Example — invalid response (toxic content):**
```json
{
  "status": "invalid",
  "errors": [
    {
      "code": "toxic_content",
      "message": "Le contenu contient du contenu toxique",
      "detail": "Propos haineux détectés"
    }
  ],
  "quality": null
}
```

---

## GET /health

```json
{ "status": "ok" }
```

---

## Integration Notes

- **Always check `status` field** — HTTP is always 200, even for failed validations
- **Quality is non-blocking** — Low quality doesn't make `status` invalid
- **Multiple errors** — A response can contain several moderation errors
- **Messages in French** — Error messages and quality feedback are localized in French
- **Timeout** — 30 seconds recommended (LLM calls can be slow)
- **Interactive docs** — `/docs` (Swagger), `/redoc`, `/openapi.json`
