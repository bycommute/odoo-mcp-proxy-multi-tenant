"""
MCP Multi-Tenant Server for Hostinger deployment
"""
import argparse
import uvicorn
import sys
import os
from typing import Optional, Dict
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.core.models import User, APIToken
from app.core.odoo_client import OdooClient
from app.utils.logger import logger
from pydantic import BaseModel
from typing import Optional
import secrets
import string

# Initialize FastMCP server for Odoo tools
mcp = FastMCP(name="odoo-mcp-proxy", json_response=False, stateless_http=False)

# Global storage for user sessions
user_sessions: Dict[str, OdooClient] = {}

# Pydantic models
class OdooConfigRequest(BaseModel):
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str

def generate_api_token() -> str:
    """Generate a secure API token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def get_odoo_client_from_token(token: str, db: Session) -> OdooClient:
    """Get Odoo client from API token"""
    # Get user by token
    api_token = db.query(APIToken).filter(
        APIToken.token == token,
        APIToken.is_active == True
    ).first()
    
    if not api_token:
        raise HTTPException(status_code=401, detail="Token API invalide")
    
    user = db.query(User).filter(User.user_id == api_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé ou inactif")
    
    # Create or get cached Odoo client
    if token not in user_sessions:
        user_sessions[token] = OdooClient(
            user.odoo_url,
            user.odoo_db,
            user.odoo_username,
            user.odoo_password
        )
    
    return user_sessions[token]

@mcp.tool()
async def search_partners(name: str = None, limit: int = 10) -> str:
    """Search for partners in Odoo.
    
    Args:
        name: Optional name to search for
        limit: Maximum number of results to return
    """
    try:
        # This will be set by the middleware
        odoo_client = getattr(search_partners, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
            
        logger.info(f"Searching partners with name: {name}, limit: {limit}")
        
        # Build search domain
        domain = []
        if name:
            domain.append(('name', 'ilike', name))
        
        # Search partners
        result = odoo_client.search_read(
            'res.partner',
            domain,
            ['name', 'email', 'phone', 'is_company'],
            limit=limit
        )
        
        if not result:
            return "Aucun partenaire trouvé."
        
        # Format results
        partners = []
        for partner in result:
            partner_info = f"""
Nom: {partner.get('name', 'N/A')}
Email: {partner.get('email', 'N/A')}
Téléphone: {partner.get('phone', 'N/A')}
Type: {'Entreprise' if partner.get('is_company') else 'Particulier'}
"""
            partners.append(partner_info)
        
        return f"Partenaires trouvés ({len(partners)}):\n" + "\n---\n".join(partners)
        
    except Exception as e:
        logger.error(f"Error searching partners: {str(e)}")
        return f"Erreur lors de la recherche des partenaires: {str(e)}"

@mcp.tool()
async def search_products(name: str = None, limit: int = 10) -> str:
    """Search for products in Odoo.
    
    Args:
        name: Optional name to search for
        limit: Maximum number of results to return
    """
    try:
        odoo_client = getattr(search_products, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
            
        logger.info(f"Searching products with name: {name}, limit: {limit}")
        
        # Build search domain
        domain = []
        if name:
            domain.append(('name', 'ilike', name))
        
        # Search products
        result = odoo_client.search_read(
            'product.product',
            domain,
            ['name', 'list_price', 'default_code', 'type'],
            limit=limit
        )
        
        if not result:
            return "Aucun produit trouvé."
        
        # Format results
        products = []
        for product in result:
            product_info = f"""
Nom: {product.get('name', 'N/A')}
Code: {product.get('default_code', 'N/A')}
Prix: {product.get('list_price', 0)} €
Type: {product.get('type', 'N/A')}
"""
            products.append(product_info)
        
        return f"Produits trouvés ({len(products)}):\n" + "\n---\n".join(products)
        
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return f"Erreur lors de la recherche des produits: {str(e)}"

@mcp.tool()
async def search_invoices(partner_name: str = None, limit: int = 10) -> str:
    """Search for invoices in Odoo.
    
    Args:
        partner_name: Optional partner name to filter by
        limit: Maximum number of results to return
    """
    try:
        odoo_client = getattr(search_invoices, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
            
        logger.info(f"Searching invoices with partner: {partner_name}, limit: {limit}")
        
        # Build search domain
        domain = []
        if partner_name:
            domain.append(('partner_id.name', 'ilike', partner_name))
        
        # Search invoices
        result = odoo_client.search_read(
            'account.move',
            domain,
            ['name', 'partner_id', 'amount_total', 'state', 'invoice_date'],
            limit=limit
        )
        
        if not result:
            return "Aucune facture trouvée."
        
        # Format results
        invoices = []
        for invoice in result:
            invoice_info = f"""
