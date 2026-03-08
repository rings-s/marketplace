# Project Invoice & Scope of Work
## KSA Furniture Marketplace — Full-Stack Platform

---

| | |
|---|---|
| **Prepared for** | \[Client Name\] |
| **Prepared by** | Ahmed |
| **Date** | March 8, 2026 |
| **Invoice #** | MKT-2026-001 |
| **Currency** | USD |

---

## Executive Summary

A production-grade, KSA-compliant second-hand and new furniture marketplace platform — built for the Saudi market from the ground up. The platform covers a complete FastAPI backend (REST API + WebSocket) and a React Native mobile application (iOS + Android), with full Arabic/English bilingual support, Saudi phone verification, Moyasar payment integration, and real-time chat.

---

## Platform Overview

| Layer | Technology |
|---|---|
| Backend API | Python 3.12 + FastAPI 0.115 + Granian ASGI |
| Database | PostgreSQL 17 + SQLAlchemy 2.0 async |
| Cache / Pub-Sub | Redis 7 |
| Background Workers | arq (async job queue) |
| Mobile App | React Native + Expo SDK 55 (iOS + Android) |
| Payments | Moyasar (Saudi payment gateway) |
| Storage | S3-compatible (photos/media) |
| Auth | Google OAuth 2.0 + JWT (access + refresh) |
| Real-Time | WebSocket + Redis pub/sub |
| Deployment | Docker + docker-compose + CI/CD (GitHub Actions) |

---

## Part 1 — Backend API

### 1.1 Core Infrastructure

- **Clean hexagonal architecture** — Routers → Services → Repositories → Models. Each layer is independently testable and replaceable.
- **Async throughout** — Every database query, cache call, and HTTP request is fully async; no blocking I/O.
- **GZip compression** — All API responses compressed at minimum 500 bytes. Reduces mobile data usage by 40–70%.
- **Response envelope** — Every endpoint returns a consistent `{success, data, meta}` structure with request ID and locale, making mobile integration predictable.
- **Correlation ID middleware** — Every request tagged with a UUID propagated through logs for traceability.
- **Locale middleware** — Detects `Accept-Language: ar` / `en` and sets locale context for bilingual responses.
- **Prometheus metrics** — Live request count, latency histograms, and error rates exposed at `/metrics`.
- **Structured logging** — JSON logs via `structlog` with request ID, user ID, and operation context.
- **Rate limiting** — `slowapi` with per-route and global limits (200 req/min default, 1 OTP/min per user).
- **CORS** — Configurable allowed origins per environment.
- **Docker + docker-compose** — Full local environment: PostgreSQL 17, Redis 7, backend, and worker in one command.
- **GitHub Actions CI** — Lint (ruff), type check (mypy), test suite (pytest + coverage), and Docker build on every push.
- **Alembic migrations** — Version-controlled database schema with async migration engine.

---

### 1.2 Authentication & Users

- **Google OAuth 2.0** — ID token verification via `google-auth`. Upserts user on first login (links existing email accounts).
- **JWT access tokens** — 15-minute expiry, signed with HS256.
- **JWT refresh tokens** — 30-day expiry, stored in HttpOnly cookie (XSS-safe).
- **Role-based access control** — Four roles: `buyer`, `seller_individual`, `seller_store`, `admin`.
- **KSA phone validation** — Regex `^\+9665\d{8}$` enforced at schema level.
- **Phone OTP verification** — 6-digit cryptographically random code stored in Redis with 5-minute TTL, 60-second resend rate limit, 3-attempt lockout. Sets `user.is_verified = True` on success.
- **User profiles** — Full name, username, avatar, city, phone, role, verified status.
- **Password-free** — Auth is entirely Google OAuth + OTP; no stored passwords.

**Endpoints:** `POST /auth/google`, `POST /auth/refresh`, `POST /auth/logout`, `GET /users/me`, `PATCH /users/me`, `GET /users/{id}`

---

### 1.3 Stores

- One store per seller account (enforced at DB level).
- Commercial register number, store name, logo, description.
- Verified badge (admin-granted).
- Live average rating — recalculated automatically after each review.

**Endpoints:** `POST /stores`, `GET /stores/me`, `GET /stores/{id}`, `PATCH /stores/{id}`

---

### 1.4 Furniture Listings (Items)

