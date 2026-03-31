---
name: line-login
description: >
  LINE Login v2.1 — OAuth 2.0 + OpenID Connect integration. Authorization code flow with PKCE, token management, ID token verification, user profile, and security best practices.

  Trigger on: "LINE Login", "sign in with LINE", "LINE OAuth", "LINE authentication", "LINE access token", "LINE ID token", "LINE PKCE", "social login LINE", "LINE user profile", "LINE OpenID Connect", "liff.login", "integrate LINE login", "LINE Login channel".

  也觸發於：「LINE 登入」、「LINE Login 整合」、「LINE OAuth」、「用 LINE 帳號登入」、「LINE 身份驗證」、「LINE ID Token」、「LINE PKCE」、「LINE 社群登入」、「LINE 使用者資料」、「LINE Login 通道」。
version: 1.0.0
---

# LINE Login v2.1

> Respond in the same language the user writes in. 使用者用中文提問請用中文回答。

LINE Login is a free OAuth 2.0 + OpenID Connect service. Works with web apps, native iOS/Android, and Unity games.

**Always use PKCE.** Never use the implicit flow.

---

## Authorization flow

```
User → Your app → LINE Authorization Server → User approves → Your server
       (build URL)                            (code callback)  (exchange token)
```

### Step 1: Generate PKCE + state

```typescript
import * as crypto from 'crypto';

function generateAuthParams() {
  const state    = crypto.randomBytes(16).toString('hex');      // CSRF
  const nonce    = crypto.randomBytes(16).toString('hex');      // Replay
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url');
  return { state, nonce, verifier, challenge };
}
```

### Step 2: Build authorization URL

```typescript
function buildAuthUrl(params: ReturnType<typeof generateAuthParams>) {
  const url = new URL('https://access.line.me/oauth2/v2.1/authorize');
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('client_id',     process.env.LINE_LOGIN_CHANNEL_ID!);
  url.searchParams.set('redirect_uri',  process.env.LINE_REDIRECT_URI!);
  url.searchParams.set('scope',         'profile openid email');
  url.searchParams.set('state',         params.state);
  url.searchParams.set('nonce',         params.nonce);
  url.searchParams.set('code_challenge',        params.challenge);
  url.searchParams.set('code_challenge_method', 'S256');
  return url.toString();
}
// Store { state, nonce, verifier } in server-side session (not cookies)
```

### Step 3: Handle callback — verify state first

```typescript
app.get('/auth/callback', async (req, res) => {
  const { code, state } = req.query;
  const session = await getSession(req);

  // ❗ Must verify state before anything else
  if (state !== session.state) {
    return res.status(400).send('CSRF detected');
  }

  const tokens = await exchangeCode(code as string, session.verifier);
  const user   = await verifyIdToken(tokens.id_token, session.nonce);
  // Create your own session with user.sub as the identifier
});
```

### Step 4: Exchange authorization code

```typescript
async function exchangeCode(code: string, verifier: string) {
  const { data } = await axios.post(
    'https://api.line.me/oauth2/v2.1/token',
    new URLSearchParams({
      grant_type:    'authorization_code',
      code,
      redirect_uri:  process.env.LINE_REDIRECT_URI!,
      client_id:     process.env.LINE_LOGIN_CHANNEL_ID!,
      client_secret: process.env.LINE_LOGIN_CHANNEL_SECRET!,
      code_verifier: verifier,
    })
  );
  return data;
  // { access_token, token_type, refresh_token, expires_in, scope, id_token }
}
```

### Step 5: Verify ID token on your server

```typescript
// NEVER trust userId sent from client — always verify server-side
async function verifyIdToken(idToken: string, nonce: string) {
  const { data } = await axios.post(
    'https://api.line.me/oauth2/v2.1/verify',
    new URLSearchParams({
      id_token:  idToken,
      client_id: process.env.LINE_LOGIN_CHANNEL_ID!,
      nonce,
    })
  );
  // Throws 400 if invalid, expired, or nonce mismatch
  return data;
  // { sub (=userId), name, picture, email, amr, ... }
}
```

---

## Token lifetimes

| Token | Validity | Refresh |
|-------|----------|---------|
| Access token | 30 days | Via refresh token |
| Refresh token | 90 days | — |
| ID token | 10 minutes (verify window) | Re-login |

---

## Get user profile (with access token)

```typescript
const { data: profile } = await axios.get('https://api.line.me/v2/profile', {
  headers: { Authorization: `Bearer ${accessToken}` }
});
// { userId, displayName, pictureUrl, statusMessage }
```

---

## Refresh access token

```typescript
async function refreshToken(refreshToken: string) {
  const { data } = await axios.post(
    'https://api.line.me/oauth2/v2.1/token',
    new URLSearchParams({
      grant_type:    'refresh_token',
      refresh_token: refreshToken,
      client_id:     process.env.LINE_LOGIN_CHANNEL_ID!,
      client_secret: process.env.LINE_LOGIN_CHANNEL_SECRET!,
    })
  );
  return data; // New access_token + refresh_token
}
```

---

## Revoke token

```typescript
await axios.post('https://api.line.me/oauth2/v2.1/revoke',
  new URLSearchParams({
    access_token:  token,
    client_id:     process.env.LINE_LOGIN_CHANNEL_ID!,
    client_secret: process.env.LINE_LOGIN_CHANNEL_SECRET!,
  })
);
```

---

## Add LINE Official Account as friend on login

Add `bot_prompt=aggressive` (or `normal`) to the authorization URL:

```typescript
url.searchParams.set('bot_prompt', 'aggressive');
```

---

## Scopes

| Scope | Data returned |
|-------|---------------|
| `profile` | userId, displayName, pictureUrl, statusMessage |
| `openid` | ID token (required for `nonce`) |
| `email` | Email (requires channel approval) |
| `phone` | Phone number (corporate customers only) |

---

## Security checklist

- [ ] Always use authorization code flow (never implicit)
- [ ] PKCE (`code_challenge` + `code_verifier`) on every request
- [ ] `state` param generated per-request (16+ random bytes), verified in callback
- [ ] `nonce` param generated per-request, verified in ID token
- [ ] ID token verified **server-side** via `/oauth2/v2.1/verify`
- [ ] Never trust `userId` sent from client/frontend
- [ ] Store `state`, `nonce`, `verifier` in server-side session (not URL params)
- [ ] Revoke tokens on logout
- [ ] Use HTTPS everywhere

---

## Reference files

- `references/oauth-flow.md` — full flow diagram, all endpoints, error codes
- `references/token-management.md` — refresh, revoke, verify, token introspection
- `references/user-profile.md` — profile API, ID token claims, email handling
- `references/security.md` — CSRF, replay attacks, PKCE deep dive

## Key links

- Docs: https://developers.line.biz/en/docs/line-login/
- API Reference: https://developers.line.biz/en/reference/line-login/
- Security checklist: https://developers.line.biz/en/docs/line-login/security-checklist/
