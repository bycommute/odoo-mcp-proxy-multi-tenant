# 🔌 Intégration Make.com (anciennement Integromat)

Ce guide explique comment utiliser **Odoo MCP Proxy** avec **Make.com** pour automatiser vos workflows Odoo.

## 🎯 Pourquoi utiliser cette intégration ?

- ✅ **Simple REST API** - Pas besoin de comprendre MCP
- ✅ **Compatible Make.com** - Module HTTP standard
- ✅ **Toutes les méthodes Odoo** - Lecture, écriture, recherche, création, suppression
- ✅ **Multi-tenant** - Chaque utilisateur a son propre token
- ✅ **Sécurisé** - Authentification par token Bearer

## 📋 Prérequis

1. Un compte sur http://145.223.102.57/test
2. Votre **API Token** généré depuis l'interface
3. Un compte Make.com

## 🚀 Configuration dans Make.com

### Étape 1 : Créer un module HTTP

1. Dans votre scénario Make.com, ajoutez un module **HTTP > Make a request**
2. Configurez comme suit :

**URL :**
```
http://145.223.102.57/api/odoo/execute
```

**Method :**
```
POST
```

**Headers :**
```json
{
  "Authorization": "Bearer VOTRE_API_TOKEN",
  "Content-Type": "application/json"
}
```

### Étape 2 : Exemples de requêtes

#### 1️⃣ Rechercher des partenaires (clients/fournisseurs)

**Body (JSON) :**
```json
{
  "model": "res.partner",
  "method": "search_read",
  "domain": "[[\"is_company\", \"=\", true]]",
  "fields": "name,email,phone,city",
  "limit": 100
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "result": [
      {
        "id": 123,
        "name": "Acme Corp",
        "email": "contact@acme.com",
        "phone": "+33123456789",
        "city": "Paris"
      }
    ]
  },
  "error": null
}
```

---

#### 2️⃣ Rechercher des commandes de vente

**Body (JSON) :**
```json
{
  "model": "sale.order",
  "method": "search_read",
  "domain": "[[\"state\", \"=\", \"sale\"]]",
  "fields": "name,partner_id,amount_total,date_order",
  "limit": 50
}
```

---

#### 3️⃣ Créer un nouveau partenaire

**Body (JSON) :**
```json
{
  "model": "res.partner",
  "method": "create",
  "values": "{\"name\": \"Nouveau Client\", \"email\": \"client@example.com\", \"phone\": \"+33987654321\"}"
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "result": 456
  },
  "error": null
}
```
Le champ `data.result` contient l'ID du nouveau partenaire créé.

---

#### 4️⃣ Mettre à jour un partenaire existant

**Body (JSON) :**
```json
{
  "model": "res.partner",
  "method": "write",
  "ids": "123",
  "values": "{\"phone\": \"+33111222333\", \"city\": \"Lyon\"}"
}
```

---

#### 5️⃣ Lire des enregistrements spécifiques

**Body (JSON) :**
```json
{
  "model": "res.partner",
  "method": "read",
  "ids": "123,456,789",
  "fields": "name,email,phone"
}
```

---

#### 6️⃣ Rechercher des factures

**Body (JSON) :**
```json
{
  "model": "account.move",
  "method": "search_read",
  "domain": "[[\"move_type\", \"=\", \"out_invoice\"], [\"state\", \"=\", \"posted\"]]",
  "fields": "name,partner_id,amount_total,invoice_date,state",
  "limit": 100
}
```

---

#### 7️⃣ Rechercher des produits

**Body (JSON) :**
```json
{
  "model": "product.product",
  "method": "search_read",
  "domain": "[[\"sale_ok\", \"=\", true]]",
  "fields": "name,default_code,list_price,qty_available",
  "limit": 200
}
```

## 📊 Structure des réponses

Toutes les réponses suivent ce format :

```json
{
  "success": true,        // true si succès, false si erreur
  "data": { ... },        // Données retournées par Odoo
  "error": null           // Message d'erreur si success = false
}
```

### En cas d'erreur :

