"""
Script to load bakery data from CSV to database and vector DB
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.database import engine, Base, SessionLocal
from app.models import Bakery
from app.utils import load_bakery_csv, validate_bakery_data
from app.services import EmbeddingService, RAGService
from app.repositories import VectorRepository
import uuid


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def load_bakeries_from_csv(csv_path: str):
    """Load bakeries from CSV file"""
    print(f"Loading bakeries from {csv_path}...")
    
    bakery_data_list = load_bakery_csv(csv_path)
    print(f"Loaded {len(bakery_data_list)} bakeries from CSV")
    
    # Get database session
    db = SessionLocal()
    rag_service = RAGService(db)
    embedding_service = EmbeddingService()
    vector_repo = VectorRepository()
    
    try:
        # Process each bakery
        for i, bakery_data in enumerate(bakery_data_list, 1):
            if not validate_bakery_data(bakery_data):
                print(f"✗ Skipping invalid bakery: {bakery_data}")
                continue
            
            try:
                # Check if bakery already exists
                existing = db.query(Bakery).filter(
                    Bakery.name == bakery_data["name"],
                    Bakery.address == bakery_data["address"]
                ).first()
                
                if existing:
                    print(f"⊘ Bakery already exists: {bakery_data['name']}")
                    continue
                
                # Generate bakery ID
                bakery_id = uuid.uuid4()
                
                # Create bakery record
                bakery = Bakery(
                    id=bakery_id,
                    name=bakery_data["name"],
                    shop_id=bakery_data.get("shop_id"),
                    rating=bakery_data.get("rating"),
                    address=bakery_data["address"],
                    tel=bakery_data.get("tel"),
                    website=bakery_data.get("website"),
                    category=bakery_data.get("category"),
                    district=bakery_data.get("district"),
                    ai_summary=bakery_data.get("ai_summary"),
                )
                
                # Save to RDB
                db.add(bakery)
                db.commit()
                db.refresh(bakery)
                
                # Generate embedding
                embedding = embedding_service.embed_bakery_content(bakery_data)
                
                # Save to Vector DB
                metadata = {
                    "bakery_id": str(bakery_id),
                    "name": bakery_data["name"],
                    "address": bakery_data["address"],
                    "district": bakery_data.get("district"),
                }
                vector_repo.upsert_vector(str(bakery_id), embedding, metadata)
                
                # Update bakery with vector_db_id
                bakery.vector_db_id = str(bakery_id)
                db.commit()
                
                print(f"✓ [{i}/{len(bakery_data_list)}] {bakery_data['name']} loaded successfully")
                
            except Exception as e:
                db.rollback()
                print(f"✗ Error loading {bakery_data.get('name')}: {str(e)}")
                continue
    
    finally:
        db.close()
    
    print(f"\n✓ Data loading completed!")


if __name__ == "__main__":
    csv_path = "bakery_list.csv"
    
    # Initialize database
    init_db()
    
    # Load data
    load_bakeries_from_csv(csv_path)
