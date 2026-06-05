# CivicLens AI Backend

Backend server for CivicLens AI - Intelligent Civic Complaint Management System.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the backend directory:
```env
MONGO_URI="mongodb+srv://user:password@cluster.mongodb.net/"
DB_NAME="hackathon"
GEMINI_API_KEY="your-api-key"
```

### 4. Run the Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: http://localhost:8000

API Documentation: http://localhost:8000/api/docs

## API Endpoints

### Complaints
- `POST /api/v1/complaints/` - Submit a new complaint
- `GET /api/v1/complaints/` - List all complaints
- `GET /api/v1/complaints/{id}` - Get complaint by ID
- `PATCH /api/v1/complaints/{id}` - Update complaint

### Analytics
- `GET /api/v1/complaints/analytics/dashboard` - Get dashboard stats

## Project Structure
```
backend/
├── app/
│   ├── models/
│   │   └── complaint.py       # Data models
│   ├── services/
│   │   ├── ai_service.py      # AI classification
│   │   └── complaint_service.py # Business logic
│   ├── routes/
│   │   └── complaints.py      # API routes
│   ├── config.py              # Configuration
│   ├── database.py            # MongoDB connection
│   └── main.py                # FastAPI app
└── requirements.txt           # Dependencies
```

## Key Features

- **AI Classification**: Instant complaint categorization using Gemini API
- **Severity Detection**: Automatic severity and priority scoring
- **Language Detection**: Support for Urdu, English, and Roman Urdu
- **Duplicate Detection**: Smart grouping of similar complaints
- **MongoDB Integration**: Scalable document storage
- **RESTful API**: Clean, well-documented endpoints

## Technologies

- FastAPI - Modern web framework
- Pydantic - Data validation
- PyMongo - MongoDB driver
- Google Generative AI - Gemini API
- Sentence Transformers - Embedding models
- Uvicorn - ASGI server
