# 🚀 Odoo MCP Proxy Multi-Tenant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

**Connectez votre instance Odoo à ChatGPT, Claude et autres agents IA via le protocole MCP.**

Une solution multi-tenant complète pour exposer votre Odoo aux agents IA modernes. Configuration en 2 minutes, sécurisé par token, compatible avec tous les agents IA supportant le protocole MCP.

🌐 **[Demo Live](http://145.223.102.57/)** | 📖 **[Documentation](docs/)** | 🐛 **[Issues](https://github.com/bycommute/odoo-mcp-proxy-multi-tenant/issues)**

---

## ✨ Fonctionnalités

- 🔌 **Intégration native MCP** - Compatible ChatGPT, Claude, et tous les agents IA
- 🏢 **Multi-tenant** - Gérez plusieurs instances Odoo depuis une seule application
- 🔒 **Sécurisé** - Authentification par token API, chiffrement, conformité RGPD
- ⚡ **Rapide** - Configuration en 2 minutes, pas d'installation complexe
- 🔄 **Temps réel** - Synchronisation instantanée avec vos données Odoo
- 📊 **Analytics** - Suivez l'utilisation avec des métriques détaillées

## 🎯 Cas d'usage

### 💬 Support client intelligent
ChatGPT peut consulter les commandes, factures et historique client directement dans Odoo pour un support ultra-rapide.

### 📊 Analyse de données
L'IA analyse vos ventes, prévisions et KPIs pour des insights actionnables en temps réel.

### 🤖 Automatisation
Créez des workflows automatisés entre Odoo et vos outils IA pour gagner du temps.

### 🎯 CRM et ventes
Qualification automatique des leads, suggestions de produits et prévisions de ventes.

---

## 🚀 Quick Start

### Prérequis

- Python 3.8+
- Une instance Odoo accessible
- Un serveur avec accès internet (VPS, cloud, etc.)

### Installation (5 minutes)

```bash
# 1. Cloner le repo
git clone https://github.com/bycommute/odoo-mcp-proxy-multi-tenant.git
cd odoo-mcp-proxy-multi-tenant

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080
```

🎉 **C'est tout !** Ouvrez `http://localhost:8080` dans votre navigateur.

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [🚀 Déploiement](docs/DEPLOYMENT.md) | Guide complet pour déployer sur Hostinger, AWS, etc. |
| [🔒 HTTPS Setup](docs/HTTPS_SETUP.md) | Configurer un domaine et SSL (Let's Encrypt) |
| [🎨 Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md) | Structure et design du frontend |
| [📁 Project Structure](docs/PROJECT_STRUCTURE.md) | Organisation du code |

---

## 🏗️ Architecture

```
┌─────────────────┐
│   ChatGPT/      │
│   Claude/       │  MCP Protocol
│   Agents IA     │  (JSON-RPC 2.0)
└────────┬────────┘
         │
         │ HTTPS + Bearer Token
         ▼
┌─────────────────────────────┐
│  Odoo MCP Proxy             │
│  (FastAPI + FastMCP)        │
│                             │
│  • Authentification         │
│  • Multi-tenant             │
│  • MCP Tools                │
└────────┬────────────────────┘
         │
         │ XML-RPC
         ▼
┌─────────────────┐
│  Odoo Instance  │
│  (Votre ERP)    │
└─────────────────┘
```

---

## 🛠️ Technologies

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne
- **MCP**: [FastMCP](https://github.com/jlowin/fastmcp) - Implémentation MCP
- **Database**: SQLite (ou PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Nginx, Gunicorn, Systemd

---

## 📦 Structure du projet

```
odoo-mcp-proxy-multi-tenant/
├── app/
│   ├── core/                    # Composants principaux
│   │   ├── database.py          # Configuration DB
│   │   ├── models.py            # Modèles (User, APIToken)
│   │   └── odoo_client.py       # Client Odoo RPC
│   └── mcp_multi_tenant_server.py  # Serveur principal
│
├── frontend/
│   ├── css/                     # Styles
│   ├── js/                      # JavaScript
│   ├── use-cases/               # Pages de cas d'usage
│   ├── index.html               # Landing page
│   └── test.html                # Page de test
│
├── docs/                        # Documentation
├── scripts/                     # Scripts de déploiement
└── tests/                       # Tests
```

---

## 🔐 Sécurité

- ✅ Authentification par Bearer Token
- ✅ Tokens API uniques par instance
- ✅ Chiffrement des données en transit (HTTPS)
- ✅ Headers de sécurité (HSTS, CSP, etc.)
- ✅ Validation des entrées
- ✅ Rate limiting (optionnel)

---

## 🌐 Déploiement

### Option 1 : Déploiement rapide (Hostinger VPS)

```bash
./scripts/deploy_mcp_hostinger.sh
```

### Option 2 : Déploiement avec HTTPS

```bash
# 1. Configurer votre domaine (DNS A record)
# 2. Lancer le script
./scripts/setup_https.sh votre-domaine.com
```

Voir [Guide de déploiement](docs/DEPLOYMENT.md) pour plus de détails.

---

## 🧪 Tests

```bash
# Tests rapides
./tests/quick_test.sh

# Tests complets
python tests/run_all_tests.py

# Test de déploiement
./tests/test_deployment.py
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 Roadmap

- [x] Backend MCP multi-tenant
- [x] Landing page SEO optimisée
- [x] 3 cas d'usage (Support, Analytics, CRM)
- [x] Scripts de déploiement automatisés
- [x] Documentation complète
- [ ] Dashboard utilisateur
- [ ] Système d'authentification (comptes)
- [ ] 3 cas d'usage supplémentaires (Email, Finance, Automation)
- [ ] Analytics avancées
- [ ] API REST complémentaire
- [ ] Support PostgreSQL
- [ ] Docker/Docker Compose
- [ ] Monitoring (Prometheus/Grafana)

---

## 📄 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocole MCP
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [FastMCP](https://github.com/jlowin/fastmcp) - Implémentation MCP
- [Odoo](https://www.odoo.com/) - ERP open source

---

## 📞 Support

- 📧 Email: support@bycommute.com
- 🐛 Issues: [GitHub Issues](https://github.com/bycommute/odoo-mcp-proxy-multi-tenant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/bycommute/odoo-mcp-proxy-multi-tenant/discussions)

---

**Fait avec ❤️ par [bycommute](https://github.com/bycommute)**

[![Star on GitHub](https://img.shields.io/github/stars/bycommute/odoo-mcp-proxy-multi-tenant?style=social)](https://github.com/bycommute/odoo-mcp-proxy-multi-tenant)