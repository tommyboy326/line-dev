# Webhook Events Reference

## Event base structure

```typescript
interface WebhookBody {
  destination: string;   // Bot's userId
  events: WebhookEvent[];
}

interface WebhookEvent {
  type: string;
  mode: 'active' | 'standby';
  timestamp: number;     // Unix ms
  source: Source;
  webhookEventId: string;  // Unique per event
  deliveryContext: { isRedelivery: boolean };
  replyToken?: string;   // Present on replyable events
}

interface Source {
  type: 'user' | 'group' | 'room';
  userId?: string;       // U...
  groupId?: string;      // C...
  roomId?: string;       // R...
}
```

## Message event

```typescript
{
  type: 'message',
  replyToken: '...',
  message: {
    type: 'text' | 'image' | 'video' | 'audio' | 'file' | 'location' | 'sticker',
    id: '...',           // Message ID (use to get binary content)
    // For text:
    text: 'Hello',
    mention?: { mentionees: [{ type: 'user', userId: '...' }] },
    // For sticker:
    packageId: '1', stickerId: '1', stickerResourceType: 'STATIC',
    // For location:
    title: '...', address: '...', latitude: 0, longitude: 0,
  }
}
```

### Get image/video/audio content

```typescript
const stream = await client.getMessageContent(message.id);
// Pipe to file or process buffer
```

## Follow / Unfollow events

```typescript
{ type: 'follow',   replyToken: '...', source: { type: 'user', userId: '...' } }
{ type: 'unfollow', source: { type: 'user', userId: '...' } }  // No replyToken
```

## Postback event

```typescript
{
  type: 'postback',
  replyToken: '...',
  postback: {
    data: 'action=buy&itemId=123',     // Your custom string (max 300 chars)
    params?: {
      // datetimepicker result:
      datetime?: '2024-01-15T14:30',
      date?: '2024-01-15',
      time?: '14:30',
    }
  }
}
```

## Join / Leave events

```typescript
{ type: 'join',  replyToken: '...', source: { type: 'group', groupId: '...' } }
{ type: 'leave', source: { type: 'group', groupId: '...' } }  // No replyToken
```

## Member joined / left

```typescript
{
  type: 'memberJoined',
  replyToken: '...',
  joined: { members: [{ type: 'user', userId: '...' }] }
}
{
  type: 'memberLeft',
  left: { members: [{ type: 'user', userId: '...' }] }
}
```

## Beacon event

```typescript
{
  type: 'beacon',
  replyToken: '...',
  beacon: {
    hwid: '...',
    type: 'enter' | 'leave' | 'banner',
    dm?: string  // Device message (hex string)
  }
}
```

## Account link event

```typescript
{
  type: 'accountLink',
  replyToken: '...',
  link: { result: 'ok' | 'failed', nonce: '...' }
}
```

## Deduplication

```typescript
const processed = new Set<string>();

async function handleEvent(event: WebhookEvent) {
  if (processed.has(event.webhookEventId)) return;
  processed.add(event.webhookEventId);
  // ... process event
}
// Use Redis with TTL for production
```
