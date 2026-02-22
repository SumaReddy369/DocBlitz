# Deployment Guide: AI Document Q&A Platform

This guide walks you through deploying the platform so **anyone can access it via a public link**.

---

## Option 1: Railway (Recommended - Easiest)

Railway offers free tier with PostgreSQL + app hosting.

### Steps

1. **Create Railway account**: [railway.app](https://railway.app)

2. **Create new project** → Add **PostgreSQL** (creates a database)

3. **Add backend service**:
   - Connect your GitHub repo
   - Set root directory to project root
   - Add **Dockerfile** for backend (or use Nixpacks)
   - Or: Add service → Deploy from GitHub → Select repo

4. **Configure backend**:
   - Variables: `OPENAI_API_KEY`, `SECRET_KEY`, `DATABASE_URL` (from Railway PostgreSQL)
   - Add `CORS_ORIGINS` = your frontend URL (e.g. `https://your-app.vercel.app`)

5. **Add frontend service** (Vercel - see Option 2) or deploy frontend on Railway too

6. **Get your backend URL** (e.g. `https://your-backend.railway.app`)

7. **Deploy frontend** on Vercel with `NEXT_PUBLIC_API_URL` = your backend URL

---

## Option 2: Vercel (Frontend) + Railway (Backend + DB)

### Backend on Railway

1. Create Railway project with PostgreSQL
2. Deploy backend (from GitHub or Dockerfile)
3. Set env vars: `OPENAI_API_KEY`, `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`
4. Copy backend URL

### Frontend on Vercel

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com) → Import project
3. Set **Root Directory** to `frontend`
4. Add env var: `NEXT_PUBLIC_API_URL` = `https://your-backend.railway.app`
5. Deploy

### Update CORS

In Railway backend env, set:
```
CORS_ORIGINS=https://your-app.vercel.app
```

---

## Option 3: Render

### Backend

1. Create **Web Service** from GitHub
2. Root directory: project root (or backend)
3. Build: `cd backend && pip install -r requirements.txt`
4. Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add **PostgreSQL** from Render dashboard
6. Env: `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `CORS_ORIGINS`

### Frontend

1. Create **Static Site** or **Web Service**
2. Root: `frontend`
3. Build: `npm install && npm run build`
4. Publish: `npm run start` or use static export
5. Env: `NEXT_PUBLIC_API_URL` = backend URL

---

## Option 4: Docker Compose (VPS: DigitalOcean, AWS EC2, etc.)

For a VPS (e.g. DigitalOcean Droplet):

```bash
# On your server
git clone https://github.com/yourusername/ai-doc-qa-platform.git
cd ai-doc-qa-platform

# Create .env
cp .env.example .env
# Edit .env: OPENAI_API_KEY, SECRET_KEY

# Run
docker-compose up -d

# App: http://YOUR_SERVER_IP:3000
# API: http://YOUR_SERVER_IP:8000
```

**Make it public**: Use a domain + Nginx reverse proxy, or expose ports 80/443.

---

## Checklist Before Deployment

- [ ] `OPENAI_API_KEY` set (required)
- [ ] `SECRET_KEY` changed from default
- [ ] `DATABASE_URL` points to your PostgreSQL (with pgvector)
- [ ] `CORS_ORIGINS` includes your frontend URL
- [ ] `NEXT_PUBLIC_API_URL` (frontend) points to your backend URL

---

## Quick Local Test

```bash
# Terminal 1
export OPENAI_API_KEY=sk-your-key
docker-compose up

# Open http://localhost:3000
```

---

## Share Your App

Once deployed:
- **Frontend URL**: Share this (e.g. `https://docqa.vercel.app`)
- Users can register, upload PDFs, and ask questions
- Each user has their own documents (auth required)
