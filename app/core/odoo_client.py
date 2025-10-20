"""
Client Odoo pour les appels JSON-RPC
Basé sur votre code existant qui fonctionne bien
"""

import requests
import json
from typing import Dict, Any, Optional
from loguru import logger

class OdooClient:
    """Client Odoo utilisant JSON-RPC (compatible Odoo 19+)"""
    
    def __init__(self, odoo_url: str, odoo_db: str, odoo_username: str, odoo_password: str):
        self.odoo_url = odoo_url.strip()
        self.odoo_db = odoo_db
        self.odoo_username = odoo_username
        self.odoo_password = odoo_password
        
        # Normalisation de l'URL Odoo
        if not self.odoo_url.startswith("http://") and not self.odoo_url.startswith("https://"):
            self.odoo_url = f"https://{self.odoo_url}"
        
        self.auth_url = f"{self.odoo_url}/jsonrpc"
        self.uid = None
    
    def authenticate(self) -> bool:
        """Authentification auprès d'Odoo"""
        try:
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [self.odoo_db, self.odoo_username, self.odoo_password, {}]
                },
                "id": 1
            }
            
            response = requests.post(self.auth_url, json=auth_payload)
            auth_data = response.json()
            
            if "error" in auth_data or not auth_data.get("result"):
                logger.error(f"Erreur d'authentification Odoo: {auth_data}")
                return False
            
            self.uid = auth_data["result"]
            if not self.uid:
                logger.error("UID vide après authentification")
                return False
            
            logger.info(f"Authentification Odoo réussie pour {self.odoo_username}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification Odoo: {e}")
            return False
    
    def execute_method(self, model: str, method: str, args: list = None, kwargs: dict = None) -> Dict[str, Any]:
        """Exécuter une méthode Odoo"""
        if not self.uid:
            if not self.authenticate():
                return {"error": "Authentification Odoo échouée"}
        
        try:
            args = args or []
            kwargs = kwargs or {}
            
            execute_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.odoo_db,
                        self.uid,
                        self.odoo_password,
                        model,
                        method,
                        args,
                        kwargs
                    ]
                },
                "id": 2
            }
            
            response = requests.post(self.auth_url, json=execute_payload)
            execute_data = response.json()
            
            if "error" in execute_data:
                logger.error(f"Erreur Odoo: {execute_data['error']}")
                return {"error": f"Erreur Odoo: {execute_data['error']}"}
            
            result = execute_data.get("result")
            logger.info(f"Méthode Odoo exécutée: {model}.{method}")
            return {"result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la méthode Odoo: {e}")
            return {"error": str(e)}
    
    def search_read(self, model: str, domain: list, fields: list, limit: int = None) -> list:
        """Search and read records from Odoo
        
        Args:
            model: Odoo model name
            domain: Search domain
            fields: List of fields to read
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        try:
            # First search for record IDs
            search_result = self.execute_method(
                model,
                "search",
                [domain],
                {"limit": limit} if limit else {}
            )
            
            if "error" in search_result:
                return []
            
            record_ids = search_result.get("result", [])
            if not record_ids:
                return []
            
            # Then read the records
            read_result = self.execute_method(
                model,
                "read",
                [record_ids, fields]
            )
            
            if "error" in read_result:
                return []
            
            return read_result.get("result", [])
            
        except Exception as e:
            logger.error(f"Erreur lors de search_read: {str(e)}")
            return []
    
    def read(self, model: str, record_id: int, fields: list) -> dict:
        """Read a specific record from Odoo
        
        Args:
            model: Odoo model name
            record_id: ID of the record to read
            fields: List of fields to read
            
        Returns:
            Record data
        """
        try:
            result = self.execute_method(
                model,
                "read",
                [record_id, fields]
            )
            
            if "error" in result:
                return {}
            
            records = result.get("result", [])
            return records[0] if records else {}
            
        except Exception as e:
            logger.error(f"Erreur lors de read: {str(e)}")
            return {}
    
    def test_connection(self) -> bool:
        """Tester la connexion à Odoo"""
        try:
            result = self.execute_method("res.users", "search_read", [[], ["id", "name"], 0, 1])
            return "error" not in result
        except Exception as e:
            logger.error(f"Erreur lors du test de connexion: {e}")
            return False
