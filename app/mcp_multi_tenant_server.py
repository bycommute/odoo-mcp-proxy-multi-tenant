"""
MCP Multi-Tenant Server for Hostinger deployment
"""
import argparse
import uvicorn
import sys
import os
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Depends, Request, Header
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
async def execute_odoo_method(
    model: str,
    method: str,
    domain: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    ids: Optional[str] = None,
    values: Optional[str] = None
) -> str:
    """🚀 UNIVERSAL ODOO TOOL - Execute any Odoo method on any model.
    
    This tool allows you to:
    - search_read: Search and read records with domain filter
    - search: Search for record IDs
    - read: Read specific records by IDs
    - create: Create new records
    - write: Update existing records
    - unlink: Delete records
    
    Args:
        model: Odoo model name (e.g., 'res.partner', 'product.product', 'sale.order')
        method: Method to execute ('search_read', 'search', 'read', 'create', 'write', 'unlink')
        domain: Search domain as JSON string (for search/search_read). Ex: "[[\"is_company\", \"=\", true]]"
        fields: Comma-separated fields to return (for search_read/read). Ex: "name,email,phone"
        limit: Max number of records (for search/search_read). Default: 10
        ids: Comma-separated IDs (for read/write/unlink). Ex: "1,2,3"
        values: Values as JSON string (for create/write). Ex: "{\"name\": \"John\", \"email\": \"john@example.com\"}"
    """
    try:
        import json
        
        odoo_client = getattr(execute_odoo_method, '_odoo_client', None)
        if not odoo_client:
            return "Erreur: Client Odoo non configuré"
        
        logger.info(f"Executing Odoo method: {model}.{method}")
        
        # Build arguments based on method
        args = []
        kwargs = {}
        
        if method in ['search', 'search_read']:
            # Parse domain
            if domain:
                try:
                    parsed_domain = json.loads(domain)
                    args.append(parsed_domain)
                except:
                    args.append([])
            else:
                args.append([])
            
            # Add kwargs
            if fields:
                kwargs['fields'] = [f.strip() for f in fields.split(',')]
            if limit:
                kwargs['limit'] = limit
            elif limit is None:
                kwargs['limit'] = 10  # Default limit
                
        elif method == 'read':
            # Parse IDs
            if ids:
                id_list = [int(i.strip()) for i in ids.split(',')]
                args.append(id_list)
            else:
                return "Erreur: 'ids' requis pour la méthode 'read'"
            
            if fields:
                kwargs['fields'] = [f.strip() for f in fields.split(',')]
                
        elif method == 'create':
            # Parse values
            if values:
                try:
                    parsed_values = json.loads(values)
                    args.append([parsed_values])
                except Exception as e:
                    return f"Erreur lors du parsing de 'values': {str(e)}"
            else:
                return "Erreur: 'values' requis pour la méthode 'create'"
                
        elif method == 'write':
            # Parse IDs and values
            if not ids:
                return "Erreur: 'ids' requis pour la méthode 'write'"
            if not values:
                return "Erreur: 'values' requis pour la méthode 'write'"
            
            try:
                id_list = [int(i.strip()) for i in ids.split(',')]
                parsed_values = json.loads(values)
                args.append(id_list)
                args.append(parsed_values)
            except Exception as e:
                return f"Erreur lors du parsing: {str(e)}"
                
        elif method == 'unlink':
            # Parse IDs
            if ids:
                id_list = [int(i.strip()) for i in ids.split(',')]
                args.append(id_list)
            else:
                return "Erreur: 'ids' requis pour la méthode 'unlink'"
        
        # Execute the method
        result = odoo_client.execute_method(
            model=model,
            method=method,
            args=args,
            kwargs=kwargs
        )
        
        # Check for error
        if isinstance(result, dict) and 'error' in result:
            return f"Erreur Odoo: {result['error']}"
        
        # Format result
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
            
            # Set Odoo client for the universal tool
            execute_odoo_method._odoo_client = odoo_client
            
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
            # Return list of available tools - Only the universal tool
            tools = [
                {
                    "name": "execute_odoo_method",
                    "description": "🚀 UNIVERSAL ODOO TOOL - Execute any Odoo method on any model. Supports search, read, write, create, unlink, and all custom methods. This is the most powerful tool with full access to Odoo.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string", 
                                "description": "Odoo model name (e.g., 'res.partner', 'product.product', 'sale.order', 'account.move', 'stock.picking')"
                            },
                            "method": {
                                "type": "string",
                                "description": "Method to execute (e.g., 'search_read', 'search', 'read', 'create', 'write', 'unlink')"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Search domain as JSON string. Example: \"[[\\\"is_company\\\", \\\"=\\\", true]]\" or \"[]\" for all records"
                            },
                            "fields": {
                                "type": "string",
                                "description": "Comma-separated list of fields to return. Example: \"name,email,phone\" or leave empty for all fields"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of records to return. Default: 10"
                            },
                            "ids": {
                                "type": "string",
                                "description": "Comma-separated list of record IDs for read/write/unlink. Example: \"1,2,3\""
                            },
                            "values": {
                                "type": "string",
                                "description": "Values to create/write as JSON string. Example: \"{\\\"name\\\": \\\"John\\\", \\\"email\\\": \\\"john@example.com\\\"}\""
                            }
                        },
                        "required": ["model", "method"]
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
                
                # Set Odoo client for the universal tool
                setattr(execute_odoo_method, '_odoo_client', odoo_client)
                
                # Call the universal tool
                if tool_name == "execute_odoo_method":
                    result = await execute_odoo_method(
                        model=arguments.get("model"),
                        method=arguments.get("method"),
                        domain=arguments.get("domain"),
                        fields=arguments.get("fields"),
                        limit=arguments.get("limit"),
                        ids=arguments.get("ids"),
                        values=arguments.get("values")
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

# REST API endpoints for Make.com and other integrations
class OdooMethodRequest(BaseModel):
    model: str
    method: str
    domain: Optional[str] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    ids: Optional[str] = None
    values: Optional[str] = None

class OdooMethodResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@app.post("/api/odoo/execute", response_model=OdooMethodResponse)
async def execute_odoo_rest(
    request: OdooMethodRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    🚀 REST API endpoint for Make.com and other integrations
    
    Execute any Odoo method via simple HTTP POST request.
    No MCP protocol needed - just standard REST API!
    
    **Authentication:**
    - Header: `Authorization: Bearer YOUR_API_TOKEN`
    
    **Examples:**
    
    1. Search partners:
    ```bash
    curl -X POST http://145.223.102.57/api/odoo/execute \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "model": "res.partner",
        "method": "search_read",
        "domain": "[[\"is_company\", \"=\", true]]",
        "fields": "name,email,phone",
        "limit": 10
      }'
    ```
    
    2. Read specific records:
    ```bash
    curl -X POST http://145.223.102.57/api/odoo/execute \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "model": "res.partner",
        "method": "read",
        "ids": "1,2,3",
        "fields": "name,email"
      }'
    ```
    
    3. Create a record:
    ```bash
    curl -X POST http://145.223.102.57/api/odoo/execute \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "model": "res.partner",
        "method": "create",
        "values": "{\"name\": \"John Doe\", \"email\": \"john@example.com\"}"
      }'
    ```
    
    4. Update a record:
    ```bash
    curl -X POST http://145.223.102.57/api/odoo/execute \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "model": "res.partner",
        "method": "write",
        "ids": "123",
        "values": "{\"phone\": \"+33123456789\"}"
      }'
    ```
    """
    try:
        # Check authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
        token = authorization.split(" ", 1)[1]
        
        # Get Odoo client
        try:
            odoo_client = get_odoo_client_from_token(token, db)
        except HTTPException:
            raise HTTPException(status_code=401, detail="Invalid API token")
        
        # Build arguments based on method
        import json
        args = []
        kwargs = {}
        
        if request.method in ['search', 'search_read']:
            # Parse domain
            if request.domain:
                try:
                    parsed_domain = json.loads(request.domain)
                    args.append(parsed_domain)
                except:
                    args.append([])
            else:
                args.append([])
            
            # Add kwargs
            if request.fields:
                kwargs['fields'] = [f.strip() for f in request.fields.split(',')]
            if request.limit:
                kwargs['limit'] = request.limit
            elif request.limit is None:
                kwargs['limit'] = 10  # Default limit
                
        elif request.method == 'read':
            # Parse IDs
            if request.ids:
                id_list = [int(i.strip()) for i in request.ids.split(',')]
                args.append(id_list)
            else:
                return OdooMethodResponse(success=False, error="'ids' requis pour la méthode 'read'")
            
            if request.fields:
                kwargs['fields'] = [f.strip() for f in request.fields.split(',')]
                
        elif request.method == 'create':
            # Parse values
            if request.values:
                try:
                    parsed_values = json.loads(request.values)
                    args.append([parsed_values])
                except Exception as e:
                    return OdooMethodResponse(success=False, error=f"Erreur lors du parsing de 'values': {str(e)}")
            else:
                return OdooMethodResponse(success=False, error="'values' requis pour la méthode 'create'")
                
        elif request.method == 'write':
            # Parse IDs and values
            if not request.ids:
                return OdooMethodResponse(success=False, error="'ids' requis pour la méthode 'write'")
            if not request.values:
                return OdooMethodResponse(success=False, error="'values' requis pour la méthode 'write'")
            
            try:
                id_list = [int(i.strip()) for i in request.ids.split(',')]
                parsed_values = json.loads(request.values)
                args.append(id_list)
                args.append(parsed_values)
            except Exception as e:
                return OdooMethodResponse(success=False, error=f"Erreur lors du parsing: {str(e)}")
                
        elif request.method == 'unlink':
            # Parse IDs
            if request.ids:
                id_list = [int(i.strip()) for i in request.ids.split(',')]
                args.append(id_list)
            else:
                return OdooMethodResponse(success=False, error="'ids' requis pour la méthode 'unlink'")
        
        # Execute the method
        result = odoo_client.execute_method(
            model=request.model,
            method=request.method,
            args=args,
            kwargs=kwargs
        )
        
        # Check for error
        if isinstance(result, dict) and 'error' in result:
            return OdooMethodResponse(success=False, error=str(result['error']))
        
        return OdooMethodResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing Odoo method via REST API: {str(e)}")
        return OdooMethodResponse(success=False, error=str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MCP Multi-Tenant server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting MCP Multi-Tenant server on {args.host}:{args.port}")
    
    # Start the server
    uvicorn.run(app, host=args.host, port=args.port)
