// Test Page JavaScript - Odoo MCP Proxy

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('configForm');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const testResultDiv = document.getElementById('testResult');
    const testBtn = document.getElementById('testBtn');
    
    // Configuration du formulaire
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Masquer les divs précédentes
        hideAllResults();
        
        // Récupérer les données du formulaire
        const formData = new FormData(form);
        let odooUrl = formData.get('odooUrl');
        
        // Ajouter https:// si pas présent
        if (odooUrl && !odooUrl.startsWith('http://') && !odooUrl.startsWith('https://')) {
            odooUrl = 'https://' + odooUrl;
        }
        
        const data = {
            odoo_url: odooUrl,
            odoo_db: formData.get('odooDb'),
            odoo_username: formData.get('odooUsername'),
            odoo_password: formData.get('odooPassword')
        };
        
        try {
            // Afficher un indicateur de chargement
            const submitBtn = form.querySelector('button[type="submit"]');
            setButtonLoading(submitBtn, 'Configuration en cours...');
            
            // Envoyer la requête
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Afficher le résultat
                showSuccess(result);
            } else {
                // Afficher l'erreur
                showError(result.detail || 'Erreur inconnue');
            }
            
        } catch (error) {
            console.error('Erreur:', error);
            showError('Erreur de connexion au serveur. Vérifiez que le serveur est accessible.');
        } finally {
            // Restaurer le bouton
            resetButton(submitBtn, '⚡ Générer le token API');
        }
    });

    // Test de connexion
    testBtn.addEventListener('click', async function() {
        hideAllResults();
        
        // Récupérer les données du formulaire
        const formData = new FormData(form);
        let odooUrl = formData.get('odooUrl');
        
        // Ajouter https:// si pas présent
        if (odooUrl && !odooUrl.startsWith('http://') && !odooUrl.startsWith('https://')) {
            odooUrl = 'https://' + odooUrl;
        }
        
        const data = {
            odoo_url: odooUrl,
            odoo_db: formData.get('odooDb'),
            odoo_username: formData.get('odooUsername'),
            odoo_password: formData.get('odooPassword')
        };
        
        // Vérifier que les champs requis sont remplis
        if (!data.odoo_url || !data.odoo_db || !data.odoo_username || !data.odoo_password) {
            showTestResult('Veuillez remplir tous les champs requis pour tester la connexion.', 'error');
            return;
        }
        
        try {
            // Afficher un indicateur de chargement
            setButtonLoading(testBtn, 'Test en cours...');
            
            // Envoyer la requête de test
            const response = await fetch('/api/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showTestResult('✅ Connexion réussie ! Vous pouvez maintenant générer votre token API.', 'success');
            } else {
                showTestResult(`❌ Échec de la connexion : ${result.detail || 'Erreur inconnue'}`, 'error');
            }
            
        } catch (error) {
            console.error('Erreur:', error);
            showTestResult('❌ Erreur de connexion au serveur. Vérifiez que le serveur est accessible.', 'error');
        } finally {
            // Restaurer le bouton
            resetButton(testBtn, '🔍 Tester la connexion');
        }
    });
});

// Fonctions utilitaires
function hideAllResults() {
    document.getElementById('result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('testResult').classList.add('hidden');
}

function showSuccess(result) {
    const apiToken = result.api_token;
    const mcpUrl = result.mcp_url;
    const restUrl = 'http://145.223.102.57/api/odoo/execute';
    
    // Remplir les champs de base
    document.getElementById('apiToken').textContent = apiToken;
    document.getElementById('userId').textContent = result.user_id;
    
    // Mode 1: MCP pour agents IA
    document.getElementById('mcpUrl').textContent = mcpUrl;
    document.getElementById('mcpAuth').textContent = `Authorization: Bearer ${apiToken}`;
    
    // Mode 2: REST API
    document.getElementById('restUrl').textContent = restUrl;
    document.getElementById('restAuth').textContent = `Authorization: Bearer ${apiToken}`;
    
    // Exemple cURL
    const curlExample = `curl -X POST ${restUrl} \\
  -H "Authorization: Bearer ${apiToken}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "res.partner",
    "method": "search_read",
    "domain": "[[\\"is_company\\", \\"=\\", true]]",
    "fields": "name,email,phone",
    "limit": 10
  }'`;
    
    document.getElementById('curlExample').textContent = curlExample;
    
    // Afficher le div de résultat
    document.getElementById('result').classList.remove('hidden');
    
    // Faire défiler vers le résultat
    document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
    
    // Afficher une notification
    showNotification('Configuration réussie !', 'success');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('error').classList.remove('hidden');
    
    // Faire défiler vers l'erreur
    document.getElementById('error').scrollIntoView({ behavior: 'smooth' });
    
    // Afficher une notification
    showNotification('Erreur de configuration', 'error');
}

function showTestResult(message, type) {
    document.getElementById('testMessage').textContent = message;
    document.getElementById('testResult').classList.remove('hidden');
    
    // Changer la classe selon le type
    const testResult = document.getElementById('testResult');
    testResult.className = `card test-result ${type === 'success' ? 'success' : 'error'}`;
    
    // Faire défiler vers le résultat
    testResult.scrollIntoView({ behavior: 'smooth' });
}

function setButtonLoading(button, text) {
    button.disabled = true;
    button.classList.add('loading');
    button.textContent = text;
}

function resetButton(button, text) {
    button.disabled = false;
    button.classList.remove('loading');
    button.textContent = text;
}

// Fonctions pour copier les informations
function copyToken() {
    const token = document.getElementById('apiToken').textContent;
    copyToClipboard(token, 'Token API copié !');
}

function copyMcpUrl() {
    const url = document.getElementById('mcpUrl').textContent;
    copyToClipboard(url, 'URL MCP copiée !');
}

function copyMcpAuth() {
    const auth = document.getElementById('mcpAuth').textContent;
    copyToClipboard(auth, 'Header MCP copié !');
}

function copyRestUrl() {
    const url = document.getElementById('restUrl').textContent;
    copyToClipboard(url, 'URL REST API copiée !');
}

function copyRestAuth() {
    const auth = document.getElementById('restAuth').textContent;
    copyToClipboard(auth, 'Header REST API copié !');
}

function copyCurlExample() {
    const example = document.getElementById('curlExample').textContent;
    copyToClipboard(example, 'Exemple cURL copié !');
}

function copyToClipboard(text, message) {
    if (navigator.clipboard && window.isSecureContext) {
        // Utiliser l'API Clipboard moderne
        navigator.clipboard.writeText(text).then(function() {
            showNotification(message, 'success');
        }).catch(function(err) {
            console.error('Erreur lors de la copie:', err);
            fallbackCopy(text, message);
        });
    } else {
        // Fallback pour les navigateurs plus anciens
        fallbackCopy(text, message);
    }
}

function fallbackCopy(text, message) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification(message, 'success');
    } catch (err) {
        console.error('Erreur lors de la copie:', err);
        showNotification('Erreur lors de la copie', 'error');
    }
    
    document.body.removeChild(textArea);
}

function showNotification(message, type) {
    // Supprimer les notifications existantes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Créer une nouvelle notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Supprimer la notification après 4 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

// Validation en temps réel des champs
document.addEventListener('DOMContentLoaded', function() {
    const requiredFields = document.querySelectorAll('input[required]');
    
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.style.borderColor = 'var(--error-color)';
            } else {
                this.style.borderColor = 'var(--gray-200)';
            }
        });
        
        field.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.style.borderColor = 'var(--gray-200)';
            }
        });
    });
});
