#!/bin/bash
set -e

# Variables de connexion SSH
VPS_USER="root"
VPS_HOST="145.223.102.57"
VPS_PASS="1029KLll,ndlkn"
APP_DIR="/opt/odoo-mcp-proxy"

echo "🚀 Déploiement MCP Multi-Tenant sur Hostinger VPS"
echo "================================================="

# 1. Créer le package de déploiement
echo "📦 1. Création du package de déploiement..."
cd "/Users/quentinpro/Desktop/Odoo MCP Proxy Multi-Tenant"

# Supprimer l'ancien package
rm -f odoo-mcp-proxy-mcp.zip

# Créer le nouveau package
zip -r odoo-mcp-proxy-mcp.zip \
    app/ \
    frontend/ \
    requirements.txt \
    docs/ \
    scripts/ \
    tests/ \
    .env.example \
    .gitignore \
    README.md \
    -x "*.pyc" "__pycache__/*" "*.db" "venv/*" "logs/*" "*.log" "test_*.py" "debug_*.py"

echo "✅ Package créé: odoo-mcp-proxy-mcp.zip"

# 2. Envoyer le package sur le VPS
echo "📤 2. Envoi du package sur le VPS..."
sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no odoo-mcp-proxy-mcp.zip "$VPS_USER@$VPS_HOST:/tmp/" || {
    echo "❌ Erreur lors de l'envoi du package"
    exit 1
}

# 3. Déployer sur le VPS
echo "🔄 3. Déploiement sur le VPS..."
sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "
    echo '📁 3.1. Arrêt des services existants...'
    pkill -f 'python.*mcp' || true
    pkill -f 'python.*app.main' || true
    sleep 2
    
    echo '📁 3.2. Sauvegarde de l\'ancienne version...'
    if [ -d '$APP_DIR' ]; then
        mv $APP_DIR ${APP_DIR}_backup_\$(date +%Y%m%d_%H%M%S) || true
    fi
    
    echo '📁 3.3. Création du nouveau répertoire...'
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    echo '📁 3.4. Extraction du package...'
    unzip -o /tmp/odoo-mcp-proxy-mcp.zip
    rm /tmp/odoo-mcp-proxy-mcp.zip
    
    echo '📁 3.5. Installation des dépendances...'
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo '📁 3.6. Configuration de la base de données...'
    source venv/bin/activate
    python -c 'from app.core.database import init_db; init_db()'
    
    echo '📁 3.7. Démarrage du serveur MCP Streamable HTTP...'
    nohup python app/mcp_streamable_wrapper.py --host=0.0.0.0 --port=8080 > logs/mcp_server.log 2>&1 &
    
    echo '⏳ 3.8. Attente du démarrage...'
    sleep 5
    
    echo '🧪 3.9. Test du serveur...'
    curl -f http://localhost:8080/health || {
        echo '❌ Le serveur ne répond pas'
        exit 1
    }
    
    echo '✅ Déploiement terminé avec succès !'
"

# 4. Test final
echo "🧪 4. Test final du déploiement..."
sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "
    echo 'Test de l\'API Health...'
    curl -s http://localhost:8080/health | grep -q 'healthy' || {
        echo '❌ API Health ne répond pas correctement'
        exit 1
    }
    
    echo 'Test de l\'interface web...'
    curl -s http://localhost:8080/ | grep -q 'Odoo MCP' || {
        echo '❌ Interface web ne répond pas correctement'
        exit 1
    }
    
    echo '✅ Tous les tests sont passés !'
"

echo ""
echo "🎉 Déploiement MCP Multi-Tenant terminé avec succès !"
echo "🌐 Interface web: http://$VPS_HOST"
echo "🔧 API Health: http://$VPS_HOST/health"
echo "🤖 MCP Endpoint: http://$VPS_HOST/mcp"
echo ""
echo "📋 Pour utiliser avec OpenAI MCP:"
echo "   URL: http://$VPS_HOST/mcp"
echo "   Headers: Authorization: Bearer YOUR_API_TOKEN"
