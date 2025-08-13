# 🤖 Verbiage - Chat GPT avec Outils › L1-2

Une application de chat en terminal utilisant GPT avec support d'outils comme la recherche web.

## ✨ Fonctionnalités

- **Chat interactif** avec GPT-4 en terminal
- **Outils intégrés** comme `web_search_preview` pour la recherche web
- **Gestion de conversations** avec sauvegarde automatique
- **Interface riche** avec coloration syntaxique et markdown
- **Historique persistant** des conversations en JSON

## 🚀 Installation

### Méthode recommandée avec pipx
```bash
pipx install verbiage
```

### Configuration initiale
1. Créez le dossier de configuration :
```bash
mkdir -p ~/.config/verbiage
```

2. Éditez le fichier de configuration :
```bash
nano ~/.config/verbiage/config.json
```

3. Ajoutez votre clé OpenRouter et les paramètres :
```json
{
  "api_key": "votre-clé-openrouter",
  "model": "deepseek/deepseek-chat-v3-0324:free",
  "conversations_dir": "~/.config/verbiage/conversations",
  "agents_dir": "~/.config/verbiage/agents",
  "default_agent": "assistant"
}
```

## 🎯 Utilisation
Après installation :
```bash
verbiage
```

## Pour les développeurs
Pour contribuer ou développer localement :

```bash
git clone https://github.com/votre-utilisateur/verbiage.git
cd verbiage

# Installation en mode développement avec pipx
pipx install -e .

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `/new` | Créer une nouvelle conversation |
| `/load <id>` | Charger une conversation existante |
| `/list` | Lister toutes les conversations |
| `/help` | Afficher l'aide |
| `/quit` | Quitter l'application |

### Exemple d'utilisation

```
🤖 Verbiage - Chat GPT avec Outils

Votre message: Quelles sont les dernières nouvelles sur l'IA aujourd'hui ?

🤖 Assistant:
Je vais chercher les dernières nouvelles sur l'IA pour vous...

[Contenu de la réponse avec recherche web]

🔧 Outils utilisés: web_search_preview

[08/01/2025 14:31] Votre message: ⬅️ Format de date amélioré + navigation avec flèches

💡 Ctrl+J pour nouvelle ligne, Enter pour envoyer

                                            ┌─ 👤 Vous #2 ─────────────────┐
                                            │ Message multi-ligne          │
                                            │ avec plusieurs paragraphes   │
                                            └──────────────────────────────┘

┌─ 🤖 Assistant #3 ──────────────────────────────────────────────────────────┐
│ Voici ma réponse avec recherche web...                                     │
└─────────────────────────────────────────────────────────────────────────────┘
🔧 Outils utilisés: web_search_preview
📚 Sources:
  [1] Titre de la source - https://example.com
```

## 📁 Structure du projet

```
verbiage/
├── src/
│   └── verbiage.py      # Module principal
├── conversations/       # Conversations sauvegardées (JSON)
├── requirements.txt     # Dépendances Python
├── start.py             # Script de lancement
├── .env.example        # Configuration d'exemple
├── venv/               # Environnement virtuel (généré)
└── README.md           # Cette documentation
```

## 🛠️ Format des conversations

Les conversations sont sauvegardées au format JSON dans le dossier `conversations/` :

```json
{
  "id": "20250108_143022",
  "title": "Recherche sur l'IA",
  "messages": [
    {
      "role": "user",
      "content": "Quelles sont les nouvelles sur l'IA ?",
      "timestamp": "2025-01-08T14:30:22.123456",
      "tools_used": null
    },
    {
      "role": "assistant",
      "content": "Voici les dernières nouvelles...",
      "timestamp": "2025-01-08T14:30:25.789012",
      "tools_used": ["web_search_preview"]
    }
  ],
  "created_at": "2025-01-08T14:30:22.120000",
  "updated_at": "2025-01-08T14:30:25.790000"
}
```

## 🔧 Configuration

### Variables d'environnement

- `OPENAI_API_KEY` : Clé API OpenAI (obligatoire)

### Outils disponibles

Actuellement, l'application supporte :
- **web_search_preview** : Recherche d'informations en temps réel sur le web

### Améliorations interface
- **Navigation avec flèches** : Utilisez ← → pour naviguer dans votre texte
- **Historique des commandes** : Utilisez ↑ ↓ pour parcourir l'historique
- **Format de date lisible** : `[08/01/2025 14:31]` au lieu de `[20250108_143107]`
- **Saisie multi-ligne** : Ctrl+Enter pour nouvelle ligne, Enter pour envoyer
- **Gestion des messages** : Modifier, supprimer, annuler les messages
- **Système d'agents** : Agents prédéfinis (assistant, developer, researcher...)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Résolution de problèmes

### Erreur: "OPENAI_API_KEY non définie"
Vérifiez que votre clé API est configurée :
```bash
echo $OPENAI_API_KEY
# ou vérifiez le fichier .env
```

### Erreur: "Module non trouvé"
Réinstallez les dépendances :
```bash
pip install -r requirements.txt
```

### L'API responses.create ne fonctionne pas
L'application basculera automatiquement vers l'API standard `chat.completions`.

## 🎨 Interface

L'application utilise Rich pour une interface colorée :
- Messages utilisateur en bleu
- Réponses assistant en vert avec formatage Markdown
- Indicateurs d'outils utilisés
- Gestion interactive des conversations

---

**Verbiage** - Chat GPT avec outils en terminal ! 🤖