```json
{
  "success": false,
  "data": null,
  "error": "Message d'erreur détaillé"
}
```

## 🔍 Paramètres disponibles

| Paramètre | Type | Requis | Description | Exemple |
|-----------|------|--------|-------------|---------|
| `model` | string | ✅ Oui | Nom du modèle Odoo | `"res.partner"` |
| `method` | string | ✅ Oui | Méthode à exécuter | `"search_read"` |
| `domain` | string | ❌ Non | Filtre de recherche (JSON string) | `"[[\"is_company\", \"=\", true]]"` |
| `fields` | string | ❌ Non | Champs à retourner (virgule) | `"name,email,phone"` |
| `limit` | integer | ❌ Non | Nombre max de résultats | `100` |
| `ids` | string | ❌ Non | IDs des enregistrements (virgule) | `"1,2,3"` |
| `values` | string | ❌ Non | Valeurs pour create/write (JSON string) | `"{\"name\": \"Test\"}"` |

## 🎯 Méthodes Odoo disponibles

| Méthode | Description | Paramètres requis |
|---------|-------------|-------------------|
| `search_read` | Rechercher et lire des enregistrements | `model`, `domain` (optionnel), `fields`, `limit` |
| `search` | Rechercher des IDs seulement | `model`, `domain` (optionnel), `limit` |
| `read` | Lire des enregistrements spécifiques | `model`, `ids`, `fields` (optionnel) |
| `create` | Créer un nouvel enregistrement | `model`, `values` |
| `write` | Mettre à jour des enregistrements | `model`, `ids`, `values` |
| `unlink` | Supprimer des enregistrements | `model`, `ids` |

## 💡 Cas d'usage Make.com

### 1. Synchronisation CRM → Google Sheets
```
Trigger: Webhook (depuis Odoo ou timer)
  ↓
HTTP: Rechercher nouveaux clients dans Odoo
  ↓
Google Sheets: Ajouter lignes
```

### 2. Création automatique de partenaires depuis un formulaire
```
Trigger: Webhook (TypeForm, Google Forms, etc.)
  ↓
HTTP: Créer partenaire dans Odoo
  ↓
Email: Notification de confirmation
```

### 3. Export quotidien des commandes
```
Trigger: Scheduled (tous les jours à 8h)
  ↓
HTTP: Rechercher commandes de la veille
  ↓
Email: Envoyer rapport CSV
```

### 4. Mise à jour des stocks depuis un e-commerce
```
Trigger: Webhook (Shopify, WooCommerce, etc.)
  ↓
HTTP: Mettre à jour produit dans Odoo
  ↓
Slack: Notification
```

## 🛠️ Modèles Odoo les plus utilisés

| Modèle | Description | Champs courants |
|--------|-------------|-----------------|
| `res.partner` | Clients, fournisseurs, contacts | `name`, `email`, `phone`, `city`, `country_id` |
| `sale.order` | Commandes de vente | `name`, `partner_id`, `amount_total`, `state`, `date_order` |
| `product.product` | Produits | `name`, `default_code`, `list_price`, `qty_available` |
| `account.move` | Factures/Notes de crédit | `name`, `partner_id`, `amount_total`, `state`, `invoice_date` |
| `stock.picking` | Bons de livraison | `name`, `partner_id`, `state`, `scheduled_date` |
| `crm.lead` | Opportunités CRM | `name`, `partner_id`, `expected_revenue`, `probability` |
| `project.task` | Tâches projet | `name`, `project_id`, `user_id`, `date_deadline` |

## 🔐 Sécurité

- ✅ Utilisez toujours **HTTPS en production**
- ✅ Ne partagez **jamais** votre token API
- ✅ Générez un **token différent** par intégration
- ✅ Révoqué immédiatement un token compromis

## 📞 Support

- 🌐 Documentation complète : http://145.223.102.57/
- 🧪 Interface de test : http://145.223.102.57/test
- 💬 GitHub : https://github.com/bycommute/odoo-mcp-proxy-multi-tenant

---

**🎉 C'est tout ! Vous pouvez maintenant connecter Make.com à Odoo en quelques clics !**

