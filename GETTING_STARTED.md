# GETTING STARTED

## CivicLens AI - 5-Minute Quick Start

### Prerequisites
- Python 3.9+
- Git
- MongoDB Atlas account (free tier OK)
- Gemini API key (free)

---

## 🚀 Quick Setup (Windows)

### Step 1: Clone & Navigate
```bash
cd Desktop/Hackathon
```

### Step 2: Backend Setup
```bash
cd backend
setup.bat
```

When setup completes:
1. Copy the `.env.example` content
2. Create `.env` in the project root with your credentials
3. Run from the project root:
   ```bash
   python app.py
   ```

Expected output:
```
✅ Connected to MongoDB: hackathon
✅ Gemini API initialized
🚀 Server starting on http://localhost:8000
📚 API Docs: http://localhost:8000/api/docs
```

### Step 3: Open the Application
- Frontend and API are both served by the Python backend.
- Open: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## 🎯 Your First Test

### 1. Open Frontend
Go to: http://localhost:8000

### 2. Submit a Complaint
- Click "Report" button
- Fill form:
  - **Description**: "There's a big pothole on Main Street near the park"
  - **Location**: "Downtown / Main Street"
  - **Language**: English
  - **Category**: Leave blank (AI decides)
- Click "Submit Complaint"

### 3. See AI Analysis
You'll get:
```
Category: Roads
Severity: High
Priority: 75/100
Department: Public Works
Recommendation: Schedule road inspection and repair
```

### 4. Track Your Complaint
- Copy the Complaint ID
- Click "Track Status"
- Paste ID to see full timeline

### 5. View Dashboard
- Click "Analytics"
- See your complaint in:
  - Total complaints count
  - Category breakdown chart
  - Recent submissions

---

## 🔧 Environment Setup

### Backend (.env)

Create `backend/.env`:
```bash
# MongoDB URI from Atlas
MONGO_URI="mongodb+srv://user:password@cluster.mongodb.net/"

# Database name
DB_NAME="hackathon"

# Gemini API key from makersuite.google.com
GEMINI_API_KEY="AIza..."
```

### Get Your Credentials

#### MongoDB Atlas
1. Go to: mongodb.com/cloud/atlas
2. Create free account
3. Create cluster (free tier)
4. Click "Connect"
5. Copy connection string
6. Replace `<password>` with your password

#### Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy to GEMINI_API_KEY

---

## 📁 Project Structure

```
Hackathon/
├── backend/
│   ├── app/
│   │   ├── models/         # Data schemas
│   │   ├── services/       # Business logic
│   │   ├── routes/         # API endpoints
│   │   ├── config.py       # Settings
│   │   ├── database.py     # MongoDB connection
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   ├── setup.bat           # Quick setup
│   └── run.bat             # Start server
│
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── components/     # Reusable components
│   │   ├── services/       # API client
│   │   ├── styles/         # CSS files
│   │   └── App.jsx         # Main component
│   ├── package.json        # JS dependencies
│   ├── vite.config.js      # Build config
│   └── index.html          # Entry HTML
│
├── README.md               # Project overview
└── DEPLOYMENT.md           # Deployment guide
```

---

## 🎨 System Features Explained

### Complaint Submission Flow
```
User Input
    ↓
AI Classification (Gemini API)
    ↓
Language Detection
    ↓
Duplicate Detection (Embeddings)
    ↓
MongoDB Storage
    ↓
Unique ID Generation
    ↓
Display to User
```

### AI Analysis Breakdown
- **Category**: Which department should handle it
- **Severity**: How urgent (Low/Medium/High/Critical)
- **Priority**: Score 1-100 based on impact
- **Department**: Responsible agency
- **Recommendation**: Specific action steps

### Dashboard Analytics
- Real-time complaint count
- Category pie chart
- Severity breakdown
- Top locations heatmap
- High-priority alerts
- Duplicate clusters

---

## 🐛 Troubleshooting

### Backend Won't Start
**Error**: `Cannot connect to MongoDB`
```bash
# Fix: Check .env file
# 1. Verify MONGO_URI is correct
# 2. Whitelist your IP in MongoDB Atlas
# 3. Check internet connection
```

**Error**: `Gemini API error`
```bash
# Fix: Verify API key
# 1. Check GEMINI_API_KEY in .env
# 2. Visit https://makersuite.google.com/app/apikey
# 3. Create new key if needed
```

### Frontend Won't Load
**Error**: `API connection failed`
```bash
# Fix: Check backend is running
# 1. Verify backend running on localhost:8000
# 2. Check frontend .env VITE_API_URL
# 3. Clear browser cache (Ctrl+Shift+Delete)
```

### Database Issues
**Error**: `Connection timeout`
```bash
# Fix: MongoDB Atlas
# 1. Go to Security → Network Access
# 2. Add current IP address
# 3. Or allow all: 0.0.0.0/0 (dev only)
```

---

## 📊 Test Data

### Sample Complaints
```
1. "Pothole on Main Street" → Roads/High
2. "Water leak at intersection" → Water/Critical
3. "Broken streetlight downtown" → Electricity/High
4. "Trash pile in park" → Sanitation/Medium
5. "Traffic jam at peak hours" → Traffic/High
```

### Expected Results
- Each creates unique complaint ID
- Dashboard shows aggregated stats
- Similar complaints grouped together

---

## 🚀 Next Steps

### Short Term
1. ✅ Run locally and test
2. ✅ Submit several complaints
3. ✅ Test status tracking
4. ✅ Explore dashboard

### Medium Term
1. Deploy to Render/Railway
2. Share with testers
3. Gather feedback
4. Add more test data

### Long Term
1. Mobile app version
2. Email notifications
3. Advanced analytics
4. Integration with city services

---

## 💡 Pro Tips

### Speed Up Development
```bash
# Terminal shortcuts
# Backend: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Frontend: npm run dev -- --open

# Auto-reload on file changes
# Both use --reload/--watch flags
```

### Testing APIs Locally
Use Postman or Thunder Client:
```
POST http://localhost:8000/api/v1/complaints/
Body:
{
  "text": "Test complaint",
  "location": "Test City",
  "language": "English"
}
```

### View Real-time Logs
```bash
# Backend: Check terminal for request logs
# Frontend: Browser console (F12 → Console tab)
# Database: MongoDB Atlas dashboard
```

---

## 🎓 Learning Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- MongoDB Docs: https://docs.mongodb.com/
- Vite Docs: https://vitejs.dev/

---

## ✅ Verification Checklist

Before submission/deployment:
- [ ] Backend running without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can submit complaint successfully
- [ ] AI classification works
- [ ] Can track complaint by ID
- [ ] Dashboard shows data
- [ ] No console errors
- [ ] Environment variables set
- [ ] README files updated
- [ ] Git repository clean

---

## 🎯 Common Mistakes to Avoid

1. ❌ Forgetting to create .env file
   - ✅ Create and fill with credentials

2. ❌ Using old MongoDB connection string
   - ✅ Update with new password if changed

3. ❌ Running setup multiple times
   - ✅ Once is enough, just run.bat next time

4. ❌ Accessing wrong API URL in frontend
   - ✅ Check VITE_API_URL in .env

5. ❌ Not whitelisting IP in MongoDB
   - ✅ Add your IP or allow all (dev)

---

## 🆘 Getting Help

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review API docs: http://localhost:8000/api/docs
3. Check console logs (F12 in browser)
4. Read backend README.md
5. Read frontend README.md

---

## 🎉 You're Ready!

You now have a complete, production-ready civic complaint system running locally.

**Next**: Deploy to cloud, gather real data, win the hackathon! 🏆

