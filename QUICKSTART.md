# CivicLens AI - Quick Start Guide (5 Minutes!)

## ⚡ Fastest Setup

### Windows (30 seconds)
```bash
cd backend
setup.bat
```

### Mac/Linux (30 seconds)
```bash
cd backend
bash setup.sh
```

That's it! The setup creates a virtual environment and installs dependencies.

---

## 🔑 Step 2: Add Credentials (1 minute)

Create a `.env` file in the `backend` folder:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=hackathon
GEMINI_API_KEY=AIzaSy...
```

**Where to get them:**
- **MongoDB URI**: [atlas.mongodb.com](https://atlas.mongodb.com) (free tier available)
- **Gemini API Key**: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

---

## 🚀 Step 3: Start (30 seconds)

### Windows
```bash
cd backend
run.bat
```

### Mac/Linux
```bash
cd backend
bash run.sh
```

You'll see:
```
✅ Database initialized
🚀 Uvicorn running on http://0.0.0.0:8000
```

---

## 🌐 Step 4: Access Your App (Instant!)

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | **Main App** ← Start here! |
| http://localhost:8000/submit.html | Report issue |
| http://localhost:8000/track.html | Track complaint |
| http://localhost:8000/dashboard.html | Analytics |
| http://localhost:8000/api/docs | API Documentation |

---

## ✅ Test It Out

### 1. Submit a Complaint
- Go to http://localhost:8000
- Click "Report Issue"
- Fill in the form
- AI analyzes instantly
- Get your complaint ID

### 2. Track Your Complaint
- Go to Track Status page
- Paste your complaint ID
- See timeline and details

### 3. View Analytics
- Go to Dashboard
- See charts and statistics
- Watch real-time updates

---

## 📁 Project Structure

```
Hackathon/
├── backend/              ← Python/FastAPI
│   ├── app/             ← Application code
│   ├── requirements.txt ← Dependencies
│   ├── setup.bat/.sh   ← Setup script
│   └── run.bat/.sh     ← Start server
│
├── frontend/            ← HTML/CSS/JS (served by backend)
│   ├── index.html       ← Home page
│   ├── submit.html      ← Complaint form
│   ├── track.html       ← Track status
│   ├── dashboard.html   ← Analytics
│   ├── js/              ← JavaScript files
│   └── css/             ← Stylesheets
│
└── docs/               ← Documentation
```

---

## 🛠️ Tech Stack (Really Simple!)

```
Frontend:    HTML5 + CSS3 + Bootstrap5 + JavaScript
Backend:     Python + FastAPI
Database:    MongoDB (Cloud - MongoDB Atlas)
AI:          Google Gemini API
Charts:      Chart.js
```

**That's it! No npm, no Node.js, no build process.**

---

## 🐛 Troubleshooting

### "MongoDB connection failed"
- Check your `MONGO_URI` in `.env`
- Make sure MongoDB Atlas cluster is running
- Verify username/password are correct

### "Gemini API key not valid"
- Get key from [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- Paste entire key (starts with `AIzaSy...`)
- Make sure you have API enabled

### "Address already in use port 8000"
- Another app is using port 8000
- Kill the process or use different port:
  ```bash
  uvicorn app.main:app --port 8001
  ```

### "Module not found"
- Make sure virtual environment is activated
- Re-run setup: `setup.bat`

---

## 📝 Features at a Glance

✅ **Instant AI Analysis**
- Auto-categorizes complaints
- Detects severity level
- Generates recommendations

✅ **No Login Required**
- Citizens report directly
- Get unique complaint ID
- Track progress anytime

✅ **Beautiful Dashboard**
- Real-time statistics
- Interactive charts
- Geographic hotspots
- Critical alerts

✅ **Multi-Language**
- Supports Urdu, English, Roman Urdu
- Auto-detects language

✅ **Mobile Responsive**
- Works on phones, tablets, desktops
- Beautiful on all screens

---

## 🎯 Next Steps

### For Development
1. Make changes to frontend files (no rebuild needed!)
2. Refresh browser to see changes
3. Check console (F12) for errors

### For Deployment
1. Follow [DEPLOYMENT.md](DEPLOYMENT.md)
2. Deploy to Render.com (free)
3. Share link with others

### For Customization
1. Edit HTML files directly
2. Modify colors in `frontend/css/style.css`
3. Add new pages as needed

---

## 🎓 Learning Resources

| Document | Purpose |
|----------|---------|
| README.md | Project overview |
| REBUILD_SUMMARY.md | What changed from React |
| API_DOCUMENTATION.md | REST API reference |
| ARCHITECTURE.md | System design |
| TROUBLESHOOTING.md | Common issues |

---

## 💡 Pro Tips

### Fast Development
- Keep backend running: `run.bat`
- Edit HTML/CSS files
- Refresh browser (no rebuild!)
- Changes appear instantly

### Debugging
- Open browser DevTools (F12)
- Check Console for errors
- Check Network tab for API calls
- Use Postman for API testing

### Performance
- Bootstrap classes handle responsive design
- Chart.js renders efficiently
- API calls are optimized
- Database queries indexed

---

## 🚀 You're Ready!

Your CivicLens AI app is now:
- ✨ Set up and running
- 📊 Fully functional
- 🎨 Beautiful UI
- ⚡ Production ready

**Start building!** 🎉

---

## ❓ Questions?

### Check These First
1. **Setup issues** → TROUBLESHOOTING.md
2. **How to use API** → API_DOCUMENTATION.md
3. **Project structure** → README.md
4. **Technical details** → ARCHITECTURE.md

### Common Commands
```bash
# Backend setup
cd backend && setup.bat

# Backend start
cd backend && run.bat

# View logs
# Watch terminal output while running

# Stop backend
# Press Ctrl+C in terminal
```

---

## 🎉 Final Checklist

Before submitting:
- [ ] .env file created with credentials
- [ ] Backend runs without errors
- [ ] Frontend loads at http://localhost:8000
- [ ] Can submit complaints
- [ ] AI analysis displays correctly
- [ ] Can track complaints by ID
- [ ] Dashboard shows charts
- [ ] Mobile layout looks good

**All checked? You're ready to win! 🏆**

