# Configuration MCP pour OpenAI

## 📋 Configuration OpenAI Agent Builder

### Informations de connexion

**URL MCP :** `http://145.223.102.57/mcp`  
**Authentification :** Bearer Token  
**Token :** Généré depuis http://145.223.102.57/test

### Étapes de configuration

1. **Générer votre token API**
   - Allez sur http://145.223.102.57/test
   - Remplissez vos informations Odoo (URL, DB, Username, Password)
   - Cliquez sur "Tester la connexion" pour vérifier
   - Cliquez sur "Générer Token API"
   - Copiez le token affiché

2. **Configurer dans OpenAI**
   - Allez dans Agent Builder
   - Sélectionnez "Add action" ou "Add MCP server"
   - Type: MCP Server (Hosted)
   - URL: `http://145.223.102.57/mcp`
   - Authentication: Bearer Token
   - Token: Collez votre token API

3. **Vérifier la connexion**
   - OpenAI devrait afficher "5 tools available"
   - Si vous voyez "Unable to load tools", vérifiez :
     - Que votre token est correct
     - Que l'URL est exactement `http://145.223.102.57/mcp`
     - Que le type d'authentification est "Bearer Token"

## 🛠️ Outils disponibles

### 1. `search_partners`
Rechercher des partenaires/clients dans Odoo.

**Paramètres :**
- `name` (string, optionnel) : Nom à rechercher
- `limit` (integer, optionnel) : Nombre maximum de résultats (défaut: 10)

**Exemple :**
```
Cherche les clients dont le nom contient "Acme"
```

### 2. `search_products`
Rechercher des produits dans Odoo.

**Paramètres :**
- `name` (string, optionnel) : Nom du produit à rechercher
- `limit` (integer, optionnel) : Nombre maximum de résultats (défaut: 10)

**Exemple :**
```
Trouve les 5 produits les plus chers
```

### 3. `search_invoices`
Rechercher des factures dans Odoo.

**Paramètres :**
- `partner_name` (string, optionnel) : Nom du partenaire pour filtrer
- `limit` (integer, optionnel) : Nombre maximum de résultats (défaut: 10)

**Exemple :**
```
Liste les factures du client "Acme Corp"
```

### 4. `get_partner_details`
Obtenir les détails complets d'un partenaire spécifique.

**Paramètres :**
- `partner_id` (integer, **requis**) : ID du partenaire

**Exemple :**
```
Donne-moi les détails du partenaire ID 123
```

### 5. `execute_odoo_method` 🚀 **UNIVERSEL**
**L'outil le plus puissant** : Exécute n'importe quelle méthode Odoo sur n'importe quel modèle.

**Paramètres :**
- `model` (string, **requis**) : Nom du modèle Odoo (ex: `res.partner`, `product.product`, `sale.order`, `account.move`, `stock.picking`)
- `method` (string, **requis**) : Méthode à exécuter (ex: `search`, `read`, `search_read`, `create`, `write`, `unlink`)
- `args` (array, optionnel) : Arguments positionnels de la méthode
- `kwargs` (object, optionnel) : Arguments nommés (ex: `fields`, `limit`, `offset`, `order`)

**Exemples d'utilisation :**

#### Rechercher des commandes de vente
```
Utilise execute_odoo_method pour chercher les commandes de vente confirmées:
- model: "sale.order"
- method: "search_read"
- args: [[["state", "=", "sale"]]]
- kwargs: {"fields": ["name", "partner_id", "amount_total"], "limit": 10}
```

#### Lire les données d'un produit
```
Utilise execute_odoo_method pour lire le produit ID 42:
- model: "product.product"
- method: "read"
- args: [[42]]
- kwargs: {"fields": ["name", "list_price", "qty_available"]}
```

#### Créer un nouveau contact
```
Utilise execute_odoo_method pour créer un nouveau contact:
- model: "res.partner"
- method: "create"
- args: [[{"name": "Nouveau Client", "email": "client@example.com", "phone": "+33123456789"}]]
```

#### Mettre à jour un contact
```
Utilise execute_odoo_method pour mettre à jour le contact ID 123:
- model: "res.partner"
- method: "write"
- args: [[123], {"phone": "+33987654321"}]
```

