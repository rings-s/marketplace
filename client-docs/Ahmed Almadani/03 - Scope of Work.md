---
title: Scope of Work — MKT-2026-001
client: Ahmed Almadani
project: KSA Furniture Marketplace
tags:
  - client/ahmed-almadani
  - scope
---

# Scope of Work
### Project: KSA Furniture Marketplace — MKT-2026-001

> [!info]
> This document defines the complete product scope for the KSA Furniture Marketplace Platform. It covers all user-facing features and API capabilities included in [[01 - Invoice #MKT-2026-001]].

---

## Platform Overview

A bilingual (Arabic & English) online marketplace for buying and selling furniture in Saudi Arabia, supporting individual sellers and registered stores, with real-time chat, secure payments, and a native mobile app.

---

## Module 1 — Backend API Platform

### 1.1 Authentication & Security

**Capabilities:**
- Google sign-in (one-tap login for mobile)
- OTP phone verification (Saudi mobile numbers)
- Secure session management with auto-refresh
- Role-based access control (Buyer, Individual Seller, Store Seller, Admin)
- Device registration for push notifications

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/google` | Sign in with Google |
| POST | `/api/v1/auth/refresh` | Refresh authentication session |
| POST | `/api/v1/auth/logout` | End session |
| POST | `/api/v1/otp/send` | Send OTP to mobile number |
| POST | `/api/v1/otp/verify` | Verify OTP code |
| POST | `/api/v1/devices/token` | Register device for push notifications |
| DELETE | `/api/v1/devices/token` | Unregister device |

---

### 1.2 User Profile Management

**Capabilities:**
- View and update personal profile (name, phone, city, avatar)
- View any user's public profile

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get my profile |
| PATCH | `/api/v1/users/me` | Update my profile |
| GET | `/api/v1/users/{id}` | View a public user profile |

---

### 1.3 Store Management

**Capabilities:**
- Create and manage a seller store
- Store profile with name, logo, description, and commercial registration
- Store ratings and reviews

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/stores` | Create a store |
| GET | `/api/v1/stores/me` | Get my store |
| GET | `/api/v1/stores/{id}` | Get any store's public profile |
| PATCH | `/api/v1/stores/{id}` | Update my store |

---

### 1.4 Listings Management

**Capabilities:**
- Create listings with bilingual title and description (AR/EN)
- Set price, condition, category, city, and GPS location
- Attach multiple photos per listing
- Edit or delete listings
- Track view counts per listing
- Filter listings by city, category, condition, price range, and keyword search
- Infinite-scroll listing feed

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/items` | Browse listings (filtered & paginated) |
| POST | `/api/v1/items` | Create a new listing |
| GET | `/api/v1/items/{id}` | Get listing detail |
| PATCH | `/api/v1/items/{id}` | Update a listing |
| DELETE | `/api/v1/items/{id}` | Remove a listing |

---

### 1.5 Media Upload

**Capabilities:**
- Batch upload up to 10 photos per request
- Client uploads directly to cloud storage (fast, no server bottleneck)
- Photo confirmation after upload

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/uploads/presigned` | Request upload links (1–10 photos) |
| POST | `/api/v1/uploads/confirm` | Confirm successful photo uploads |

---

### 1.6 Favorites / Wishlist

**Capabilities:**
- Save and unsave listings to a personal wishlist
- View all saved listings

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/favorites/{item_id}` | Save a listing |
| DELETE | `/api/v1/favorites/{item_id}` | Remove from wishlist |
| GET | `/api/v1/favorites` | View my wishlist |

---

### 1.7 Real-Time Chat

**Capabilities:**
- Buyer initiates a conversation linked to a specific listing
- Real-time messaging between buyer and seller
- Support for text messages and image sharing
- Read receipts and typing indicators
- Message history (paginated)
- Works on mobile even with brief connectivity interruptions

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/threads` | Start a conversation |
| GET | `/api/v1/chat/threads` | List my conversations |
| GET | `/api/v1/chat/threads/{id}/messages` | Load message history |
| POST | `/api/v1/chat/threads/{id}/messages` | Send a message |
| WS | `/ws?token=...` | Live messaging connection |

---

### 1.8 Price Offers & Negotiation

**Capabilities:**
- Buyer submits a price offer on a listing
- Seller can accept, reject, or counter-offer
- Full negotiation history per order
- One active offer at a time per conversation (clean flow)

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders/{id}/offers` | Submit an offer |
| PATCH | `/api/v1/orders/{id}/offers/{offer_id}/accept` | Accept an offer |
| PATCH | `/api/v1/orders/{id}/offers/{offer_id}/reject` | Reject an offer |
| PATCH | `/api/v1/orders/{id}/offers/{offer_id}/counter` | Counter-offer |
| GET | `/api/v1/orders/{id}/offers` | View offer history |

---

### 1.9 Orders & Transaction Management

**Capabilities:**
- Order created when buyer initiates a purchase inquiry
- Order statuses: Inquiry → Reserved → Completed / Cancelled
- Buyer and seller can cancel before completion
- Full order history for both parties

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Create an order |
| GET | `/api/v1/orders` | List my orders |
| GET | `/api/v1/orders/{id}` | Order detail |
| PATCH | `/api/v1/orders/{id}/cancel` | Cancel an order |

---

### 1.10 Payments

**Capabilities:**
- Secure payment checkout (credit card, STC Pay, Apple Pay)
- Saudi-compliant payment gateway integration
- 1% platform fee deducted automatically
- Payment status tracking
- Refund support
- Webhook-based real-time payment confirmation

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/checkout` | Initiate payment |
| GET | `/api/v1/payments/callback` | Confirm payment after 3D Secure |
| POST | `/api/v1/payments/webhook` | Payment gateway event handler |
| POST | `/api/v1/payments/{id}/refund` | Refund a payment (admin) |

---

### 1.11 Reviews & Ratings

**Capabilities:**
- Buyer leaves a review after a completed order
- Star rating (1–5) with written comment
- Seller/store rating aggregate displayed on profiles

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reviews` | Leave a review |
| GET | `/api/v1/reviews/users/{id}` | View a user's reviews |

---

### 1.12 Push Notifications

**Capabilities:**
- New message alerts
- Offer received / accepted / rejected alerts
- Order status updates
- Review received notification

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| Automated | — | Triggered by platform events |

---

### 1.13 Tags & Categories

**Capabilities:**
- Predefined category and tag system (bilingual AR/EN)
- Attach tags to listings for better discoverability

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tags` | List all tags |
| POST | `/api/v1/tags` | Create tag (admin) |

---

### 1.14 Content Reporting & Moderation

**Capabilities:**
- Users can report listings, users, or stores
- Admin review queue for reports

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports` | Submit a report |
| GET | `/api/v1/reports` | Admin: view reports |
| PATCH | `/api/v1/reports/{id}` | Admin: update report status |

---

### 1.16 SMS Gateway Integration

**Capabilities:**
- OTP codes delivered via SMS to Saudi mobile numbers (+9665XXXXXXXX)
- Integration with OurSMS (oursms.com) — Saudi-native SMS provider
- Graceful fallback: SMS failure does not block OTP generation
- Arabic message body for OTP delivery
- Rate limiting: one OTP per minute per user

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/otp/send` | Send OTP via SMS to verified Saudi number |
| POST | `/api/v1/otp/verify` | Verify submitted OTP code |

> **Note:** OurSMS account credentials (App SID, App Secret, Sender ID) are the client's responsibility.

---

### 1.17 Location & Map Features

**Capabilities:**
- Forward geocoding: convert an address or city name to GPS coordinates
- Reverse geocoding: convert GPS coordinates to a human-readable address
- Proximity search: find listings within a configurable radius (0.1–100 km)
- Results sorted by distance (nearest first)
- Open-source stack — no Google Maps API key required; powered by Nominatim (OpenStreetMap)
- Restricted to Saudi Arabia (`countrycodes=sa`)

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/geocode/reverse?lat=&lon=` | Reverse geocode coordinates to address |
| POST | `/api/v1/geocode/search` | Forward geocode: address/city → coordinates |
| GET | `/api/v1/items/nearby?lat=&lon=&radius_km=&size=` | List nearby listings with distance |

**Mobile Integration:**
- Leaflet.js for web map display
- `react-native-maps` for native iOS & Android map view
- Listing creation: GPS auto-fill with manual override option
- Listing detail: map pin showing item location

---

### 1.15 Notifications Center

**Capabilities:**
- In-app notification inbox
- Mark individual or all notifications as read
- Persistent notification history

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | List my notifications |
| PUT | `/api/v1/notifications/{id}/read` | Mark one as read |
| POST | `/api/v1/notifications/read-all` | Mark all as read |

---

## Module 2 — Mobile Application (iOS & Android)

### Screens & Features

| Screen | Description |
|--------|-------------|
| Splash & Onboarding | First-launch welcome, language selection |
| Login / Sign-In | Google sign-in, phone OTP verification |
| Home Feed | Listings grid with search bar and filters |
| Search & Filter | Full filtering: city, category, condition, price |
| Listing Detail | Photos carousel, price, seller info, offer button |
| Create Listing | Multi-photo upload, bilingual fields, location picker |
| Edit Listing | Same form pre-filled for updates |
| Chat List | All conversations, last message preview |
| Chat Screen | Real-time messaging, image sharing |
| Offer Flow | Submit, accept, reject, counter-offer |
| Orders | Buyer and seller order lists with status |
| Order Detail | Full order timeline and actions |
| Payment Checkout | Card, STC Pay, Apple Pay |
| My Profile | Avatar, stats, listings, reviews |
| Store Profile | Store info, listings, ratings |
| Favorites | Saved listings grid |
| Notifications | In-app notification center |
| Settings | Language, account, logout |

### Platform Support
- iOS 15+ (iPhone and iPad)
- Android 10+ (phone and tablet)
- Arabic (RTL) and English (LTR) fully supported
- Optimized for offline-first experience

---

## Module 3 — Delivery & Handoff

| Deliverable | Description |
|------------|-------------|
| Production Deployment | Platform deployed to production environment |
| Admin Credentials | All accounts and access keys handed to client |
| API Reference | Full endpoint documentation |
| Environment Setup Guide | How to configure and maintain the platform |
| UAT Support | Developer available for 2 weeks post-delivery for critical bug fixes |

---

## Exclusions (Not In Scope)

The following are **not included** in this agreement:
- Admin dashboard web panel (can be quoted separately)
- AI recommendation engine
- Ongoing maintenance after the 30-day warranty period
- Third-party service subscriptions (hosting, payment gateway, SMS, storage)
- Content creation (photos, descriptions, data entry)

---

> [!note] Related Documents
> - [[01 - Invoice #MKT-2026-001]] — Pricing breakdown
> - [[02 - Development Contract]] — Legal terms
> - [[00 - Hub]] — Project dashboard
