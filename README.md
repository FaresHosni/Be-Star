# Be Star Ticketing Platform 🎟️

Authentication & Ticketing System for Events.

## 🚀 Deployment

### Prerequisites
- Docker & Docker Compose
- Git

### Installation on VPS

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FaresHosni/Be-Star.git
   cd Be-Star
   ```

2. **Run with Docker Compose:**
   ```bash
   docker compose up -d --build
   ```

3. **Verify running containers:**
   ```bash
   docker ps
   ```

### 🌐 Access
- **Frontend:** http://localhost:3005 (or your domain via Cloudflare Tunnel)
- **Backend:** Internal Docker Network (exposed on port 8000 internally)

## 🛠️ Tech Stack
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** Python + FastAPI + SQLAlchemy
- **Database:** SQLite (persisted in `./backend/data`)

## 📝 License
Proprietary Software. All rights reserved.
