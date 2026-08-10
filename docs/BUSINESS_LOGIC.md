# Business Logic — BeatFlow API

## Authentication

- Three entity types can authenticate: **Artist**, **Listener**, **Label** (label uses artist credentials)
- JWT tokens are valid for 24 hours
- All endpoints **except** registration (`POST /artists`, `POST /listeners`) and login endpoints require auth
- Send token as: `Authorization: Bearer <token>`
- Expired/invalid tokens return `401`
- Genre listing (`GET /genres`, `GET /genres/:id`) is public — no auth required

---

## Genres (Reference Table)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/genres` | GET | No | List all genres (ordered by name) |
| `/genres/:id` | GET | No | Get genre by ID |

### Rules
- Genres are pre-seeded and read-only
- Available genres: `rock`, `pop`, `hip-hop`, `electronic`, `jazz`, `classical`, `r&b`, `country`, `latin`, `metal`
- No creation, update, or deletion via API

---

## Artists

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/artists` | GET | Yes | List active artists (filterable by `?genre_id=`) |
| `/artists` | POST | No | Register new artist |
| `/artists/:id` | GET | Yes | Get artist by ID |
| `/artists/:id` | PUT | Yes | Update artist fields |
| `/artists/:id` | DELETE | Yes | Delete artist (fails if has published albums or pending royalties) |
| `/artists/login` | POST | No | Authenticate |

### Rules
- Required fields: `stage_name`, `first_name`, `last_name`, `email`, `password`
- All required fields must be strings and non-empty
- `stage_name`: max 100 characters
- `email`: valid format, unique (409 on duplicate)
- `password`: min 8 characters, hashed with bcrypt
- `bio`: max 500 characters (optional)
- `genre_id`: must reference an existing genre (404 if not found)
- `country`: optional string
- `total_earnings`: read-only, starts at 0.00, updated by royalty payments
- Password never appears in any response
- DELETE returns 409 if artist has published albums
- DELETE returns 409 if artist has pending or processing royalties
- DELETE cascades: draft/archived albums → tracks → playlist_tracks, streams, royalties, licenses


---

## Albums

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/albums` | GET | Yes | List albums (filterable by `?artist_id=`, `?status=`) |
| `/albums` | POST | Yes | Create new album (starts in 'draft') |
| `/albums/:id` | GET | Yes | Get album by ID |
| `/albums/:id` | PUT | Yes | Update album fields/status |
| `/albums/:id` | DELETE | Yes | Delete album (fails if published or has active licenses) |

### Rules
- Required fields: `artist_id`, `title`
- `title`: non-empty string, max 200 characters
- `artist_id`: must reference an existing **active** artist (404 otherwise)
- `description`: max 500 characters (optional)
- `release_year`: 1900–2100 (optional)
- `genre_id`: must reference an existing genre (404 if not found)
- `cover_url`: optional string
- New albums always start in `draft` status
- **Cannot publish an album with 0 tracks** (400)
- DELETE returns 409 if album status is `published`
- DELETE returns 409 if any track has active licenses (`requested`, `approved`, `active`)
- DELETE cascades: tracks → playlist_tracks, streams, royalties, licenses

### Status Machine
```
draft → published   (requires at least 1 track)
draft → archived
published → archived
archived → (nothing)   TERMINAL
```

---

## Tracks

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/tracks` | GET | Yes | List tracks (filterable by `?album_id=`, `?genre_id=`, `?is_available=`) |
| `/tracks` | POST | Yes | Create new track |
| `/tracks/:id` | GET | Yes | Get track by ID |
| `/tracks/:id` | PUT | Yes | Update track fields |
| `/tracks/:id` | DELETE | Yes | Delete track (fails if has active licenses or pending royalties) |

### Rules
- Required fields: `album_id`, `title`, `duration_seconds`, `track_number`
- `title`: non-empty string, max 200 characters
- `album_id`: must reference an existing album (404 otherwise)
- **Cannot add tracks to an archived album** (400)
- `duration_seconds`: 30–3600 (30 seconds to 1 hour)
- `track_number`: 1–50
- **Track number must be unique within the same album** (409 on conflict)
- `genre_id`: must reference an existing genre (optional)
- `is_available`: boolean (default true)
- `is_explicit`: boolean (default false)
- `play_count`: read-only, starts at 0, incremented by streams
- DELETE returns 409 if track has active licenses (`requested`, `approved`, `active`)
- DELETE returns 409 if track has pending or processing royalties
- DELETE cascades: playlist_tracks, streams, royalties (paid/failed), licenses (expired/revoked)

---

## Listeners

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/listeners` | GET | Yes | List active listeners (ordered by username) |
| `/listeners` | POST | No | Register new listener |
| `/listeners/:id` | GET | Yes | Get listener by ID |
| `/listeners/:id` | PUT | Yes | Update listener fields |
| `/listeners/:id` | DELETE | Yes | Delete listener (fails if has active subscription) |
| `/listeners/login` | POST | No | Authenticate |

