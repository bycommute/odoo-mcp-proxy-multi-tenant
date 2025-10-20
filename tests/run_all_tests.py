#!/usr/bin/env python3
"""
Script de test complet pour Odoo MCP Proxy Multi-Tenant
"""

import requests
import json
import time
import subprocess
import sys
import os
import signal
import psutil

# Configuration
BASE_URL = "http://localhost:8000"
ODOO_CONFIG = {
    "odoo_url": "https://bycommute.odoo.com",
    "odoo_db": "bycommute",
    "odoo_username": "quentin.candaele@bycommute.fr",
    "odoo_password": "%JLr69mbaK3^",
    "user_name": "Quentin Candaele",
    "user_email": "quentin.candaele@bycommute.fr"
}

class TestRunner:
    def __init__(self):
        self.server_process = None
        self.api_token = None
        self.test_results = []
    
    def start_server(self):
        """Démarrer le serveur de test"""
        print("🚀 Démarrage du serveur de test...")
        try:
            # Changer vers le répertoire du projet
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(project_dir)
            
            # Démarrer le serveur
            self.server_process = subprocess.Popen([
                sys.executable, "tests/test_server_fixed.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Attendre que le serveur démarre
            for i in range(10):
                try:
                    response = requests.get(f"{BASE_URL}/", timeout=1)
                    if response.status_code == 200:
                        print("✅ Serveur démarré avec succès")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Impossible de démarrer le serveur")
            return False
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage: {e}")
            return False
    
    def stop_server(self):
        """Arrêter le serveur"""
        if self.server_process:
            print("🛑 Arrêt du serveur...")
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
    
    def test_health(self):
        """Test 1: Santé de l'API"""
        print("\n🔍 Test 1: Santé de l'API")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API accessible - {data['message']}")
                self.test_results.append(("Santé API", True, data))
                return True
            else:
                print(f"❌ API inaccessible (status: {response.status_code})")
                self.test_results.append(("Santé API", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.test_results.append(("Santé API", False, str(e)))
            return False
    
    def test_configuration(self):
        """Test 2: Configuration Odoo"""
        print("\n🔍 Test 2: Configuration Odoo")
        try:
            response = requests.post(
                f"{BASE_URL}/config",
                json=ODOO_CONFIG,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.api_token = data['api_token']
                print(f"✅ Configuration réussie")
                print(f"   Token: {self.api_token[:8]}...")
                print(f"   User ID: {data['user_id']}")
                self.test_results.append(("Configuration Odoo", True, data))
                return True
            else:
                print(f"❌ Configuration échouée (status: {response.status_code})")
                print(f"   Réponse: {response.text}")
                self.test_results.append(("Configuration Odoo", False, f"Status: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la configuration: {e}")
            self.test_results.append(("Configuration Odoo", False, str(e)))
            return False
    
    def test_mcp_list_tools(self):
        """Test 3: MCP List Tools"""
        print("\n🔍 Test 3: MCP List Tools")
        if not self.api_token:
            print("❌ Pas de token API disponible")
            self.test_results.append(("MCP List Tools", False, "Pas de token"))
            return False
        
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
            
            response = requests.post(
                f"{BASE_URL}/mcp",
                json=mcp_request,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_token}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                print(f"✅ {len(tools)} tools disponibles:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
                self.test_results.append(("MCP List Tools", True, data))
                return True
            else:
                print(f"❌ List tools échoué (status: {response.status_code})")
                print(f"   Réponse: {response.text}")
                self.test_results.append(("MCP List Tools", False, f"Status: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du test list tools: {e}")
            self.test_results.append(("MCP List Tools", False, str(e)))
            return False
    
    def test_mcp_call_tool(self):
        """Test 4: MCP Call Tool"""
        print("\n🔍 Test 4: MCP Call Tool")
        if not self.api_token:
            print("❌ Pas de token API disponible")
            self.test_results.append(("MCP Call Tool", False, "Pas de token"))
            return False
        
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
                f"{BASE_URL}/mcp",
                json=mcp_request,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_token}"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Call tool réussi")
                content = data.get("result", {}).get("content", [])
                if content:
                    text = content[0].get("text", "")
                    print(f"   Résultat: {text[:100]}...")
                self.test_results.append(("MCP Call Tool", True, data))
                return True
            else:
                print(f"❌ Call tool échoué (status: {response.status_code})")
                print(f"   Réponse: {response.text}")
                self.test_results.append(("MCP Call Tool", False, f"Status: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du test call tool: {e}")
            self.test_results.append(("MCP Call Tool", False, str(e)))
            return False
    
    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if not success and isinstance(details, str):
                print(f"    Erreur: {details}")
        
        print(f"\nRésultat: {passed}/{total} tests réussis")
        
        if passed == total:
            print("🎉 Tous les tests sont passés avec succès !")
        else:
            print("⚠️  Certains tests ont échoué")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 DÉMARRAGE DES TESTS COMPLETS")
        print("="*60)
        
        try:
            # Démarrer le serveur
            if not self.start_server():
                return False
            
            # Exécuter les tests
            self.test_health()
            self.test_configuration()
            self.test_mcp_list_tools()
            self.test_mcp_call_tool()
            
            # Afficher le résumé
            self.print_summary()
            
            return True
            
        finally:
            # Arrêter le serveur
            self.stop_server()

def main():
    """Fonction principale"""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
