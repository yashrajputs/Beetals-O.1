import os
import sqlite3
import json
import hashlib
import pickle
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import streamlit as st

# Try to import ChromaDB, use fallback if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

class DatabaseManager:
    def __init__(self, db_path: str = "insurance_claims.db", chroma_path: str = "./chroma_db"):
        """Initialize database connections"""
        self.db_path = db_path
        self.chroma_path = chroma_path
        self.init_sqlite()
        self.init_chromadb()
    
    def init_sqlite(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Create tables
        cursor = self.conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_clauses INTEGER,
                processed_date TIMESTAMP,
                file_size INTEGER
            )
        ''')
        
        # Clauses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clauses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                title TEXT,
                text TEXT,
                page_number INTEGER,
                section_type TEXT,
                clause_index INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Vector index metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                collection_name TEXT UNIQUE,
                vector_count INTEGER,
                model_name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        self.conn.commit()
    
    def init_chromadb(self):
        """Initialize ChromaDB client"""
        if not CHROMADB_AVAILABLE:
            self.chroma_client = None
            return
            
        try:
            # Create ChromaDB client with persistent storage
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            # ChromaDB not available, use fallback search silently
            self.chroma_client = None
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate MD5 hash of file content"""
        return hashlib.md5(file_content).hexdigest()
    
    def document_exists(self, filename: str, file_content: bytes) -> Optional[int]:
        """Check if document already exists by filename and hash"""
        file_hash = self.calculate_file_hash(file_content)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM documents WHERE filename = ? AND file_hash = ?",
            (filename, file_hash)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def store_document(self, filename: str, file_content: bytes, structured_clauses: List[Dict]) -> int:
        """Store document and its clauses in the database"""
        file_hash = self.calculate_file_hash(file_content)
        file_size = len(file_content)
        
        cursor = self.conn.cursor()
        
        try:
            # Insert document
            cursor.execute('''
                INSERT INTO documents (filename, file_hash, total_clauses, file_size, processed_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, file_hash, len(structured_clauses), file_size, datetime.now()))
            
            document_id = cursor.lastrowid
            
            # Insert clauses
            for idx, clause in enumerate(structured_clauses):
                cursor.execute('''
                    INSERT INTO clauses (document_id, title, text, page_number, section_type, clause_index)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    document_id,
                    clause.get('title', ''),
                    clause.get('text', ''),
                    clause.get('page_number', 0),
                    clause.get('section_type', ''),
                    idx
                ))
            
            self.conn.commit()
            return document_id
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise Exception(f"Document already exists: {str(e)}")
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Failed to store document: {str(e)}")
    
    def store_vector_index(self, document_id: int, structured_clauses: List[Dict], 
                          model_name: str = "default") -> str:
        """Store vector embeddings in ChromaDB"""
        if not CHROMADB_AVAILABLE or self.chroma_client is None:
            # Store minimal metadata in SQLite for fallback search
            collection_name = f"doc_{document_id}_fallback"
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO vector_metadata (document_id, collection_name, vector_count, model_name)
                VALUES (?, ?, ?, ?)
            ''', (document_id, collection_name, len(structured_clauses), "fallback"))
            self.conn.commit()
            return collection_name
            
        try:
            # Create unique collection name
            collection_name = f"doc_{document_id}_vectors"
            
            # Get or create collection
            try:
                collection = self.chroma_client.get_collection(collection_name)
                # If collection exists, delete it to recreate
                self.chroma_client.delete_collection(collection_name)
            except:
                pass  # Collection doesn't exist, which is fine
            
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"document_id": document_id}
            )
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for idx, clause in enumerate(structured_clauses):
                ids.append(f"clause_{idx}")
                documents.append(clause['text'])
                metadatas.append({
                    'title': clause.get('title', ''),
                    'page_number': clause.get('page_number', 0),
                    'section_type': clause.get('section_type', ''),
                    'clause_index': idx
                })
            
            # Add documents to collection (ChromaDB will generate embeddings)
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            # Store metadata in SQLite
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO vector_metadata (document_id, collection_name, vector_count, model_name)
                VALUES (?, ?, ?, ?)
            ''', (document_id, collection_name, len(structured_clauses), model_name))
            
            self.conn.commit()
            return collection_name
            
        except Exception as e:
            # Fallback to simple metadata storage
            collection_name = f"doc_{document_id}_fallback"
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO vector_metadata (document_id, collection_name, vector_count, model_name)
                VALUES (?, ?, ?, ?)
            ''', (document_id, collection_name, len(structured_clauses), "fallback"))
            self.conn.commit()
            return collection_name
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict]:
        """Retrieve document information by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_clauses_by_document_id(self, document_id: int) -> List[Dict]:
        """Retrieve all clauses for a document"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM clauses 
            WHERE document_id = ? 
            ORDER BY clause_index
        ''', (document_id,))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_vector_collection(self, document_id: int) -> Optional[Any]:
        """Get ChromaDB collection for a document"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT collection_name FROM vector_metadata WHERE document_id = ?",
            (document_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None
        
        collection_name = result[0]
        try:
            return self.chroma_client.get_collection(collection_name)
        except Exception:
            return None
    
    def search_similar_clauses(self, document_id: int, query: str, k: int = 5) -> List[Dict]:
        """Search for similar clauses using vector similarity"""
        collection = self.get_vector_collection(document_id)
        if not collection:
            raise Exception("Vector collection not found for this document")
        
        try:
            # Query the collection
            results = collection.query(
                query_texts=[query],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            similar_clauses = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    clause = {
                        'text': results['documents'][0][i],
                        'title': results['metadatas'][0][i]['title'],
                        'page_number': results['metadatas'][0][i]['page_number'],
                        'section_type': results['metadatas'][0][i]['section_type'],
                        'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    similar_clauses.append(clause)
            
            return similar_clauses
            
        except Exception as e:
            raise Exception(f"Failed to search similar clauses: {str(e)}")
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents from database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT d.*, v.collection_name, v.vector_count 
            FROM documents d 
            LEFT JOIN vector_metadata v ON d.id = v.document_id 
            ORDER BY d.upload_date DESC
        ''')
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document and all related data"""
        try:
            cursor = self.conn.cursor()
            
            # Get collection name
            cursor.execute(
                "SELECT collection_name FROM vector_metadata WHERE document_id = ?",
                (document_id,)
            )
            result = cursor.fetchone()
            
            # Delete from ChromaDB
            if result:
                collection_name = result[0]
                try:
                    self.chroma_client.delete_collection(collection_name)
                except Exception:
                    pass  # Collection might not exist
            
            # Delete from SQLite
            cursor.execute("DELETE FROM clauses WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM vector_metadata WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Failed to delete document: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        # Get document count
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        # Get clause count
        cursor.execute("SELECT COUNT(*) FROM clauses")
        clause_count = cursor.fetchone()[0]
        
        # Get total file size
        cursor.execute("SELECT SUM(file_size) FROM documents")
        total_size = cursor.fetchone()[0] or 0
        
        return {
            'document_count': doc_count,
            'clause_count': clause_count,
            'total_file_size': total_size,
            'database_path': self.db_path,
            'chroma_path': self.chroma_path
        }
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'conn'):
            self.conn.close()
