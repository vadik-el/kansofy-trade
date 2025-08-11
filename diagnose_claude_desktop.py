#!/usr/bin/env python3
"""
Claude Desktop Integration Diagnostics

This script helps diagnose common issues with MCP server integration.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def check_config_file():
    """Check if Claude Desktop configuration exists and is valid"""
    config_path = Path.home() / ".config/claude-desktop/claude_desktop_config.json"
    
    print("🔍 Checking Claude Desktop configuration...")
    print(f"   Config path: {config_path}")
    
    if not config_path.exists():
        print("   ❌ Configuration file does not exist!")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        print("   ✅ Configuration file exists and is valid JSON")
        
        if "mcpServers" in config:
            servers = config["mcpServers"]
            print(f"   📋 Found {len(servers)} MCP server(s):")
            
            for name, server_config in servers.items():
                print(f"      - {name}")
                print(f"        Command: {server_config.get('command')}")
                print(f"        Args: {server_config.get('args')}")
                print(f"        CWD: {server_config.get('cwd')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading configuration: {e}")
        return False

def check_python_path():
    """Check if the Python path in config is valid"""
    config_path = Path.home() / ".config/claude-desktop/claude_desktop_config.json"
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        kansofy_config = config.get("mcpServers", {}).get("kansofy-trade")
        if not kansofy_config:
            print("   ❌ kansofy-trade server not found in config")
            return False
        
        python_path = kansofy_config.get("command")
        if not python_path:
            print("   ❌ No python command specified")
            return False
        
        print(f"🐍 Checking Python executable...")
        print(f"   Path: {python_path}")
        
        if not Path(python_path).exists():
            print("   ❌ Python executable does not exist!")
            return False
        
        print("   ✅ Python executable exists")
        
        # Test if it's actually Python
        try:
            result = subprocess.run([python_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ Python version: {result.stdout.strip()}")
                return True
            else:
                print(f"   ❌ Python check failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Error checking Python: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking Python path: {e}")
        return False

def check_mcp_server():
    """Check if MCP server script exists and imports work"""
    config_path = Path.home() / ".config/claude-desktop/claude_desktop_config.json"
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        kansofy_config = config.get("mcpServers", {}).get("kansofy-trade")
        if not kansofy_config:
            return False
        
        mcp_script = kansofy_config.get("args", [None])[0]
        working_dir = kansofy_config.get("cwd")
        python_path = kansofy_config.get("command")
        
        print(f"🔧 Checking MCP server script...")
        print(f"   Script: {mcp_script}")
        print(f"   Working dir: {working_dir}")
        
        if not Path(mcp_script).exists():
            print("   ❌ MCP server script does not exist!")
            return False
        
        print("   ✅ MCP server script exists")
        
        # Test basic import
        print("   🧪 Testing MCP server imports...")
        try:
            import_test = f"""
import sys
sys.path.insert(0, '{working_dir}')
try:
    import mcp_server
    print("SUCCESS: MCP server imports work")
except ImportError as e:
    print(f"ERROR: Import failed - {{e}}")
except Exception as e:
    print(f"ERROR: Other error - {{e}}")
"""
            
            result = subprocess.run([python_path, "-c", import_test],
                                  capture_output=True, text=True, 
                                  cwd=working_dir, timeout=10)
            
            print(f"      Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"      Errors: {result.stderr.strip()}")
            
            return "SUCCESS" in result.stdout
            
        except Exception as e:
            print(f"   ❌ Error testing imports: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking MCP server: {e}")
        return False

def check_claude_desktop_running():
    """Check if Claude Desktop is running"""
    print("🖥️  Checking if Claude Desktop is running...")
    
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        claude_processes = [line for line in result.stdout.split('\n') 
                          if 'Claude.app' in line and 'MacOS/Claude' in line]
        
        if claude_processes:
            print("   ✅ Claude Desktop is running")
            print(f"   📊 Found {len(claude_processes)} Claude process(es)")
            return True
        else:
            print("   ❌ Claude Desktop is not running")
            print("   💡 Try starting Claude Desktop")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking processes: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🔍 Claude Desktop MCP Integration Diagnostics")
    print("=" * 50)
    
    checks = [
        ("Configuration File", check_config_file),
        ("Python Executable", check_python_path), 
        ("MCP Server Script", check_mcp_server),
        ("Claude Desktop Running", check_claude_desktop_running),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}")
        print("-" * 30)
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed!")
        print("💡 If you still don't see the MCP server in Claude Desktop:")
        print("   1. Make sure you've restarted Claude Desktop")
        print("   2. Look for any error messages in Claude Desktop")
        print("   3. Try the diagnostic commands in the README")
    else:
        print(f"\n⚠️  {total - passed} issues found - fix these first")
        print("\n🔧 Common solutions:")
        print("   - Restart Claude Desktop after config changes")
        print("   - Check file permissions on MCP server script")
        print("   - Verify virtual environment is activated")
        print("   - Ensure all dependencies are installed")

if __name__ == "__main__":
    main()