# Message Sending APIs

## Reply message (free)

```
POST https://api.line.me/v2/bot/message/reply
```

- Uses `replyToken` from webhook event — expires after 1 minute
- Max 5 messages per call
- Free (doesn't use monthly quota)

```typescript
await client.replyMessage(event.replyToken, [
  { type: 'text', text: 'Hello' },
  { type: 'sticker', packageId: '1', stickerId: '1' }
]);
```

## Push message (costs quota)

```
POST https://api.line.me/v2/bot/message/push
```

```typescript
await client.pushMessage(userId, { type: 'text', text: 'Hi!' });
// userId: U... (individual), C... (group), R... (room)
```

## Multicast (up to 500 users, costs quota)

```
POST https://api.line.me/v2/bot/message/multicast
```

```typescript
await client.multicast(['Uaaa', 'Ubbb', 'Uccc'], { type: 'text', text: 'Hi all' });
```

## Broadcast (all followers, costs quota)

```
POST https://api.line.me/v2/bot/message/broadcast
```

```typescript
await client.broadcast({ type: 'text', text: 'Announcement' });
```

## Narrowcast (filtered audience, costs quota)

```
POST https://api.line.me/v2/bot/message/narrowcast
```

```typescript
await axios.post('https://api.line.me/v2/bot/message/narrowcast', {
  messages: [{ type: 'text', text: 'Hi segment' }],
  recipient: { type: 'audience', audienceGroupId: 12345 },
  filter: { demographic: { type: 'age', gte: 'age_25', lte: 'age_34' } },
  limit: { upToRemainingQuota: true }
}, { headers: { Authorization: `Bearer ${token}` } });
```

## Loading animation

```
POST https://api.line.me/v2/bot/chat/loading/start
```

```typescript
await axios.post('https://api.line.me/v2/bot/chat/loading/start',
  { chatId: userId, loadingSeconds: 20 },   // Max 60s
  { headers: { Authorization: `Bearer ${token}` } }
);
// Auto-stops when you send a reply
```

## Retry failed requests

Add `X-Line-Retry-Key` header (UUID v4) to retry safely:

```typescript
const retryKey = crypto.randomUUID();
await axios.post(url, body, {
  headers: { Authorization: `Bearer ${token}`, 'X-Line-Retry-Key': retryKey }
});
// Safe to retry with same retryKey — LINE deduplicates
```
