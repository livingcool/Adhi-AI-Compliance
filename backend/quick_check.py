import sqlite3

# Check database
conn = sqlite3.connect('data/metadata.db')
cursor = conn.cursor()

# Check documents
cursor.execute("SELECT COUNT(*) FROM documents")
doc_count = cursor.fetchone()[0]
print(f"Documents in DB: {doc_count}")

# Check text chunks
cursor.execute("SELECT COUNT(*) FROM text_chunks")
chunk_count = cursor.fetchone()[0]
print(f"Text chunks in DB: {chunk_count}")

# Show sample data
if chunk_count > 0:
    cursor.execute("SELECT d.source_file_name, d.doc_type, d.status, COUNT(tc.id) as chunks FROM documents d LEFT JOIN text_chunks tc ON d.id = tc.document_id GROUP BY d.id")
    for row in cursor.fetchall():
        print(f"\n{row[0]} ({row[1]}): {row[2]} - {row[3]} chunks")
    
    cursor.execute("SELECT text_content FROM text_chunks LIMIT 3")
    print("\nSample chunks:")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {row[0][:100]}...")

conn.close()

# Check FAISS
import os
faiss_path = 'data/vectors/main_index.faiss'
if os.path.exists(faiss_path):
    import faiss
    index = faiss.read_index(faiss_path)
    print(f"\nFAISS index: {index.ntotal} vectors")
else:
    print(f"\nFAISS index: NOT FOUND at {faiss_path}")