- **Bilingual titles and descriptions** — Arabic + English fields for every item.
- **Condition grading** — `new`, `like_new`, `good`, `fair`.
- **Categories and tags** — Free-form category + structured tag system (admin-managed tags, many-to-many).
- **Multi-photo upload** — Presigned S3 PUT URLs (batch 1–10 photos). Client uploads directly to S3; no files pass through the server.
- **Geolocation** — City + latitude/longitude for map display.
- **Status lifecycle** — `active` → `reserved` → `sold` / `deleted`.
- **View counter** — Incremented on every detail fetch.
- **Seller type** — Individual seller or store listing (auto-linked to store).
- **Cursor-based pagination** — Stable infinite scroll using base64-encoded `created_at + id` cursor. No duplicate items between pages when new listings appear.
- **Advanced filtering** — City, category, condition, seller type, price range (min/max), full-text search (Arabic + English title).
- **Redis caching** — Item detail cached 60 seconds. Invalidated on update/delete.

**Endpoints:** `GET /items` (cursor + filters), `GET /items/{id}`, `POST /items`, `PATCH /items/{id}`, `DELETE /items/{id}`

---

### 1.5 Multi-Photo S3 Upload

- Client requests 1–10 presigned PUT URLs in a single call.
- Each URL is valid for 10 minutes.
- Client uploads directly to S3 (no bandwidth cost to the server).
- Client confirms uploads; server verifies via `head_object` and returns final CDN URLs.
- Supports custom S3-compatible endpoints (MinIO, Cloudflare R2, etc.).

**Endpoints:** `POST /uploads/presigned`, `POST /uploads/confirm`

---

### 1.6 Real-Time Chat (WebSocket)

- **Per-user Redis channels** — `chat:user:{id}` pub/sub. Scales horizontally across multiple backend instances.
- **Thread model** — One thread per buyer–seller–item combination.
- **Message types** — Text, image (URL), voice (URL).
- **Read receipts** — Per-message `is_read` flag.
- **Typing indicators** — Real-time typing event broadcast to the other party.
- **HTTP fallback** — REST endpoints for sending messages when WebSocket is unavailable.
- **JWT authentication over WebSocket** — Token passed as query parameter on connect.

**Events:** `message`, `typing`, `read` | **Endpoints:** `GET /chat/threads`, `POST /chat/threads`, `GET /chat/threads/{id}/messages`, `POST /chat/threads/{id}/messages`

---

### 1.7 Order Negotiation (State Machine)

The core marketplace transaction flow — buyer and seller negotiate price before payment.

```
[inquiry created]
  → seller posts offer        → [offer: pending, buyer's turn]
  → buyer counters            → [old offer: superseded] + [new offer: pending, seller's turn]
  → either party accepts      → [offer: accepted] + [order: reserved]
  → buyer pays (Moyasar)      → [order: completed]
  → either party cancels      → [order: cancelled]
```

- **One pending offer at a time** — Posting a counter automatically supersedes the current pending offer.
- **Party enforcement** — Only parties to the order can make/accept/reject/counter offers.
- **Completed order lock** — Cancelled orders cannot be un-cancelled; completed orders cannot be cancelled.

**Endpoints:** `POST /orders`, `GET /orders`, `GET /orders/{id}`, `POST /orders/{id}/offers`, `POST /orders/{id}/offers/{oid}/accept`, `POST /orders/{id}/offers/{oid}/reject`, `POST /orders/{id}/offers/{oid}/counter`, `POST /orders/{id}/cancel`

---

### 1.8 Payments (Moyasar — KSA)

- **Moyasar integration** — Saudi-native payment gateway. Supports creditcard, stcpay, applepay.
- **1% platform fee** — Calculated to 2 decimal places on every transaction. `platform_fee = amount × 0.01`, `seller_amount = amount × 0.99`.
- **SAR / Halalas** — All amounts stored in SAR; converted to halalas (× 100) for Moyasar API calls.
- **Idempotency** — Every payment has a unique `given_id`; duplicate webhook events are ignored via `WebhookEvent` table.
- **Server-side verification** — Amount and currency verified against Moyasar after 3DS redirect (prevents tampering).
- **Webhook secret** — `hmac.compare_digest` constant-time comparison prevents timing attacks.
- **Refund support** — Full or partial refund via Moyasar API.
- **Payment status lifecycle** — `initiated` → `paid` → `completed` / `failed` / `refunded` / `voided`.

