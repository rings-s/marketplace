# UX Features Design — KSA Furniture Marketplace
**Date:** 2026-03-07
**Target client:** Mobile (React Native + Expo SDK 55)
**Constraint:** No AI features

---

## Scope & Priority Order

| # | Feature | Mobile unblocking value |
|---|---------|------------------------|
| 1 | GZip + Response envelope | All endpoints consistent immediately |
| 2 | Cursor pagination | Home screen infinite scroll |
| 3 | Multi-photo presigned S3 upload | Sellers can create real listings |
| 4 | Phone OTP (Redis only) | Trust gate before order flow |
| 5 | Order negotiation | Core marketplace transaction flow |
| 6 | Reviews & ratings | Seller trust after completed orders |
| 7 | Expo push notifications | Real-time event delivery to device |
| 8 | Redis response caching | Performance UX on item/store detail |

---

## New Domain Models

### PhoneOTP (Redis only — no DB table)
```
key:   otp:{user_id}
value: {code: "123456", attempts: 0}
TTL:   300 seconds
```

### PriceOffer
```
id UUID PK
order_id FK(Order)
offered_by FK(User)
amount_sar Numeric(12,2)
message str nullable
status enum(pending/accepted/rejected/countered/superseded)
created_at
```

### Notification
```
id UUID PK
user_id FK(User)
type enum(new_message/offer_received/offer_accepted/offer_rejected/order_update/review_received)
title_ar str
title_en str
body_ar str
body_en str
data JSONB
is_read bool default False
created_at
```

### Review
```
id UUID PK
order_id FK(Order) UNIQUE
reviewer_id FK(User)
reviewee_id FK(User)
rating int CHECK(1..5)
comment str nullable
created_at
```

### ExpoToken
```
user_id FK(User) PK
token str
created_at
updated_at
```

---

## API Contracts

### Response Envelope (all endpoints)
```json
{
  "success": true,
  "data": { ... },
  "meta": { "request_id": "uuid", "locale": "ar" }
}
```

### Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message_ar": "المورد غير موجود",
    "message_en": "Resource not found"
  },
  "meta": { "request_id": "uuid", "locale": "ar" }
}
```

### Uploads
```
POST /api/v1/uploads/presigned   body: {count: 1-10, item_id?: uuid}
  → [{upload_url, key, photo_index}]

POST /api/v1/uploads/confirm     body: {keys: [str]}
  → [{key, url}]
```

### OTP
```
POST /api/v1/otp/send            body: {phone: "+9665XXXXXXXX"}
  → {expires_in: 300}            rate-limited: 1/60s per user

POST /api/v1/otp/verify          body: {phone, code}
  → {verified: true}             max 3 attempts, sets user.is_verified=True
```

### Orders (negotiation flow)
```
POST /api/v1/orders                             → OrderResponse (inquiry)
GET  /api/v1/orders                             → paginated list
GET  /api/v1/orders/{id}                        → OrderResponse
POST /api/v1/orders/{id}/offers                 → OfferResponse (first offer)
POST /api/v1/orders/{id}/offers/{oid}/accept    → OfferResponse
POST /api/v1/orders/{id}/offers/{oid}/reject    → OfferResponse
POST /api/v1/orders/{id}/offers/{oid}/counter   → OfferResponse (new offer, old=superseded)
POST /api/v1/orders/{id}/cancel                 → OrderResponse
```

### Reviews
```
POST /api/v1/reviews             body: {order_id, rating: 1-5, comment?}
  → ReviewResponse               only buyer, only after order.status=completed

GET  /api/v1/users/{id}/reviews  → paginated ReviewResponse list
```

### Notifications
```
GET  /api/v1/notifications              ?cursor=&size=20  → {items, next_cursor, has_more}
PUT  /api/v1/notifications/{id}/read                      → NotificationResponse
POST /api/v1/notifications/read-all                       → {count: n}
```

### Device Tokens
```
POST /api/v1/devices/token       body: {token: "ExponentPushToken[...]"}
  → {registered: true}
DELETE /api/v1/devices/token     → {removed: true}
```

### Items (enhanced)
```
GET /api/v1/items?cursor=xxx&size=20
  → {items: [...], next_cursor: "base64str", has_more: bool, total: int}
  (cursor = base64-encoded created_at+id for stable ordering)
```

---

## Architecture Details

### Caching (cache-aside, Redis)
- `item:{id}` TTL 60s — invalidated on PATCH/DELETE
- `store:{id}` TTL 120s — invalidated on store write
- Never cache user-specific data
- `@redis_cache(key, ttl)` async decorator on service methods

### Expo Push Notification Flow
```
1. Event occurs (message, offer, order update)
2. notification.py → INSERT Notification row
3. if user has ExpoToken → arq.enqueue_job("send_expo_push", token, title, body, data)
4. worker sends httpx POST to https://exp.host/--/exponent-push-token/v2/push
5. Expo delivers to FCM/APNs — fire-and-forget, non-blocking
```

### S3 Presigned Upload Flow
```
1. POST /uploads/presigned {count: 3}
2. storage.py → boto3.generate_presigned_url("put_object") × count, TTL 600s
3. Client uploads files directly to S3 (PUT request with Content-Type: image/*)
4. POST /uploads/confirm {keys: [...]}
5. storage.py → s3.head_object() to verify each key exists
6. Returns final CDN URLs for client to patch onto item
```

### Order Negotiation State Machine
```
[created: inquiry]
  → seller posts offer          → [offer: pending, buyer's turn]
  → buyer counters              → [offer: superseded] + [new offer: pending, seller's turn]
  → seller accepts              → [offer: accepted] + [order: agreed]
  → either cancels              → [order: cancelled]
[order: agreed]
  → buyer pays                  → [order: completed]
```
Business rule: Only ONE `pending` offer per order at a time.

### OTP Rate Limiting & Security
- Redis key `otp_sent:{user_id}` TTL 60s → 429 if exists
- Redis key `otp:{user_id}` value includes `attempts` counter
- On 3 failed attempts → delete key, force re-send
- Code is 6 digits, cryptographically random (`secrets.randbelow(1_000_000)`)

---

## New Files

```
app/
  middleware/
    gzip.py              ← GZip middleware config
    response_envelope.py ← wrap all responses in {success, data, meta}
  services/
    storage.py           ← S3 presigned URL generation + confirmation
    otp.py               ← Redis OTP generate/verify
    notification.py      ← create DB notification + trigger Expo push
    order.py             ← negotiation state machine
  models/
    notification.py
    review.py
    offer.py
    device.py
  schemas/
    upload.py
    otp.py
    order.py
    review.py
    notification.py
    device.py
  repositories/
    notification.py
    review.py
    offer.py
    order.py
    device.py
  api/routers/
    uploads.py
    otp.py
    orders.py
    reviews.py
    notifications.py
    devices.py
  workers/
    tasks.py             ← add send_expo_push task
```

---

## Testing Plan
- Unit tests: OTP generate/verify logic, offer state machine transitions, fee calculation
- Integration tests: `httpx.AsyncClient` for each new router
- State machine tests: all valid and invalid transitions
