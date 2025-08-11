#!/bin/bash
"""
Kansofy-Trade Test Runner
=========================

This script runs the comprehensive test suite for the Kansofy-Trade platform.
It ensures the server is running and executes all validation tests.

Usage:
    ./run_tests.sh              # Run full test suite
    ./run_tests.sh --quick      # Run quick tests (skip performance)
    ./run_tests.sh --verbose    # Run with detailed output
"""

set -e  # Exit on any error

echo "🚀 Kansofy-Trade Test Runner"
echo "============================"

# Check if server is running
echo "📡 Checking if server is running..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running. Please start with:"
    echo "   source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate" 
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check dependencies
echo "📦 Checking dependencies..."
if ! python -c "import sentence_transformers, docling, httpx" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Run the comprehensive test suite
echo "🧪 Running comprehensive test suite..."
echo "======================================"

# Pass command line arguments to the test script
python test_comprehensive.py "$@"

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed! System is ready for documentation and GitHub release."
else
    echo "❌ Some tests failed. Please check the report above and fix issues before proceeding."
fi

echo ""
echo "📊 Test report saved to: test_report.txt"
echo "🔍 For detailed logs, run with --verbose flag"

exit $TEST_EXIT_CODE