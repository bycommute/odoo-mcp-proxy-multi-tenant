# Structure du projet Odoo MCP Proxy

## 📁 Arborescence complète

```
Odoo MCP Proxy Multi-Tenant/
│
├── app/                            # Application backend
│   ├── __init__.py
│   ├── core/                       # Composants principaux
│   │   ├── __init__.py
│   │   ├── database.py             # Configuration SQLAlchemy
│   │   ├── models.py               # Modèles de données (User, APIToken)
│   │   └── odoo_client.py          # Client Odoo RPC
│   │
│   └── mcp_multi_tenant_server.py  # Serveur principal (FastAPI + MCP)
│
├── frontend/                       # Interface web
│   ├── css/
│   │   ├── landing.css             # Styles landing page
│   │   └── test.css                # Styles page de test
│   ├── js/
│   │   ├── landing.js              # JavaScript landing page
│   │   └── test.js                 # JavaScript page de test
│   ├── use-cases/                  # Pages de cas d'usage
│   │   ├── analytics.html
│   │   ├── crm.html
│   │   └── support.html
│   ├── index.html                  # Landing page principale
│   ├── test.html                   # Page de configuration/test
│   ├── robots.txt                  # SEO - Directives crawlers
│   └── sitemap.xml                 # SEO - Plan du site
│
├── docs/                           # Documentation
│   ├── DEPLOYMENT.md               # Guide de déploiement
│   ├── FRONTEND_ARCHITECTURE.md    # Architecture frontend
│   ├── HTTPS_SETUP.md              # Guide HTTPS / SSL
│   └── PROJECT_STRUCTURE.md        # Ce fichier
│
├── scripts/                        # Scripts de déploiement
│   ├── deploy_frontend_complete.sh # Déploiement frontend
│   ├── deploy_mcp_hostinger.sh     # Déploiement complet
│   └── setup_https.sh              # Configuration HTTPS
│
├── tests/                          # Tests
│   ├── quick_test.sh
│   ├── run_all_tests.py
│   └── test_deployment.py
│
├── logs/                           # Logs de l'application
│   └── app.log
│
├── .gitignore                      # Fichiers ignorés par Git
├── env.example                     # Exemple de variables d'environnement
├── odoo_mcp_proxy.db              # Base de données SQLite
├── README.md                       # Documentation principale
└── requirements.txt                # Dépendances Python
```

## 🎯 Fichiers principaux

### Backend

| Fichier | Description | Rôle |
|---------|-------------|------|
| `app/mcp_multi_tenant_server.py` | **Serveur principal** | FastAPI + MCP, gère tout |
| `app/core/database.py` | Configuration DB | SQLAlchemy setup |
| `app/core/models.py` | Modèles | User, APIToken |
| `app/core/odoo_client.py` | Client Odoo | Connexion RPC à Odoo |

### Frontend

| Fichier | Description | URL |
|---------|-------------|-----|
| `frontend/index.html` | Landing page | `/` |
| `frontend/test.html` | Page de test | `/test` |
| `frontend/css/landing.css` | Styles landing | - |
| `frontend/css/test.css` | Styles test | - |
| `frontend/js/landing.js` | JS landing | - |
| `frontend/js/test.js` | JS test | - |
| `frontend/use-cases/*.html` | Cas d'usage | `/use-cases/*` |

### Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `scripts/deploy_frontend_complete.sh` | Déploie le frontend | `./scripts/deploy_frontend_complete.sh` |
| `scripts/deploy_mcp_hostinger.sh` | Déploie tout | `./scripts/deploy_mcp_hostinger.sh` |
| `scripts/setup_https.sh` | Configure HTTPS | `./scripts/setup_https.sh domain.com` |

### Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale |
| `docs/DEPLOYMENT.md` | Guide de déploiement |
| `docs/FRONTEND_ARCHITECTURE.md` | Architecture frontend |
| `docs/HTTPS_SETUP.md` | Configuration HTTPS |
| `docs/PROJECT_STRUCTURE.md` | Structure du projet |

## 🔄 Flux de l'application

