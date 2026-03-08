# YouTube Learning Platform — Microservices Backend

A production-grade, microservices-based learning platform built with **FastAPI**, **PostgreSQL**, and **Docker**.  
Each service is an independent FastAPI application with its own database schema and Docker container.

---

## Architecture Overview

```
Client / Browser
      │
      ▼
┌─────────────────────┐  :8000
│     API Gateway     │  ← single entry point for all clients
└──────────┬──────────┘
           │  (HTTP proxy — path-based routing)
    ┌──────┼────────────────────────────────────────────┐
    │      │                                            │
    ▼      ▼           ▼              ▼                 ▼
User    Content    Progress       Analytics       Recommendation
Service  Service    Service        Service          Service
:8001    :8002      :8003          :8004            :8005
  │        │          │              │
user-db content-db progress-db analytics-db
```

---

## Service Responsibilities

| Service                    | Port | Database     | Key Responsibilities                                       |
| -------------------------- | ---- | ------------ | ---------------------------------------------------------- |
| **api-gateway**            | 8000 | —            | Reverse-proxy, rate limiting, health aggregation           |
| **user-service**           | 8001 | user_db      | User registration & profile retrieval                      |
| **content-service**        | 8002 | content_db   | YouTube playlist sync, video metadata, cache-first serving |
| **progress-service**       | 8003 | progress_db  | Watch progress, resume playback, course completion         |
| **analytics-service**      | 8004 | analytics_db | Player events, drop-off detection, popularity index        |
| **recommendation-service** | 8005 | —            | Stateless recommendation engine (resume → next → popular)  |

---

