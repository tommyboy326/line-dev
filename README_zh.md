# LINE 開發者 Skills（Claude Code 擴充套件）

專為 LINE 平台開發設計的 Claude Code Skills，提供完整的中英文雙語支援。

## 包含的 Skills

| Skill | 觸發方式 | 涵蓋內容 |
|-------|----------|----------|
| `messaging-api` | `/messaging-api` | Webhook、機器人、Flex Message、圖文選單、訊息類型 |
| `line-login` | `/line-login` | OAuth 2.0 + PKCE、Token 管理、使用者資料 |
| `line-liff` | `/line-liff` | LIFF SDK、瀏覽器 API、插件、Pluggable SDK |
| `line-mini-app` | `/line-mini-app` | 服務訊息、內購、快速填寫、審核上架 |
| `line-notification-message` | `/line-notification-message` | 電話號碼推播（企業客戶） |

## 安裝方式

### 透過 Claude Code Plugin Marketplace

```bash
/plugin marketplace add kaiwu/line-dev
/plugin install line-dev@kaiwu-line-dev
```

### 透過 npx 安裝個別 Skills

```bash
# 安裝所有 skills
npx skills add kaiwu/line-dev

# 安裝單一 skill
npx skills add kaiwu/line-dev@messaging-api
npx skills add kaiwu/line-dev@line-login
npx skills add kaiwu/line-dev@line-liff
npx skills add kaiwu/line-dev@line-mini-app
npx skills add kaiwu/line-dev@line-notification-message
```

## 使用方式

Skills 會根據你的查詢**自動觸發**，也可以用斜線命令直接呼叫：

```
/messaging-api  如何建立 LINE Flex Message？
/line-login     LINE Login 的 PKCE 怎麼實作？
/line-liff      liff.isInClient() 是什麼？
/line-mini-app  LINE MINI App 如何發送服務訊息？
```

中英文查詢皆可，Claude 會用你提問的語言回答。

## 各 Skill 詳細說明

### messaging-api — LINE Messaging API

涵蓋建立 LINE 機器人的完整流程：

- **Webhook 設定**：簽章驗證（HMAC-SHA256）、SSL/TLS 需求、非同步處理
- **訊息類型**：文字、貼圖、圖片、影片、位置、模板訊息、Flex Message、圖片地圖
- **訊息發送**：回覆（reply）、推播（push）、多目標（multicast）、廣播（broadcast）、窄播（narrowcast）
- **Rich Menu（圖文選單）**：建立、上傳圖片、設定預設、每個使用者個別設定、分頁切換
- **Channel Access Token**：Stateless（推薦）、長效型、短效型
- **Flex Message**：佈局引擎、所有元件說明，附 3 個範例 JSON（商品卡片、收據、確認卡片）

**觸發情境**：「建立 LINE 機器人」、「設定 Webhook」、「如何發送推播」、「Flex Message 怎麼做」

---

### line-login — LINE Login

LINE 的 OAuth 2.0 + OpenID Connect 整合：

- **授權流程**：完整的授權碼流程，附程式碼範例
- **PKCE**：`code_verifier` + `code_challenge` 產生與驗證
- **CSRF 防護**：`state` 參數的正確使用方式
- **Token 管理**：交換、刷新、撤銷
- **ID Token 驗證**：伺服器端驗證（絕不信任客戶端傳來的 userId）
- **安全清單**：完整的安全實作要點

**觸發情境**：「LINE Login 整合」、「用 LINE 帳號登入」、「OAuth PKCE 實作」

---

### line-liff — LIFF（LINE 前端框架）

在 LINE 聊天中執行的網頁應用程式開發：

- **初始化**：`liff.init()` 正確用法、`withLoginOnExternalBrowser`
- **核心 API**：`getProfile()`、`sendMessages()`、`closeWindow()`、`scanCodeV2()`、`shareTargetPicker()`
- **環境偵測**：`isInClient()`、`getOS()`、`getContext()`
- **LIFF 瀏覽器 vs 外部瀏覽器**：功能差異對照表
- **Pluggable SDK**：按需匯入，減少打包體積約 34%
- **LIFF 插件**：自訂插件開發、hooks 系統
- **開發與測試**：ngrok 本機開發、LIFF CLI

**觸發情境**：「LIFF 開發」、「liff.init() 怎麼用」、「LIFF 應用程式」

---

### line-mini-app — LINE MINI App

在 LINE 內部運行的完整服務應用程式：

- **Console 設定**：三個內部通道（LINE Login、Messaging API、MINI App）
- **服務訊息**：Notification Token 取得與儲存、服務訊息發送 API
- **Common Profile 快速填寫**：使用者個人資料自動填入
- **內購（IAP）**：商品查詢、購買流程、收據驗證
- **審核上架**：未認證 → 已認證流程、提交清單、常見退件原因
- **效能指南**：首次內容繪製 < 3 秒目標

