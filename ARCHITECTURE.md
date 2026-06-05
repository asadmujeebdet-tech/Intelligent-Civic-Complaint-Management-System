# ARCHITECTURE GUIDE

## CivicLens AI - System Design & Architecture

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React SPA (Vite)                                        │  │
│  │  - Home Page (Hero + Features)                           │  │
│  │  - Submit Complaint (Form + AI Analysis)                │  │
│  │  - Track Complaint (Status Timeline)                     │  │
│  │  - Dashboard (Analytics + Charts)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                       │
│                    HTTP/REST API                                 │
│                    JSON Requests                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Application Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python)                                        │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Route Layer (REST API)                          │   │  │
│  │  │ - POST /complaints/                             │   │  │
│  │  │ - GET /complaints/                              │   │  │
│  │  │ - GET /complaints/{id}                          │   │  │
│  │  │ - PATCH /complaints/{id}                        │   │  │
│  │  │ - GET /dashboard                                │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │           │                                             │  │
│  │  ┌────────▼─────────────────────────────────────────┐  │  │
│  │  │ Service Layer (Business Logic)                   │  │  │
│  │  │ - ComplaintService (CRUD)                        │  │  │
│  │  │ - AIService (Gemini + Embeddings)               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │           │                                             │  │
│  │  ┌────────▼─────────────────────────────────────────┐  │  │
│  │  │ Data Access Layer                                │  │  │
│  │  │ - MongoDB Connection                            │  │  │
│  │  │ - Collections: complaints, complaint_groups     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                    │
│              PyMongo Driver                                   │
│              JSON Documents                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                    Data Layer                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MongoDB Atlas (NoSQL Database)                      │   │
│  │  Collections:                                        │   │
│  │  - complaints (main data)                           │   │
│  │  - complaint_groups (clustering)                    │   │
│  │  - users (optional)                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                          │
┌────────────────────────▼─────────────────────────────────────┐
│                  External AI APIs                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Google Gemini API                                  │    │
│  │ - Text Classification                            │    │
│  │ - Category Detection                             │    │
│  │ - Recommendation Generation                      │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Sentence Transformers (Local)                      │    │
│  │ - Embedding Generation                            │    │
│  │ - Similarity Calculation                          │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Diagram

### Complaint Submission Flow

```
User Input Form
    ↓
Validation (Pydantic)
    ↓
Language Detection (langdetect)
    ↓
AI Classification (Gemini API)
    ├─ Category Detection
    ├─ Severity Scoring
    ├─ Priority Calculation
    └─ Recommendation Generation
    ↓
Embedding Generation (SentenceTransformers)
    ↓
Duplicate Detection
    ├─ Search Similar Complaints
    ├─ Calculate Similarity
    └─ Create/Update Group
    ↓
MongoDB Insert
    ├─ Store Complaint Document
    └─ Create Indexes
    ↓
Response to Client
    ├─ Complaint ID
    ├─ AI Analysis
    └─ Status: Success
    ↓
Frontend Display
    ├─ Success Message
    ├─ Show Complaint ID
    └─ Display AI Results
```

---

## 📦 Component Architecture

### Backend Components

```
app/
├── config.py
│   └─ Settings & Environment Loading
│       Pydantic Settings
│       Environment Variables
│
├── database.py
│   └─ MongoDB Connection Manager
│       Connect/Disconnect
│       Index Creation
│       Connection Pooling
│
├── models/
│   └─ complaint.py
│       Pydantic Schemas
│       Data Validation
│       Type Definitions
│
├── services/
│   ├── ai_service.py
│   │   ├─ Language Detection
│   │   ├─ Classification
│   │   ├─ Embedding Generation
│   │   └─ Duplicate Detection
│   │
│   └─ complaint_service.py
│       ├─ Create Complaint
│       ├─ Retrieve Complaints
│       ├─ Update Complaint
│       ├─ Dashboard Stats
│       └─ Group Management
│
├── routes/
│   └─ complaints.py
│       ├─ POST /complaints/
│       ├─ GET /complaints/
│       ├─ GET /complaints/{id}
│       ├─ PATCH /complaints/{id}
│       └─ GET /analytics/dashboard
│
└── main.py
    ├─ FastAPI App
    ├─ Middleware
    ├─ Startup/Shutdown Events
    └─ CORS Configuration
```

