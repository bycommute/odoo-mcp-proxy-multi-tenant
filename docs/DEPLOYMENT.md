# 🚀 Guide de Déploiement - Odoo MCP Proxy Multi-Tenant

## ⚠️ IMPORTANT : Bonnes pratiques de diagnostic

**Si quelque chose ne marche pas lors du déploiement, résolvez le problème à la source au lieu d'être un bourrin !**

### Étapes de diagnostic recommandées :

1. **Vérifier l'état du serveur** :
   ```bash
   ssh root@145.223.102.57 "ps aux | grep python | grep -v grep"
   ```

2. **Vérifier les logs d'erreur** :
   ```bash
   ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && tail -20 logs/mcp_server.log"
   ```

3. **Tester la connectivité locale** :
   ```bash
   ssh root@145.223.102.57 "curl -f http://localhost:8080/health"
   ```

4. **Vérifier les ports ouverts** :
   ```bash
   ssh root@145.223.102.57 "netstat -tlnp | grep 8080"
   ```

5. **Tester les dépendances** :
   ```bash
   ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && source venv/bin/activate && python -c 'from app.core.database import init_db; print(\"OK\")'"
   ```

## 🎯 Déploiement Automatique (Recommandé)

### Déploiement MCP Multi-Tenant
```bash
./scripts/deploy_mcp_hostinger.sh
```

Ce script :
1. Crée un package de déploiement
2. Envoie le package sur le VPS Hostinger
3. Installe les dépendances MCP
4. Démarre le serveur MCP Multi-Tenant sur le port 8080
5. Teste le déploiement

### Vérification du déploiement
```bash
# Test de l'API Health (via Nginx)
curl http://145.223.102.57/health

# Test de l'interface web (via Nginx)
curl http://145.223.102.57/

# Test de l'endpoint MCP (via Nginx)
curl -X POST http://145.223.102.57/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 🏗️ Architecture de déploiement

```
Internet → Nginx (Port 80) → Python Server (Port 8080)
```

- **Nginx** : Proxy inverse sur le port 80 (accessible depuis l'extérieur)
- **Python Server** : Serveur MCP sur le port 8080 (interne uniquement)
- **Base de données** : SQLite locale

**Pourquoi Nginx ?** Hostinger bloque l'accès direct au port 8080, donc Nginx fait le proxy.

## 🔧 Configuration du serveur

### Variables d'environnement
Le serveur utilise les variables suivantes :
- `DATABASE_URL` : URL de la base de données SQLite
- `SECRET_KEY` : Clé secrète pour JWT
- `LOG_LEVEL` : Niveau de logging

### Ports utilisés
- **8080** : Serveur MCP Multi-Tenant (interne)
- **80** : Nginx (reverse proxy, accessible)

## 🚀 Démarrage manuel

### Sur le VPS
```bash
cd /opt/odoo-mcp-proxy
source venv/bin/activate
python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080
```

### En local
```bash
python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8000
```

## 🧪 Tests de déploiement

### Test automatique
```bash
cd tests/
python test_deployment.py
```

### Test manuel
1. Accéder à l'interface web : `http://145.223.102.57/`
2. Configurer une instance Odoo
3. Tester la connexion
4. Générer un token API
5. Vérifier l'URL MCP

## 🔍 Dépannage

### Le serveur ne démarre pas
1. **Vérifier les logs** : `ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && tail -20 logs/mcp_server.log"`
2. **Vérifier les dépendances** : `ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && source venv/bin/activate && pip list | grep mcp"`
3. **Vérifier le port** : `ssh root@145.223.102.57 "netstat -tlnp | grep 8080"`

### Erreur 502 Bad Gateway
1. **Vérifier que le serveur Python fonctionne** : `ssh root@145.223.102.57 "ps aux | grep mcp"`
2. **Vérifier les logs** : `ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && tail -f logs/mcp_server.log"`
3. **Redémarrer le serveur** si nécessaire

### Erreur de connexion Odoo
1. Vérifier les identifiants
2. Vérifier l'URL Odoo
3. Tester la connexion via l'interface

### Problème MCP
1. **Vérifier que le serveur répond** : `curl http://145.223.102.57/health`
2. **Vérifier les headers d'authentification**
3. **Vérifier le token API**

## 📋 Maintenance

### Mise à jour du code
```bash
# Redéployer
./scripts/deploy_mcp_hostinger.sh
```

### Sauvegarde
```bash
# Sauvegarder la base de données
cp /opt/odoo-mcp-proxy/odoo_mcp_proxy.db /backup/

# Sauvegarder les logs
cp -r /opt/odoo-mcp-proxy/logs/ /backup/
```

### Monitoring
```bash
# Vérifier les processus
ps aux | grep mcp

# Vérifier les logs en temps réel
tail -f /opt/odoo-mcp-proxy/logs/mcp_server.log
```

## 🌐 URLs de production

- **Interface web** : `http://145.223.102.57/`
- **API Health** : `http://145.223.102.57/health`
- **MCP Endpoint** : `http://145.223.102.57/mcp`

## 🔑 Utilisation avec OpenAI MCP

1. **Générer un token API** via l'interface web
2. **Utiliser l'URL MCP** : `http://145.223.102.57/mcp`
3. **Ajouter l'authentification** : `Authorization: Bearer YOUR_TOKEN`