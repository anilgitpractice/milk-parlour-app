import sqlite3

def upgrade_database():
    print("Connecting to milkparlour.db...")
    # Connect directly to the SQLite file, bypassing SQLAlchemy completely
    conn = sqlite3.connect("milkparlour.db")
    cursor = conn.cursor()

    # 1. Add address to the Users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN address VARCHAR DEFAULT 'No address provided'")
        print("✅ Success: Added 'address' column to the 'users' table!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Notice for users table: {e}")

    # 2. Add address to the Customers table
    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN address VARCHAR DEFAULT 'No address provided'")
        print("✅ Success: Added 'address' column to the 'customers' table!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Notice for customers table: {e}")

    # Save and close
    conn.commit()
    conn.close()
    print("🚀 Database upgrade complete! You can now start your server.")

if __name__ == "__main__":
    upgrade_database()