Numéro: {invoice.get('name', 'N/A')}
Client: {invoice.get('partner_id', ['N/A'])[1] if invoice.get('partner_id') else 'N/A'}
Montant: {invoice.get('amount_total', 0)} €
État: {invoice.get('state', 'N/A')}
Date: {invoice.get('invoice_date', 'N/A')}
"""
            invoices.append(invoice_info)
        
        return f"Factures trouvées ({len(invoices)}):\n" + "\n---\n".join(invoices)
        
    except Exception as e:
        logger.error(f"Error searching invoices: {str(e)}")
        return f"Erreur lors de la recherche des factures: {str(e)}"

@mcp.tool()
async def get_partner_details(partner_id: int) -> str:
    """Get detailed information about a specific partner.
    
    Args:
        partner_id: ID of the partner to get details for
    """
    try:
        odoo_client = getattr(get_partner_details, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
            
        logger.info(f"Getting partner details for ID: {partner_id}")
        
        # Get partner details
        partner = odoo_client.read(
            'res.partner',
            partner_id,
            ['name', 'email', 'phone', 'street', 'city', 'zip', 'country_id', 'vat', 'website']
        )
        
        if not partner:
            return f"Aucun partenaire trouvé avec l'ID {partner_id}."
        
        # Format result
        return f"""
Détails du partenaire (ID: {partner_id}):
Nom: {partner.get('name', 'N/A')}
Email: {partner.get('email', 'N/A')}
Téléphone: {partner.get('phone', 'N/A')}
Adresse: {partner.get('street', 'N/A')}, {partner.get('zip', 'N/A')} {partner.get('city', 'N/A')} ({partner.get('country_id', [None, 'N/A'])[1]})
TVA: {partner.get('vat', 'N/A')}
Site Web: {partner.get('website', 'N/A')}
"""
        
    except Exception as e:
        logger.error(f"Error getting partner details: {str(e)}")
        return f"Erreur lors de la récupération des détails du partenaire: {str(e)}"

@mcp.tool()
async def execute_odoo_method(
    model: str,
    method: str,
    args: list = None,
    kwargs: dict = None
) -> str:
    """🚀 UNIVERSAL ODOO TOOL - Execute any Odoo method on any model. This is the most powerful tool that gives full access to Odoo.
    
    This tool allows you to:
    - Read data: search(), read(), search_read()
    - Write data: create(), write(), unlink()
    - Execute any custom method defined in Odoo
    
    Args:
        model: Odoo model name (e.g., 'res.partner', 'product.product', 'sale.order', 'account.move')
        method: Method to execute (e.g., 'search', 'read', 'create', 'write', 'unlink', 'search_read')
        args: List of positional arguments for the method (optional)
        kwargs: Dictionary of keyword arguments for the method (optional)
    
    Examples:
        # Search partners
        execute_odoo_method('res.partner', 'search', [[['is_company', '=', True]]], {'limit': 10})
        
        # Read partner data
        execute_odoo_method('res.partner', 'read', [[1, 2, 3]], {'fields': ['name', 'email']})
        
        # Search and read in one call
        execute_odoo_method('product.product', 'search_read', [[['type', '=', 'product']]], {'fields': ['name', 'list_price'], 'limit': 20})
        
        # Create a partner
        execute_odoo_method('res.partner', 'create', [[{'name': 'New Partner', 'email': 'new@example.com'}]])
        
        # Update a partner
        execute_odoo_method('res.partner', 'write', [[1], {'phone': '+33123456789'}])
        
        # Get sale orders
        execute_odoo_method('sale.order', 'search_read', [[['state', '=', 'sale']]], {'fields': ['name', 'partner_id', 'amount_total']})
    """
    try:
        odoo_client = getattr(execute_odoo_method, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
        
        logger.info(f"Executing Odoo method: {model}.{method} with args={args}, kwargs={kwargs}")
        
        # Execute the method
        result = odoo_client.execute_method(
            model=model,
            method=method,
            args=args or [],
            kwargs=kwargs or {}
        )
        
        # Check for error
        if isinstance(result, dict) and 'error' in result:
            return f"Erreur Odoo: {result['error']}"
        
        # Format result
        import json
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        logger.error(f"Error executing Odoo method: {str(e)}")
        return f"Erreur: {str(e)}"

# Create FastAPI app with MCP integration
app = FastAPI(title="Odoo MCP Multi-Tenant Server")

# Mount static files
from fastapi.staticfiles import StaticFiles
# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.middleware("http")
async def mcp_auth_middleware(request: Request, call_next):
    """Middleware to authenticate MCP requests and set Odoo client"""
    
    # Only apply to MCP POST endpoints (not GET)
    if request.url.path.startswith("/mcp") and request.method == "POST":
        # Get token from headers
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401, 
                content={"error": "Token API manquant"}
            )
        
        token = auth_header.split(" ", 1)[1]
        
        # Get database session
        db = next(get_db())
        try:
            # Get Odoo client
            odoo_client = get_odoo_client_from_token(token, db)
            
            # Set Odoo client for tools
            search_partners._odoo_client = odoo_client
            search_products._odoo_client = odoo_client
            search_invoices._odoo_client = odoo_client
            
        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401, 
                content={"error": str(e)}
            )
        finally:
            db.close()
    
    response = await call_next(request)
    return response

# MCP Streamable HTTP endpoints
@app.get("/mcp")
async def mcp_get_endpoint(request: Request):
    """Handle GET requests to MCP endpoint - return server info"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "odoo-mcp-proxy",
                "version": "1.0.0"
            },
            "message": "MCP Server is running. Use POST requests for full functionality.",
            "endpoints": {
                "initialize": "POST /mcp with JSON-RPC 2.0",
                "tools_list": "POST /mcp with method: tools/list",
                "tools_call": "POST /mcp with method: tools/call"
            }
        }
    }

