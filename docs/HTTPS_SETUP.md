# Guide de configuration HTTPS pour Odoo MCP Proxy

## 🎯 Objectif

Mettre en place un nom de domaine personnalisé avec un certificat SSL/HTTPS gratuit (Let's Encrypt) pour sécuriser votre installation Odoo MCP Proxy.

## 📋 Prérequis

- Un serveur VPS accessible (votre Hostinger : `145.223.102.57`)
- Un nom de domaine (acheté chez OVH, Gandi, Namecheap, etc.)
- Accès SSH au serveur

## 🌐 Étape 1 : Configuration DNS

### Option A : Sous-domaine existant

Si vous avez déjà un domaine (ex: `mon-entreprise.com`), créez un sous-domaine :

1. Connectez-vous à votre registrar (OVH, Gandi, etc.)
2. Allez dans la gestion DNS
3. Ajoutez un enregistrement de type **A** :

```
Type: A
Nom: odoo-mcp (ou mcp, ou n'importe quel nom)
Valeur: 145.223.102.57
TTL: 3600 (ou Auto)
```

Résultat : `odoo-mcp.mon-entreprise.com` → `145.223.102.57`

### Option B : Nouveau domaine

1. Achetez un domaine chez un registrar (5-15€/an)
2. Configurez les DNS pour pointer vers votre serveur :

```
Type: A
Nom: @ (racine du domaine)
Valeur: 145.223.102.57
TTL: 3600
```

### Vérification DNS

Attendez que la propagation DNS soit terminée (5 min à 48h, généralement 1h) :

```bash
# Vérifier que le domaine pointe vers votre serveur
dig +short votre-domaine.com

# Devrait afficher : 145.223.102.57
```

Ou utilisez un outil en ligne : https://dnschecker.org/

## 🔒 Étape 2 : Installation HTTPS (automatique)

### Méthode automatique (recommandée)

Utilisez le script fourni :

```bash
cd /Users/quentinpro/Desktop/Odoo\ MCP\ Proxy\ Multi-Tenant/
./scripts/setup_https.sh votre-domaine.com
```

**Ce script va :**
1. ✅ Vérifier la configuration DNS
2. ✅ Installer Certbot sur le serveur
3. ✅ Configurer Nginx avec SSL
4. ✅ Générer le certificat Let's Encrypt
5. ✅ Activer la redirection HTTP → HTTPS
6. ✅ Configurer le renouvellement automatique

**Durée : 2-3 minutes**

### Méthode manuelle

Si vous préférez faire manuellement :

#### 1. Installer Certbot sur le serveur

```bash
ssh root@145.223.102.57
apt-get update
apt-get install -y certbot python3-certbot-nginx
```

#### 2. Configurer Nginx

Créez `/etc/nginx/sites-available/odoo-mcp` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com;
    
    # Certificats SSL (seront ajoutés par Certbot)
    
    # Sécurité SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    
    # Headers de sécurité
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. Activer la configuration

```bash
ln -s /etc/nginx/sites-available/odoo-mcp /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 4. Obtenir le certificat SSL

```bash
certbot --nginx -d votre-domaine.com --agree-tos --email votre@email.com
```

#### 5. Activer le renouvellement automatique

```bash
systemctl enable certbot.timer
systemctl start certbot.timer
```

## 🔧 Étape 3 : Mettre à jour l'application

### Modifier l'URL MCP dans le code

Éditez `app/api/config.py` (ou `app/mcp_multi_tenant_server.py`) :

```python
# Remplacer
"mcp_url": f"http://145.223.102.57/mcp"

# Par
"mcp_url": f"https://votre-domaine.com/mcp"
```

### Redéployer l'application

```bash
# Copier le fichier modifié
sshpass -p "1029KLll,ndlkn" scp app/mcp_multi_tenant_server.py root@145.223.102.57:/opt/odoo-mcp-proxy/app/

# Redémarrer le serveur
sshpass -p "1029KLll,ndlkn" ssh root@145.223.102.57 "cd /opt/odoo-mcp-proxy && pkill -f python && source venv/bin/activate && nohup python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080 > logs/mcp_server.log 2>&1 &"
```

## ✅ Étape 4 : Vérification

### Test du certificat SSL

```bash
# Test basique
curl -I https://votre-domaine.com

# Test détaillé du certificat
openssl s_client -connect votre-domaine.com:443 -servername votre-domaine.com

# Test avec SSL Labs (recommandé)
# Ouvrir : https://www.ssllabs.com/ssltest/analyze.html?d=votre-domaine.com
```

### Test de l'application

1. **Landing page** : `https://votre-domaine.com/`
2. **Page de test** : `https://votre-domaine.com/test`
3. **Health check** : `https://votre-domaine.com/health`
4. **MCP endpoint** : `https://votre-domaine.com/mcp`

### Vérifier la redirection HTTP → HTTPS

```bash
curl -I http://votre-domaine.com
# Devrait afficher : Location: https://votre-domaine.com/
```

## 🔄 Renouvellement automatique

### Vérifier que le renouvellement est configuré

```bash
ssh root@145.223.102.57
systemctl status certbot.timer
```

### Test du renouvellement

```bash
certbot renew --dry-run
```

### Renouvellement manuel (si nécessaire)

```bash
certbot renew
systemctl reload nginx
```

## 🛡️ Sécurité supplémentaire

### Headers de sécurité recommandés

Nginx est déjà configuré avec :
- ✅ HSTS (Strict-Transport-Security)
- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ X-XSS-Protection

### Firewall (optionnel mais recommandé)

```bash
ssh root@145.223.102.57

# Installer UFW
apt-get install -y ufw

# Autoriser SSH, HTTP et HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Activer le firewall
ufw --force enable
```

## 🚨 Troubleshooting

### Problème 1 : "DNS not pointing to server"

**Cause** : Le DNS n'est pas encore propagé ou mal configuré

**Solution** :
```bash
# Vérifier le DNS
dig +short votre-domaine.com

# Si ça ne pointe pas vers 145.223.102.57, attendre ou vérifier la config DNS
```

### Problème 2 : "Certificate generation failed"

**Cause** : Nginx n'est pas accessible sur le port 80 ou le domaine ne pointe pas vers le serveur

**Solution** :
```bash
# Vérifier que Nginx écoute sur le port 80
netstat -tlnp | grep :80

# Vérifier que le domaine est accessible
curl -I http://votre-domaine.com
```

### Problème 3 : "502 Bad Gateway"

**Cause** : L'application Python n'est pas démarrée

**Solution** :
```bash
ssh root@145.223.102.57
cd /opt/odoo-mcp-proxy
source venv/bin/activate
python app/mcp_multi_tenant_server.py --host=0.0.0.0 --port=8080
```

### Problème 4 : "Mixed content warnings"

**Cause** : L'application charge des ressources en HTTP au lieu de HTTPS

**Solution** : Vérifier que toutes les URLs dans le code utilisent des chemins relatifs ou HTTPS

## 📊 Coûts

| Élément | Coût |
|---------|------|
| Nom de domaine | 5-15€/an |
| Certificat SSL | **Gratuit** (Let's Encrypt) |
| Serveur VPS | Déjà payé (Hostinger) |
| **TOTAL** | **5-15€/an** |

## 🎓 Ressources

- **Let's Encrypt** : https://letsencrypt.org/
- **Certbot** : https://certbot.eff.org/
- **SSL Labs Test** : https://www.ssllabs.com/ssltest/
- **DNS Checker** : https://dnschecker.org/

## 📝 Résumé

1. **Acheter un domaine** : 5-15€/an
2. **Configurer le DNS** : 5 minutes
3. **Attendre la propagation** : 1 heure
4. **Lancer le script** : `./scripts/setup_https.sh votre-domaine.com`
5. **Mettre à jour l'URL dans le code** : 2 minutes
6. **Tester** : 5 minutes

**Total : ~1h30 de travail pour un site HTTPS professionnel !**