### Rules
- Required fields: `username`, `email`, `password`, `first_name`, `last_name`
- All required fields must be strings and non-empty
- `username`: 3–50 characters, alphanumeric and underscores only, unique (409 on duplicate)
- `email`: valid format, unique (409 on duplicate)
- `password`: min 8 characters
- `date_of_birth`: YYYY-MM-DD format, must be at least 13 years old (optional)
- `country`: optional string
- Password never appears in any response
- Updatable fields: `first_name`, `last_name`, `country`
- DELETE returns 409 if listener has active or paused subscription
- DELETE cascades: playlists → playlist_tracks, streams, subscriptions (cancelled/expired)

---

## Subscriptions

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/subscriptions` | GET | Yes | List subscriptions (filterable by `?listener_id=`, `?status=`) |
| `/subscriptions` | POST | Yes | Create a new subscription |
| `/subscriptions/:id` | GET | Yes | Get subscription by ID |
| `/subscriptions/:id` | PUT | Yes | Update subscription status or plan |

### Rules
- Required fields: `listener_id`, `plan`
- `listener_id`: must reference an existing active listener (404 otherwise)
- Plans: `free`, `basic`, `premium`
- **Only ONE active or paused subscription per listener** (409 if duplicate)
- Expiration auto-calculated:
  - `free`: no expiration (null)
  - `basic`: 30 days from creation
  - `premium`: 365 days from creation
- Can only change `plan` while subscription status is `active` (400 otherwise)
- Changing plan recalculates `expires_at`

### Status Machine
```
active → paused      (sets paused_at timestamp)
active → cancelled   (sets cancelled_at timestamp)
paused → active      (clears paused_at)
paused → cancelled   (sets cancelled_at timestamp)
cancelled → (nothing)   TERMINAL
expired → (nothing)     TERMINAL
```

### Side Effects
| Transition | Side Effect |
|---|---|
| → paused | Sets `paused_at = NOW()` |
| → cancelled | Sets `cancelled_at = NOW()` |
| paused → active | Clears `paused_at = NULL` |

---

## Playlists

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/playlists` | GET | Yes | List playlists (filterable by `?listener_id=`, `?is_public=`) |
| `/playlists` | POST | Yes | Create a new playlist |
| `/playlists/:id` | GET | Yes | Get playlist by ID (includes tracks) |
| `/playlists/:id` | PUT | Yes | Update playlist fields |
| `/playlists/:id` | DELETE | Yes | Delete playlist (cascades tracks) |

### Rules
- Required fields: `listener_id`, `name`
- `listener_id`: must reference an existing active listener (404 otherwise)
- `name`: non-empty string, max 200 characters
- `description`: max 500 characters (optional)
- `is_public`: boolean (default false)
- **Maximum 50 playlists per listener** (400 if exceeded)
- `track_count`: read-only, auto-updated when tracks are added/removed
- GET by ID returns the playlist with an embedded `tracks` array
- DELETE cascades: all playlist_tracks entries (ON DELETE CASCADE)

---

## Playlist Tracks (Junction)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/playlist-tracks` | GET | Yes | List entries (requires `?playlist_id=` parameter) |
| `/playlist-tracks` | POST | Yes | Add a track to a playlist |
| `/playlist-tracks/:id` | GET | Yes | Get entry by ID |
| `/playlist-tracks/:id` | PUT | Yes | Update track position |
| `/playlist-tracks/:id` | DELETE | Yes | Remove track from playlist |

