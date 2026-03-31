---
name: line-liff
description: >
  Reference for building, reviewing, and debugging LIFF (LINE Front-end Framework) web apps inside LINE. Covers liff.init(), user profile, sendMessages, shareTargetPicker, scanCodeV2, LIFF plugins, Pluggable SDK, LIFF CLI, and browser environment differences.

  Trigger on: "LIFF", "LINE Front-end Framework", "liff.init", "liff.getProfile", "liff.sendMessages", "liff.login", "liff.closeWindow", "LIFF app", "LIFF ID", "liff.line.me", "LINE in-app browser", "liff.isInClient", "LIFF plugin", "liff.scanCode", "Create LIFF App", "LIFF CLI".

  也觸發於：「LIFF 開發」、「LIFF 應用程式」、「liff.init」、「liff.getProfile」、「liff.sendMessages」、「LIFF 登入」、「LIFF 瀏覽器」、「LINE 內建瀏覽器」、「LIFF 插件」、「LIFF ID」、「liff.line.me」。
version: 1.0.0
---

# LIFF (LINE Front-end Framework)

> Respond in the same language the user writes in. 使用者用中文提問請用中文回答。

LIFF is a web app platform that runs inside LINE. LIFF apps can:
- Access LINE user profile (userId, displayName, pictureUrl)
- Send messages to the current chat on behalf of the user
- Open a native share picker
- Scan QR codes

**Critical rule:** Call `liff.init()` before any other LIFF API. It will throw if called out of order.

---

## Setup

1. Create a **LINE Login channel** in [console](https://developers.line.biz/console/)
2. Go to LIFF tab → Add → set endpoint URL and size (`compact` / `tall` / `full`)
3. Copy the `liffId`

```bash
npm install @line/liff
# or CDN: <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
```

---

## Initialize

```typescript
import liff from '@line/liff';

await liff.init({
  liffId: 'YOUR_LIFF_ID',
  withLoginOnExternalBrowser: true  // auto-login when opened outside LINE
});

if (!liff.isLoggedIn()) {
  liff.login({ redirectUri: window.location.href });
  return;
}
```

---

## User profile

```typescript
const profile = await liff.getProfile();
// { userId, displayName, pictureUrl, statusMessage }

// For server-side user verification:
const idToken = liff.getIDToken();  // Send this to your server
// Server verifies via: POST https://api.line.me/oauth2/v2.1/verify
// { id_token: idToken, client_id: CHANNEL_ID }
```

**Never trust `profile.userId` directly from the client — always verify the ID token on your server.**

---

## Environment detection

```typescript
liff.isInClient()  // true = opened inside LINE app
liff.getOS()       // 'ios' | 'android' | 'web'
liff.getLanguage() // 'zh-Hant' | 'en' | 'ja' | ...
liff.getContext()  // { type, userId, groupId?, roomId?, ... }
```

| Feature | LIFF browser (in LINE) | External browser |
|---------|------------------------|-----------------|
| `sendMessages()` | ✅ | ❌ |
| `closeWindow()` | ✅ | ❌ |
| `scanCodeV2()` | ✅ | varies |
| `getProfile()` | ✅ | ✅ (after login) |

---

## Send message to current chat

```typescript
// Only works when isInClient() === true
await liff.sendMessages([
  { type: 'text', text: 'Hello from LIFF!' },
  { type: 'sticker', packageId: '1', stickerId: '1' }
]);
// Max 5 messages, sent as the user to the current chat
```

---

## Share target picker

```typescript
const result = await liff.shareTargetPicker(
  [{ type: 'text', text: 'Check this out!' }],
  { isMultiple: true }
);
if (result?.status === 'success') console.log('Shared');
```

---

## QR code scanner

```typescript
// Use scanCodeV2 (scanCode is deprecated)
const { value } = await liff.scanCodeV2();
console.log(value);
```

---

## Navigation

```typescript
liff.closeWindow();                   // Close LIFF, return to chat
liff.openWindow({ url: 'https://example.com', external: false });

// Permanent link to current page
const link = await liff.permanentLink.createUrl();
// https://liff.line.me/{liffId}/current-path?query=value
```

---

## Access token (for LINE API calls)

```typescript
const token = liff.getAccessToken(); // Short-lived, expires
// Use for: GET https://api.line.me/v2/profile
```

---

## Pluggable SDK (reduce bundle size ~34%)

```typescript
import liff from '@line/liff/core';
import GetProfile  from '@line/liff/get-profile';
import SendMessages from '@line/liff/send-messages';

liff.use(new GetProfile());
liff.use(new SendMessages());
await liff.init({ liffId: 'YOUR_LIFF_ID' });
```

---

## LIFF plugins

```typescript
const myPlugin = {
  name: 'analytics',
  install({ hooks }) {
    hooks.on('init:start', () => { /* track init */ });
  },
  track(event: string) { /* ... */ }
};

liff.use(myPlugin);
await liff.init({ liffId: 'YOUR_LIFF_ID' });
liff.$analytics.track('page_view');
```

---

## Development

```bash
# Expose localhost via HTTPS
npx ngrok http 3000
# or: cloudflared tunnel --url http://localhost:3000

# Update LIFF endpoint URL in console to your HTTPS URL
# Open https://liff.line.me/{liffId} in LINE

# LIFF CLI
npx @line/liff-cli serve --liff-id YOUR_LIFF_ID --port 3000
```

---

## React hook

```typescript
import { useEffect, useState } from 'react';
import liff from '@line/liff';

export function useLiff(liffId: string) {
  const [ready, setReady] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    liff.init({ liffId, withLoginOnExternalBrowser: true })
      .then(async () => {
        if (liff.isLoggedIn()) setProfile(await liff.getProfile());
        setReady(true);
      })
      .catch(setError);
  }, [liffId]);

  return { ready, profile, error, liff };
}
```

---

## Reference files

- `references/api.md` — full liff.* API reference with parameters and return types
- `references/guidelines.md` — endpoint URL rules, size constraints, allowed domains
- `references/plugins.md` — plugin system, hooks, lifecycle
- `references/server-auth.md` — ID token verification, server-side auth patterns
- `references/navigation.md` — URL scheme, permanent links, openWindow
- `references/cli.md` — LIFF CLI and Create LIFF App scaffold

## Key links

- Docs: https://developers.line.biz/en/docs/liff/
- API Reference: https://developers.line.biz/en/reference/liff/
- LIFF Playground: https://liff-playground.netlify.app/
