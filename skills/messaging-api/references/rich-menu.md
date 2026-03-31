# Rich Menu Reference

## Image spec

| Property | Value |
|----------|-------|
| Size (full) | 2500 × 1686 px |
| Size (half) | 2500 × 843 px |
| Format | JPEG or PNG |
| Max file size | 1 MB |

## Create, upload, activate

```typescript
import { Client } from '@line/bot-sdk';
import * as fs from 'fs';

const client = new Client({ channelAccessToken: token });

// 1. Create
const richMenuId = await client.createRichMenu({
  size: { width: 2500, height: 843 },
  selected: true,
  name: 'Main Menu',
  chatBarText: 'Menu',
  areas: [
    {
      bounds: { x: 0, y: 0, width: 833, height: 843 },
      action: { type: 'message', label: 'Support', text: 'Support' }
    },
    {
      bounds: { x: 833, y: 0, width: 834, height: 843 },
      action: { type: 'uri', label: 'Website', uri: 'https://example.com' }
    },
    {
      bounds: { x: 1667, y: 0, width: 833, height: 843 },
      action: {
        type: 'uri', label: 'LIFF',
        uri: 'https://liff.line.me/YOUR_LIFF_ID'
      }
    }
  ]
});

// 2. Upload image
const image = fs.readFileSync('./menu.jpg');
await client.setRichMenuImage(richMenuId, image, 'image/jpeg');

// 3. Set as default for all users
await client.setDefaultRichMenu(richMenuId);
```

## Per-user rich menu

```typescript
// Link to specific user
await client.linkRichMenuToUser(userId, richMenuId);

// Unlink (user gets default menu)
await client.unlinkRichMenuFromUser(userId);

// Link to multiple users at once
await client.linkRichMenuToUsers([userId1, userId2], richMenuId);
```

## Tab switching

Create two rich menus and link them via `richmenuswitch` action:

```typescript
const menuA = await client.createRichMenu({ /* ... areas include switch action */ });
const menuB = await client.createRichMenu({ /* ... */ });

// In menuA area:
{
  action: {
    type: 'richmenuswitch',
    richMenuAliasId: 'richmenu-alias-b',
    data: 'switched_to_b'
  }
}

// Create aliases
await axios.post('https://api.line.me/v2/bot/richmenu/alias',
  { richMenuAliasId: 'richmenu-alias-a', richMenuId: menuA },
  { headers: { Authorization: `Bearer ${token}` } }
);
```

## Manage

```typescript
await client.deleteRichMenu(richMenuId);
const menus = await client.getRichMenuList();        // All menus
const menu  = await client.getRichMenu(richMenuId);  // One menu
const def   = await client.getDefaultRichMenu();      // Current default
await client.deleteDefaultRichMenu();                 // Remove default
```
