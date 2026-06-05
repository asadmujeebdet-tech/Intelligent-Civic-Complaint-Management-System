from pymongo import MongoClient
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB Database Connection Manager"""
    
    client = None
    db = None
    
    @classmethod
    def connect(cls):
        """Connect to MongoDB"""
        try:
            cls.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.DB_NAME]
            
            # Create indexes
            cls._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {settings.DB_NAME}")
            return cls.db
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("✅ Disconnected from MongoDB")
    
    @classmethod
    def _create_indexes(cls):
        """Create necessary indexes"""
        try:
            # Complaints collection indexes
            complaints = cls.db['complaints']
            complaints.create_index('created_at')
            complaints.create_index('status')
            complaints.create_index('category')
            complaints.create_index('severity')
            complaints.create_index('priority')
            complaints.create_index('duplicate_group_id')
            complaints.create_index('complaint_id')
            complaints.create_index('location')
            complaints.create_index('assigned_department')
            complaints.create_index([('latitude', 1), ('longitude', 1)])

            groups = cls.db['complaint_groups']
            groups.create_index('complaint_ids')

            history = cls.db['status_history']
            history.create_index('complaint_id')
            history.create_index('timestamp')
            
            logger.info("✅ Indexes created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")

def get_db():
    """Get database connection"""
    if Database.db is None:
        Database.connect()
    return Database.db
