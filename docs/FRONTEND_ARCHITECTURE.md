# Architecture Frontend - Odoo MCP Proxy

## 📁 Structure des fichiers

```
frontend/
├── index.html              # Landing page principale (version simplifiée)
├── index_complex.html      # Landing page complète (backup)
├── index_simple.html       # Landing page simplifiée (source)
├── test.html              # Page de configuration/test MCP
├── robots.txt             # SEO - Directives pour les crawlers
├── sitemap.xml            # SEO - Plan du site
├── css/
│   ├── landing.css        # Styles pour la landing page
│   └── test.css          # Styles pour la page de test
├── js/
│   ├── landing.js        # JavaScript pour la landing page
│   └── test.js          # JavaScript pour la page de test
└── use-cases/
    └── support.html      # Cas d'usage : Support client
```

## 🌐 Pages disponibles

### 1. Landing Page (`/`)
**URL :** `http://145.223.102.57/`

**Objectif :** Présenter la solution Odoo MCP Proxy et ses avantages

**Sections :**
- **Navigation** : Header fixe avec liens vers les sections et CTA "Tester maintenant"
- **Hero** : Titre principal avec gradient, description et boutons CTA
- **Fonctionnalités** : Grid de 6 cartes présentant les avantages
- **CTA** : Section d'appel à l'action
- **Footer** : Copyright et liens

**Design :**
- Gradient violet/rose en background
- Navigation fixe avec backdrop blur
- Cards avec hover effects
- Responsive (mobile-first)
- Smooth scrolling pour les ancres

### 2. Page de test (`/test`)
**URL :** `http://145.223.102.57/test`

**Objectif :** Permettre aux utilisateurs de configurer leur instance Odoo et générer un token API

**Fonctionnalités :**
- Formulaire de configuration Odoo (URL, DB, Username, Password)
- Bouton "Tester la connexion" pour vérifier avant de générer
- Génération du token API
- Affichage du token et de l'URL MCP
- Instructions d'utilisation avec ChatGPT
- Boutons de copie pour le token et l'URL

**Navigation :**
- Bouton "Retour à l'accueil" en haut
- Header avec lien vers la landing page

### 3. Cas d'usage : Support client (`/use-cases/support.html`)
**URL :** `http://145.223.102.57/use-cases/support.html`

**Objectif :** Expliquer comment utiliser Odoo MCP pour le support client

**Sections :**
- Hero spécifique au cas d'usage
- Fonctionnalités du support intelligent
- Comment ça marche (3 étapes)
- CTA
- Footer avec navigation

## 🎨 Design System

### Couleurs
```css
--primary-color: #2563eb;       /* Bleu principal */
--primary-hover: #1d4ed8;       /* Bleu hover */
--success-color: #10b981;       /* Vert succès */
--error-color: #ef4444;         /* Rouge erreur */
--warning-color: #f59e0b;       /* Orange warning */

/* Grays */
--gray-50 à --gray-900          /* Échelle de gris */

/* Gradients */
linear-gradient(135deg, #667eea 0%, #764ba2 100%)  /* Gradient principal */
linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)  /* Gradient texte */
```

### Typographie
- **Font** : Inter (Google Fonts)
- **Poids** : 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold), 800 (Extra-Bold)
- **Tailles** :
  - Hero title : 3.5rem (2.5rem mobile)
  - Section title : 2.5rem (2rem mobile)
  - Body : 1rem
  - Large : 1.25rem

### Spacing
```css
--space-1: 0.25rem
--space-2: 0.5rem
--space-4: 1rem
--space-8: 2rem
--space-12: 3rem
--space-16: 4rem
--space-24: 6rem
```