### Frontend Components

```
src/
├── pages/
│   ├─ Home.jsx
│   │  ├─ Hero Section
│   │  ├─ Stats Cards
│   │  ├─ Features Grid
│   │  └─ CTA Section
│   │
│   ├─ SubmitComplaint.jsx
│   │  ├─ Complaint Form
│   │  ├─ AI Analysis Display
│   │  ├─ Success State
│   │  └─ Error Handling
│   │
│   ├─ TrackComplaint.jsx
│   │  ├─ Search Bar
│   │  ├─ Timeline Display
│   │  ├─ Complaint Details
│   │  └─ AI Recommendations
│   │
│   └─ Dashboard.jsx
│       ├─ KPI Cards
│       ├─ Category Chart
│       ├─ Severity Distribution
│       ├─ Location Heatmap
│       └─ Insights Panel
│
├── components/
│   └─ Navbar.jsx
│       ├─ Logo
│       ├─ Navigation Links
│       └─ Mobile Menu
│
├── services/
│   └─ api.js
│       ├─ Axios Instance
│       ├─ Base URL Config
│       └─ API Methods
│
└── styles/
    ├─ global.css (Base Styles)
    ├─ navbar.css
    ├─ home.css
    ├─ submit.css
    ├─ track.css
    └─ dashboard.css
```

---

## 🔗 Data Flow Examples

### Example 1: Submit Complaint

```
Frontend: User submits form
    ↓ (POST /api/v1/complaints/)
Backend: ComplaintService.create_complaint()
    ↓
1. Language Detection
   - Input: complaint text
   - Process: langdetect library
   - Output: "English", "Urdu", etc.
    ↓
2. AI Classification
   - Input: text + location
   - API Call: Gemini
   - Output: category, severity, priority
    ↓
3. Embedding Generation
   - Input: complaint text
   - Model: SentenceTransformers
   - Output: vector [768 dimensions]
    ↓
4. Duplicate Detection
   - Query: Find similar complaints
   - Calculate: Cosine Similarity
   - If > 0.85: Create group
    ↓
5. MongoDB Insert
   - Collection: complaints
   - Document: full complaint object
   - Indexes: category, severity, status
    ↓
Backend: Return response with ID
    ↓ (JSON response)
Frontend: Display success + ID
```

### Example 2: View Dashboard

```
Frontend: User clicks Analytics
    ↓ (GET /api/v1/complaints/analytics/dashboard)
Backend: ComplaintService.get_dashboard_stats()
    ↓
Aggregations:
1. Count total complaints
2. Count by status
3. Group by category
4. Group by severity
5. Top locations
6. Count critical
7. Count high priority
8. Count duplicate groups
    ↓
Database: Multiple queries
1. db.complaints.count_documents()
2. db.complaints.aggregate()
    ↓
Backend: Build response object
    ↓ (JSON with statistics)
Frontend: Recharts visualizes data
    ↓
User: Sees charts and insights
```

---

## 🗄️ Database Schema Details

### complaints Collection

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  
  // User Input
  text: String (10-2000 chars),
  location: String,
  language: String (enum: "English", "Urdu", "Roman Urdu"),
  
  // AI Analysis Results
  category: String (enum: Roads, Water, Electricity, ...),
  severity: String (enum: Low, Medium, High, Critical),
  priority: Number (1-100),
  department: String,
  ai_recommendation: String,
  ai_confidence: Number (0.0-1.0),
  
  // System Fields
  status: String (enum: open, in-progress, resolved),
  created_at: ISODate,
  updated_at: ISODate,
  
  // Duplicate Detection
  duplicate_group_id: ObjectId (nullable),
  embeddings: Array<Number> (768 dimensions),
  
  // Indexes
  _id (primary)
  created_at (for sorting)
  status (for filtering)
  category (for filtering)
  severity (for filtering)
  priority (for sorting)
  duplicate_group_id (for grouping)
}
```

### complaint_groups Collection

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439012"),
  
  issue_type: "duplicate_cluster",
  complaint_ids: [ObjectId, ObjectId, ObjectId],
  hotspot_location: String,
  created_at: ISODate,
  
  // Indexes
  _id (primary)
  complaint_ids (for searching)
}
```

---

## 🔐 Security Architecture

