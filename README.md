# 🚀 Odoo MCP Proxy Multi-Tenant

Un proxy MCP (Model Context Protocol) multi-tenant qui permet de connecter n'importe quelle instance Odoo à ChatGPT et autres agents IA.

## ✨ Fonctionnalités

- **🌐 Interface Web** : Configuration simple via navigateur
- **🔐 Multi-tenant** : Chaque utilisateur connecte sa propre instance Odoo
- **🔑 Token API** : Génération automatique de tokens sécurisés
- **🧪 Test de connexion** : Validation des identifiants avant configuration
- **📱 Responsive** : Interface adaptée mobile et desktop
- **⚡ MCP Compatible** : Fonctionne avec ChatGPT, Ponaï et autres agents IA

## 🎯 Utilisation

### 1. Accéder à l'interface
Rendez-vous sur : **http://145.223.102.57**

> ⚠️ **Bonnes pratiques de diagnostic** : Si quelque chose ne marche pas lors du déploiement, résolvez le problème à la source au lieu d'être un bourrin ! Consultez la [documentation de déploiement](docs/DEPLOYMENT.md) pour les étapes de diagnostic.

### 2. Configurer votre instance Odoo
- **URL Odoo** : `votre-instance.odoo.com` (avec ou sans https://)
- **Base de données** : Nom de votre base Odoo
- **Email de connexion** : Votre email Odoo
- **Mot de passe** : Votre mot de passe Odoo

### 3. Tester et générer
1. Cliquez sur "🔍 Tester la connexion" pour vérifier vos identifiants
2. Si le test réussit, cliquez sur "⚡ Générer le token API"
3. Copiez le **Token API** et l'**URL MCP** générés

### 4. Utiliser avec ChatGPT
1. Dans ChatGPT, allez dans les paramètres
2. Configurez un serveur MCP
3. Utilisez l'URL MCP et le Token API comme identifiants
4. Vous pouvez maintenant interagir avec votre Odoo via ChatGPT !

## 🛠️ Déploiement

### Prérequis
- VPS Ubuntu 24.04
- Python 3.8+
- Nginx
- Accès SSH root

### Installation automatique
```bash
# Télécharger le script de déploiement
wget https://raw.githubusercontent.com/votre-repo/odoo-mcp-proxy/main/scripts/manual_deploy.sh
chmod +x manual_deploy.sh

# Exécuter le déploiement
./manual_deploy.sh
```

### Installation manuelle
```bash
# 1. Cloner le projet
git clone https://github.com/votre-repo/odoo-mcp-proxy.git
cd odoo-mcp-proxy

# 2. Installer les dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 4. Initialiser la base de données
python -c "from app.core.database import create_tables; create_tables()"

# 5. Démarrer le serveur
python -m app.main
```

## 📁 Structure du projet

```
Odoo MCP Proxy Multi-Tenant/
├── app/                    # 🎯 Application principale
│   ├── api/               # Endpoints FastAPI
│   │   ├── config.py      # Configuration Odoo
│   │   ├── health.py      # Health check
│   │   ├── mcp.py         # Endpoints MCP
│   │   └── test_connection.py # Test connexion
│   ├── core/              # Modèles et client Odoo
│   │   ├── database.py    # Configuration DB
│   │   ├── models.py      # Modèles SQLAlchemy
│   │   └── odoo_client.py # Client Odoo
│   ├── services/          # Logique MCP
│   │   └── mcp_service.py # Service MCP
│   ├── utils/             # Configuration
│   │   ├── config.py      # Settings
│   │   └── logger.py      # Logging
│   └── main.py            # Point d'entrée
├── frontend/              # 🌐 Interface web
│   ├── index.html         # Page principale
│   ├── style.css          # Styles CSS
│   └── script.js          # JavaScript
├── scripts/               # 🚀 Scripts de déploiement
│   └── manual_deploy.sh   # Déploiement manuel
├── tests/                 # 🧪 Tests
│   ├── run_all_tests.py   # Tests complets
│   ├── test_deployment.py # Tests déploiement
│   └── quick_test.sh      # Test rapide
├── docs/                  # 📚 Documentation
│   └── STRUCTURE.md       # Structure détaillée
├── .env.example           # Configuration exemple
├── .gitignore             # Fichiers à ignorer
├── requirements.txt       # Dépendances Python
└── README.md              # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement
```bash
# Application
APP_NAME=Odoo MCP Proxy Multi-Tenant
APP_VERSION=1.0.0
DEBUG=false

# Serveur
HOST=0.0.0.0
PORT=8000

# Base de données
DATABASE_URL=sqlite:///./data/odoo_mcp_proxy.db

# Sécurité
SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# CORS
CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=INFO
```

## 🧪 Tests

### Tests locaux
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer tous les tests
python tests/run_all_tests.py

# Test rapide
bash tests/quick_test.sh
```

### Tests de déploiement
```bash
# Test du déploiement
python tests/test_deployment.py
```

## 📊 Endpoints API

### Health Check
```http
GET /api/health
```

### Test de connexion
```http
POST /api/test-connection
Content-Type: application/json

{
  "odoo_url": "votre-instance.odoo.com",
  "odoo_db": "nom_base",
  "odoo_username": "email@example.com",
  "odoo_password": "mot_de_passe"
}
```

### Configuration
```http
POST /api/config
Content-Type: application/json

{
  "odoo_url": "votre-instance.odoo.com",
  "odoo_db": "nom_base",
  "odoo_username": "email@example.com",
  "odoo_password": "mot_de_passe"
}
```

### MCP Endpoint
```http
POST /api/mcp
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

## 🛡️ Sécurité

- **Tokens API** : Générés de manière sécurisée (32 caractères aléatoires)
- **Validation** : Test de connexion avant génération de token
- **CORS** : Configuré pour les requêtes cross-origin
- **Logs** : Traçabilité des opérations

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation dans `/docs/`
- Vérifier les logs dans `/logs/`

---

**Développé avec ❤️ pour la communauté Odoo et IA**