# Message Object Schemas

## Text
```json
{
  "type": "text",
  "text": "Hello!\nLine 2",
  "emojis": [{ "index": 0, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "001" }]
}
```

## Sticker
```json
{ "type": "sticker", "packageId": "1", "stickerId": "1" }
```

## Image
```json
{
  "type": "image",
  "originalContentUrl": "https://example.com/full.jpg",
  "previewImageUrl": "https://example.com/preview.jpg"
}
```

## Video
```json
{
  "type": "video",
  "originalContentUrl": "https://example.com/video.mp4",
  "previewImageUrl": "https://example.com/thumb.jpg",
  "trackingId": "track-001"
}
```

## Location
```json
{
  "type": "location",
  "title": "Office",
  "address": "Taipei, Taiwan",
  "latitude": 25.033964,
  "longitude": 121.564468
}
```

## Buttons template
```json
{
  "type": "template",
  "altText": "Buttons",
  "template": {
    "type": "buttons",
    "thumbnailImageUrl": "https://example.com/img.jpg",
    "title": "Menu",
    "text": "Select an option",
    "actions": [
      { "type": "postback", "label": "Buy", "data": "action=buy" },
      { "type": "uri", "label": "Details", "uri": "https://example.com" },
      { "type": "message", "label": "Help", "text": "I need help" }
    ]
  }
}
```

## Carousel template
```json
{
  "type": "template",
  "altText": "Carousel",
  "template": {
    "type": "carousel",
    "columns": [
      {
        "thumbnailImageUrl": "https://example.com/item1.jpg",
        "title": "Item 1", "text": "Desc",
        "actions": [{ "type": "postback", "label": "Select", "data": "item=1" }]
      }
    ]
  }
}
```

## Quick replies (attach to any message)
```json
{
  "type": "text",
  "text": "Choose:",
  "quickReply": {
    "items": [
      { "type": "action", "action": { "type": "message", "label": "Yes", "text": "Yes" } },
      { "type": "action", "action": { "type": "location", "label": "Location" } },
      { "type": "action", "action": { "type": "camera", "label": "Camera" } },
      { "type": "action", "action": { "type": "cameraRoll", "label": "Album" } }
    ]
  }
}
```

## Limits

| Field | Limit |
|-------|-------|
| Messages per reply/push | 5 |
| Text length | 5000 chars |
| Image max | 10 MB |
| Video max | 200 MB |
| Carousel columns | 10 |
| Quick reply items | 13 |