### Rules
- Required fields for creation: `playlist_id`, `track_id`
- `playlist_id`: must reference an existing playlist (404 otherwise)
- `track_id`: must reference an existing track (404 otherwise)
- Track must be `is_available = true` to be added (400 otherwise)
- **Same track cannot be added twice to the same playlist** (409)
- **Maximum 100 tracks per playlist** (400 if exceeded)
- `position`: auto-incremented if not provided, must be positive integer
- GET list requires `playlist_id` query parameter (400 if missing)
- Adding/removing updates `track_count` on the parent playlist
- Removing a track updates playlist `updated_at`

---

## Streams (Play Events)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/streams` | GET | Yes | List streams (filterable by `?listener_id=`, `?track_id=`) |
| `/streams` | POST | Yes | Record a stream |
| `/streams/:id` | GET | Yes | Get stream by ID |

### Rules
- Required fields: `listener_id`, `track_id`, `duration_seconds`
- `listener_id`: must reference an existing active listener (404 otherwise)
- `track_id`: must reference an existing track (404 otherwise)
- Track must be `is_available = true` (400 otherwise)
- **Track must belong to a published album** (400 otherwise)
- `duration_seconds`: minimum 10 (anything less doesn't count as a stream)
- Duration is capped at track's `duration_seconds` (cannot exceed track length)
- **Listener must have an active subscription** (403 if no active subscription)
- Plan-based daily limits:
  - `free`: 5 streams per day
  - `basic`: 50 streams per day
  - `premium`: unlimited
- Exceeding daily limit returns 403 with descriptive message
- `completed`: automatically set to `true` if listener played >= 80% of track duration
- Streams are immutable — no update or delete

### Side Effects
| Event | Side Effect |
|---|---|
| Stream created | Track's `play_count` incremented by 1 |

---

## Royalties

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/royalties` | GET | Yes | List royalties (filterable by `?artist_id=`, `?track_id=`, `?status=`) |
| `/royalties` | POST | Yes | Create a royalty payment record |
| `/royalties/:id` | GET | Yes | Get royalty by ID |
| `/royalties/:id` | PUT | Yes | Update royalty status (state machine) |

### Rules
- Required fields: `artist_id`, `track_id`, `stream_count`, `amount`, `period_start`, `period_end`
- `artist_id`: must reference an existing artist (404 otherwise)
- `track_id`: must reference an existing track (404 otherwise)
- **Track must belong to the specified artist** (via album ownership) (400 otherwise)
- `stream_count`: non-negative integer
- `amount`: 0 to 1,000,000
- `period_start` and `period_end`: valid dates in YYYY-MM-DD format
- `period_end` must be after `period_start` (400 otherwise)
- **One royalty record per track per period** (409 if duplicate track + period_start + period_end)
- `failure_reason`: required when transitioning to `failed`, max 255 characters
- Royalties are never deleted — only status transitions

### Status Machine
```
pending → processing   (sets processed_at)
pending → failed       (sets failed_at + failure_reason)
processing → paid      (sets paid_at, updates artist total_earnings)
processing → failed    (sets failed_at + failure_reason)
failed → pending       (retry: clears failed_at and failure_reason)
paid → (nothing)       TERMINAL
```

### Side Effects
| Transition | Side Effect |
|---|---|
| → processing | Sets `processed_at = NOW()` |
| → paid | Sets `paid_at = NOW()`, adds `amount` to artist's `total_earnings` |
| → failed | Sets `failed_at = NOW()`, stores `failure_reason` |
| failed → pending | Clears `failed_at` and `failure_reason` (retry) |

---

## Licenses

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/licenses` | GET | Yes | List licenses (filterable by `?track_id=`, `?status=`, `?license_type=`) |
| `/licenses` | POST | Yes | Request a license for a track |
| `/licenses/:id` | GET | Yes | Get license by ID |
| `/licenses/:id` | PUT | Yes | Update license status (state machine) |

### Rules
- Required fields: `track_id`, `licensee_name`, `licensee_email`, `license_type`, `fee`
- `track_id`: must reference an existing track (404 otherwise)
- Track must be `is_available = true` for licensing (400 otherwise)
- `licensee_name`: non-empty string, max 200 characters
- `licensee_email`: valid email format
- License types: `sync`, `mechanical`, `performance`, `master`
- `fee`: 100 to 1,000,000
- `territory`: max 100 characters (default: "worldwide")
- `starts_at`: optional date (YYYY-MM-DD)
- `expires_at`: optional date, must be after `starts_at` if both provided
- **One active license per type per track** (409 if `requested`, `approved`, or `active` of same type exists)
- `revocation_reason`: required when revoking, max 255 characters
- Licenses are never deleted — only status transitions

### Status Machine
```
requested → approved   (sets approved_at)
requested → revoked    (sets revoked_at + reason, track becomes unavailable)
approved → active      (sets starts_at if not already set)
approved → revoked     (sets revoked_at + reason, track becomes unavailable)
active → expired
active → revoked       (sets revoked_at + reason, track becomes unavailable)
expired → (nothing)    TERMINAL
revoked → (nothing)    TERMINAL
```

### Side Effects
| Transition | Side Effect |
|---|---|
| → approved | Sets `approved_at = NOW()` |
| → active | Sets `starts_at = TODAY` if not already set |
| → revoked | Sets `revoked_at = NOW()`, sets track `is_available = false` |

---

## Relationships & Dependency Chain

```
Genre (reference)
  │
Artist (1) ──► (N) Album (1) ──► (N) Track
  │                                     │
  │                                     ├──► (N) Playlist Track ◄── Playlist ◄── Listener
  │                                     │
  │                                     ├──► (N) Stream ◄── Listener (requires Subscription)
  │                                     │
  │                                     ├──► (N) Royalty ──► Artist
  │                                     │
  │                                     └──► (N) License
  │
Listener (1) ──► (N) Subscription
           ──► (N) Playlist (1) ──► (N) Playlist Track
           ──► (N) Stream
```

### Factory Dependency Depths

| Entity | Dependencies Required | Depth |
|---|---|---|
| Genre | None (seeded) | 0 |
| Artist | None (standalone) | 0 |
| Listener | None (standalone) | 0 |
| Album | Artist | 1 |
| Subscription | Listener | 1 |
| Playlist | Listener | 1 |
| Track | Album → Artist | 2 |
| Playlist Track | Playlist + Track (→ Album → Artist) | 3 |
| Stream | Listener + Subscription + Track (→ Album → Artist, published) | 3 |
| Royalty | Artist + Track (→ Album → Artist) | 2 |
| License | Track (→ Album → Artist) | 2 |

---

## Delete Cascade Rules

| Entity | Constraint | Cascade |
|---|---|---|
| **Artist** | Fails if has published albums | Draft/archived albums → tracks → playlist_tracks, streams, royalties, licenses |
| **Artist** | Fails if has pending/processing royalties | — |
| **Album** | Fails if status is `published` | tracks → playlist_tracks, streams, royalties, licenses |
| **Album** | Fails if tracks have active licenses | — |
| **Track** | Fails if has active licenses (requested/approved/active) | playlist_tracks, streams, royalties (paid/failed), licenses (expired/revoked) |
| **Track** | Fails if has pending/processing royalties | — |
| **Listener** | Fails if has active/paused subscription | playlists → playlist_tracks, streams, subscriptions |
| **Playlist** | No constraints | playlist_tracks (ON DELETE CASCADE) |
| **Playlist Track** | No constraints | Direct delete |
| **Subscription** | No delete endpoint | Status transitions only |
| **Stream** | No delete endpoint | Immutable |
| **Royalty** | No delete endpoint | Status transitions only |
| **License** | No delete endpoint | Status transitions only |

---

## Cleanup Strategy for Testing

To clean up test data created during delivery/royalty/license tests, transition stateful entities to terminal states BEFORE deleting upstream dependencies:

1. **Licenses**: transition to `expired` or `revoked` (unlocks track delete)
2. **Royalties**: transition to `paid` or leave as `failed` (unlocks track/artist delete)
3. **Subscriptions**: transition to `cancelled` (unlocks listener delete)
4. **Albums**: transition to `archived` first if published (unlocks album delete)

Once stateful entities are in terminal states, cascade deletes work cleanly from Artist/Listener down.

---

## Error Response Format

All errors follow this structure:


### HTTP Status Code Guide

| Code | Usage |
|---|---|
| 200 | Success (GET, PUT, DELETE) |
| 201 | Created (POST) |
| 400 | Validation error, invalid state transition, business rule violation |
| 401 | Missing or invalid token |
| 403 | Forbidden (no subscription, plan limit reached) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email, duplicate resource, constraint violation) |
| 500 | Internal server error (should never happen with valid input) |
