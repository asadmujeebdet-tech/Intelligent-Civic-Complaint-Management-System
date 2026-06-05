# TROUBLESHOOTING GUIDE

## CivicLens AI - Common Issues & Solutions

---

## 🔴 Backend Issues

### Issue 1: "ModuleNotFoundError: No module named 'pymongo'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'pymongo'
```

**Causes:**
- Requirements not installed
- Wrong virtual environment activated
- Python path issue

**Solutions:**
```bash
# 1. Check virtual environment is activated
# Windows: venv\Scripts\activate.bat
# Mac/Linux: source venv/bin/activate

# 2. Reinstall requirements
pip install -r requirements.txt

# 3. Verify installation
python -c "import pymongo; print(pymongo.__version__)"

# Expected output: 4.6.0 (or similar)
```

---

### Issue 2: "Cannot connect to MongoDB"

**Symptoms:**
```
ServerSelectionTimeoutError
Failed to connect to MongoDB: timed out
```

**Causes:**
- MongoDB URI incorrect
- Credentials wrong
- IP not whitelisted
- Internet connection issue
- MongoDB server down

**Solutions:**
```bash
# 1. Verify .env file exists
ls backend/.env  # Linux/Mac
dir backend\.env  # Windows

# 2. Check MONGO_URI format
# Correct: mongodb+srv://user:password@cluster.mongodb.net/
# Wrong: mongodb://...  (missing +srv)

# 3. Test MongoDB connection
python -c "from pymongo import MongoClient; \
           client = MongoClient('your_mongo_uri'); \
           print(client.admin.command('ping'))"

# 4. Whitelist IP in MongoDB Atlas
# - Go to Security → Network Access
# - Add your IP or 0.0.0.0/0 (development only)

# 5. Check password contains no special characters
# If password has @, !, etc., URL encode it
# Example: user%40domain → user@domain
```

---

### Issue 3: "Gemini API error: Invalid API key"

**Symptoms:**
```
google.auth.exceptions.InvalidValue: Invalid API key
API error 400
```

**Causes:**
- API key invalid/expired
- API key not enabled
- API key in wrong format
- Rate limit exceeded

**Solutions:**
```bash
# 1. Get new API key
# Visit: https://makersuite.google.com/app/apikey
# Click "Create API Key" if needed

# 2. Add to .env
GEMINI_API_KEY="AIzaSy..."

# 3. Verify key format
# Should start with "AIzaSy"
# Should be ~39 characters

# 4. Test API
python -c "import google.generativeai as genai; \
           genai.configure(api_key='YOUR_KEY'); \
           print('API configured successfully')"

# 5. Check rate limits
# Free tier: 60 requests/minute
# Wait if you've exceeded limit
```

---

### Issue 4: "Port 8000 already in use"

**Symptoms:**
```
OSError: [Errno 10048] Only one usage of each socket address
Address already in use
```

**Causes:**
- Backend already running
- Port in use by another process
- Port number conflict

**Solutions:**
```bash
# 1. Kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>

# 2. Use different port
python -m uvicorn app.main:app --port 9000

# 3. Check what's using the port
# Windows: netstat -ano | findstr LISTENING
# Mac/Linux: sudo lsof -i -P -n | grep LISTEN
```

---

### Issue 5: "ModuleNotFoundError: No module named 'google.generativeai'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solutions:**
```bash
# 1. Install the package
pip install google-generativeai

# 2. Verify installation
python -c "import google.generativeai; print('Success')"

# 3. Update requirements if needed
pip install -r requirements.txt --upgrade
```

---

### Issue 6: Slow Database Queries

**Symptoms:**
- Dashboard takes >5 seconds to load
- Complaints list is slow

**Solutions:**
```python
# 1. Check indexes are created
db.complaints.list_indexes()

# 2. Create missing indexes manually
db.complaints.create_index('created_at')
db.complaints.create_index('status')
db.complaints.create_index('category')

# 3. Monitor query performance
# Enable MongoDB profiling
db.setProfilingLevel(1)

