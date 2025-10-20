#!/usr/bin/env python3
"""
Test script for deployed Odoo MCP Proxy
"""
import requests
import json
import time
import sys

def test_deployment(base_url="http://localhost:8000"):
    """Test the deployed application"""
    
    print(f"🧪 Testing Odoo MCP Proxy at {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Configuration
    print("\n🔍 Test 2: Configuration")
    config_data = {
        "odoo_url": "https://bycommute.odoo.com",
        "odoo_db": "bycommute",
        "odoo_username": "quentin.candaele@bycommute.fr",
        "odoo_password": "%JLr69mbaK3^",
        "user_name": "Quentin Candaele",
        "user_email": "quentin.candaele@bycommute.fr"
    }
    
    try:
        response = requests.post(
            f"{base_url}/config",
            json=config_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            api_token = data['api_token']
            print(f"✅ Configuration successful")
            print(f"   Token: {api_token[:8]}...")
        else:
            print(f"❌ Configuration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test 3: MCP List Tools
    print("\n🔍 Test 3: MCP List Tools")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            print(f"✅ MCP List Tools successful: {len(tools)} tools available")
        else:
            print(f"❌ MCP List Tools failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP List Tools error: {e}")
        return False
    
    # Test 4: MCP Call Tool
    print("\n🔍 Test 4: MCP Call Tool")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_partners",
                "arguments": {
                    "domain": [],
                    "fields": ["id", "name", "email"],
                    "limit": 3
                }
            },
            "id": 2
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCP Call Tool successful")
            content = data.get("result", {}).get("content", [])
            if content:
                text = content[0].get("text", "")
                print(f"   Result: {text[:100]}...")
        else:
            print(f"❌ MCP Call Tool failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ MCP Call Tool error: {e}")
        return False
    
    print("\n🎉 All tests passed! The deployment is working correctly.")
    return True

if __name__ == "__main__":
    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    success = test_deployment(base_url)
    sys.exit(0 if success else 1)
