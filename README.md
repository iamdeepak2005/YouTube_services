# 📺 YouTube Learning Platform Backend

A premium, microservices-based backend designed to turn YouTube playlists into a structured learning management system. Built with **FastAPI**, **PostgreSQL**, and **Docker**, it features automated content syncing, intelligent progress tracking, and personalized recommendations.

---

## 🏗️ System Architecture

![High Level Architecture](diagrams/microservices_architecture_diagram_1772957936232.png)

The system consists of 5 independent microservices orchestrated via an **API Gateway**:

- **API Gateway (Port 8000):** Unified entry point.
- **User Service (Port 8001):** Identity management.
- **Content Service (Port 8002):** Automated YouTube syncing.
- **Progress Service (Port 8003):** Watch-time tracking.
- **Analytics Service (Port 8004):** Interaction & engagement metrics.
- **Recommendation Service (Port 8005):** Intelligent lesson logic.

---

## 📊 Database Design (ERD)

![Database Schema](diagrams/ERD.png)

Each microservice maintains its own isolated PostgreSQL database, ensuring high scalability and fault tolerance. Data consistency is maintained through shared unique identifiers (`user_id`, `video_id`).

---

## ⚙️ Core Logic & Features

### 1. Lazy-Loading Content Sync

The **Content Service** uses a "Cache-First" strategy. When you request a playlist, the service automatically fetches metadata from the YouTube Data API v3 and permanently stores it in our database.

- **Benefit:** No manual data entry for courses and lightning-fast responses for subsequent users.

### 2. Decision-Driven Recommendations

The **Recommendation Service** intelligently decides what a user should watch next by aggregating data from across the platform.

![Recommendation Engine Logic](diagrams/Recommended%20engine.png)

**Logic Flow:**

1. **Resume Point:** If a user has an unfinished video (watched < 90%), recommend they finish it.
2. **Next Lesson:** If the previous video is complete, recommend the next chronological lesson in the playlist.
3. **Global Trending:** If the whole course is finished, recommend the platform's most popular video via the Analytics Service.

### 3. Decoupled Event Logging

When a user pauses or completes a video, the frontend sends **one** request to the **Progress Service**. The backend then uses **Asynchronous Background Tasks** to silently notify the **Analytics Service**, keeping the user experience fast and responsive.

---

## 🚀 Deployment

The entire stack is containerized using **Docker** and orchestrated with **Docker Compose**, including health-check-based dependency management.

![Docker Deployment](diagrams/Docker.png)

### Quick Start

```bash
# 1. Provide your YouTube API Key in .env
# 2. Start the entire platform
docker-compose up --build
```

---

## 🛠️ API Reference (Payloads for Frontend)

### 👤 User Service

**POST** `/users`

```json
{
  "email": "learner@example.com"
}
```

### 📈 Progress Service (Unified Event Entry)

**POST** `/video/progress`
_Use this for Play, Pause, Seek, and Completion events._

```json
{
  "user_id": "UUID-FROM-USER-SERVICE",
  "video_id": "YOUTUBE-VIDEO-ID",
  "watched_seconds": 120,
  "event_type": "pause" // Optional: "play", "pause", "seek", "complete"
}
```

### 📺 Content Service

**GET** `/playlist/{playlist_id}`
_Registers and returns the full course curriculum._

**GET** `/video/metadata/{video_id}`
_Returns titles, thumbnails, and **ready-to-use iframe embed codes**._

### 📊 Analytics Service

**GET** `/analytics/popular`
_Returns the platform leaderboard (Total views & Completion rates)._

**GET** `/analytics/dropoff/{video_id}`
_Returns the exact second where most users drop off for a specific video._

### 🤖 Recommendation Service

**GET** `/recommend/{playlist_id}?user_id={uuid}`
_Returns the exact next step for the user with an internal reason code._
