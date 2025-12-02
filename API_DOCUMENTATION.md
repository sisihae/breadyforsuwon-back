# BreadyForSuwon API Documentation

## Overview

BreadyForSuwon is a RAG-powered bakery recommendation chatbot backend for exploring bakeries in Suwon. It provides user authentication, bakery search, wishlist management, visit record tracking, and chat history.

**Base URL:** `http://localhost:8000/api/v1`

---

## Authentication

### Login with Kakao OAuth

**Endpoint:** `GET /auth/kakao/login`

**Description:** Returns the Kakao OAuth authorize URL for the frontend to redirect users to.

**Response:**

```json
{
  "authorize_url": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}
```

---

### Kakao OAuth Callback

**Endpoint:** `GET /auth/kakao/callback`

**Query Parameters:**

- `code` (string, required): Authorization code from Kakao

**Description:** Exchanges authorization code for access token, fetches user profile, creates/finds user in DB, and sets HTTP-only session cookie.

**Response:** Redirects to frontend URL with session cookie set.

**Cookie:**

- `session`: JWT token (HttpOnly, SameSite=lax)
- Max-Age: 7 days

---

### Logout

**Endpoint:** `POST /auth/logout`

**Description:** Clears the session cookie to log out the user.

**Response:**

```json
{
  "ok": true
}
```

---

### Get Current User Profile

**Endpoint:** `GET /me`

**Authentication:** Required (session cookie)

**Description:** Returns current user profile with visit records count and wishlist count.

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-01T10:00:00",
  "visit_records_count": 5,
  "wishlist_count": 3
}
```

---

## Bakeries

### Get All Bakeries

**Endpoint:** `GET /bakeries`

**Query Parameters:**

- `skip` (integer, optional, default=0): Number of records to skip
- `limit` (integer, optional, default=10): Number of records to return

**Description:** Returns list of all bakeries.

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "르뱅드마리",
    "address": "경기 수원시 팔달구 행궁로 30",
    "rating": 4.8
  }
]
```

---

### Get Bakery by ID

**Endpoint:** `GET /bakeries/{bakery_id}`

**Path Parameters:**

- `bakery_id` (UUID): Bakery ID

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "르뱅드마리",
  "address": "경기 수원시 팔달구 행궁로 30",
  "rating": 4.8,
  "bread_tags": ["Croissant", "Sourdough"]
}
```

---

## Bread Tags

### Get All Bread Tags

**Endpoint:** `GET /tags`

**Description:** Returns list of all available bread tags/types.

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Croissant"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Sourdough"
  }
]
```

---

### Get Bakeries by Tag

**Endpoint:** `GET /tags/{tag_name}/bakeries`

**Path Parameters:**

- `tag_name` (string): Name of the bread tag

**Description:** Returns list of bakeries that sell a specific bread type.

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "르뱅드마리",
    "address": "경기 수원시 팔달구 행궁로 30",
    "rating": 4.8
  }
]
```

---

## Chat & Search

### Chat with RAG Bot

**Endpoint:** `POST /chat`

**Authentication:** Optional

**Request Body:**

```json
{
  "message": "수원에서 맛있는 크루아상 파는 빵집 추천해줘",
  "bread_tags": ["Croissant"]
}
```

**Description:** Sends a message to the RAG chatbot. Returns AI-generated response with relevant bakeries.

**Response:**

```json
{
  "response": "수원에서 크루아상을 파는 빵집 중에 르뱅드마리가 유명합니다...",
  "bakeries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "르뱅드마리",
      "address": "경기 수원시 팔달구 행궁로 30"
    }
  ]
}
```

---

### Search Bakeries

**Endpoint:** `POST /search`

**Request Body:**

```json
{
  "query": "크루아상",
  "bread_tags": ["Croissant"]
}
```

**Description:** Searches bakeries by query and optional bread tags using vector embeddings.

**Response:**

```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "르뱅드마리",
      "address": "경기 수원시 팔달구 행궁로 30",
      "score": 0.92
    }
  ]
}
```

---

### Get Chat History

**Endpoint:** `GET /chat/history`

**Authentication:** Optional

**Query Parameters:**

- `limit` (integer, optional, default=100): Number of recent records to return

**Description:** Returns recent chat history entries with metadata.

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_message": "수원 빵집 추천해줘",
    "bot_response": "수원의 인기 빵집들을 소개합니다...",
    "metadata_json": {
      "sources": ["르뱅드마리", "베이커리카페 밀"],
      "bread_tags": ["Croissant"],
      "bakery_ids": ["550e8400-e29b-41d4-a716-446655440000"]
    },
    "created_at": "2025-12-01T10:00:00"
  }
]
```

---

## Wishlist

### Get All Wishlist Items

**Endpoint:** `GET /wishlist`

**Authentication:** Required (session cookie)

