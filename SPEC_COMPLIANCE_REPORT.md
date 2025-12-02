# API Specification Compliance Report

## Summary
Current implementation differs from the specification in several ways:
- ✅ Some features implemented but with different structure
- ❌ Some endpoints missing or have different paths
- ⚠️ Some features use different authentication method (cookies vs Bearer tokens)

---

## Detailed Comparison

### Authentication

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `POST /api/auth/kakao` with `{code, redirectUri}` | `GET /auth/kakao/callback?code=...` | ❌ Different | Current: callback-style, redirects with cookie. Spec: code exchange endpoint |
| Response: `{user, token}` | Session cookie (HttpOnly) | ⚠️ Different | Current returns cookie, spec expects JSON with token |
| N/A | `GET /auth/kakao/login` (authorize URL) | ✅ Extra | Additional helper endpoint |
| N/A | `POST /auth/logout` | ✅ Extra | Logout support |
| N/A | `GET /me` (user profile) | ✅ Extra | Current user profile with counts |

**Action needed:** Create a new endpoint that accepts `POST /api/auth/kakao` with `{code, redirectUri}` and returns `{user, token}` instead of redirect+cookie approach.

---

### Chatbot

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `POST /api/chatbot/query` | `POST /chat` | ⚠️ Different path | Same functionality but different endpoint |
| Body: `{message, userId?}` | Body: `{message, bread_tags}` | ⚠️ Different | Spec uses userId, implementation uses bread_tags array |
| Response: `{response, relatedBakeries?}` | Response: `{response, bakeries}` | ✅ Similar | Response format is compatible |

**Action needed:** Create `/api/chatbot/query` endpoint or alias to `/chat`.

---

### Bakeries

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `GET /api/bakeries` with query filters | `GET /bakeries` | ⚠️ Partial | Missing: category, rating, distance filters |
| Query: `?category=bread&rating=4.5&distance=5km` | No query support | ❌ Missing | Filters not implemented |
| `GET /api/bakeries/:id` | `GET /bakeries/{bakery_id}` | ✅ Similar | Path parameter style differs (REST vs UUID) |

**Action needed:** Add query filter support for category, rating, distance.

---

### Wishlist

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `GET /api/wishlist` | `GET /wishlist` | ⚠️ Different path | Same functionality |
| Auth: `Authorization: Bearer <token>` | Session cookie | ⚠️ Different auth | Current uses HttpOnly cookie, spec uses Bearer token |
| Response: `{bakeries: Bakery[]}` | Response: `{WishlistItemResponse[]}` | ⚠️ Different structure | Current includes more fields (note, visited, dates) |
| `POST /api/wishlist/:bakeryId` | `POST /wishlist` with body `{bakery_id}` | ⚠️ Different style | Current uses JSON body instead of URL param |
| Response: `{success: boolean}` | Response: `{WishlistItemResponse}` | ⚠️ Different | Current returns full item, spec returns simple boolean |
| `DELETE /api/wishlist/:bakeryId` | `DELETE /wishlist/{item_id}` | ⚠️ Different | Current uses item_id not bakery_id |

**Action needed:** Align paths, response formats, and auth method.

---

### Visit History

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `GET /api/visits` | `GET /visit-records` | ⚠️ Different path | Same functionality |
| Auth: `Authorization: Bearer <token>` | Session cookie | ⚠️ Different auth | Current uses cookie |
| Response: `{visits: VisitRecord[]}` | Response: `{BakeryVisitRecordResponse[]}` | ✅ Similar | Response format is compatible |
| `POST /api/visits` with `{bakeryId, rating, review}` | `POST /visit-records` with additional `visit_date` | ⚠️ Different | Current requires visit_date |
| `PUT /api/visits/:id` | `PATCH /visit-records/{record_id}` | ⚠️ Different | HTTP method differs (PUT vs PATCH) |

**Action needed:** Update endpoints, auth method, and make visit_date optional with default to today.

---

### User Profile

| Spec | Implementation | Status | Notes |
|------|---|---|---|
| `GET /api/user/profile` | `GET /me` | ⚠️ Different path | Same functionality, different path |
| Auth: `Authorization: Bearer <token>` | Session cookie | ⚠️ Different auth | Current uses cookie |
| Response: `{user: UserProfile}` | Response: `{UserProfileResponse}` | ✅ Similar | Compatible, but different field names |
| `PUT /api/user/profile` | Not implemented | ❌ Missing | Update profile endpoint missing |
| Body: `{name, profileImage}` | N/A | ❌ Missing | Profile update not implemented |

**Action needed:** Create `PUT /api/user/profile` endpoint and add profileImage support.

---

## Recommendations

### Priority 1: Critical Differences
1. **Authentication Method:** Implement Bearer token support alongside/instead of cookie-based auth
   - Option A: Support both (cookie for browser, Bearer for mobile/API)
   - Option B: Migrate to Bearer token only
   
2. **API Path Structure:** Current uses `/api/v1/*` but spec uses `/api/*`
   - Either update all paths or use `/api/*` directly without v1 prefix

### Priority 2: Missing Features
1. Add `PUT /api/user/profile` for profile updates
2. Add query filters to `/api/bakeries` (category, rating, distance)
3. Add profileImage field to User model

### Priority 3: Alignment Changes
1. Align response formats (return `{success: boolean}` for delete operations)
2. Make visit_date optional (default to today)
3. Align wishlist delete to use bakery_id instead of item_id
4. Implement `/api/chatbot/query` or alias
5. Add pagination query support where needed

---

## Quick Fix Checklist

- [ ] Create `/api/auth/kakao` POST endpoint accepting `{code, redirectUri}`
- [ ] Add Bearer token support to authentication
- [ ] Create `/api/user/profile` PUT endpoint
- [ ] Add query filters to bakery endpoint
- [ ] Make visit_date optional in visit records
- [ ] Update wishlist delete endpoint to accept bakery_id
- [ ] Create `/api/chatbot/query` endpoint
- [ ] Add profileImage field to User model
- [ ] Consider removing v1 prefix or adding /api prefix alias

---

## Notes

Current implementation is functional and well-structured, but differs from spec in:
1. **Authentication:** Cookie-based vs Bearer token
2. **Path structure:** Uses `/api/v1/*` vs `/api/*`
3. **Response formats:** Some endpoints return more data than spec requires
4. **HTTP methods:** Uses PATCH instead of PUT in some places
5. **Missing features:** Profile update, search filters, token response format

The implementation can be adapted to match the spec by:
1. Adding new endpoints alongside existing ones
2. Supporting both authentication methods
3. Creating response format adapters
4. Adding missing features incrementally
