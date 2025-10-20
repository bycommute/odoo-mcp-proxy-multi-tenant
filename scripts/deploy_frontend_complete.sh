#!/bin/bash

# Script de déploiement complet du frontend - Odoo MCP Proxy
# Ce script déploie la nouvelle architecture frontend avec landing page et cas d'usage

set -e

# Configuration
HOST="145.223.102.57"
USER="root"
PASSWORD="1029KLll,ndlkn"
REMOTE_DIR="/opt/odoo-mcp-proxy"
LOCAL_FRONTEND_DIR="frontend"

echo "🚀 Déploiement du frontend complet - Odoo MCP Proxy"
echo "=================================================="

# Vérifier que le dossier frontend existe
if [ ! -d "$LOCAL_FRONTEND_DIR" ]; then
    echo "❌ Erreur: Le dossier frontend n'existe pas"
    exit 1
fi

echo "📁 Synchronisation des fichiers frontend..."

# Synchroniser tous les fichiers frontend
sshpass -p "$PASSWORD" rsync -avz --delete \
    --exclude="*.log" \
    --exclude=".DS_Store" \
    --exclude="node_modules" \
    "$LOCAL_FRONTEND_DIR/" \
    "$USER@$HOST:$REMOTE_DIR/frontend/"

echo "✅ Fichiers frontend synchronisés"

echo "🔄 Redémarrage du serveur..."

# Redémarrer le serveur
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$HOST" << 'EOF'
cd /opt/odoo-mcp-proxy

# Arrêter le serveur existant
pkill -f "python.*mcp_multi_tenant_server" || true
sleep 2

# Activer l'environnement virtuel et redémarrer
source venv/bin/activate
nohup python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080 > logs/mcp_server.log 2>&1 &
echo "Server restarted"

# Attendre un peu et tester
sleep 5
curl -f http://localhost:8080/health && echo "Health check OK" || echo "Health check failed"
EOF

echo "🧪 Test de la nouvelle architecture..."

# Tester les nouvelles pages
echo "Test de la landing page..."
curl -f http://$HOST/ > /dev/null && echo "✅ Landing page accessible" || echo "❌ Landing page inaccessible"

echo "Test de la page de test..."
curl -f http://$HOST/test > /dev/null && echo "✅ Page de test accessible" || echo "❌ Page de test inaccessible"

echo "Test du sitemap..."
curl -f http://$HOST/sitemap.xml > /dev/null && echo "✅ Sitemap accessible" || echo "❌ Sitemap inaccessible"

echo "Test du robots.txt..."
curl -f http://$HOST/robots.txt > /dev/null && echo "✅ Robots.txt accessible" || echo "❌ Robots.txt inaccessible"

echo ""
echo "🎉 Déploiement terminé !"
echo "========================"
echo "🌐 Landing page: http://$HOST/"
echo "🧪 Page de test: http://$HOST/test"
echo "📄 Sitemap: http://$HOST/sitemap.xml"
echo "🤖 Robots.txt: http://$HOST/robots.txt"
echo ""
echo "✨ Nouvelle architecture déployée avec succès !"
