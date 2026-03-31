# Flex Message Reference

Design visually at: https://developers.line.biz/flex-simulator/

## Container types

- `bubble` — single card
- `carousel` — horizontally scrollable bubbles (max 12)

## Bubble sections

```json
{
  "type": "bubble",
  "size": "mega",              // nano | micro | kilo | mega | giga
  "direction": "ltr",
  "header": {},
  "hero": {},
  "body": {},
  "footer": {},
  "styles": {
    "header": { "backgroundColor": "#FFFFFF", "separator": false },
    "hero":   { "backgroundColor": "#FFFFFF" },
    "body":   { "backgroundColor": "#FFFFFF" },
    "footer": { "backgroundColor": "#F5F5F5", "separator": true }
  }
}
```

## Box (layout container)

```json
{
  "type": "box",
  "layout": "vertical",    // horizontal | vertical | baseline
  "contents": [],
  "flex": 1,
  "spacing": "md",         // none | xs | sm | md | lg | xl | xxl
  "margin": "md",
  "paddingAll": "md",
  "backgroundColor": "#FFFFFF",
  "borderColor": "#E0E0E0",
  "borderWidth": "1px",
  "cornerRadius": "8px"
}
```

## Components

### Text
```json
{
  "type": "text",
  "text": "Hello",
  "size": "md",        // xxs | xs | sm | md | lg | xl | xxl | 3xl | 4xl | 5xl
  "weight": "bold",    // regular | bold
  "color": "#333333",
  "align": "start",    // start | center | end
  "wrap": true,
  "maxLines": 3,
  "flex": 0,
  "action": { "type": "uri", "uri": "https://example.com" }
}
```

### Button
```json
{
  "type": "button",
  "style": "primary",       // primary | secondary | link
  "color": "#1DB446",
  "action": { "type": "postback", "label": "Buy", "data": "action=buy" },
  "height": "sm"            // sm | md
}
```

### Image
```json
{
  "type": "image",
  "url": "https://example.com/img.jpg",
  "size": "full",           // xxs | xs | sm | md | lg | xl | xxl | 3xl | 4xl | 5xl | full
  "aspectRatio": "20:13",
  "aspectMode": "cover",    // cover | fit
  "action": { "type": "uri", "uri": "https://example.com" }
}
```

### Icon
```json
{ "type": "icon", "url": "https://example.com/star.png", "size": "sm" }
```

### Separator
```json
{ "type": "separator", "margin": "md", "color": "#E0E0E0" }
```

### Spacer
```json
{ "type": "spacer", "size": "md" }
```

### Video (hero section)
```json
{
  "type": "video",
  "url": "https://example.com/video.mp4",
  "previewUrl": "https://example.com/thumb.jpg",
  "altContent": { "type": "image", "url": "https://example.com/thumb.jpg", "size": "full" },
  "action": { "type": "uri", "uri": "https://example.com" }
}
```

## Actions

```json
{ "type": "uri",      "label": "Open", "uri": "https://example.com" }
{ "type": "postback", "label": "Buy",  "data": "action=buy", "displayText": "I want to buy" }
{ "type": "message",  "label": "Help", "text": "I need help" }
{ "type": "datetimepicker", "label": "Date", "data": "pick", "mode": "datetime" }
```
