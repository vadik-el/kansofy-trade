#!/usr/bin/env python3
"""Manual document processing tool for uploaded documents"""

import asyncio
import sys
from app.services.document_processor import DocumentProcessor

async def process_document_manually(doc_id: int):
    """Process a specific document by ID"""
    
    print(f"Processing document {doc_id}...")
    
    processor = DocumentProcessor()
    
    try:
        success = await processor.process_document_async(doc_id)
        
        if success:
            print(f"✅ Document {doc_id} processed successfully!")
            
            # Show extracted content summary
            import sqlite3
            conn = sqlite3.connect('kansofy_trade.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT filename, status, content, file_size 
                FROM documents WHERE id = ?
            ''', (doc_id,))
            result = cursor.fetchone()
            
            if result:
                print(f"\n📄 File: {result[0]}")
                print(f"📊 Status: {result[1]}")
                print(f"📏 Size: {result[3] / 1024:.1f} KB")
                if result[2]:
                    print(f"📝 Content: {len(result[2])} characters extracted")
                    print(f"\nFirst 200 chars of content:")
                    print(result[2][:200] + "...")
            
            conn.close()
        else:
            print(f"❌ Processing failed for document {doc_id}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def process_all_pending():
    """Process all pending documents"""
    
    import sqlite3
    conn = sqlite3.connect('kansofy_trade.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, filename 
        FROM documents 
        WHERE status IN ('pending', 'uploaded')
    ''')
    pending = cursor.fetchall()
    conn.close()
    
    if not pending:
        print("✅ No pending documents to process")
        return
    
    print(f"Found {len(pending)} pending document(s):")
    for doc_id, filename in pending:
        print(f"  - ID {doc_id}: {filename}")
    
    print("\nProcessing all pending documents...")
    
    processor = DocumentProcessor()
    
    for doc_id, filename in pending:
        print(f"\n📄 Processing {filename} (ID: {doc_id})...")
        try:
            success = await processor.process_document_async(doc_id)
            if success:
                print(f"  ✅ Success!")
            else:
                print(f"  ❌ Failed")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n✅ Batch processing complete!")

async def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        # Process specific document
        try:
            doc_id = int(sys.argv[1])
            await process_document_manually(doc_id)
        except ValueError:
            print("❌ Error: Please provide a valid document ID number")
            print("Usage: python manual_process.py [document_id]")
            print("   Or: python manual_process.py  (to process all pending)")
    else:
        # Process all pending
        await process_all_pending()

if __name__ == "__main__":
    asyncio.run(main())