**Endpoints:** `POST /payments/checkout`, `GET /payments/callback`, `POST /payments/webhook`, `POST /payments/{id}/refund`

---

### 1.9 Reviews & Ratings

- Only the **buyer** can review after an order is `completed`.
- One review per order (enforced at DB level with `UNIQUE` constraint).
- Rating 1–5 with optional text comment (CHECK constraint in DB).
- Store average rating updated automatically after each review.

**Endpoints:** `POST /reviews`, `GET /reviews/users/{user_id}`

---

### 1.10 Expo Push Notifications

- **ExpoToken registration** — Device token stored per user (upsert on re-registration).
- **Notification record** — Every event creates a `Notification` row with Arabic and English title/body.
- **Async push delivery** — Push is enqueued to arq worker immediately; never blocks the API response.
- **Worker sends to Expo API** — `https://exp.host/--/exponent-push-token/v2/push` → FCM (Android) / APNs (iOS).
- **Notification types** — `new_message`, `offer_received`, `offer_accepted`, `offer_rejected`, `order_update`, `review_received`.
- **Read/unread tracking** — Per-notification `is_read` flag with mark-single and mark-all-read endpoints.
- **Cursor-based notification list** — Infinite scroll for notification inbox.

**Endpoints:** `POST /devices/token`, `DELETE /devices/token`, `GET /notifications`, `PUT /notifications/{id}/read`, `POST /notifications/read-all`

---

### 1.11 Favorites & Social

- Toggle favorite on any listing.
- Report system — Report items, users, or stores with admin review queue.

**Endpoints:** `POST /favorites/{item_id}`, `DELETE /favorites/{item_id}`, `GET /favorites`, `POST /reports`

---

### 1.12 Redis Response Caching

| Cache Key | TTL | Invalidated On |
|---|---|---|
| `item:{id}` | 60 seconds | `PATCH /items/{id}`, `DELETE /items/{id}` |
| `store:{id}` | 120 seconds | `PATCH /stores/{id}` |

- Cache-aside pattern — read from Redis, fall through to DB on miss, write back to Redis.
- Never caches user-specific or auth-sensitive data.

---

### 1.13 Background Worker (arq)

| Task | Trigger |
|---|---|
| `send_expo_push` | Any notification event |
| `send_notification_email` | Order/payment events |
| `send_payment_notification` | Payment status change |
| `process_image` | Post-upload image optimization (hook) |

---

## Part 2 — Mobile Application (React Native + Expo SDK 55)

### 2.1 Core Infrastructure

- **Expo SDK 55** — New Architecture (Fabric + JSI) enabled for maximum performance.
- **iOS + Android** — Single codebase targeting both platforms.
- **TanStack Query** — Server state management, caching, background refetching, optimistic updates.
- **FlashList** — High-performance virtualized list (replaces FlatList) for item feeds and chat.
- **Reanimated 3** — Smooth 60/120fps animations on the UI thread.
- **Expo Router** — File-based navigation (Stack + Tab + Modal).
- **NativeWind / Tailwind** — Utility-first styling with RTL support.
- **i18n** — Full Arabic (RTL) and English (LTR) with dynamic locale switching.
- **Zustand** — Lightweight global state (auth, locale, unread counts).

---

### 2.2 Authentication Screens

- Google Sign-In (native `expo-auth-session`)
- OTP phone verification screen with countdown timer and resend
- Profile completion (username, city, role selection)
- JWT stored securely in `expo-secure-store`
- Silent token refresh on app foreground

---

### 2.3 Home & Discovery

- **Infinite scroll feed** — FlashList + cursor pagination from backend
- **Filter bar** — City, category, condition, price range, seller type
- **Search** — Bilingual full-text search with debounce
- **Featured categories** — Horizontal scroll category chips
- **Pull-to-refresh**
- **Skeleton loaders** — While items are loading
- **Empty state** — Illustrated empty search results

---

### 2.4 Item Detail

- **Photo gallery** — Swipeable full-screen image viewer
- **Seller card** — Avatar, name, rating, verified badge
- **Price and condition** — Clear bilingual display
- **Location** — City + map pin (MapView)
- **Favorite button** — Heart toggle with optimistic update
- **Contact seller** — Opens or creates chat thread
- **Make inquiry** — Starts order flow
- **Share listing** — Native share sheet

---

### 2.5 Multi-Photo Upload (Seller Flow)