@app.post("/mcp")
async def mcp_endpoint_no_slash(request: Request):
    """Handle MCP Streamable HTTP requests without trailing slash"""
    return await mcp_endpoint_with_slash(request)

@app.post("/mcp/")
async def mcp_endpoint_with_slash(request: Request):
    """Handle MCP Streamable HTTP requests"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        logger.info(f"MCP request: {method} with params: {params}")
        
        if method == "initialize":
            # MCP handshake - required by OpenAI
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "odoo-mcp-proxy",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            # Return list of available tools
            tools = [
                {
                    "name": "search_partners",
                    "description": "Search for partners in Odoo",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name to search for"},
                            "limit": {"type": "integer", "description": "Maximum number of results"}
                        }
                    }
                },
                {
                    "name": "search_products", 
                    "description": "Search for products in Odoo",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name to search for"},
                            "limit": {"type": "integer", "description": "Maximum number of results"}
                        }
                    }
                },
                {
                    "name": "search_invoices",
                    "description": "Search for invoices in Odoo", 
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "partner_name": {"type": "string", "description": "Partner name to filter by"},
                            "limit": {"type": "integer", "description": "Maximum number of results"}
                        }
                    }
                },
                {
                    "name": "get_partner_details",
                    "description": "Get detailed information about a specific partner",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "partner_id": {"type": "integer", "description": "ID of the partner"}
                        },
                        "required": ["partner_id"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }
            
        elif method == "tools/call":
            # Handle tool calls
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Get Odoo client from token
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32600, "message": "Missing or invalid authorization"}
                }
            
            token = auth_header.split(" ", 1)[1]
            db = next(get_db())
            
            try:
                odoo_client = get_odoo_client_from_token(token, db)
                
                # Set Odoo client for tools
                setattr(search_partners, '_odoo_client', odoo_client)
                setattr(search_products, '_odoo_client', odoo_client)
                setattr(search_invoices, '_odoo_client', odoo_client)
                setattr(get_partner_details, '_odoo_client', odoo_client)
                setattr(execute_odoo_method, '_odoo_client', odoo_client)
                
                # Call the appropriate tool
                if tool_name == "search_partners":
                    result = await search_partners(
                        name=arguments.get("name"),
                        limit=arguments.get("limit", 10)
                    )
                elif tool_name == "search_products":
                    result = await search_products(
                        name=arguments.get("name"),
                        limit=arguments.get("limit", 10)
                    )
                elif tool_name == "search_invoices":
                    result = await search_invoices(
                        partner_name=arguments.get("partner_name"),
                        limit=arguments.get("limit", 10)
                    )
                elif tool_name == "get_partner_details":
                    result = await get_partner_details(
                        partner_id=arguments.get("partner_id")
                    )
                elif tool_name == "execute_odoo_method":
                    result = await execute_odoo_method(
                        model=arguments.get("model"),
                        method=arguments.get("method"),
                        args=arguments.get("args"),
                        kwargs=arguments.get("kwargs")
                    )
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": result}]}
                }
                
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {str(e)}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
            finally:
                db.close()
                
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }
            
    except Exception as e:
        logger.error(f"MCP endpoint error: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": request_id if 'request_id' in locals() else None,
            "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
        }

@app.get("/")
async def root():
    """Serve the landing page"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/index.html")

