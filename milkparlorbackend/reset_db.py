import os
from database import engine
from models import Base
import time

print("Starting deep database reset...")

# 1. Manually delete the database file if it exists
db_path = "milkparlour.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️ Deleted {db_path}")

# Small pause to ensure Windows releases the file handle
time.sleep(1) 

# 2. Force SQLAlchemy to clear its internal schema memory
print("Clearing SQLAlchemy metadata cache...")
Base.metadata.clear()

# 3. Force SQLAlchemy to build brand new tables
print("Building fresh database tables from models.py...")
Base.metadata.create_all(bind=engine)

print("🚀 Database reset complete! The Ghost is dead.")