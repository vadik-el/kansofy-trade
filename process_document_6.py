#!/usr/bin/env python3
"""Process document 6 directly"""

import asyncio
from app.services.document_processor import DocumentProcessor

async def process_doc_6():
    """Process document 6"""
    
    print("=" * 60)
    print("Processing Document 6 (VEL_CV.pdf)")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    try:
        print("\n⏳ Processing document...")
        success = await processor.process_document_async(6)
        
        if success:
            print("✅ Document processed successfully!")
        else:
            print("❌ Processing failed")
            
        # Check final status
        import sqlite3
        conn = sqlite3.connect('kansofy_trade.db')
        cursor = conn.cursor()
        cursor.execute('SELECT status, content, summary FROM documents WHERE id = 6')
        result = cursor.fetchone()
        
        if result:
            print(f"\n📊 Final Status: {result[0]}")
            if result[1]:
                print(f"   Content extracted: {len(result[1])} characters")
            if result[2]:
                print(f"   Summary: {result[2][:100]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(process_doc_6())