@app.get("/test")
async def read_test():
    """Serve the test page"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/test.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "mcp_endpoint": "/mcp"}

@app.get("/sitemap.xml")
async def sitemap():
    """Serve the sitemap"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/sitemap.xml", media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    """Serve the robots.txt"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/robots.txt", media_type="text/plain")

@app.post("/mcp-debug")
async def mcp_debug(request: Request):
    """Debug endpoint to see what OpenAI sends"""
    try:
        body = await request.json()
        headers = dict(request.headers)
        
        logger.info(f"DEBUG - Headers: {headers}")
        logger.info(f"DEBUG - Body: {body}")
        
        return {
            "debug": True,
            "headers": headers,
            "body": body,
            "auth_header": headers.get("authorization", "MISSING")
        }
    except Exception as e:
        logger.error(f"DEBUG error: {str(e)}")
        return {"error": str(e)}

# API endpoints for frontend
@app.post("/api/config")
async def configure_odoo(config: OdooConfigRequest, db: Session = Depends(get_db)):
    """Configure a new Odoo instance and generate API token"""
    
    try:
        logger.info(f"Configuring Odoo instance: {config.odoo_url}")
        
        # Test Odoo connection
        client = OdooClient(config.odoo_url, config.odoo_db, config.odoo_username, config.odoo_password)
        if not client.test_connection():
            raise HTTPException(status_code=400, detail="Impossible de se connecter à Odoo. Vérifiez vos identifiants.")
        
        # Generate API token
        api_token = generate_api_token()
        
        # Create user
        user = User(
            odoo_url=config.odoo_url,
            odoo_db=config.odoo_db,
            odoo_username=config.odoo_username,
            odoo_password=config.odoo_password,  # TODO: Encrypt password
        )
        
        db.add(user)
        db.flush()  # To get the ID
        
        # Create API token
        token_record = APIToken(
            token=api_token,
            user_id=user.user_id
        )
        
        db.add(token_record)
        db.commit()
        
        logger.info(f"Configuration successful for user: {user.user_id}")
        
        return {
            "success": True,
            "message": "Configuration Odoo créée avec succès",
            "api_token": api_token,
            "mcp_url": f"http://145.223.102.57/mcp",  # Hostinger IP (via Nginx)
            "user_id": user.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la configuration: {str(e)}")

@app.post("/api/test-connection")
async def test_odoo_connection(config: OdooConfigRequest):
    """Test Odoo connection without saving"""
    
    try:
        logger.info(f"Testing Odoo connection: {config.odoo_url}")
        
        # Test Odoo connection
        client = OdooClient(config.odoo_url, config.odoo_db, config.odoo_username, config.odoo_password)
        
        if client.test_connection():
            return {
                "success": True,
                "message": "Connexion Odoo réussie !"
            }
        else:
            return {
                "success": False,
                "message": "Impossible de se connecter à Odoo. Vérifiez vos identifiants."
            }
            
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        return {
            "success": False,
            "message": f"Erreur lors du test de connexion: {str(e)}"
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MCP Multi-Tenant server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting MCP Multi-Tenant server on {args.host}:{args.port}")
    
    # Start the server
    uvicorn.run(app, host=args.host, port=args.port)
