# API DOCUMENTATION

## CivicLens AI - REST API Reference

Base URL: `http://localhost:8000/api/v1`

---

## 📋 Endpoints

### Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "CivicLens AI Backend",
  "version": "1.0.0"
}
```

---

### Submit Complaint
```
POST /api/v1/complaints/
```

**Request Body:**
```json
{
  "text": "Pothole on Main Street",
  "location": "Downtown",
  "category": "Roads",
  "language": "English"
}
```

**Parameters:**
- `text` (string, required): Complaint description (10-2000 chars)
- `location` (string, required): City/area name
- `category` (string, optional): Pre-selected category
- `language` (string, optional): "English", "Urdu", "Roman Urdu"

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Complaint submitted successfully",
  "complaint_id": "507f1f77bcf86cd799439011",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "text": "Pothole on Main Street",
    "category": "Roads",
    "severity": "High",
    "priority": 75,
    "language": "English",
    "location": "Downtown",
    "status": "open",
    "department": "Public Works",
    "ai_recommendation": "Schedule road inspection and repair.",
    "ai_confidence": 0.95,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/complaints/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Pothole on Main Street near the park",
    "location": "Downtown",
    "language": "English"
  }'
```

---

### Get Complaint
```
GET /api/v1/complaints/{complaint_id}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "text": "Pothole on Main Street",
    "category": "Roads",
    "severity": "High",
    "priority": 75,
    "language": "English",
    "location": "Downtown",
    "status": "open",
    "department": "Public Works",
    "ai_recommendation": "Schedule road inspection and repair.",
    "created_at": "2024-01-15T10:30:00Z",
    "duplicate_group_id": null
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Complaint not found"
}
```

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/complaints/507f1f77bcf86cd799439011"
```

---

### List Complaints
```
GET /api/v1/complaints/?skip=0&limit=50&status=open&category=Roads
```

**Query Parameters:**
- `skip` (integer, default: 0): Pagination offset
- `limit` (integer, default: 50): Results per page (max: 100)
- `status` (string, optional): Filter by status
- `category` (string, optional): Filter by category

**Response (200 OK):**
```json
{
  "status": "success",
  "total": 3,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "text": "Pothole on Main Street",
      "category": "Roads",
      "severity": "High",
      "priority": 75,
      "status": "open"
      // ... more fields
    },
    // ... more complaints
  ]
}
```

**Example cURL:**
```bash
# List all open complaints
curl "http://localhost:8000/api/v1/complaints/?status=open"

# List Roads category complaints, paginated
curl "http://localhost:8000/api/v1/complaints/?category=Roads&skip=0&limit=10"
```

---

### Update Complaint
```
PATCH /api/v1/complaints/{complaint_id}
```

**Request Body:**
```json
{
  "status": "in-progress"
}
```

**Allowed Fields:**
- `status`: "open", "in-progress", "resolved"
- `category`: Category name
- Any other updateable field

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Complaint updated successfully"
}
```

**Example cURL:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/complaints/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress"}'
```

---

### Get Dashboard Analytics
```
GET /api/v1/complaints/analytics/dashboard
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total_complaints": 45,
    "open_complaints": 12,
    "in_progress_complaints": 15,
    "resolved_complaints": 18,
    "resolved_percentage": 40.0,
    "category_breakdown": {
      "Roads": 15,
      "Water": 8,
      "Electricity": 5,
      "Sanitation": 7,
      "Traffic": 6,
      "Public Safety": 2,
      "Environment": 2
    },
    "severity_breakdown": {
      "Low": 8,
      "Medium": 15,
      "High": 18,
      "Critical": 4
    },
    "top_locations": [
      {"location": "Downtown", "count": 18},
      {"location": "Main Street", "count": 12},
      {"location": "City Center", "count": 8},
      {"location": "North End", "count": 4},
      {"location": "South Park", "count": 3}
    ],
    "high_priority_count": 22,
    "critical_count": 4,
    "duplicate_clusters": 3
  }
}
```

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/complaints/analytics/dashboard"
```

---

## 📊 Data Types

### Complaint Status
- `open`: Newly submitted
- `in-progress`: Being handled
- `resolved`: Completed

### Categories
- `Roads`
- `Water`
- `Electricity`
- `Sanitation`
- `Traffic`
- `Public Safety`
- `Environment`

### Severity Levels
- `Low`: Minor issue
- `Medium`: Moderate concern
- `High`: Urgent attention needed
- `Critical`: Immediate action required

### Languages
- `English`
- `Urdu` (اردو)
- `Roman Urdu`

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "detail": "Complaint description must be at least 10 characters"
}
```

### 404 Not Found
```json
{
  "detail": "Complaint not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🔄 Common Workflows

### Workflow 1: Submit and Track
```
1. POST /api/v1/complaints/ → Get complaint_id
2. GET /api/v1/complaints/{id} → Check status
3. PATCH /api/v1/complaints/{id} → Update status (admin)
```

### Workflow 2: Analytics Dashboard
```
1. GET /api/v1/complaints/analytics/dashboard → Get stats
2. GET /api/v1/complaints/?category=Roads → Filter by category
3. GET /api/v1/complaints/?status=in-progress → Filter by status
```

---

## 📈 Rate Limits
- No rate limiting in development
- Gemini API: 60 requests/minute (free tier)
- MongoDB Atlas: Depends on cluster tier

---

## 🧪 Testing with Postman

1. Import collection (create new request)
2. Set base URL: `http://localhost:8000/api/v1`
3. Create endpoints for each operation
4. Test with sample data

---

## 🔗 Interactive API Docs

Visit: `http://localhost:8000/api/docs`

Provides:
- Interactive endpoint testing
- Automatic request/response examples
- Swagger UI documentation
- Schema validation

---

## 📝 Notes

- All timestamps in ISO 8601 format (UTC)
- IDs are MongoDB ObjectIds (24 hex characters)
- Complaint ID used for tracking by citizens
- All requests return JSON

