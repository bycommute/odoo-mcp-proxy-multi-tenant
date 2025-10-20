#!/bin/bash

# Script de configuration HTTPS avec Let's Encrypt - Odoo MCP Proxy
# Usage: ./setup_https.sh <votre-domaine.com>

set -e

# Vérifier que le domaine est fourni
if [ -z "$1" ]; then
    echo "❌ Erreur: Veuillez fournir un nom de domaine"
    echo "Usage: ./setup_https.sh votre-domaine.com"
    exit 1
fi

DOMAIN=$1
HOST="145.223.102.57"
USER="root"
PASSWORD="1029KLll,ndlkn"

echo "🔒 Configuration HTTPS pour $DOMAIN"
echo "=================================================="

# Vérifier que le domaine pointe bien vers le serveur
echo "📡 Vérification DNS..."
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)
if [ "$DOMAIN_IP" != "$HOST" ]; then
    echo "⚠️  Attention: Le domaine $DOMAIN pointe vers $DOMAIN_IP au lieu de $HOST"
    echo "   Assurez-vous que votre DNS est correctement configuré avant de continuer"
    read -p "   Continuer quand même ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installation de Certbot sur le serveur..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$HOST" << 'EOF'
# Installer Certbot et le plugin Nginx
apt-get update
apt-get install -y certbot python3-certbot-nginx

echo "✅ Certbot installé"
EOF

echo "⚙️  Configuration de Nginx pour $DOMAIN..."

# Créer la configuration Nginx avec le domaine
cat > /tmp/nginx_ssl.conf << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirection HTTP vers HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
    
    # Location pour Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # Les certificats SSL seront ajoutés par Certbot
    
    # Sécurité SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    
    # Headers de sécurité
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Taille max des uploads
    client_max_body_size 100M;
    
    # Logs
    access_log /var/log/nginx/odoo-mcp-access.log;
    error_log /var/log/nginx/odoo-mcp-error.log;
    
    # Proxy vers l'application Python
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_EOF

# Envoyer la config sur le serveur
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /tmp/nginx_ssl.conf "$USER@$HOST:/etc/nginx/sites-available/odoo-mcp"

echo "🔧 Activation de la configuration..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$HOST" << EOF
# Créer le lien symbolique
ln -sf /etc/nginx/sites-available/odoo-mcp /etc/nginx/sites-enabled/odoo-mcp

# Supprimer la config par défaut si elle existe
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Recharger Nginx
systemctl reload nginx

echo "✅ Nginx configuré"
EOF

echo "🔐 Génération du certificat SSL avec Let's Encrypt..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$HOST" << EOF
# Obtenir le certificat SSL
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Configurer le renouvellement automatique
systemctl enable certbot.timer
systemctl start certbot.timer

echo "✅ Certificat SSL installé"
EOF

echo ""
echo "🎉 Configuration HTTPS terminée !"
echo "=================================================="
echo ""
echo "✅ Votre site est maintenant accessible en HTTPS :"
echo "   🌐 https://$DOMAIN"
echo ""
echo "📝 Notes importantes :"
echo "   • Le certificat est valide 90 jours"
echo "   • Le renouvellement automatique est activé"
echo "   • HTTP redirige automatiquement vers HTTPS"
echo ""
echo "🧪 Test de la configuration :"
echo "   curl -I https://$DOMAIN"
echo ""
echo "🔄 Mettre à jour l'URL MCP dans l'application :"
echo "   Modifier app/api/config.py pour utiliser https://$DOMAIN/mcp"
echo ""