#### Rechercher des mouvements de stock
```
Utilise execute_odoo_method pour chercher les réceptions de stock:
- model: "stock.picking"
- method: "search_read"
- args: [[["picking_type_code", "=", "incoming"]]]
- kwargs: {"fields": ["name", "partner_id", "state"], "limit": 5}
```

## 📊 Modèles Odoo les plus utilisés

| Modèle | Description | Exemples de méthodes |
|--------|-------------|----------------------|
| `res.partner` | Clients, Fournisseurs, Contacts | `search_read`, `create`, `write` |
| `product.product` | Produits | `search_read`, `read`, `write` |
| `sale.order` | Commandes de vente | `search_read`, `read`, `create` |
| `purchase.order` | Commandes d'achat | `search_read`, `read` |
| `account.move` | Factures, Écritures comptables | `search_read`, `read` |
| `account.payment` | Paiements | `search_read`, `create` |
| `stock.picking` | Transferts de stock | `search_read`, `read` |
| `stock.quant` | Stock disponible | `search_read` |
| `crm.lead` | Opportunités | `search_read`, `create`, `write` |
| `project.project` | Projets | `search_read` |
| `project.task` | Tâches | `search_read`, `create` |
| `hr.employee` | Employés | `search_read` |

## 🔍 Syntaxe de domaine Odoo

Pour les recherches, Odoo utilise une syntaxe de domaine spécifique :

```python
[
  ["field_name", "operator", value]
]
```

**Opérateurs courants :**
- `=` : égal
- `!=` : différent
- `>`, `>=`, `<`, `<=` : comparaison
- `like`, `ilike` : contient (ilike = insensible à la casse)
- `in`, `not in` : dans une liste
- `=?` : égal ou null

**Combinaisons :**
- `|` : OU logique
- `&` : ET logique (par défaut)

**Exemples :**
```python
# Partenaires dont le nom contient "Acme"
[["name", "ilike", "Acme"]]

# Produits avec prix > 100 ET type = "product"
[["list_price", ">", 100], ["type", "=", "product"]]

# Commandes en état "sale" OU "done"
["|", ["state", "=", "sale"], ["state", "=", "done"]]
```

## 💡 Exemples de prompts pour ChatGPT

### Recherche simple
```
Liste-moi les 10 derniers clients créés
```

### Analyse de données
```
Donne-moi un résumé des commandes de vente du mois dernier avec le montant total
```

### Opérations complexes
```
Utilise execute_odoo_method pour:
1. Chercher tous les produits en rupture de stock
2. Créer une liste avec nom et quantité disponible
3. Trie par nom
```

### Création de données
```
Crée un nouveau contact pour l'entreprise "TechCorp":
- Nom: TechCorp
- Email: contact@techcorp.com
- Téléphone: +33123456789
- Type: Société
```

### Mise à jour de données
```
Mets à jour le téléphone du client ID 456 avec le numéro +33987654321
```

## 🚨 Troubleshooting

### Erreur : "Unable to load tools"

**Causes possibles :**
1. URL incorrecte → Vérifiez que c'est bien `http://145.223.102.57/mcp`
2. Token invalide → Générez un nouveau token
3. Type d'authentification incorrect → Utilisez "Bearer Token"

**Solution :**
1. Régénérez un token sur http://145.223.102.57/test
2. Supprimez et recréez la connexion MCP dans OpenAI
3. Vérifiez les logs du serveur

### Erreur : "Authentication failed"

**Cause :** Token expiré ou invalide

**Solution :**
1. Générez un nouveau token
2. Mettez à jour la configuration dans OpenAI

### Erreur : "Model not found" ou "Method not found"

**Cause :** Modèle ou méthode Odoo inexistant

**Solution :**
1. Vérifiez le nom du modèle (sensible à la casse)
2. Vérifiez que le module Odoo est installé
3. Consultez la liste des modèles disponibles

## 📚 Ressources

- **Documentation Odoo ORM** : https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html
- **Documentation MCP** : https://modelcontextprotocol.io/
- **GitHub du projet** : https://github.com/bycommute/odoo-mcp-proxy-multi-tenant

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du serveur
2. Testez votre connexion Odoo sur http://145.223.102.57/test
3. Ouvrez une issue sur GitHub

---

**Configuration testée et validée** ✅  
**5 outils disponibles** | **Accès complet à Odoo** | **Multi-tenant**