### 1. Landing page (`/`)
```
User → http://145.223.102.57/
     → Nginx (port 80)
     → Python FastAPI (port 8080)
     → frontend/index.html
```

### 2. Page de test (`/test`)
```
User → /test
     → frontend/test.html
     → Form submit → /api/config (POST)
     → Génère token API
     → Retourne token + URL MCP
```

### 3. MCP Endpoint (`/mcp`)
```
ChatGPT/Claude → /mcp (POST)
              → Authentification Bearer token
              → Traitement JSON-RPC 2.0
              → Appels Odoo RPC
              → Réponse JSON-RPC
```

## 🗂️ Organisation des fichiers

### Fichiers à ne pas modifier
- `odoo_mcp_proxy.db` - Base de données (généré automatiquement)
- `logs/` - Logs (généré automatiquement)
- `venv/` - Environnement virtuel Python
- `__pycache__/` - Cache Python

### Fichiers à modifier selon les besoins
- `frontend/*.html` - Pages web
- `frontend/css/*.css` - Styles
- `frontend/js/*.js` - JavaScript
- `app/mcp_multi_tenant_server.py` - Logique backend

### Fichiers de configuration
- `requirements.txt` - Dépendances Python
- `env.example` - Variables d'environnement
- `.gitignore` - Fichiers ignorés

## 📦 Dépendances principales

```txt
fastapi         # Framework web
uvicorn         # Serveur ASGI
sqlalchemy      # ORM
fastmcp         # Protocole MCP
httpx           # Client HTTP
python-dotenv   # Variables d'env
```

## 🚀 Points d'entrée

### Développement local
```bash
cd app/
python mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080
```

### Production (Hostinger)
```bash
cd /opt/odoo-mcp-proxy
source venv/bin/activate
nohup python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080 > logs/mcp_server.log 2>&1 &
```

## 🔍 Fichiers supprimés (nettoyage)

Les fichiers suivants ont été supprimés car obsolètes :
- ❌ `app/main.py` - Remplacé par mcp_multi_tenant_server.py
- ❌ `app/mcp_streamable_wrapper.py` - Obsolète
- ❌ `app/api/` - Logique intégrée dans le serveur principal
- ❌ `app/services/` - Logique intégrée dans le serveur principal
- ❌ `app/utils/` - Logique intégrée dans le serveur principal
- ❌ `frontend/index_complex.html` - Backup inutile
- ❌ `frontend/index_simple.html` - Backup inutile
- ❌ `frontend/script.js` - Remplacé par js/test.js
- ❌ `frontend/style.css` - Remplacé par css/test.css
- ❌ `docs/STRUCTURE.md` - Fusionné avec PROJECT_STRUCTURE.md
- ❌ `*.zip` - Fichiers de backup

## 📝 Notes importantes

1. **Un seul fichier backend** : `app/mcp_multi_tenant_server.py` gère tout
2. **Structure frontend claire** : HTML, CSS, JS séparés
3. **Documentation complète** : Tous les guides dans `docs/`
4. **Scripts de déploiement** : Automatisation dans `scripts/`
5. **Pas de fichiers en double** : Structure nettoyée

## 🔧 Maintenance

### Ajouter une nouvelle page
1. Créer `frontend/nouvelle-page.html`
2. Ajouter dans `app/mcp_multi_tenant_server.py` :
   ```python
   @app.get("/nouvelle-page")
   async def nouvelle_page():
       return FileResponse("frontend/nouvelle-page.html")
   ```
3. Mettre à jour `frontend/sitemap.xml`
4. Déployer avec `./scripts/deploy_frontend_complete.sh`

### Ajouter un cas d'usage
1. Créer `frontend/use-cases/nouveau-cas.html`
2. Ajouter le lien dans `frontend/index.html`
3. Mettre à jour `frontend/sitemap.xml`
4. Déployer

### Modifier le backend
1. Éditer `app/mcp_multi_tenant_server.py`
2. Tester localement
3. Déployer avec `./scripts/deploy_mcp_hostinger.sh`