### Shadows
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1)
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1)
```

### Border Radius
```css
--radius: 8px
--radius-lg: 12px
```

## 🔍 SEO Optimisation

### Meta Tags
Chaque page inclut :
- **Title** : Optimisé pour les mots-clés
- **Description** : 150-160 caractères
- **Keywords** : Mots-clés pertinents
- **Author** : Odoo MCP Proxy
- **Robots** : index, follow

### Open Graph (Facebook)
- `og:type` : website
- `og:url` : URL canonique
- `og:title` : Titre optimisé
- `og:description` : Description
- `og:image` : Image de partage

### Twitter Cards
- `twitter:card` : summary_large_image
- `twitter:url` : URL
- `twitter:title` : Titre
- `twitter:description` : Description
- `twitter:image` : Image

### Structured Data (JSON-LD)
- Type : SoftwareApplication
- Name, Description, URL
- ApplicationCategory : BusinessApplication
- Offers (prix)
- Provider

### Fichiers SEO
- **`sitemap.xml`** : Plan du site avec priorités et fréquences de mise à jour
- **`robots.txt`** : Directives pour les crawlers
  - Allow: /
  - Disallow: /test, /api/, /mcp
  - Allow: /use-cases/

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile */
@media (max-width: 768px)

/* Tablet */
@media (max-width: 1024px)
```

### Mobile Optimisations
- Navigation burger menu (à implémenter)
- Hero title réduit (2.5rem)
- Grid en une colonne
- Buttons en colonne
- Footer en colonne

## ⚡ Performance

### Optimisations
1. **Fonts** : Preconnect pour Google Fonts
2. **CSS** : Inline ou fichiers séparés selon la page
3. **JavaScript** : Chargé en fin de body
4. **Images** : Pas d'images lourdes, utilisation d'emojis

### Chargement
- CSS critique inline (version simple)
- JavaScript différé
- Lazy loading (à implémenter pour les images)

## 🚀 Déploiement

### Script de déploiement
```bash
./scripts/deploy_frontend_complete.sh
```

**Actions :**
1. Synchronise les fichiers frontend via rsync
2. Redémarre le serveur Python
3. Teste les endpoints (/, /test, /sitemap.xml, /robots.txt)
4. Affiche les URLs accessibles

### Configuration serveur
Le serveur FastAPI sert les fichiers :
```python
# Static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Pages
@app.get("/")          # Landing page
@app.get("/test")      # Test page
@app.get("/sitemap.xml")
@app.get("/robots.txt")
```

## 🎯 Prochaines étapes

### Court terme
1. ✅ Landing page simple fonctionnelle
2. ✅ Page de test opérationnelle
3. ✅ SEO de base (sitemap, robots.txt)
4. ⏳ Ajouter le menu mobile
5. ⏳ Tester la landing page complexe

### Moyen terme
1. Créer plus de cas d'usage (analytics, automation)
2. Ajouter un système d'authentification
3. Créer un dashboard utilisateur
4. Analytics de l'utilisation

### Long terme
1. Système de comptes multi-utilisateurs
2. Gestion des abonnements (gratuit, pro, enterprise)
3. Documentation interactive
4. Blog et tutoriels

## 📝 Notes

### Version actuelle
- **Landing page** : Version simplifiée (CSS inline)
- **Raison** : Plus rapide à charger, styles intégrés
- **Backup** : Version complexe disponible dans `index_complex.html`

### Navigation
- Le header est **fixe** sur toutes les pages
- Liens vers `/test` depuis la landing page
- Lien retour vers `/` depuis la page de test
- Smooth scrolling pour les ancres

### Compatibilité
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive
- Pas de dépendances externes (sauf Google Fonts)

## 🛠️ Maintenance

### Modifier la landing page
1. Éditer `frontend/index_simple.html`
2. Copier vers `frontend/index.html`
3. Déployer avec `./scripts/deploy_frontend_complete.sh`

### Modifier la page de test
1. Éditer `frontend/test.html`
2. Modifier les styles dans `frontend/css/test.css`
3. Modifier le JavaScript dans `frontend/js/test.js`
4. Déployer

### Ajouter un cas d'usage
1. Créer `frontend/use-cases/nouveau-cas.html`
2. Utiliser `support.html` comme template
3. Ajouter au `sitemap.xml`
4. Ajouter un lien dans la landing page
5. Déployer
