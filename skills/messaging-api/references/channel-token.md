# Channel Access Token & Webhook Security

## Token types

| Type | Validity | Best for |
|------|----------|----------|
| Stateless (v2.1) | Short-lived JWT, no revocation needed | Serverless, Lambda, Workers |
| Long-lived | 30 days, manual revoke | Prototyping, simple bots |
| Short-lived (v2.1) | 30 days, programmatic issue | Scheduled rotation |

## Stateless token (recommended for production)

```typescript
import * as jwt from 'jsonwebtoken';
import axios from 'axios';

async function getStatelessToken(channelId: string, privateKey: string, keyId: string) {
  const now = Math.floor(Date.now() / 1000);
  const assertion = jwt.sign(
    { iss: channelId, sub: channelId, aud: 'https://api.line.me/', token_exp: 60, jti: `${now}` },
    privateKey,
    { algorithm: 'RS256', expiresIn: '30m', header: { typ: 'JWT', alg: 'RS256', kid: keyId } }
  );
  const { data } = await axios.post('https://api.line.me/oauth2/v2.1/token',
    new URLSearchParams({
      grant_type: 'client_credentials',
      client_assertion_type: 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
      client_assertion: assertion,
    })
  );
  return data.access_token;
}
```

## Webhook signature verification (HMAC-SHA256)

```typescript
import * as crypto from 'crypto';

// CRITICAL: Use raw body (Buffer), NOT parsed JSON
function verify(channelSecret: string, rawBody: string | Buffer, signature: string): boolean {
  if (!signature) return false;
  const expected = crypto.createHmac('sha256', channelSecret).update(rawBody).digest('base64');
  try {
    return crypto.timingSafeEqual(Buffer.from(expected, 'base64'), Buffer.from(signature, 'base64'));
  } catch { return false; }
}
```

## SSL/TLS requirements

- Valid CA-signed certificate (no self-signed)
- TLS 1.2+ only
- Full certificate chain installed (including intermediates)
- Respond within **1 second** — process events asynchronously

## Secret management

Never hardcode. Use environment variables or cloud secret managers:
```typescript
const SECRET = process.env.LINE_CHANNEL_SECRET;
if (!SECRET) throw new Error('LINE_CHANNEL_SECRET required');
```
