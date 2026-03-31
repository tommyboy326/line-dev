# LINE Developer Skills for Claude Code

Bilingual (English / 繁體中文) Claude Code skills for LINE platform development.

## Skills

| Skill | Description |
|-------|-------------|
| `messaging-api` | Webhooks, bots, Flex Messages, Rich Menus, message types |
| `line-login` | OAuth 2.0 + PKCE, token management, user profile |
| `line-liff` | LIFF SDK, browser APIs, plugins, Pluggable SDK |
| `line-mini-app` | Service messages, IAP, Quick Fill, submission review |
| `line-notification-message` | Phone-number-based push (corporate customers) |

## Installation

**As Claude Code Plugin (marketplace):**

```bash
/plugin marketplace add kaiwu/line-dev
/plugin install line-dev@kaiwu-line-dev
```

**Individual skills via npx:**

```bash
npx skills add kaiwu/line-dev
# or specific skill:
npx skills add kaiwu/line-dev@messaging-api
npx skills add kaiwu/line-dev@line-login
npx skills add kaiwu/line-dev@line-liff
npx skills add kaiwu/line-dev@line-mini-app
npx skills add kaiwu/line-dev@line-notification-message
```

## Usage

Skills auto-trigger based on your query. You can also invoke them directly:

```
/messaging-api   How do I create a Flex Message?
/line-login      How do I implement PKCE?
/line-liff       What is liff.isInClient()?
/line-mini-app   How do I send a service message?
```

## Testing & optimization

Test trigger accuracy with the included scripts:

```bash
# Test all skills (1 iteration)
./scripts/test_all.sh

# Test a specific skill
./scripts/test_skill.sh messaging-api

# Optimize skill description (up to 5 AI iterations)
./scripts/test_skill.sh messaging-api --max-iterations 5

# End-to-end test with actual Claude invocations
./scripts/test_skill_e2e.sh messaging-api --runs 3

# Test all e2e
for skill in messaging-api line-login line-liff line-mini-app line-notification-message; do
  ./scripts/test_skill_e2e.sh "$skill"
done
```

### Assessment format (`scripts/test-data/<skill>/assessment_set.json`)

```json
[
  { "query": "How do I send a LINE push message?", "should_trigger": true },
  { "query": "How do I integrate LINE Login?",     "should_trigger": false }
]
```

### Scope config (`scripts/test-data/<skill>/scope.json`)

```json
{
  "knowledge_domain": "LINE Messaging API",
  "assess_scope": ["- The skill covers ..."],
  "improve_scope": ["- The skill covers ... NOT: ..."]
}
```

## Development

```
skills/
├── messaging-api/
│   ├── SKILL.md                 # Main skill (frontmatter + instructions)
│   ├── assets/examples/         # Flex Message JSON templates
│   └── references/              # Detailed API reference files
├── line-login/
├── line-liff/
├── line-mini-app/
└── line-notification-message/

scripts/
├── optimize_description.py      # AI-powered description optimizer
├── test_skill.sh                # Single skill test runner
├── test_all.sh                  # All skills test runner
├── test_skill_e2e.sh            # E2E test with actual Claude CLI
└── test-data/<skill>/
    ├── assessment_set.json      # Trigger/no-trigger query pairs
    └── scope.json               # Knowledge domain + scope constraints
```

## License

Apache 2.0