### Input Validation
```
User Input
    ↓
Pydantic Validation
    ├─ Type checking
    ├─ Length validation
    ├─ Format validation
    └─ Enum validation
    ↓
Sanitization
    ├─ Trim whitespace
    ├─ Remove special chars
    └─ Encode/Escape
    ↓
Database Query
    └─ Parameterized queries
```

### Environment Security
```
Sensitive Data (.env)
    ├─ MONGO_URI
    ├─ GEMINI_API_KEY
    └─ DB_NAME
    
Never in:
    ❌ Source code
    ❌ .gitignore exclusion
    ❌ Logs
    ❌ Error messages
    
Access:
    ✓ Environment variables
    ✓ Settings class (Pydantic)
    ✓ Runtime only
```

---

## ⚡ Performance Considerations

### Database Optimization
```
Indexes:
- created_at: For sorting
- status: For filtering
- category: For filtering
- severity: For filtering
- priority: For sorting

Queries:
- Use projections (select fields)
- Limit results with pagination
- Sort on indexed fields
- Use aggregation pipeline
```

### API Optimization
```
Frontend:
- Code splitting
- Lazy loading
- Compression
- Caching headers

Backend:
- Connection pooling
- Query optimization
- Response caching
- Async operations
```

### Embedding Storage
```
Trade-offs:
- Store embeddings: 768 floats per complaint
- Size: ~3KB per complaint
- Allows fast similarity search
- Alternative: Regenerate on demand
```

---

## 🔄 Scalability Strategy

### Current (Development)
- Single backend instance
- MongoDB free tier
- Synchronous operations
- In-memory embeddings

### Production Ready
```
Phase 1: Increase capacity
- MongoDB cluster (auto-scaling)
- Multiple backend replicas
- Load balancing
- Database connection pooling

Phase 2: Optimize
- Redis caching layer
- Async job queue (Celery)
- Elasticsearch for full-text
- Elasticsearch + Vector search

Phase 3: Distributed
- Microservices architecture
- Separate AI service
- Message queues
- Distributed caching
```

---

## 🧠 AI Pipeline Details

### Language Detection
```
Input: "کیا یہ سڑک ٹوٹی ہے"
    ↓
langdetect library
    ↓
Output: "ur" (Urdu)
    ↓
Map to: "Urdu"
```

### Classification
```
Input: 
  text: "Pothole on Main Street"
  location: "Downtown"
  
Prompt to Gemini:
  "Analyze this civic complaint and classify it..."
    ↓
Gemini Response:
  {
    category: "Roads",
    severity: "High",
    priority: 75,
    department: "Public Works",
    recommendation: "Schedule road inspection...",
    confidence: 0.95
  }
```

### Duplicate Detection
```
New Complaint Text
    ↓
Generate Embedding (SentenceTransformers)
    ↓
Query Database (find all embeddings)
    ↓
Calculate Cosine Similarity
    for each existing complaint:
      similarity = dot_product(new, existing) / (norm(new) * norm(existing))
    ↓
If similarity >= 0.85:
    Create duplicate_group
    Update complaint_group_id
```

---

## 📊 Monitoring & Logging

### What to Monitor
```
Backend:
- Request/Response times
- Error rates
- API endpoint usage
- Database query times
- Memory usage
- CPU usage

Frontend:
- Page load time
- API response time
- JavaScript errors
- User interactions
- Network requests

Database:
- Connection pool usage
- Query performance
- Storage usage
- Index usage
```

### Logging Strategy
```
Backend (Python logging):
- INFO: API requests/responses
- WARNING: Slow queries
- ERROR: Exceptions
- DEBUG: Detailed execution

Frontend (Browser console):
- INFO: Page navigation
- WARNING: API errors
- ERROR: JavaScript errors

Database (MongoDB logs):
- Query execution
- Index usage
- Connection events
```

---

## 🎯 Design Patterns Used

1. **Service Layer Pattern**
   - Business logic separated from routes
   - Reusable services

2. **Repository Pattern**
   - Database access abstraction
   - Easy to swap backends

3. **Singleton Pattern**
   - AI service single instance
   - Database connection pooling

4. **MVC Pattern (Frontend)**
   - Pages (Views)
   - Components (Controllers)
   - Services (Models)

5. **Factory Pattern**
   - Complaint creation
   - Complex object building

---

This architecture ensures scalability, maintainability, and production-readiness.

