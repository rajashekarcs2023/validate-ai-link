# DiamondHacks 2026 - Agent Link Validator API

A REST API to validate asi1.ai agent profile links submitted by users on the portal.

---

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn validate_api:app --port 8080
```

- API: `http://localhost:8080`
- Swagger docs: `http://localhost:8080/docs`

---

## Endpoint

### `POST /validate`

**Request:**

```json
{
  "link": "https://asi1.ai/ai/your-agent-handle"
}
```

**Response:**

```json
{
  "valid": true,
  "message": "Valid link. Username: 'your-agent-handle'"
}
```

---

## Validation Rules

The API checks the submitted link in this order:

| Step | Check | Example Error |
|------|-------|---------------|
| 1 | **Format** — must match `https://asi1.ai/ai/<username>` | `"Invalid link. Must be in the format: https://asi1.ai/ai/<username>"` |
| 2 | **Blocklist** — rejects example/placeholder usernames from the docs | `"'sherlockholmes' is an example agent from the docs. Please submit your own agent link."` |
| 3 | **Duplicate** — rejects already-submitted usernames (persisted to `seen_usernames.json`) | `"Duplicate link. Username 'myagent' has already been submitted."` |
| 4 | **Existence** — checks the asi1.ai API to confirm the agent actually exists (not 404) | `"Agent 'fakeuser' does not exist on asi1.ai."` |

### Notes
- **Case-insensitive** — `SherlockHolmes` and `sherlockholmes` are treated as the same username.
- **Trailing slashes & query params** are stripped automatically.
- Both `http://` and `https://` are accepted.
- Duplicate tracking is saved to `seen_usernames.json` and persists across restarts.

---

## Frontend Integration

Call the API from your form's submit/validation handler:

```javascript
const res = await fetch("http://localhost:8080/validate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ link: inputField.value }),
});

const { valid, message } = await res.json();

if (!valid) {
  // Show `message` as an error on the input field
} else {
  // Link is valid, proceed with form submission
}
```

---

## Files

- `validate_api.py` — FastAPI server (single endpoint)
- `validate_link.py` — Core validation logic
- `requirements.txt` — Python dependencies
- `seen_usernames.json` — Auto-generated file tracking submitted usernames
