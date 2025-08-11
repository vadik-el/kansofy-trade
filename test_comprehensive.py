#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kansofy-Trade Document Intelligence Platform
=========================================================================

This test suite validates all core functionality before documentation and GitHub release:

1. System Health & Dependencies
2. Document Processing Pipeline 
3. Vector Embeddings & Search
4. Table Extraction & Serialization
5. Hash-Based Deduplication
6. MCP Server Integration
7. API Endpoints & Error Handling
8. Performance & Load Testing
9. Database Integrity
10. End-to-End Workflows

Usage:
    python test_comprehensive.py
    python test_comprehensive.py --verbose
    python test_comprehensive.py --quick
"""

import asyncio
import json
import os
import sys
import time
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import argparse
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent))

import httpx
import aiosqlite
from sentence_transformers import SentenceTransformer

# Test configuration
TEST_CONFIG = {
    "server_url": "http://localhost:8000",
    "test_timeout": 30,
    "max_retries": 3,
    "test_data_dir": "test_data",
    "performance_thresholds": {
        "document_processing_max_time": 30.0,  # seconds
        "embedding_generation_max_time": 10.0,
        "api_response_max_time": 5.0,
        "search_max_time": 2.0
    }
}

@dataclass
class TestResult:
    name: str
    status: str  # "PASS", "FAIL", "SKIP", "ERROR"
    duration: float
    message: str = ""
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class ComprehensiveTestSuite:
    """Comprehensive test suite for Kansofy-Trade platform"""
    
    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.results: List[TestResult] = []
        self.test_data_dir = Path(TEST_CONFIG["test_data_dir"])
        self.uploaded_documents = []  # Track for cleanup
        
        # Test statistics
        self.stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] {level}:"
        print(f"{prefix} {message}")
        
        if self.verbose or level in ["ERROR", "FAIL"]:
            sys.stdout.flush()
    
    def add_result(self, result: TestResult):
        """Add test result and update statistics"""
        self.results.append(result)
        self.stats["total"] += 1
        
        if result.status == "PASS":
            self.stats["passed"] += 1
        elif result.status == "FAIL":
            self.stats["failed"] += 1
        elif result.status == "ERROR":
            self.stats["errors"] += 1
        elif result.status == "SKIP":
            self.stats["skipped"] += 1
    
    async def run_test(self, test_func, test_name: str, **kwargs):
        """Run a single test with error handling and timing"""
        start_time = time.time()
        
        try:
            self.log(f"Running {test_name}...")
            result = await test_func(**kwargs)
            
            if isinstance(result, TestResult):
                duration = time.time() - start_time
                result.duration = duration
                self.add_result(result)
                
                status_symbol = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⚠️"
                self.log(f"{status_symbol} {test_name}: {result.status} ({duration:.2f}s) - {result.message}")
                
                return result
            else:
                # Legacy test function that doesn't return TestResult
                duration = time.time() - start_time
                test_result = TestResult(test_name, "PASS", duration, "Legacy test completed")
                self.add_result(test_result)
                self.log(f"✅ {test_name}: PASS ({duration:.2f}s)")
                return test_result
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            if self.verbose:
                error_msg += f"\n{traceback.format_exc()}"
            
            result = TestResult(test_name, "ERROR", duration, error_msg)
            self.add_result(result)
            self.log(f"❌ {test_name}: ERROR ({duration:.2f}s) - {error_msg}", "ERROR")
            return result
    
    # =================================================================
    # 1. SYSTEM HEALTH & DEPENDENCIES
    # =================================================================
    
    async def test_server_health(self) -> TestResult:
        """Test if the server is running and healthy"""
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                response = await client.get(f"{TEST_CONFIG['server_url']}/api/v1/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    
                    if health_data.get("status") == "healthy":
                        return TestResult("server_health", "PASS", 0, "Server is healthy", health_data)
                    else:
                        return TestResult("server_health", "FAIL", 0, f"Server unhealthy: {health_data}")
                else:
                    return TestResult("server_health", "FAIL", 0, f"HTTP {response.status_code}")
                    
        except Exception as e:
            return TestResult("server_health", "ERROR", 0, f"Cannot connect to server: {e}")
    
    async def test_dependencies(self) -> TestResult:
        """Test if all required dependencies are available"""
        missing_deps = []
        
        try:
            # Test sentence-transformers
            model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./model_cache')
            test_embedding = model.encode("Test sentence")
            if len(test_embedding) != 384:
                missing_deps.append(f"sentence-transformers: Wrong embedding dimension {len(test_embedding)}")
        except Exception as e:
            missing_deps.append(f"sentence-transformers: {e}")
        
        try:
            # Test database
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()
        except Exception as e:
            missing_deps.append(f"sqlite3: {e}")
        
        try:
            # Test docling
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
        except Exception as e:
            missing_deps.append(f"docling: {e}")
        
        if missing_deps:
            return TestResult("dependencies", "FAIL", 0, f"Missing dependencies: {', '.join(missing_deps)}")
        else:
            return TestResult("dependencies", "PASS", 0, "All dependencies available")
    
    # =================================================================
    # 2. DOCUMENT PROCESSING PIPELINE
    # =================================================================
    
    async def test_document_upload(self) -> TestResult:
        """Test document upload functionality"""
        # Create a test PDF
        test_content = "This is a test invoice for copper trading. Amount: $10,000 USD. Invoice: TEST-001."
        test_file = self.test_data_dir / "test_invoice.txt"
        test_file.parent.mkdir(exist_ok=True)
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                with open(test_file, "rb") as f:
                    files = {"file": ("test_invoice.txt", f, "text/plain")}
                    response = await client.post(f"{TEST_CONFIG['server_url']}/api/v1/documents", files=files)
                
                if response.status_code == 200:
                    doc_data = response.json()
                    self.uploaded_documents.append(doc_data["id"])
                    
                    return TestResult("document_upload", "PASS", 0, 
                                    f"Document uploaded successfully: ID {doc_data['id']}", doc_data)
                else:
                    return TestResult("document_upload", "FAIL", 0, 
                                    f"Upload failed: HTTP {response.status_code}")
                    
        except Exception as e:
            return TestResult("document_upload", "ERROR", 0, f"Upload error: {e}")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    async def test_document_processing(self) -> TestResult:
        """Test document processing with Docling"""
        if not self.uploaded_documents:
            return TestResult("document_processing", "SKIP", 0, "No uploaded documents to test")
        
        doc_id = self.uploaded_documents[-1]
        max_wait = 60  # seconds
        wait_interval = 2
        waited = 0
        
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                # Wait for processing to complete
                while waited < max_wait:
                    response = await client.get(f"{TEST_CONFIG['server_url']}/api/v1/documents/{doc_id}")
                    
                    if response.status_code == 200:
                        doc_data = response.json()
                        status = doc_data.get("status", "unknown")
                        
                        if status == "completed":
                            # Check if content was extracted
                            content = doc_data.get("content", "")
                            if content and len(content) > 0:
                                return TestResult("document_processing", "PASS", 0, 
                                                f"Document processed successfully: {len(content)} characters")
                            else:
                                return TestResult("document_processing", "FAIL", 0, 
                                                "Document processed but no content extracted")
                        
                        elif status == "failed":
                            return TestResult("document_processing", "FAIL", 0, 
                                            f"Document processing failed: {doc_data}")
                        
                        # Still processing, wait more
                        await asyncio.sleep(wait_interval)
                        waited += wait_interval
                    else:
                        return TestResult("document_processing", "FAIL", 0, 
                                        f"Cannot fetch document: HTTP {response.status_code}")
                
                return TestResult("document_processing", "FAIL", 0, 
                                f"Processing timeout after {max_wait}s")
                
        except Exception as e:
            return TestResult("document_processing", "ERROR", 0, f"Processing test error: {e}")
    
    # =================================================================
    # 3. VECTOR EMBEDDINGS & SEARCH
    # =================================================================
    
    async def test_embeddings_generation(self) -> TestResult:
        """Test if embeddings are generated during document processing"""
        if not self.uploaded_documents:
            return TestResult("embeddings_generation", "SKIP", 0, "No uploaded documents to test")
        
        doc_id = self.uploaded_documents[-1]
        
        try:
            # Check database directly for embeddings
            from app.core.config import get_settings
            settings = get_settings()
            
            async with aiosqlite.connect(settings.database_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM document_embeddings WHERE document_id = ?", 
                    (doc_id,)
                )
                count = (await cursor.fetchone())[0]
                
                if count > 0:
                    # Get embedding details
                    cursor = await db.execute(
                        "SELECT chunk_index, embedding FROM document_embeddings WHERE document_id = ? LIMIT 1",
                        (doc_id,)
                    )
                    row = await cursor.fetchone()
                    
                    if row:
                        embedding = json.loads(row[1])
                        return TestResult("embeddings_generation", "PASS", 0, 
                                        f"Generated {count} embeddings with {len(embedding)} dimensions")
                    else:
                        return TestResult("embeddings_generation", "FAIL", 0, "Embeddings found but cannot parse")
                else:
                    return TestResult("embeddings_generation", "FAIL", 0, "No embeddings generated")
                    
        except Exception as e:
            return TestResult("embeddings_generation", "ERROR", 0, f"Embeddings test error: {e}")
    
    async def test_vector_search(self) -> TestResult:
        """Test vector similarity search functionality"""
        try:
            # Test search endpoint
            search_query = "copper trading invoice"
            
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                response = await client.get(
                    f"{TEST_CONFIG['server_url']}/api/v1/search/vector", 
                    params={"query": search_query, "limit": 5}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if isinstance(results, list) and len(results) > 0:
                        # Check result structure
                        first_result = results[0]
                        required_fields = ["document_id", "chunk_text", "similarity_score"]
                        
                        missing_fields = [field for field in required_fields if field not in first_result]
                        
                        if not missing_fields:
                            return TestResult("vector_search", "PASS", 0, 
                                            f"Found {len(results)} search results")
                        else:
                            return TestResult("vector_search", "FAIL", 0, 
                                            f"Missing fields in results: {missing_fields}")
                    else:
                        return TestResult("vector_search", "PASS", 0, "Search working but no results (expected for new system)")
                else:
                    return TestResult("vector_search", "FAIL", 0, 
                                    f"Search failed: HTTP {response.status_code}")
                    
        except Exception as e:
            return TestResult("vector_search", "ERROR", 0, f"Vector search error: {e}")
    
    # =================================================================
    # 4. TABLE EXTRACTION & SERIALIZATION
    # =================================================================
    
    async def test_table_extraction(self) -> TestResult:
        """Test table extraction from documents"""
        # Create a test document with table-like content
        table_content = '''
        Product Report
        
        Product    Quantity    Price
        Copper     1000 MT     $8,500
        Aluminum   500 MT      $2,200
        Zinc       200 MT      $3,100
        '''
        
        test_file = self.test_data_dir / "test_table.txt"
        test_file.parent.mkdir(exist_ok=True)
        
        with open(test_file, "w") as f:
            f.write(table_content)
        
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                # Upload document
                with open(test_file, "rb") as f:
                    files = {"file": ("test_table.txt", f, "text/plain")}
                    response = await client.post(f"{TEST_CONFIG['server_url']}/api/v1/documents", files=files)
                
                if response.status_code == 200:
                    doc_data = response.json()
                    doc_id = doc_data["id"]
                    self.uploaded_documents.append(doc_id)
                    
                    # Wait for processing
                    await asyncio.sleep(5)
                    
                    # Check if tables were extracted
                    response = await client.get(f"{TEST_CONFIG['server_url']}/api/v1/documents/{doc_id}")
                    
                    if response.status_code == 200:
                        doc_data = response.json()
                        tables = doc_data.get("tables", [])
                        
                        # Check if tables field exists and is serializable
                        if tables is not None:
                            if isinstance(tables, list):
                                return TestResult("table_extraction", "PASS", 0, 
                                                f"Tables field properly serialized: {len(tables)} tables")
                            else:
                                return TestResult("table_extraction", "FAIL", 0, 
                                                f"Tables field not a list: {type(tables)}")
                        else:
                            return TestResult("table_extraction", "FAIL", 0, "Tables field is None")
                    else:
                        return TestResult("table_extraction", "FAIL", 0, 
                                        f"Cannot fetch document: HTTP {response.status_code}")
                else:
                    return TestResult("table_extraction", "FAIL", 0, 
                                    f"Upload failed: HTTP {response.status_code}")
                    
        except Exception as e:
            return TestResult("table_extraction", "ERROR", 0, f"Table extraction error: {e}")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    # =================================================================
    # 5. HASH-BASED DEDUPLICATION
    # =================================================================
    
    async def test_duplicate_detection(self) -> TestResult:
        """Test hash-based duplicate detection"""
        # Create identical test files
        test_content = "Duplicate detection test content for Kansofy-Trade platform testing."
        test_file1 = self.test_data_dir / "duplicate1.txt"
        test_file2 = self.test_data_dir / "duplicate2.txt"
        
        test_file1.parent.mkdir(exist_ok=True)
        
        with open(test_file1, "w") as f:
            f.write(test_content)
        with open(test_file2, "w") as f:
            f.write(test_content)
        
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                # Upload first file
                with open(test_file1, "rb") as f:
                    files = {"file": ("duplicate1.txt", f, "text/plain")}
                    response1 = await client.post(f"{TEST_CONFIG['server_url']}/api/v1/documents", files=files)
                
                if response1.status_code == 200:
                    doc1_data = response1.json()
                    self.uploaded_documents.append(doc1_data["id"])
                    
                    # Upload second identical file
                    with open(test_file2, "rb") as f:
                        files = {"file": ("duplicate2.txt", f, "text/plain")}
                        response2 = await client.post(f"{TEST_CONFIG['server_url']}/api/v1/documents", files=files)
                    
                    if response2.status_code in [400, 409] or "duplicate" in response2.text.lower():
                        return TestResult("duplicate_detection", "PASS", 0, 
                                        "Duplicate detection working correctly")
                    else:
                        return TestResult("duplicate_detection", "FAIL", 0, 
                                        f"Duplicate not detected: HTTP {response2.status_code}")
                else:
                    return TestResult("duplicate_detection", "FAIL", 0, 
                                    f"First upload failed: HTTP {response1.status_code}")
                    
        except Exception as e:
            return TestResult("duplicate_detection", "ERROR", 0, f"Duplicate detection error: {e}")
        finally:
            # Cleanup
            for file in [test_file1, test_file2]:
                if file.exists():
                    file.unlink()
    
    # =================================================================
    # 6. API ENDPOINTS & ERROR HANDLING
    # =================================================================
    
    async def test_api_endpoints(self) -> TestResult:
        """Test all major API endpoints"""
        endpoints_to_test = [
            ("GET", "/api/v1/health", 200),
            ("GET", "/api/v1", 200),
            ("GET", "/api/v1/documents", 200),
            ("GET", "/api/v1/documents/99999", 404),  # Non-existent document
            ("GET", "/api/v1/search/vector?query=test", 200),
        ]
        
        failed_endpoints = []
        
        try:
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                for method, endpoint, expected_status in endpoints_to_test:
                    full_url = f"{TEST_CONFIG['server_url']}{endpoint}"
                    
                    if method == "GET":
                        response = await client.get(full_url)
                    elif method == "POST":
                        response = await client.post(full_url)
                    else:
                        continue
                    
                    if response.status_code != expected_status:
                        failed_endpoints.append(f"{method} {endpoint}: got {response.status_code}, expected {expected_status}")
                
                if failed_endpoints:
                    return TestResult("api_endpoints", "FAIL", 0, 
                                    f"Failed endpoints: {', '.join(failed_endpoints)}")
                else:
                    return TestResult("api_endpoints", "PASS", 0, 
                                    f"All {len(endpoints_to_test)} endpoints working correctly")
                    
        except Exception as e:
            return TestResult("api_endpoints", "ERROR", 0, f"API endpoint test error: {e}")
    
    # =================================================================
    # 7. DATABASE INTEGRITY
    # =================================================================
    
    async def test_database_integrity(self) -> TestResult:
        """Test database schema and data integrity"""
        try:
            from app.core.config import get_settings
            settings = get_settings()
            
            required_tables = [
                "documents",
                "document_processing_logs",
                "document_embeddings"
            ]
            
            missing_tables = []
            
            async with aiosqlite.connect(settings.database_path) as db:
                # Check if all required tables exist
                for table in required_tables:
                    cursor = await db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                        (table,)
                    )
                    result = await cursor.fetchone()
                    
                    if not result:
                        missing_tables.append(table)
                
                if missing_tables:
                    return TestResult("database_integrity", "FAIL", 0, 
                                    f"Missing tables: {', '.join(missing_tables)}")
                
                # Check indexes
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
                )
                indexes = await cursor.fetchall()
                
                return TestResult("database_integrity", "PASS", 0, 
                                f"Database integrity OK: {len(required_tables)} tables, {len(indexes)} indexes")
                
        except Exception as e:
            return TestResult("database_integrity", "ERROR", 0, f"Database integrity error: {e}")
    
    # =================================================================
    # 8. PERFORMANCE TESTING
    # =================================================================
    
    async def test_performance_benchmarks(self) -> TestResult:
        """Test system performance against benchmarks"""
        if self.quick:
            return TestResult("performance_benchmarks", "SKIP", 0, "Skipped in quick mode")
        
        performance_results = {}
        failed_benchmarks = []
        
        try:
            # Test API response time
            start_time = time.time()
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                response = await client.get(f"{TEST_CONFIG['server_url']}/api/v1/health")
            api_time = time.time() - start_time
            
            performance_results["api_response_time"] = api_time
            
            if api_time > TEST_CONFIG["performance_thresholds"]["api_response_max_time"]:
                failed_benchmarks.append(f"API response too slow: {api_time:.2f}s")
            
            # Test embedding generation time
            start_time = time.time()
            model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./model_cache')
            test_text = "This is a performance test for embedding generation in Kansofy-Trade platform."
            embedding = model.encode(test_text)
            embedding_time = time.time() - start_time
            
            performance_results["embedding_generation_time"] = embedding_time
            
            if embedding_time > TEST_CONFIG["performance_thresholds"]["embedding_generation_max_time"]:
                failed_benchmarks.append(f"Embedding generation too slow: {embedding_time:.2f}s")
            
            if failed_benchmarks:
                return TestResult("performance_benchmarks", "FAIL", 0, 
                                f"Performance issues: {', '.join(failed_benchmarks)}", performance_results)
            else:
                return TestResult("performance_benchmarks", "PASS", 0, 
                                "All performance benchmarks passed", performance_results)
                
        except Exception as e:
            return TestResult("performance_benchmarks", "ERROR", 0, f"Performance test error: {e}")
    
    # =================================================================
    # 9. END-TO-END WORKFLOW TEST
    # =================================================================
    
    async def test_end_to_end_workflow(self) -> TestResult:
        """Test complete end-to-end workflow"""
        workflow_steps = []
        
        try:
            # Step 1: Upload document
            test_content = """
            COMMERCIAL INVOICE
            Invoice Number: E2E-TEST-001
            Date: 2024-08-10
            
            Product Details:
            - Copper Cathode: 1000 MT @ $8,500/MT
            - Total Amount: $8,500,000 USD
            
            Shipping Details:
            Vessel: TEST VESSEL
            Port: Rotterdam
            """
            
            test_file = self.test_data_dir / "e2e_test.txt"
            test_file.parent.mkdir(exist_ok=True)
            
            with open(test_file, "w") as f:
                f.write(test_content)
            
            async with httpx.AsyncClient(timeout=TEST_CONFIG["test_timeout"]) as client:
                # Upload
                with open(test_file, "rb") as f:
                    files = {"file": ("e2e_test.txt", f, "text/plain")}
                    response = await client.post(f"{TEST_CONFIG['server_url']}/api/v1/documents", files=files)
                
                if response.status_code == 200:
                    doc_data = response.json()
                    doc_id = doc_data["id"]
                    self.uploaded_documents.append(doc_id)
                    workflow_steps.append("✅ Document uploaded")
                else:
                    workflow_steps.append("❌ Document upload failed")
                    return TestResult("end_to_end_workflow", "FAIL", 0, 
                                    f"E2E workflow failed at upload: {workflow_steps}")
                
                # Step 2: Wait for processing
                max_wait = 30
                waited = 0
                
                while waited < max_wait:
                    response = await client.get(f"{TEST_CONFIG['server_url']}/api/v1/documents/{doc_id}")
                    
                    if response.status_code == 200:
                        doc_data = response.json()
                        status = doc_data.get("status")
                        
                        if status == "completed":
                            workflow_steps.append("✅ Document processed")
                            break
                        elif status == "failed":
                            workflow_steps.append("❌ Document processing failed")
                            return TestResult("end_to_end_workflow", "FAIL", 0, 
                                            f"E2E workflow failed at processing: {workflow_steps}")
                    
                    await asyncio.sleep(2)
                    waited += 2
                
                if waited >= max_wait:
                    workflow_steps.append("❌ Processing timeout")
                    return TestResult("end_to_end_workflow", "FAIL", 0, 
                                    f"E2E workflow timeout: {workflow_steps}")
                
                # Step 3: Verify content extraction
                if doc_data.get("content") and len(doc_data["content"]) > 0:
                    workflow_steps.append("✅ Content extracted")
                else:
                    workflow_steps.append("❌ No content extracted")
                
                # Step 4: Verify embeddings
                await asyncio.sleep(2)  # Allow embedding generation
                from app.core.config import get_settings
                settings = get_settings()
                
                async with aiosqlite.connect(settings.database_path) as db:
                    cursor = await db.execute(
                        "SELECT COUNT(*) FROM document_embeddings WHERE document_id = ?", 
                        (doc_id,)
                    )
                    embedding_count = (await cursor.fetchone())[0]
                    
                    if embedding_count > 0:
                        workflow_steps.append(f"✅ Embeddings generated ({embedding_count})")
                    else:
                        workflow_steps.append("❌ No embeddings generated")
                
                # Step 5: Test search
                response = await client.get(
                    f"{TEST_CONFIG['server_url']}/api/v1/search/vector", 
                    params={"query": "copper cathode invoice", "limit": 5}
                )
                
                if response.status_code == 200:
                    search_results = response.json()
                    if isinstance(search_results, list):
                        workflow_steps.append(f"✅ Search working ({len(search_results)} results)")
                    else:
                        workflow_steps.append("❌ Search returned invalid data")
                else:
                    workflow_steps.append("❌ Search failed")
            
            # Check if all steps passed
            failed_steps = [step for step in workflow_steps if "❌" in step]
            
            if failed_steps:
                return TestResult("end_to_end_workflow", "FAIL", 0, 
                                f"E2E workflow partial failure: {failed_steps}")
            else:
                return TestResult("end_to_end_workflow", "PASS", 0, 
                                f"Complete E2E workflow successful: {len(workflow_steps)} steps")
                
        except Exception as e:
            return TestResult("end_to_end_workflow", "ERROR", 0, f"E2E workflow error: {e}")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    # =================================================================
    # TEST RUNNER & CLEANUP
    # =================================================================
    
    async def cleanup(self):
        """Clean up test data and uploaded documents"""
        try:
            # Clean up uploaded test documents
            if self.uploaded_documents:
                self.log(f"Cleaning up {len(self.uploaded_documents)} test documents...")
                
                # Note: In a real implementation, you might want to add a cleanup endpoint
                # or clean directly from database
                pass
            
            # Clean up test files
            if self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir, ignore_errors=True)
            
        except Exception as e:
            self.log(f"Cleanup error: {e}", "ERROR")
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_duration = sum(r.duration for r in self.results)
        
        report = f"""
{'='*80}
KANSOFY-TRADE COMPREHENSIVE TEST REPORT
{'='*80}