# 4. Use aggregation pipeline
# Instead of multiple queries, use:
db.complaints.aggregate([
    {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
])
```

---

## 🟠 Frontend Issues

### Issue 1: "API request failed / 404 errors"

**Symptoms:**
```
Failed to fetch
API Error 404 Not Found
CORS error
```

**Causes:**
- Backend not running
- Wrong API URL
- CORS misconfigured
- API endpoint typo

**Solutions:**
```bash
# 1. Verify backend is running
# Should see:
# ✅ Connected to MongoDB
# 🚀 Server starting on http://localhost:8000

# 2. Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000/api/v1

# 3. Test API directly
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# 4. Check browser console (F12)
# Look for error messages

# 5. Verify CORS in backend
# app/config.py should include frontend URL
ALLOWED_ORIGINS = ["http://localhost:3000", ...]

# 6. Clear browser cache
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (Mac)
```

---

### Issue 2: "Cannot find module or package"

**Symptoms:**
```
Module not found: 'recharts'
Package '@' not found
```

**Causes:**
- Dependencies not installed
- Node modules deleted
- package.json outdated

**Solutions:**
```bash
# 1. Install all dependencies
cd frontend
npm install

# 2. Clean install
npm ci  # Uses exact versions from package-lock.json

# 3. Update dependencies
npm update

# 4. Check node_modules exists
ls node_modules  # Should show many folders

# 5. Verify Node version
node --version  # Should be 16+
npm --version   # Should be 7+
```

---

### Issue 3: "Blank page / Nothing loads"

**Symptoms:**
- Frontend URL opens but shows nothing
- White/blank screen
- No console errors

**Causes:**
- Build failed
- JavaScript error
- Vite dev server issue

**Solutions:**
```bash
# 1. Stop and restart dev server
npm run dev

# 2. Check browser console (F12)
# Look for errors

# 3. Check terminal output
# Look for compilation errors

# 4. Clear cache and restart
# Delete: frontend/node_modules
npm install
npm run dev

# 5. Check index.html
# Should have: <div id="root"></div>
# And: <script type="module" src="/src/main.jsx"></script>
```

---

### Issue 4: "Complaint submission fails / No response"

**Symptoms:**
- Click "Submit" but nothing happens
- Loading spinner spins forever
- Network request times out

**Causes:**
- Backend crashed
- API error
- Network timeout
- Large file upload

**Solutions:**
```bash
# 1. Check backend is running
# Terminal: python -m uvicorn app.main:app --reload

# 2. Check browser console (F12)
# Look for error in Network tab
# Check response body

# 3. Verify complaint text is valid
# Min 10 characters
# Max 2000 characters

# 4. Check network in browser
# F12 → Network tab
# Click Submit
# Look for failed requests
# Check response status

# 5. Increase timeout if slow
# In frontend/src/services/api.js:
axios.create({ timeout: 10000 })  // 10 seconds

# 6. Check server logs
# Backend terminal should show POST request
```

---

### Issue 5: "Charts not showing / Dashboard empty"

**Symptoms:**
- Dashboard loads but no charts
- Data shows 0 everywhere
- Charts appear but no data

**Causes:**
- No data in database
- API error
- Recharts rendering issue
- CORS issue

**Solutions:**
```bash
# 1. Submit test complaints
# Go to /submit
# Submit 3-5 test complaints

# 2. Check MongoDB has data
# MongoDB Atlas → Collections
# Should see documents in 'complaints'

# 3. Test API endpoint directly
curl http://localhost:8000/api/v1/complaints/analytics/dashboard

# Expected response with numbers

# 4. Check browser console
# F12 → Console tab
# Look for Recharts errors

# 5. Force refresh
# Ctrl+F5 (hard refresh)
# Cmd+Shift+R (Mac)

# 6. Check data format
# API should return:
{
  "data": {
    "total_complaints": 5,
    "category_breakdown": {...},
    ...
  }
}
```

---

## 🟡 Database Issues

### Issue 1: "Collection not found"

**Symptoms:**
```
KeyError: Collection not found
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**
```bash
# 1. Collections auto-create on first insert
# Just submit a complaint first

# 2. Manually create if needed
# MongoDB Atlas → Collections → Create
# Name: complaints

# 3. Check database name
# .env should have: DB_NAME="hackathon"
# MongoDB should have database: "hackathon"
```

---

### Issue 2: "Duplicate key error"

**Symptoms:**
```
E11000 duplicate key error
```

**Solutions:**
```bash
# 1. Drop duplicate index
db.complaints.dropIndex("text_1")

# 2. Remove duplicate entries
db.complaints.deleteMany({"_id": ObjectId("...")})

# 3. Reindex collection
db.complaints.reIndex()
```

---

## ✅ Verification Checklist

Before declaring success:

- [ ] Backend starts without errors
- [ ] MongoDB connection successful
- [ ] Gemini API initialized
- [ ] Frontend loads at localhost:3000
- [ ] Navigation works
- [ ] Form submits successfully
- [ ] AI analysis displays
- [ ] Complaint ID returned
- [ ] Status tracking works
- [ ] Dashboard shows data
- [ ] Charts render
- [ ] No console errors
- [ ] No network errors

---

## 🆘 Getting Help

### Step 1: Check Logs
```bash
# Backend terminal: Look for errors
# Frontend terminal: npm run dev output
# Browser console: F12 → Console
# Browser network: F12 → Network
```

### Step 2: Run Diagnostics
```bash
# Check Python
python --version  # Should be 3.9+

# Check Node
node --version    # Should be 16+

# Check MongoDB
python -c "from pymongo import MongoClient; \
           print('MongoDB OK')"

# Check Gemini
python -c "import google.generativeai; \
           print('Gemini OK')"
```

### Step 3: Review Documentation
- [GETTING_STARTED.md](GETTING_STARTED.md)
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)

### Step 4: Common Fixes
```bash
# Clear everything and restart
# Backend
rm -rf backend/venv  # or Windows: rmdir backend\venv /s
cd backend
setup.bat  # or setup.sh

# Frontend
rm -rf frontend/node_modules  # Windows: rmdir frontend\node_modules /s
cd frontend
setup.bat  # or setup.sh
```

---

## 🐛 Debug Mode

### Enable Verbose Logging
```python
# backend/app/main.py
import logging

logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed logs
```

### Enable Frontend Debugging
```javascript
// frontend/src/services/api.js
api.interceptors.response.use(
  response => {
    console.log('API Response:', response.data);
    return response;
  },
  error => {
    console.error('API Error:', error.response);
    return Promise.reject(error);
  }
);
```

---

## 📞 Support Resources

- Backend API Docs: http://localhost:8000/api/docs
- Python Docs: https://docs.python.org/
- React Docs: https://react.dev/
- MongoDB Docs: https://docs.mongodb.com/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

If issues persist, please:
1. Provide error message
2. Include terminal output
3. Check .env is properly set
4. Verify all prerequisites installed

