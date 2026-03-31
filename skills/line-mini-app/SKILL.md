---
name: line-mini-app
description: >
  Comprehensive reference for LINE MINI App — a web app that runs inside LINE without requiring users to download anything. Covers Service Messages, Common Profile Quick Fill, In-App Purchase, Console setup (3 internal channels), submission review workflow, and operational guidelines.

  Trigger on: "LINE MINI App", "MINI App", "service message", "notification token", "LINE MINI App submission", "LINE MINI App review", "in-app purchase LINE", "LINE IAP", "Common Profile Quick Fill", "LINE MINI App channel", "verified MINI App", "miniapp.line.me".

  也觸發於：「LINE MINI App」、「小程式」、「服務訊息」、「Notification Token」、「LINE MINI App 審核」、「LINE MINI App 上架」、「LINE 內購」、「快速填寫個人資料」、「LINE MINI App 通道設定」、「已認證 MINI App」。
version: 1.0.0
---

# LINE MINI App

> Respond in the same language the user writes in. 使用者用中文提問請用中文回答。

LINE MINI App is a web application that runs inside LINE — users access services without downloading a separate app.

**Built on LIFF** — LINE MINI App uses LIFF as its foundation. Read `line-liff` skill first if unfamiliar with LIFF.

---

## Console setup (3 internal channels)

Every MINI App creates three channels automatically:

| Channel | Purpose |
|---------|---------|
| **LINE Login** | User authentication via LIFF |
| **Messaging API** | Service Messages (transactional push) |
| **LINE MINI App** | App configuration, submission, IAP |

Configure in: Console → Provider → LINE MINI App channel

---

## Development stages

```
Unverified (testing, ≤50 testers) → Submit for review → Verified (public)
```

- **Unverified**: Available only to testers added in console. No submission needed.
- **Verified**: Publicly accessible. Requires review (7–14 business days).

---

## Service Messages (transactional push)

Service Messages are LINE MINI App's version of push notifications — sent to users who have interacted with your MINI App.

### Flow

```
User opens MINI App → LIFF issues notification token → Your server stores it
→ Later: POST /message/v3/notif/token/send with stored token
```

### Get notification token (client-side)

```typescript
import liff from '@line/liff';

// After liff.init()
const token = await liff.getNotificationToken();
// Send this token to your server and store it per-user
```

### Send service message (server-side)

```typescript
await axios.post(
  'https://api.line.me/message/v3/notif/token/send',
  {
    to: notificationToken,
    messages: [{
      type: 'template',
      altText: 'Order confirmed',
      template: {
        type: 'buttons',
        text: 'Your order #1234 has been confirmed.',
        actions: [{
          type: 'uri',
          label: 'View Order',
          uri: 'https://liff.line.me/YOUR_LIFF_ID/order/1234'
        }]
      }
    }]
  },
  { headers: { Authorization: `Bearer ${channelAccessToken}` } }
);
```

Notification tokens expire. Store them with a `created_at` timestamp and re-fetch if needed.

---

## Custom share messages (action button)

Add a share button in your MINI App UI:

```typescript
// Only available in LINE MINI App (not regular LIFF)
await liff.shareTargetPicker([{
  type: 'flex',
  altText: 'Check out this service',
  contents: { /* flex bubble */ }
}]);
```

---

## Common Profile Quick Fill

Lets users auto-fill forms with their LINE profile data (name, phone, address).

```typescript
// 1. Request fill (client-side, user must approve)
const result = await liff.requestQuickFill({
  fields: ['name', 'phone', 'address']
});

if (result.status === 'approved') {
  const { name, phone, address } = result.data;
  // Pre-fill your form
}
```

**Design requirements**: Must show a preview screen before submitting. See `references/common-profile.md`.

---

## In-App Purchase (IAP)

Requires separate application to LINE. Only available to verified MINI Apps.

```typescript
import liff from '@line/liff';

// 1. Get available products
const products = await liff.getIAPProducts({ channelId: 'YOUR_CHANNEL_ID' });

// 2. Initiate purchase
const receipt = await liff.purchaseIAPProduct({
  channelId: 'YOUR_CHANNEL_ID',
  productId: 'product_001',
  productType: 'CONSUMABLE'  // or 'NON_CONSUMABLE'
});

// 3. Verify receipt on your server
// POST https://api.line.me/iap/v1/orders/{orderId}/verify
```

> Full IAP flow: `references/in-app-purchase.md`

---

## Authorization flow (consent simplification)

LINE MINI App uses a simplified consent flow — users approve your app once:

```typescript
await liff.init({
  liffId: 'YOUR_LIFF_ID',
  // Consent screen shown automatically if needed
});
// No extra code needed — the MINI App channel handles consent
```

---

## Permanent links

```typescript
const link = liff.permanentLink.createUrlBy('https://liff.line.me/YOUR_LIFF_ID/product/123');
// Users can bookmark this and return directly to product page
```

---

## Submission checklist

Before submitting for review:

- [ ] App tested with ≥1 tester account in unverified mode
- [ ] Privacy policy URL set in console
- [ ] Terms of service URL set in console
- [ ] App icon uploaded (1024×1024 PNG, no transparency)
- [ ] Service message templates reviewed for content policy
- [ ] Loading screen configured
- [ ] Safe area insets respected (iPhone notch/home indicator)
- [ ] All external links open in LIFF browser (not unexpected navigation away)

> Full submission guide: `references/submission-review.md`

---

## Performance guidelines

- First contentful paint < 3 seconds on 4G
- Use LIFF Pluggable SDK to reduce bundle size
- Lazy load routes — users expect app-like speed
- Preload critical resources (logo, first screen data)

---

## Reference files

- `references/service-messages.md` — notification token lifecycle, message templates, limits
- `references/common-profile.md` — Quick Fill fields, UX requirements, data handling
- `references/in-app-purchase.md` — IAP setup, purchase flow, receipt verification
- `references/console-setup.md` — 3-channel setup, tester management, settings
- `references/submission-review.md` — review criteria, rejection reasons, re-review
- `references/features.md` — all built-in and custom features overview

## Key links

- Docs: https://developers.line.biz/en/docs/line-mini-app/
- API Reference: https://developers.line.biz/en/reference/line-mini-app/
- Playground: https://miniapp.line.me/lineminiapp_playground
