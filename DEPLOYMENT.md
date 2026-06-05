# DEPLOYMENT GUIDE

## CivicLens AI - Deployment Instructions

### Quick Overview
- Backend: FastAPI + MongoDB
- Frontend: React + Vite
- Database: MongoDB Atlas
- Deployment Platforms: Render, Railway, Vercel

---

## Option 1: Render.com (Recommended)

### Backend Deployment

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "CivicLens AI - Ready for deployment"
   git push origin main
   ```

2. **Create Render account** at render.com

3. **Deploy Backend**
   - New → Web Service
   - Connect GitHub repository
   - Runtime: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     ```
     MONGO_URI=mongodb+srv://...
     DB_NAME=hackathon
     GEMINI_API_KEY=your_key
     ```

4. **Deploy Frontend**
   - New → Static Site
   - Connect GitHub repository
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
   - Add Environment: `VITE_API_URL=https://your-backend.onrender.com/api/v1`

### Frontend Environment Variables
Update frontend `.env.production` before deployment:
```
VITE_API_URL=https://your-backend-url.onrender.com/api/v1
```

---

## Option 2: Railway.app

### Backend Deployment

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Railway**
   ```bash
   railway init
   ```

3. **Add MongoDB Plugin**
   - Dashboard → Add Plugin → MongoDB

4. **Deploy Backend**
   - Add backend start command in `Procfile`:
     ```
     web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

5. **Set Environment Variables**
   - `MONGO_URI=` (from MongoDB plugin)
   - `DB_NAME=hackathon`
   - `GEMINI_API_KEY=your_key`

### Frontend Deployment

1. **Deploy Frontend**
   - Add frontend service
   - Build: `cd frontend && npm install && npm run build`
   - Publish: `frontend/dist`

---

## Option 3: Vercel + Heroku

### Frontend on Vercel

1. **Connect GitHub**
   - vercel.com/new
   - Select repository
   - Framework: React
   - Build: `npm run build`
   - Output: `frontend/dist`

### Backend on Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add MongoDB URI**
   ```bash
   heroku config:set MONGO_URI=mongodb+srv://...
   heroku config:set GEMINI_API_KEY=your_key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

---

## Option 4: Docker + Any Cloud

### Build Docker Images

```bash
# Backend
cd backend
docker build -t civiclens-backend .
docker tag civiclens-backend:latest your-registry/civiclens-backend:latest
docker push your-registry/civiclens-backend:latest

# Frontend
cd frontend
docker build -t civiclens-frontend .
docker tag civiclens-frontend:latest your-registry/civiclens-frontend:latest
docker push your-registry/civiclens-frontend:latest
```

### Deploy with Docker Compose
```bash
docker-compose -f docker-compose.yml up -d
```

---

## Environment Variables Required

### Backend (.env)
```
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
DB_NAME=hackathon
GEMINI_API_KEY=your_api_key
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-backend-url.com/api/v1
```

---

## MongoDB Atlas Setup

1. Create free cluster at mongodb.com
2. Get connection string
3. Whitelist IP address or allow all (0.0.0.0)
4. Copy connection string to MONGO_URI

---

## Gemini API Setup

1. Go to makersuite.google.com
2. Create new API key
3. Add to GEMINI_API_KEY environment variable
4. Free tier: 60 requests/minute

---

## Post-Deployment Checks

1. ✅ Backend health check: `/health`
2. ✅ API docs available: `/api/docs`
3. ✅ Frontend loads without errors
4. ✅ Submit complaint works end-to-end
5. ✅ Database stores data correctly
6. ✅ Dashboard loads with sample data

---

## Performance Optimization

### Frontend
- Gzip compression enabled
- Code splitting implemented
- Lazy loading for routes
- Image optimization

### Backend
- Database connection pooling
- Response caching for dashboard
- Async operations
- Request logging

---

## Security Checklist

- [ ] Environment variables not in code
- [ ] MongoDB credentials secured
- [ ] API keys rotated
- [ ] CORS properly configured
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation active
- [ ] Error messages don't leak data

---

## Monitoring & Logging

### Recommended Tools
- **Backend**: Sentry for error tracking
- **Frontend**: LogRocket for session replay
- **Database**: MongoDB Atlas monitoring
- **Uptime**: Uptime Robot

---

## Scaling Tips

1. Use MongoDB Atlas auto-scaling
2. Implement Redis caching
3. Use CDN for frontend assets
4. Database connection pooling
5. Load balancing for backend

---

## Common Issues & Solutions

### "Cannot connect to MongoDB"
- Check connection string
- Whitelist IP address in MongoDB Atlas
- Verify credentials

### "CORS errors"
- Add frontend URL to ALLOWED_ORIGINS
- Verify API URL in frontend .env

### "Gemini API errors"
- Check API key validity
- Verify rate limits not exceeded
- Test with sample requests

---

For more help, check individual README files in backend/ and frontend/

