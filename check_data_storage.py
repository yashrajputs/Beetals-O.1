#!/usr/bin/env python3
"""
Check Streamlit Data Storage
This script examines where and how data is stored in the FileStarter application.
"""

import sqlite3
import os
from pathlib import Path

def check_database_storage():
    """Check SQLite database storage"""
    db_path = "insurance_claims.db"
    
    if not os.path.exists(db_path):
        print("❌ No database file found")
        return
    
    print(f"📊 Database file: {db_path}")
    print(f"📏 Database size: {os.path.getsize(db_path):,} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tables: {[table[0] for table in tables]}")
        
        # Check each table
        for table_name in [table[0] for table in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
        
        # Check documents specifically
        if 'documents' in [table[0] for table in tables]:
            cursor.execute("SELECT filename, upload_date, total_clauses, file_size FROM documents")
            docs = cursor.fetchall()
            print("\n📄 Documents stored:")
            for doc in docs:
                print(f"   - {doc[0]} ({doc[1]}, {doc[2]} clauses, {doc[3]:,} bytes)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def check_chroma_storage():
    """Check ChromaDB storage"""
    chroma_path = "chroma_db"
    
    if not os.path.exists(chroma_path):
        print("❌ No ChromaDB directory found")
        return
    
    print(f"\n🔍 ChromaDB directory: {chroma_path}")
    
    # Get all files and subdirectories
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(chroma_path):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1
            print(f"   - {file}: {size:,} bytes")
    
    print(f"📏 Total ChromaDB size: {total_size:,} bytes ({file_count} files)")

def check_streamlit_config():
    """Check Streamlit configuration"""
    streamlit_path = ".streamlit"
    
    if os.path.exists(streamlit_path):
        print(f"\n⚙️  Streamlit config directory: {streamlit_path}")
        for item in os.listdir(streamlit_path):
            item_path = os.path.join(streamlit_path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"   - {item}: {size} bytes")
    else:
        print("\n❌ No Streamlit config directory found")

def check_session_data():
    """Check for session-related data"""
    print(f"\n🔄 Session Data Storage Analysis:")
    print("   - Session state: In-memory only (lost on refresh)")
    print("   - Persistent data: SQLite database")
    print("   - Vector embeddings: ChromaDB (if available)")
    print("   - File uploads: Temporary (processed then discarded)")
    print("   - User settings: Streamlit config files")

def main():
    print("🔍 FileStarter Data Storage Analysis")
    print("=" * 50)
    
    check_database_storage()
    check_chroma_storage()
    check_streamlit_config()
    check_session_data()
    
    print("\n📍 Data Storage Summary:")
    print("   ✅ SQLite Database: Stores documents, clauses, metadata")
    print("   ✅ ChromaDB: Stores vector embeddings for search")
    print("   ✅ Streamlit Config: App configuration and secrets")
    print("   ❌ Session State: In-memory only, not persistent")

if __name__ == "__main__":
    main()
