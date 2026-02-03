# Cauldron API Contract

Validation service for AI persona system prompts. Checks for required markdown sections and toxic/NSFW content.

**Base URL:** `http://<host>:8088`

---

## POST /v1/validate

Validates a markdown system prompt.

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
  ]
}
```

**Error codes:**

| Code | Description | BFF Action |
|------|-------------|------------|
| `missing_section` | Required section missing | Show missing sections |
| `toxic_content` | Toxic content detected | Show moderation warning |
| `nsfw_content` | NSFW content detected | Show moderation warning |
| `parse_error` | Request parsing failed | Show generic error |
| `internal_error` | Service error | Retry or show unavailable |

**Example — invalid response:**
```json
{
  "status": "invalid",
  "errors": [
    {
      "code": "missing_section",
      "message": "La section requise « Profil personnel » est manquante",
      "detail": "En-tête attendu correspondant au motif : (?i)^#{2,3}\\s+Profil personnel"
    },
    {
      "code": "toxic_content",
      "message": "Le contenu contient du contenu toxique",
      "detail": "Propos haineux détectés"
    }
  ]
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
- **Multiple errors** — A response can contain several errors
- **Messages in French** — Error messages are localized in French
- **Timeout** — 30 seconds recommended (LLM moderation can be slow)
- **Interactive docs** — `/docs` (Swagger), `/redoc`, `/openapi.json`
