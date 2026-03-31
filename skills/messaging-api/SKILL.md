---
name: messaging-api
description: >
  Comprehensive reference for LINE Messaging API — webhook setup, signature verification, message sending, Flex Message design, Rich Menu management, channel access tokens, audience targeting, and insights.

  Trigger on: "build a LINE bot", "LINE chatbot", "set up a webhook", "send a push message", "reply message", "broadcast", "multicast", "narrowcast", "Flex Message", "Rich Menu", "channel access token", "LINE Official Account", "LINE OA", "replyToken", "LINE bot SDK", "webhook signature", "X-Line-Signature".

  也觸發於：「建立 LINE 機器人」、「LINE 聊天機器人」、「設定 Webhook」、「發送推播訊息」、「回覆訊息」、「廣播」、「Flex Message」、「圖文選單」、「Rich Menu」、「Channel Access Token」、「LINE 官方帳號」、「Webhook 簽章驗證」。
version: 1.0.0
---

# LINE Messaging API

> Respond in the same language the user writes in. 使用者用中文提問請用中文回答。

You are an expert in the LINE Messaging API. Guide the user to build secure, production-ready LINE bots.

**Key facts upfront:**
- All Messaging API communication is webhook-based (LINE pushes events to your server)
- You must verify `X-Line-Signature` on every request — see `references/channel-token.md`
- Your webhook endpoint must respond HTTP 200 within **1 second**
- Bot server requires HTTPS with a CA-signed cert (no self-signed)

---

## Entity hierarchy (set up first)

```
Business ID → Provider → Messaging API Channel → LINE Official Account
```

Different Providers issue different User IDs for the same user. Plan your Provider structure before development — it cannot be changed without data migration.

---

## Webhook signature verification (mandatory)

```typescript
import * as crypto from 'crypto';
import express from 'express';

// Raw body BEFORE JSON parsing
app.use('/webhook', express.raw({ type: 'application/json' }));

app.post('/webhook', (req, res) => {
  const sig = req.headers['x-line-signature'] as string;
  const body = req.body.toString();

  const expected = crypto
    .createHmac('sha256', process.env.LINE_CHANNEL_SECRET!)
    .update(body)
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sig))) {
    return res.status(401).send('Unauthorized');
  }

  res.sendStatus(200);                          // Respond within 1s
  handleEvents(JSON.parse(body).events);        // Process async
});
```

> Full security details: `references/channel-token.md`

---

## Message sending

### Reply (free, uses replyToken — expires after 1 min)

```typescript
await client.replyMessage(event.replyToken, [
  { type: 'text', text: 'Hello!' }
]);
```

### Push (costs quota)

```typescript
await client.pushMessage(userId, { type: 'text', text: 'Hi!' });
```

### Multicast (up to 500 users per call)

```typescript
await client.multicast([userId1, userId2], { type: 'text', text: 'Hi all!' });
```

### Broadcast (all followers, no IDs needed)

```typescript
await client.broadcast({ type: 'text', text: 'Announcement!' });
```

> Full API details: `references/message-sending.md`

---

## Message types quick reference

| Type | Use case |
|------|----------|
| `text` | Basic text, supports LINE emoji and mentions |
| `sticker` | LINE sticker by packageId + stickerId |
| `image` | JPEG/PNG up to 10MB |
| `video` | MP4 up to 200MB |
| `audio` | M4A up to 200MB |
| `location` | GPS coordinates + label |
| `template` | Buttons / Confirm / Carousel (mobile-only display) |
| `flex` | **Recommended** — CSS Flexbox-like, works on all clients |
| `imagemap` | Full-width image with tappable regions |

> Full examples with JSON: `references/message-objects.md`

---

## Flex Messages

Design in the [Flex Message Simulator](https://developers.line.biz/flex-simulator/) first, then copy JSON.

```typescript
await client.replyMessage(replyToken, {
  type: 'flex',
  altText: 'Product card',
  contents: {
    type: 'bubble',
    hero: {
      type: 'image', url: 'https://example.com/img.jpg',
      size: 'full', aspectRatio: '20:13', aspectMode: 'cover'
    },
    body: {
      type: 'box', layout: 'vertical',
      contents: [
        { type: 'text', text: 'Product Name', weight: 'bold', size: 'xl' },
        { type: 'text', text: 'NT$999', color: '#1DB446', size: 'lg' }
      ]
    },
    footer: {
      type: 'box', layout: 'vertical',
      contents: [{
        type: 'button', style: 'primary',
        action: { type: 'uri', label: 'Buy', uri: 'https://example.com/buy' }
      }]
    }
  }
});
```

> Layout rules, all elements, real-world templates: `references/flex-message.md`, `assets/examples/`

---

## Quick replies

```typescript
{
  type: 'text',
  text: 'Choose:',
  quickReply: {
    items: [
      { type: 'action', action: { type: 'message', label: 'Yes', text: 'Yes' } },
      { type: 'action', action: { type: 'location', label: 'Location' } },
      { type: 'action', action: { type: 'camera', label: 'Photo' } }
    ]
  }
}
```

---

## Rich Menu

```typescript
const richMenuId = await client.createRichMenu({
  size: { width: 2500, height: 843 },
  selected: true,
  name: 'Main Menu',
  chatBarText: 'Menu',
  areas: [
    {
      bounds: { x: 0, y: 0, width: 1250, height: 843 },
      action: { type: 'message', label: 'Support', text: 'I need help' }
    },
    {
      bounds: { x: 1250, y: 0, width: 1250, height: 843 },
      action: { type: 'uri', label: 'Website', uri: 'https://example.com' }
    }
  ]
});
await client.setRichMenuImage(richMenuId, imageBuffer, 'image/jpeg');
await client.setDefaultRichMenu(richMenuId);
```

> Per-user menus, tab switching: `references/rich-menu.md`

---

## Webhook events

```typescript
for (const event of events) {
  switch (event.type) {
    case 'message':    // User sent a message
    case 'follow':     // User added bot as friend
    case 'unfollow':   // User blocked bot
    case 'postback':   // User tapped postback action — event.postback.data
    case 'join':       // Bot joined group/room
    case 'leave':      // Bot left group/room
    case 'memberJoined':
    case 'memberLeft':
    case 'beacon':
  }
}
```

> Full event schemas: `references/webhook-events.md`

---

## Loading animation

```typescript
// Call immediately on receiving message, before LLM/DB calls
await axios.post('https://api.line.me/v2/bot/chat/loading/start',
  { chatId: event.source.userId, loadingSeconds: 20 },
  { headers: { Authorization: `Bearer ${token}` } }
);
```

---

## Reference files

- `references/channel-token.md` — stateless/long-lived tokens, HMAC-SHA256, SSL/TLS
- `references/message-objects.md` — all message type schemas with examples
- `references/message-sending.md` — reply/push/multicast/broadcast/narrowcast API
- `references/flex-message.md` — layout engine, all components, box sizing
- `references/rich-menu.md` — create, upload image, per-user, tab switching
- `references/webhook-events.md` — all event types with full JSON schemas
- `references/audience.md` — audience creation, management, narrowcast
- `references/url-schemes.md` — LINE URL scheme actions
- `assets/examples/` — ready-to-use Flex Message JSON templates

## Key links

- Console: https://developers.line.biz/console/
- API Reference: https://developers.line.biz/en/reference/messaging-api/
- Flex Simulator: https://developers.line.biz/flex-simulator/
- Node.js SDK: https://github.com/line/line-bot-sdk-nodejs
- Python SDK: https://github.com/line/line-bot-sdk-python
