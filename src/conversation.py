#!/usr/bin/env python3
"""
Module de gestion des conversations pour Verbiage
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationManager:
    """Gestionnaire des conversations avec persistance en JSON"""

    def __init__(self, conversations_dir: str = "conversations"):
        self.conversations_dir = Path(conversations_dir)
        self.conversations_dir.mkdir(exist_ok=True)
        self.current_conversation: Optional[Dict[str, Any]] = None

    def create_new_conversation(self, first_message: str) -> Dict[str, Any]:
        """Créer une nouvelle conversation"""
        timestamp = datetime.now()
        conversation_id = timestamp.strftime("%Y%m%d_%H%M%S")

        conversation = {
            "id": conversation_id,
            "title": first_message[:50] if len(first_message) > 50 else first_message,
            "messages": [],
            "created_at": timestamp.isoformat(),
            "updated_at": timestamp.isoformat(),
        }

        self.current_conversation = conversation
        return conversation

    def add_message(
        self,
        role: str,
        content: str,
        tools_used: Optional[List[str]] = None,
        sources: Optional[List[Dict]] = None,
    ) -> None:
        """Ajouter un message à la conversation courante"""
        if not self.current_conversation:
            raise ValueError("Aucune conversation active")

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tools_used": tools_used or [],
            "sources": sources or [],
        }

        self.current_conversation["messages"].append(message)
        self.current_conversation["updated_at"] = datetime.now().isoformat()

    def save_conversation(self) -> None:
        """Sauvegarder la conversation courante"""
        if not self.current_conversation:
            return

        filename = f"conversation_{self.current_conversation['id']}.json"
        filepath = self.conversations_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_conversation, f, indent=2, ensure_ascii=False)

    def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Charger une conversation existante"""
        filename = f"conversation_{conversation_id}.json"
        filepath = self.conversations_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            conversation = json.load(f)

        self.current_conversation = conversation
        return conversation

    def list_conversations(self) -> List[Dict[str, str]]:
        """Lister toutes les conversations disponibles"""
        conversations = []

        for filepath in self.conversations_dir.glob("conversation_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations.append(
                        {
                            "id": data["id"],
                            "title": data["title"],
                            "created_at": data["created_at"],
                            "message_count": len(data["messages"]),
                        }
                    )
            except (json.JSONDecodeError, KeyError):
                continue

        # Trier par date de création (plus récent en premier)
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations

    def delete_last_message(self) -> bool:
        """Supprimer le dernier message de la conversation"""
        if not self.current_conversation or not self.current_conversation["messages"]:
            return False

        self.current_conversation["messages"].pop()
        self.current_conversation["updated_at"] = datetime.now().isoformat()
        return True

    def delete_message(self, message_index: int) -> bool:
        """Supprimer un message par son index (1-based)"""
        if not self.current_conversation:
            return False

        messages = self.current_conversation["messages"]
        if message_index < 1 or message_index > len(messages):
            return False

        messages.pop(message_index - 1)
        self.current_conversation["updated_at"] = datetime.now().isoformat()
        return True

    def edit_message(self, message_index: int, new_content: str) -> bool:
        """Modifier le contenu d'un message par son index (1-based)"""
        if not self.current_conversation:
            return False

        messages = self.current_conversation["messages"]
        if message_index < 1 or message_index > len(messages):
            return False

        messages[message_index - 1]["content"] = new_content
        messages[message_index - 1]["timestamp"] = datetime.now().isoformat()
        self.current_conversation["updated_at"] = datetime.now().isoformat()
        return True

    def truncate_history(self, message_index: int) -> bool:
        """Tronquer l'historique après le message numéro n (1-based)"""
        if not self.current_conversation:
            return False
        msgs = self.current_conversation["messages"]
        if message_index < 1 or message_index > len(msgs):
            return False
        self.current_conversation["messages"] = msgs[:message_index]
        self.current_conversation["updated_at"] = datetime.now().isoformat()
        return True

    def get_message(self, message_index: int) -> Optional[Dict]:
        """Obtenir un message par son index (1-based)"""
        if not self.current_conversation:
            return None

        messages = self.current_conversation["messages"]
        if message_index < 1 or message_index > len(messages):
            return None

        return messages[message_index - 1]

    def get_message_count(self) -> int:
        """Obtenir le nombre de messages dans la conversation courante"""
        if not self.current_conversation:
            return 0
        return len(self.current_conversation["messages"])
