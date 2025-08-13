# 🤖 Verbiage - Chat GPT avec Outils › L1-2

Une application de chat en terminal utilisant GPT avec support d'outils comme la recherche web.

## ✨ Fonctionnalités

- **Chat interactif** avec tout les models disponibles avec OpenRouter
- **Outils intégrés** comme la recherche web
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
git clone https://github.com/valorun/verbiage.git
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

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Verbiage** - Chat GPT avec outils en terminal ! 🤖
