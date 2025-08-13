#!/usr/bin/env python3
"""
Download required AI models for TradeMCP.

This script downloads the sentence-transformers model that is used
for text embeddings and semantic analysis in the trading system.
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download required models if not already present."""
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    cache_dir = Path("model_cache")
    
    # Check if model already exists
    model_path = cache_dir / "models--sentence-transformers--all-MiniLM-L6-v2"
    if model_path.exists() and any(model_path.glob("**/*.safetensors")):
        print(f"✅ Model '{model_name}' already downloaded.")
        return True
    
    print(f"📥 Downloading model: {model_name}")
    print("This is a one-time download of ~87MB...")
    
    try:
        # Import sentence_transformers
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print("❌ Error: sentence-transformers not installed.")
            print("Please install it with: pip install sentence-transformers")
            return False
        
        # Create cache directory if it doesn't exist
        cache_dir.mkdir(exist_ok=True)
        
        # Download the model
        print("Downloading...")
        model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
        
        # Test the model
        test_sentence = "Testing model download"
        embedding = model.encode(test_sentence)
        
        print(f"✅ Model downloaded successfully!")
        print(f"📍 Location: {model_path}")
        print(f"✅ Test encoding successful (dimension: {len(embedding)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Ensure you have enough disk space (~100MB)")
        print("3. Try running: pip install --upgrade sentence-transformers")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    required = ['sentence_transformers', 'torch', 'transformers']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("⚠️  Missing dependencies detected!")
        print(f"Please install: {', '.join(missing)}")
        print(f"\nRun: pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Main function."""
    print("=" * 50)
    print("TradeMCP Model Downloader")
    print("=" * 50)
    print()
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        sys.exit(1)
    
    # Download models
    if download_models():
        print("\n✅ All models ready!")
        print("You can now run your TradeMCP application.")
    else:
        print("\n❌ Model download failed.")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()