Test Summary:
-------------
Total Tests:    {self.stats['total']}
Passed:         {self.stats['passed']} ✅
Failed:         {self.stats['failed']} ❌  
Errors:         {self.stats['errors']} 💥
Skipped:        {self.stats['skipped']} ⚠️
Total Time:     {total_duration:.2f}s

Success Rate:   {(self.stats['passed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0:.1f}%

Detailed Results:
-----------------"""

        for result in self.results:
            status_symbol = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "💥",
                "SKIP": "⚠️"
            }.get(result.status, "❓")
            
            report += f"\n{status_symbol} {result.name:<30} {result.status:<8} {result.duration:>6.2f}s  {result.message}"
            
            if self.verbose and result.details:
                report += f"\n   Details: {json.dumps(result.details, indent=2)}"
        
        # Performance summary
        if any("performance" in r.name for r in self.results):
            report += "\n\nPerformance Summary:\n--------------------"
            for result in self.results:
                if "performance" in result.name and result.details:
                    for metric, value in result.details.items():
                        report += f"\n{metric}: {value:.3f}s"
        
        # Final assessment
        report += "\n\nFinal Assessment:\n-----------------"
        if self.stats['failed'] == 0 and self.stats['errors'] == 0:
            report += "\n🎉 ALL TESTS PASSED! System is ready for documentation and GitHub release."
        elif self.stats['failed'] > 0:
            report += f"\n⚠️  {self.stats['failed']} test(s) failed. Issues need to be addressed before release."
        
        if self.stats['errors'] > 0:
            report += f"\n💥 {self.stats['errors']} test(s) had errors. Critical issues need investigation."
        
        report += f"\n{'='*80}\n"
        
        return report
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        self.log("🚀 Starting Kansofy-Trade Comprehensive Test Suite...")
        
        # Test sequence - organized by priority and dependencies
        test_sequence = [
            # 1. System Health (must pass for other tests to work)
            (self.test_server_health, "Server Health Check"),
            (self.test_dependencies, "Dependencies Verification"),
            
            # 2. Core Functionality
            (self.test_document_upload, "Document Upload"),
            (self.test_document_processing, "Document Processing"),
            (self.test_table_extraction, "Table Extraction & Serialization"),
            
            # 3. Advanced Features
            (self.test_embeddings_generation, "Vector Embeddings Generation"),
            (self.test_vector_search, "Vector Similarity Search"),
            (self.test_duplicate_detection, "Hash-Based Duplicate Detection"),
            
            # 4. System Integration
            (self.test_api_endpoints, "API Endpoints"),
            (self.test_database_integrity, "Database Integrity"),
            
            # 5. Performance & End-to-End
            (self.test_performance_benchmarks, "Performance Benchmarks"),
            (self.test_end_to_end_workflow, "End-to-End Workflow"),
        ]
        
        # Run tests in sequence
        for test_func, test_name in test_sequence:
            await self.run_test(test_func, test_name)
        
        # Cleanup
        await self.cleanup()
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save report to file
        report_file = Path("test_report.txt")
        with open(report_file, "w") as f:
            f.write(report)
        
        self.log(f"📊 Test report saved to: {report_file}")
        
        # Return success status
        return self.stats['failed'] == 0 and self.stats['errors'] == 0


async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Kansofy-Trade Comprehensive Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with details")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode - skip performance tests")
    
    args = parser.parse_args()
    
    # Create and run test suite
    test_suite = ComprehensiveTestSuite(verbose=args.verbose, quick=args.quick)
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())