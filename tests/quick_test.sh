#!/bin/bash
# Script de test rapide pour Odoo MCP Proxy Multi-Tenant

echo "🚀 TEST RAPIDE - Odoo MCP Proxy Multi-Tenant"
echo "=============================================="

# Démarrer le serveur en arrière-plan
echo "🔧 Démarrage du serveur..."
cd "/Users/quentinpro/Desktop/Odoo MCP Proxy Multi-Tenant"
source venv/bin/activate
python tests/test_server_fixed.py &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 5

# Test 1: Santé de l'API
echo ""
echo "🔍 Test 1: Santé de l'API"
curl -s http://localhost:8000/ | jq .

# Test 2: Configuration Odoo
echo ""
echo "🔍 Test 2: Configuration Odoo"
CONFIG_RESPONSE=$(curl -s -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "odoo_url": "https://bycommute.odoo.com",
    "odoo_db": "bycommute",
    "odoo_username": "quentin.candaele@bycommute.fr",
    "odoo_password": "%JLr69mbaK3^",
    "user_name": "Quentin Candaele",
    "user_email": "quentin.candaele@bycommute.fr"
  }')

echo "$CONFIG_RESPONSE" | jq .

# Extraire le token
TOKEN=$(echo "$CONFIG_RESPONSE" | jq -r '.api_token')

# Test 3: MCP List Tools
echo ""
echo "🔍 Test 3: MCP List Tools"
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }' | jq .

# Test 4: MCP Call Tool
echo ""
echo "🔍 Test 4: MCP Call Tool"
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
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
  }' | jq .

# Arrêter le serveur
echo ""
echo "🛑 Arrêt du serveur..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ Tests terminés !"