**觸發情境**：「LINE MINI App 開發」、「服務訊息」、「MINI App 上架審核」

---

### line-notification-message — LINE 通知訊息

企業客戶專用的手機號碼推播服務：

- **兩種類型**：Template（無需 UX 審查）vs Flexible（需審查）
- **手機號碼 Hash**：E.164 格式 → SHA256（非 HMAC）
- **API 端點**：`/pnp/templated/push`（202 非同步）vs `/bot/pnp/push`（200 同步）
- **5 個送達條件**：全部滿足才能成功送達
- **送達 Webhook**：追蹤送達狀態
- **速率限制**：2,000 req/秒、錯誤處理

**觸發情境**：「LINE 通知訊息」、「手機號碼推播」、「LINE PNP API」

---

## 測試與優化

本套件內建完整的 skill 測試與自動優化工具：

```bash
# 測試所有 skills 的觸發準確率
./scripts/test_all.sh

# 測試單一 skill
./scripts/test_skill.sh messaging-api

# 自動優化 skill description（最多 5 次 AI 迭代）
./scripts/test_skill.sh messaging-api --max-iterations 5 --verbose

# 使用真實 claude CLI 進行端對端測試
./scripts/test_skill_e2e.sh messaging-api --runs 3
```

### 測試資料格式

**`scripts/test-data/<skill>/assessment_set.json`**

```json
[
  { "query": "如何建立 LINE 機器人？", "should_trigger": true },
  { "query": "LINE Login 怎麼整合？",  "should_trigger": false }
]
```

**`scripts/test-data/<skill>/scope.json`**

```json
{
  "knowledge_domain": "LINE Messaging API",
  "assess_scope": ["- 此 skill 只涵蓋 Messaging API，不包含 LIFF、LINE Login..."],
  "improve_scope": ["- 此 skill 只涵蓋 Messaging API..."]
}
```

### `optimize_description.py` 運作原理

1. 讀取 `SKILL.md` 中的 `description` 欄位
2. 對每個測試查詢請 Claude 判斷「是否應該觸發此 skill」
3. 統計準確率；若有失敗案例且 `--max-iterations > 1`，請 Claude 重寫 description
4. 反覆迭代直到達到 100% 或迭代次數耗盡
5. 自動更新 `SKILL.md` 中的 description

---

## 專案結構

```
.claude-plugin/
└── plugin.json            ← Marketplace 發布設定

skills/
├── messaging-api/
│   ├── SKILL.md           ← 主要 skill 指令（雙語 description）
│   ├── assets/examples/   ← Flex Message JSON 範例
│   │   ├── product-card.json
│   │   ├── receipt.json
│   │   └── confirmation.json
│   └── references/        ← 詳細 API 參考文件
│       ├── channel-token.md
│       ├── message-objects.md
│       ├── message-sending.md
│       ├── flex-message.md
│       ├── rich-menu.md
│       └── webhook-events.md
├── line-login/
│   └── references/
│       ├── oauth-flow.md
│       ├── security.md
│       ├── token-management.md
│       └── user-profile.md
├── line-liff/
│   └── references/
│       ├── api.md
│       ├── plugins.md
│       ├── server-auth.md
│       ├── guidelines.md
│       ├── navigation.md
│       └── cli.md
├── line-mini-app/
│   └── references/
│       ├── service-messages.md
│       ├── in-app-purchase.md
│       ├── console-setup.md
│       └── submission-review.md
└── line-notification-message/
    └── references/
        ├── sending-api.md
        ├── technical-specs.md
        ├── template-system.md
        └── delivery-webhook.md

scripts/
├── optimize_description.py  ← AI 自動優化觸發準確率
├── test_skill.sh            ← 單一 skill 測試
├── test_all.sh              ← 全部 skill 測試
├── test_skill_e2e.sh        ← 端對端測試（真實 claude CLI）
└── test-data/
    ├── messaging-api/
    │   ├── assessment_set.json  ← 測試查詢（中英文）
    │   └── scope.json           ← 知識邊界定義
    ├── line-login/
    ├── line-liff/
    ├── line-mini-app/
    └── line-notification-message/
```

## 設計原則

**雙語觸發**：每個 skill 的 `description` 同時包含英文和繁體中文關鍵詞，確保中英文查詢都能正確觸發。

**邊界清晰**：每個 skill 嚴格定義涵蓋範圍，避免跨 skill 誤觸發（例如 messaging-api skill 不會在問 LINE Login 問題時觸發）。

**回應語言跟隨**：所有 skill 指示 Claude 用使用者的提問語言回答——中文問就中文答，英文問就英文答。

**安全優先**：每個 skill 預設包含安全最佳實踐（Webhook 簽章驗證、PKCE、Token 管理等），不需要另外詢問。

## 授權

Apache 2.0