**Description:** Returns all wishlist items for the current user.

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "bakery_id": "550e8400-e29b-41d4-a716-446655440002",
    "bakery_name": "르뱅드마리",
    "bakery_address": "경기 수원시 팔달구 행궁로 30",
    "bread_types": ["Croissant", "Sourdough"],
    "note": null,
    "visited": false,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-01T10:00:00"
  }
]
```

---

### Create Wishlist Item

**Endpoint:** `POST /wishlist`

**Authentication:** Required (session cookie)

**Request Body:**

```json
{
  "bakery_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Description:** Adds a bakery to the current user's wishlist.

**Response:** Same as Get Wishlist Item above.

---

### Update Wishlist Item

**Endpoint:** `PATCH /wishlist/{item_id}`

**Authentication:** Required (session cookie)

**Path Parameters:**

- `item_id` (UUID): Wishlist item ID

**Request Body:**

```json
{
  "note": "친구 추천 빵집",
  "visited": true
}
```

**Description:** Updates note and/or visited status of a wishlist item.

**Response:** Same as Get Wishlist Item above.

---

### Delete Wishlist Item

**Endpoint:** `DELETE /wishlist/{item_id}`

**Authentication:** Required (session cookie)

**Path Parameters:**

- `item_id` (UUID): Wishlist item ID

**Description:** Removes a bakery from the current user's wishlist.

**Response:**

```json
{
  "ok": true
}
```

---

## Visit Records

### Get All Visit Records

**Endpoint:** `GET /visit-records`

**Authentication:** Required (session cookie)

**Description:** Returns all visit records for the current user, sorted by visit date (most recent first).

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "bakery_id": "550e8400-e29b-41d4-a716-446655440002",
    "bakery_name": "르뱅드마리",
    "bakery_address": "경기 수원시 팔달구 행궁로 30",
    "visit_date": "2025-12-02",
    "rating": 5,
    "bread_purchased": "크루아상, 바게트",
    "review": "정말 맛있었어요!",
    "created_at": "2025-12-02T10:00:00",
    "updated_at": "2025-12-02T10:00:00"
  }
]
```

---

### Create Visit Record

**Endpoint:** `POST /visit-records`

**Authentication:** Required (session cookie)

**Request Body:**

```json
{
  "bakery_id": "550e8400-e29b-41d4-a716-446655440000",
  "visit_date": "2025-12-02",
  "rating": 5,
  "bread_purchased": "크루아상, 바게트",
  "review": "정말 맛있었어요!"
}
```

**Description:** Creates a new visit record for a bakery.

**Response:** Same as Get Visit Records above.

---

### Update Visit Record

**Endpoint:** `PATCH /visit-records/{record_id}`

**Authentication:** Required (session cookie)

**Path Parameters:**

- `record_id` (UUID): Visit record ID

**Request Body:**

```json
{
  "rating": 4,
  "review": "다시 가고 싶어요!"
}
```

**Description:** Updates visit date, rating, bread purchased, and/or review.

**Response:** Same as Get Visit Records above.

---

### Delete Visit Record

**Endpoint:** `DELETE /visit-records/{record_id}`

**Authentication:** Required (session cookie)

**Path Parameters:**

- `record_id` (UUID): Visit record ID

**Description:** Deletes a visit record.

**Response:**

```json
{
  "ok": true
}
```

---

## Error Responses

All endpoints return standard HTTP error codes with descriptive messages:

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden

```json
{
  "detail": "Cannot modify another user's data"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Data Models

### User

- `id` (UUID): Unique identifier
- `kakao_id` (string, optional): Kakao account ID
- `email` (string, optional): Email address
- `name` (string, optional): User display name
- `created_at` (datetime): Account creation timestamp

### Bakery

- `id` (UUID): Unique identifier
- `name` (string): Bakery name
- `address` (string): Bakery address
- `rating` (float): Average rating (1-5)
- `bread_tags` (array): List of bread types sold

### BreadTag

- `id` (UUID): Unique identifier
- `name` (string): Tag name (e.g., "Croissant")

### WishlistItem

- `id` (UUID): Unique identifier
- `user_id` (UUID): Owner user ID
- `bakery_id` (UUID): Associated bakery ID
- `note` (string, optional): User's note
- `visited` (boolean): Whether user has visited
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### BakeryVisitRecord

- `id` (UUID): Unique identifier
- `user_id` (UUID): Owner user ID
- `bakery_id` (UUID): Associated bakery ID
- `visit_date` (date): Date of visit
- `rating` (integer): Rating from 1-5
- `bread_purchased` (string, optional): Description of bread purchased
- `review` (string, optional): User's review
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### ChatHistory

- `id` (UUID): Unique identifier
- `user_message` (string): User's chat message
- `bot_response` (string): Bot's response
- `metadata_json` (object): Contains sources, bread_tags, bakery_ids
- `created_at` (datetime): Creation timestamp

---

## Pagination

List endpoints support optional pagination parameters:

- `skip` (integer, default=0): Number of records to skip
- `limit` (integer, default=10): Number of records to return

Example:

```
GET /bakeries?skip=10&limit=20
```

---

## Authentication Details

### Session Cookie

- **Name:** `session` (configurable)
- **Value:** JWT token containing user ID
- **HttpOnly:** True (prevents JavaScript access)
- **Secure:** True in production, False in development
- **SameSite:** `lax`
- **Max-Age:** 604800 seconds (7 days)

### How to Authenticate

1. Call `GET /auth/kakao/login` to get authorize URL
2. Redirect user to Kakao authorize URL
3. After user consents, Kakao redirects to callback
4. Backend creates user and sets session cookie
5. Include session cookie in all authenticated requests

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions may implement request throttling.

---

## Environment Variables

Configure via `.env` file:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/breadyforsuwon

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXP_SECONDS=604800
SESSION_COOKIE_NAME=session

# Kakao OAuth
KAKAO_CLIENT_ID=your_client_id
KAKAO_CLIENT_SECRET=your_client_secret
KAKAO_REDIRECT_URI=http://localhost:3000/auth/kakao/callback
FRONTEND_URL=http://localhost:3000

# App
DEBUG=True
API_V1_PREFIX=/api/v1

# OpenAI
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4

# Pinecone (Vector DB)
PINECONE_API_KEY=your_api_key
PINECONE_INDEX=bakeries
```

---

## Testing

Run all tests:

```bash
pytest -q
```

Run specific test file:

```bash
pytest -q tests/test_auth.py
pytest -q tests/test_wishlist.py
pytest -q tests/test_visit_records.py
pytest -q tests/test_me.py
```

---

## Development

### Start Server

```bash
uvicorn app.main:app --reload
```

### View API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Version

- **API Version:** v1
- **Last Updated:** December 2025
