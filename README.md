# Scalable Image Import System

A multi-service backend system for importing images from Google Drive and Dropbox to cloud storage, with metadata persistence in PostgreSQL.

## Live Demo

**Working Site URL:** [https://your-deployed-url.railway.app](https://your-deployed-url.railway.app)

> Replace with your actual deployed URL after deployment

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│ API Gateway │────▶│    Redis    │
│   (React)   │     │  (FastAPI)  │     │   (Queue)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────────────────────────┐
                    │           SUPABASE               │
                    │  ┌────────────┐  ┌────────────┐  │
                    │  │ PostgreSQL │  │  Storage   │  │
                    │  │ (metadata) │  │  (images)  │  │
                    │  └────────────┘  └────────────┘  │
                    └──────────────────────────────────┘
                                  ▲
                                  │
                           ┌─────────────┐
                           │   Worker    │
                           │  Service    │
                           └─────────────┘
```

### Services

| Service | Technology | Purpose |
|---------|------------|---------|
| **API Gateway** | FastAPI (Python) | REST API endpoints |
| **Worker Service** | Celery + Redis | Async image processing |
| **Frontend** | React + Vite | User interface |
| **Database** | Supabase PostgreSQL | Metadata storage |
| **Storage** | Supabase Storage | Image file storage |
| **Queue** | Redis (Upstash) | Task queue |

---

## Features

- Import images from **Google Drive** public folders
- Import images from **Dropbox** shared folders (Bonus)
- Source-based filtering (Bonus)
- Real-time import progress tracking
- Paginated image listing
- Responsive UI with Tailwind CSS
- Dockerized microservices
- Scalable async processing with Celery

---

## API Documentation

### Base URL
```
http://localhost:8000 (local)
https://your-api.railway.app (production)
```

### Endpoints

#### POST /import/google-drive
Import images from a public Google Drive folder.

**Request:**
```json
{
  "folder_url": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Import job started. Use GET /jobs/{job_id} to track progress."
}
```

#### POST /import/dropbox
Import images from a public Dropbox folder.

**Request:**
```json
{
  "folder_url": "https://www.dropbox.com/sh/YOUR_SHARED_LINK"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "processing",
  "message": "Import job started. Use GET /jobs/{job_id} to track progress."
}
```

#### GET /import/jobs/{job_id}
Get import job status.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "source": "google_drive",
  "total_files": 100,
  "processed_files": 45,
  "failed_files": 2,
  "progress_percent": 45.0
}
```

#### GET /images
Get paginated list of imported images.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `source` (string): Filter by source (`google_drive` or `dropbox`)

**Response:**
```json
{
  "images": [
    {
      "id": 1,
      "name": "photo.jpg",
      "google_drive_id": "xxx",
      "source": "google_drive",
      "size": 1024000,
      "mime_type": "image/jpeg",
      "storage_url": "https://...",
      "created_at": "2025-12-30T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5,
  "page_size": 20
}
```

---

## Scalability Design

### Handling 10,000+ Images

1. **Async Processing with Celery**
   - Import requests return immediately with a job ID
   - Background workers process images in parallel
   - Workers can be scaled horizontally

2. **Chunked Processing**
   - Files are fetched in batches of 100
   - Individual Celery tasks for each image
   - Uses Celery's `group()` for concurrent uploads

3. **Retry & Fault Tolerance**
   - Automatic retry with exponential backoff
   - Failed tasks tracked in database
   - Job status tracking for monitoring

4. **Rate Limiting**
   - Rate limiting on Celery tasks (10/second)
   - Respects Google Drive API limits
   - Queue throttling prevents API overload

---

## Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/image-import-system.git
cd image-import-system

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=images

# Database URL (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Redis (local Docker)
REDIS_URL=redis://redis:6379

# Google Drive API (optional)
GOOGLE_API_KEY=your-google-api-key

# Dropbox (optional)
DROPBOX_ACCESS_TOKEN=your-dropbox-access-token
```

### 3. Start Services

```bash
# Start all services
docker-compose up --build

# Or start in detached mode
docker-compose up -d --build
```

### 4. Access the Application

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Cloud Deployment

### Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings > API to get your keys
3. Create a storage bucket named `images` with public access

### Upstash Redis Setup

1. Create a free Redis database at [upstash.com](https://upstash.com)
2. Copy the Redis URL from the dashboard

### Railway Deployment

1. Create a new project at [railway.app](https://railway.app)
2. Add services from GitHub repo:
   - API Gateway (from `api-gateway/`)
   - Worker Service (from `worker-service/`)
   - Frontend (from `frontend/`)
3. Add environment variables to each service
4. Deploy!

---

## Project Structure

```
├── docker-compose.yml          # Local development
├── .env.example                # Environment template
├── README.md                   # This file
│
├── api-gateway/                # FastAPI REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app
│       ├── config.py           # Settings
│       ├── database.py         # SQLAlchemy setup
│       ├── models/             # Database models
│       ├── schemas/            # Pydantic schemas
│       ├── routes/             # API endpoints
│       └── services/           # Business logic
│
├── worker-service/             # Celery workers
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── celery_app.py       # Celery config
│       ├── tasks/              # Celery tasks
│       └── services/           # External APIs
│
├── frontend/                   # React UI
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       ├── components/
│       └── services/
│
└── postman/                    # API collection
    └── collection.json
```

---

## Testing the API

### Using Postman

Import the collection from `postman/collection.json`

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Import from Google Drive
curl -X POST http://localhost:8000/import/google-drive \
  -H "Content-Type: application/json" \
  -d '{"folder_url": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"}'

# Import from Dropbox
curl -X POST http://localhost:8000/import/dropbox \
  -H "Content-Type: application/json" \
  -d '{"folder_url": "https://www.dropbox.com/sh/YOUR_SHARED_LINK"}'

# Check job status
curl http://localhost:8000/import/jobs/YOUR_JOB_ID

# List all images
curl http://localhost:8000/images

# List with filter
curl "http://localhost:8000/images?source=google_drive&page=1&limit=20"
```

---

## Technology Stack

| Component | Technology | Why? |
|-----------|------------|------|
| API | FastAPI | Fast, async, auto-docs |
| Task Queue | Celery + Redis | Proven, scalable |
| Database | PostgreSQL | SQL requirement |
| Storage | Supabase Storage | S3-compatible, free tier |
| Frontend | React + Vite | Modern, fast builds |
| Styling | Tailwind CSS | Utility-first, responsive |

---

## License

MIT License

---

## Author

Built for Foto Owl AI - Backend Developer Assignment