- Pick up to 10 photos from camera roll (`expo-image-picker`)
- Preview grid with reorder and delete
- Direct S3 upload (presigned URL — no server bandwidth)
- Upload progress per photo
- Confirm and attach to listing

---

### 2.6 Listing Management (Seller)

- Create listing form (bilingual fields, category, condition, price, location)
- Edit listing
- Mark as sold / delete
- My listings tab with status filters

---

### 2.7 Real-Time Chat

- Thread list with last message preview and unread badge
- Chat screen with FlashList messages
- Typing indicator (animated dots)
- Image message support
- WebSocket connection with auto-reconnect
- Offline queue (messages sent when reconnected)

---

### 2.8 Order & Negotiation Flow

- Inquiry creation from item detail
- Order detail screen showing current offer status
- Make offer / counter offer form with amount and message
- Accept / reject offer with confirmation dialog
- Status timeline (inquiry → offer → agreed → paid → completed)
- Cancel order

---

### 2.9 Payments (Moyasar)

- Checkout screen — credit card, stcPay, Apple Pay
- Moyasar WebView for 3DS authentication
- Payment callback handling
- Success / failure screens
- Payment history per order

---

### 2.10 Reviews

- Post-completion review prompt
- Star rating selector (1–5)
- Optional comment input
- Seller review list on store/profile page

---

### 2.11 Push Notifications

- Expo push token registration on login
- Notification inbox with cursor scroll
- Mark as read (single and all)
- Deep links from notification tap to relevant screen
- Badge count on tab bar

---

### 2.12 Profile & Settings

- Edit profile (name, city, avatar, phone)
- My store management
- Favorites list
- Order history
- Language switcher (AR / EN)
- Logout

---

## Deliverables

| Deliverable | Included |
|---|---|
| Backend source code (Python/FastAPI) | ✅ |
| Mobile source code (React Native/Expo) | ✅ |
| PostgreSQL schema + Alembic migrations | ✅ |
| Docker + docker-compose (local dev) | ✅ |
| GitHub Actions CI/CD pipeline | ✅ |
| `.env.example` with all required variables | ✅ |
| Automated test suite (pytest) | ✅ |
| API documentation (OpenAPI/Swagger at `/docs`) | ✅ |
| Deployment guide (Render / Fly.io / AWS) | ✅ |
| 30-day post-delivery bug fix support | ✅ |

---

## Pricing

| Component | Price (USD) |
|---|---|
| Backend API — Core infrastructure, auth, users, stores | $2,500 |
| Backend API — Listings, multi-photo upload, S3 storage | $1,500 |
| Backend API — Real-time chat (WebSocket + Redis) | $1,500 |
| Backend API — Order negotiation state machine | $1,200 |
| Backend API — Moyasar payments + webhook + 1% fee engine | $1,500 |
| Backend API — Reviews, notifications, OTP, device tokens | $1,000 |
| Backend API — Redis caching, GZip, response envelope | $500 |
| Backend API — Docker, CI/CD, migrations, test suite | $800 |
| Mobile App — Infrastructure, navigation, auth screens | $1,500 |
| Mobile App — Home feed, search, item detail, gallery | $1,200 |
| Mobile App — Chat, orders, payments, reviews | $1,800 |
| Mobile App — Push notifications, profile, settings | $700 |

| | |
|---|---|
| **Subtotal** | **$16,700** |
| **Discount (full project, single delivery)** | −$700 |
| **Total** | **$16,000 USD** |

---

## Payment Terms

| Milestone | Amount | Trigger |
|---|---|---|
| Project kickoff | $5,600 (35%) | Contract signed |
| Backend API complete | $6,400 (40%) | All API endpoints delivered + tested |
| Mobile app complete | $4,000 (25%) | App builds delivered (iOS + Android) |

---

## Timeline

| Phase | Duration |
|---|---|
| Backend API (all features) | 3 weeks |
| Mobile App | 3 weeks |
| QA, testing, and final polish | 1 week |
| **Total** | **~7 weeks** |

---

## Notes

- Moyasar **test credentials** used during development; client provides **live credentials** before final delivery.
- S3 bucket and AWS/R2 credentials provided by client.
- Google OAuth client ID provided by client.
- Apple Developer account and Google Play account required for app store submission (not included in scope).
- App store submission assistance available at **$300/platform** if needed.

---

*This document constitutes a formal scope-of-work and cost estimate. A signed contract will be issued upon client approval.*
