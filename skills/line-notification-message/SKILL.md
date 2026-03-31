---
name: line-notification-message
description: >
  Reference for LINE Notification Messages — phone-number-based push (LON/PNP) for corporate customers. Covers Template and Flexible message types, E.164 phone number hashing (SHA256), API endpoints, delivery conditions, webhook completion events, and rate limits.

  Trigger on: "LINE notification message", "LINE notification messages API", "PNP", "LON", "phone number push", "LINE corporate push", "notification message template", "pnp/push", "pnp/templated/push", "LINE partner API", "LINE notification token".

  也觸發於：「LINE 通知訊息」、「手機號碼推播」、「LINE 企業推播」、「LINE PNP」、「LINE LON」、「通知訊息範本」、「LINE 夥伴 API」、「LINE 企業客戶通知」。
version: 1.0.0
---

# LINE Notification Messages

> Respond in the same language the user writes in. 使用者用中文提問請用中文回答。

LINE Notification Messages (LON/PNP) allow corporate customers to send push messages to users **identified by phone number** — even if the user hasn't added the LINE Official Account as a friend.

**Corporate customers only.** Requires application and approval from LINE.

---

## Two message types

| Type | Endpoint | Review | Response |
|------|----------|--------|----------|
| **Template** | `POST /v2/bot/message/pnp/templated/push` | No UX review | 202 (async) |
| **Flexible** | `POST /bot/pnp/push` | Requires UX review | 200 |

Use **Template** for standard notifications (order confirmed, appointment reminder).
Use **Flexible** for customized content — requires LINE to pre-approve your layout.

---

## Phone number hashing (required)

Phone numbers must be SHA256-hashed in E.164 format before sending:

```typescript
import * as crypto from 'crypto';

function hashPhone(phone: string): string {
  // 1. Normalize to E.164: +886912345678
  // 2. SHA256 hash (hex)
  return crypto.createHash('sha256').update(phone).digest('hex');
}

// Example: '+886912345678' → '3a7bd3e2...'
const hashedPhone = hashPhone('+886912345678');
```

**Important**: Use SHA256, not HMAC. The raw hash, not base64.

---

## Template message API

```typescript
const response = await axios.post(
  'https://api.line.me/v2/bot/message/pnp/templated/push',
  {
    to: hashedPhone,                      // SHA256(E.164 phone number)
    templateName: 'order_confirmation',   // Pre-registered template name
    templateParams: {
      '{orderNumber}': '12345',
      '{amount}':      'NT$999',
      '{storeName}':   'Example Store',
    }
  },
  {
    headers: {
      Authorization: `Bearer ${channelAccessToken}`,
      'X-Line-Delivery-Tag': `order-${Date.now()}`,  // Unique delivery ID
    }
  }
);
// Returns 202 — delivery is asynchronous
```

**Do NOT use `X-Line-Retry-Key`** with this endpoint.

---

## Flexible message API

```typescript
const response = await axios.post(
  'https://api.line.me/bot/pnp/push',
  {
    to: hashedPhone,
    messages: [{
      type: 'text',
      text: 'Your appointment is confirmed for tomorrow at 10:00.'
    }]
  },
  {
    headers: {
      Authorization: `Bearer ${channelAccessToken}`,
      'Content-Type': 'application/json',
    }
  }
);
// Returns 200 — synchronous
```

---

## All 5 delivery conditions (must ALL be met)

1. User has a LINE account linked to that phone number
2. User has not blocked the LINE Official Account
3. User's LINE privacy settings allow notifications from businesses
4. The account is in a country/region where the service is available
5. The message type is approved for this LINE Official Account

If any condition fails, the message is silently not delivered — no error returned.

---

## Delivery completion webhook

When a template message (202) completes delivery, LINE sends a webhook event:

```typescript
// Webhook event type: 'notificationMessageOpened' (when user opens)
// and delivery completion event in webhook body:

interface DeliveryCompletionEvent {
  type: 'notificationMessageDelivery';
  deliveryTag: string;    // Your X-Line-Delivery-Tag value
  status: 'delivered' | 'not_delivered';
  timestamp: number;
}
```

> Full webhook schema: `references/delivery-webhook.md`

---

## Rate limits

| Limit | Value |
|-------|-------|
| Requests per second | 2,000 |
| Messages per request | 5 |
| Phone numbers per batch | 1 |

For bulk sends, implement a queue with rate-limiting (e.g., p-limit, Bottleneck).

---

## Template system

Templates are pre-registered message formats with variable placeholders:

```
Template: "Your order {orderNumber} of {amount} is confirmed."
Params:   { '{orderNumber}': '12345', '{amount}': 'NT$999' }
Result:   "Your order 12345 of NT$999 is confirmed."
```

Templates require LINE approval. Submit via your LINE Business partner contact.

> Template design rules and submission: `references/template-system.md`

---

## Error handling

```typescript
try {
  await sendNotification(phone, templateName, params);
} catch (err) {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const code = err.response?.data?.message;

    if (status === 400) console.error('Invalid phone hash or params');
    if (status === 403) console.error('Account not approved for PNP');
    if (status === 429) await retryWithBackoff(); // Rate limit
  }
}
```

Error responses never contain the original phone number — they only reference the hash.

---

## Reference files

- `references/sending-api.md` — full API specs, headers, request/response schemas
- `references/technical-specs.md` — phone hashing, E.164 normalization, country coverage
- `references/template-system.md` — template format, variable syntax, approval process
- `references/delivery-webhook.md` — webhook event schema, delivery status handling

## Key links

- Docs: https://developers.line.biz/en/docs/partner-docs/line-notification-messages/overview/
- API Reference: https://developers.line.biz/en/reference/line-notification-messages/
- Technical specs: https://developers.line.biz/en/docs/partner-docs/line-notification-messages/technical-specs/