## Quick Start

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- A [YouTube Data API v3](https://console.cloud.google.com/) key

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your real YouTube API key:
#   YOUTUBE_API_KEY=AIza...
```

### 3. Start all services

```bash
docker-compose up --build
```

> First run takes ~2 minutes to build images and start all containers.

### 4. Verify everything is running

```
http://localhost:8000/health     ← gateway + all services
http://localhost:8000/           ← route map
```

---

## API Reference (via Gateway — port 8000)

All endpoints below are accessed through the **API Gateway at port 8000**.  
Each service also exposes its own Swagger UI at `http://localhost:<port>/docs`.

### User Service (`/users`)

| Method | Path          | Description            |
| ------ | ------------- | ---------------------- |
| `POST` | `/users`      | Register a new learner |
| `GET`  | `/users/{id}` | Get learner profile    |

**Register user:**

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "learner@example.com"}'
```

---

### Content Service (`/playlist`, `/video`)

| Method | Path                                 | Description                                           |
| ------ | ------------------------------------ | ----------------------------------------------------- |
| `GET`  | `/playlist/{youtube_playlist_id}`    | Get playlist + videos (cache-first, YouTube fallback) |
| `GET`  | `/video/metadata/{youtube_video_id}` | Get current + next video metadata for preloading      |
| `GET`  | `/video/next/{youtube_video_id}`     | Get the next video for autoplay                       |

**Fetch a playlist:**

```bash
curl http://localhost:8000/playlist/PLrAXtmErZgOeiKm4sgNOknc9TTnkwB4mA
```

**Cache strategy:**

- ✅ Playlist in DB and synced < 24 h → return cached data immediately
- 🔄 Playlist stale or missing → fetch from YouTube API, store, return
- ⚠️ YouTube API down → serve stale cache as fallback, or 503 if no cache

---

### Progress Service (`/video`, `/course`)

| Method | Path                                        | Description                 |
| ------ | ------------------------------------------- | --------------------------- |
| `POST` | `/video/progress`                           | Update watch progress       |
| `GET`  | `/video/resume/{video_id}?user_id=`         | Get resume timestamp        |
| `GET`  | `/course/{playlist_id}/progress?user_id=`   | Get course progress %       |
| `GET`  | `/course/{playlist_id}/completion?user_id=` | Check 90 % completion badge |

**Update progress:**

```bash
curl -X POST http://localhost:8000/video/progress \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid", "video_id": "youtube_id", "watched_seconds": 450}'
```

**Auto-completion logic:** If `watched_seconds ≥ 90%` of the video's duration (fetched from content-service), `completed = true` is set automatically.

---

### Analytics Service (`/video/event`, `/analytics`)

| Method | Path                            | Description                    |
| ------ | ------------------------------- | ------------------------------ |
| `POST` | `/video/event`                  | Record a player event          |
| `GET`  | `/analytics/dropoff/{video_id}` | Get drop-off timestamp         |
| `GET`  | `/analytics/popular?limit=10`   | Top videos by popularity index |

**Record a pause event:**

```bash
curl -X POST http://localhost:8000/video/event \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid", "video_id": "youtube_id", "event_type": "pause", "position_seconds": 120}'
```

Supported `event_type` values: `play`, `pause`, `seek`, `complete`

---

### Recommendation Service (`/recommend`)

| Method | Path                                | Description                |
| ------ | ----------------------------------- | -------------------------- |
| `GET`  | `/recommend/{playlist_id}?user_id=` | Get next recommended video |

**Priority order:**

1. 🔁 **Resume** — unfinished video started by user
2. ➡️ **Next in sequence** — next video after last completed
3. 🔥 **Popular** — most-watched video from analytics

```bash
curl "http://localhost:8000/recommend/PLrAX...?user_id=your-uuid"
```

---

## Playlist Sync Job

The content-service runs an **APScheduler background job** that:

- Executes every **24 hours**
- Calls the YouTube Data API for every stored playlist
- Updates video metadata (title, thumbnail, duration, position)
- Inserts new videos and removes deleted ones

---

## Rate Limiting

Every endpoint is rate-limited at **100 requests per minute per IP address** at both the gateway and service levels.  
Exceeding the limit returns HTTP `429 Too Many Requests`.

---

## Database Schema

### user_db

```
users (id, email, created_at)
```

### content_db

```
playlists (id, youtube_playlist_id, title, description, last_synced_at)
videos (id, youtube_video_id, playlist_id, title, thumbnail, duration, position)
```

### progress_db

```
video_progress (id, user_id, video_id, watched_seconds, completed, updated_at)
learning_sessions (id, user_id, start_time, end_time)
```

### analytics_db

```
video_events (id, user_id, video_id, event_type, position_seconds, timestamp)
```

---

## Project Structure

```
youtube-services/
├── docker-compose.yml
├── .env.example
├── README.md
└── services/
    ├── api-gateway/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py          ← FastAPI app factory + health aggregation
    │       ├── proxy.py         ← reverse proxy routes
    │       └── config.py
    ├── user-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── router.py
    │       ├── models.py
    │       ├── schemas.py
    │       ├── repository.py
    │       ├── database.py
    │       └── config.py
    ├── content-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── router.py           ← cache-first playlist serving
    │       ├── scheduler.py        ← 24-hour APScheduler sync job
    │       ├── youtube_client.py   ← YouTube Data API wrapper
    │       ├── models.py
    │       ├── schemas.py
    │       ├── repository.py
    │       ├── database.py
    │       └── config.py
    ├── progress-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── router.py         ← progress, resume, course completion
    │       ├── content_client.py ← HTTP calls to content-service
    │       ├── models.py
    │       ├── schemas.py
    │       ├── repository.py
    │       ├── database.py
    │       └── config.py
    ├── analytics-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── router.py       ← event ingestion, dropoff, popular
    │       ├── models.py
    │       ├── schemas.py
    │       ├── repository.py   ← drop-off detection + popularity index
    │       ├── database.py
    │       └── config.py
    └── recommendation-service/
        ├── Dockerfile
        ├── requirements.txt
        └── app/
            ├── main.py
            ├── router.py
            ├── engine.py          ← 3-tier recommendation logic
            ├── service_clients.py ← HTTP to content/progress/analytics
            └── config.py
```

---

## Individual Service Docs

Each service exposes its own OpenAPI docs while running:

| Service                | Swagger UI                 |
| ---------------------- | -------------------------- |
| API Gateway            | http://localhost:8000/docs |
| User Service           | http://localhost:8001/docs |
| Content Service        | http://localhost:8002/docs |
| Progress Service       | http://localhost:8003/docs |
| Analytics Service      | http://localhost:8004/docs |
| Recommendation Service | http://localhost:8005/docs |

---

## Error Handling

| Scenario                       | Behaviour                                    |
| ------------------------------ | -------------------------------------------- |
| YouTube API quota exceeded     | Serve stale cached playlist; 503 if no cache |
| Playlist not found on YouTube  | 404 with descriptive message                 |
| Video removed from YouTube     | Removed from DB on next sync cycle           |
| Downstream service unreachable | Gateway returns 503 / 504 with service name  |
| Duplicate user email           | 409 Conflict                                 |
| Rate limit exceeded            | 429 Too Many Requests                        |

---

## Stopping Services

```bash
docker-compose down           # stop containers
docker-compose down -v        # stop containers + delete database volumes
```
