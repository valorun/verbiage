#!/usr/bin/env python3
"""
Verbiage - Chat GPT avec outils en terminal
Application principale
"""

import sys

from openai import OpenAI

import sys
from openai import OpenAI

from agents import AgentManager
from api_utils import extract_sources_from_response
from config import config
from conversation import ConversationManager
from ui import VerbiageUI

# Nouveaux imports
from src.command_handlers import (
    handle_quit, handle_clear, handle_new, handle_list,
    handle_load, handle_undo, handle_delete, handle_edit,
    handle_help, handle_agents, handle_agent, handle_create_agent,
    handle_raw, handle_unknown
)
from src.api_interface import send_with_responses_api, send_with_chat_api


class VerbiageChat:
    """Application principale de chat GPT avec outils"""

    def refresh_display(self):
        """Effacer et réafficher en-tête, astuces et historique"""
        # effacer l'écran
        self.ui.clear()
        # en-tête agent
        current_agent = self.agent_manager.get_current_agent()
        if current_agent:
            self.ui.print_info(
                f"Agent actuel: {current_agent.name} - {current_agent.description}"
            )
        # astuces saisie
        self.ui.print_info("💡 Ctrl+J pour nouvelle ligne, Enter pour envoyer")
        # historique
        self.ui.display_conversation_history(
            self.conversation_manager.current_conversation
        )

    def __init__(self):
        self.ui = VerbiageUI()
        self.conversation_manager = ConversationManager(config.conversations_dir)
        self.agent_manager = AgentManager()

        # Validation de la configuration
        is_valid, errors = config.validate()
        if not is_valid:
            self.ui.print_error("Erreur de configuration:")
            for error in errors:
                self.ui.print_info(f"  - {error}")
            sys.exit(1)

        self.client = OpenAI(api_key=config.openai_api_key)
        self.available_tools = [{"type": "web_search_preview"}]
        self.debug = config.debug_mode

        self.cmd_handlers = {
            "/quit": handle_quit,
            "/clear": handle_clear,
            "/new": handle_new,
            "/list": handle_list,
            "/load": handle_load,
            "/undo": handle_undo,
            "/delete": handle_delete,
            "/edit": handle_edit,
            "/help": handle_help,
            "/agents": handle_agents,
            "/agent": handle_agent,
            "/create-agent": handle_create_agent,
            "/raw": handle_raw,
        }

    def send_message_to_gpt(self, message: str) -> tuple[str, list[str], list[dict]]:
        if config.use_responses_api:
            try:
                return send_with_responses_api(
                    self.client, 
                    self.agent_manager, 
                    self.conversation_manager, 
                    message
                )
            except Exception as e:
                if self.debug:
                    self.ui.print_warning(f"API responses échouée, fallback: {e}")
                return send_with_chat_api(
                    self.client, 
                    self.agent_manager, 
                    self.conversation_manager, 
                    message
                )
        else:
            return send_with_chat_api(
                self.client, 
                self.agent_manager, 
                self.conversation_manager, 
                message
            )


    def handle_command(self, command: str) -> bool:
        command = command.lower().strip()
        cmd = command.split()[0]
        handler = self.cmd_handlers.get(cmd, handle_unknown)
        return handler(self, command)

    def run(self) -> None:
        """Boucle principale de l'application"""
        self.ui.show_welcome()

        # Afficher l'agent actuel
        current_agent = self.agent_manager.get_current_agent()
        if current_agent:
            self.ui.print_info(
                f"Agent actuel: {current_agent.name} - {current_agent.description}"
            )

        while True:
            try:
                # Obtenir l'ID de conversation pour le prompt
                conv_id = None
                if self.conversation_manager.current_conversation:
                    conv_id = self.conversation_manager.current_conversation["id"]

                user_input = self.ui.get_user_input(conv_id)

                if not user_input:
                    continue

                # Gérer les commandes
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                    continue

                # Créer une nouvelle conversation si nécessaire
                if not self.conversation_manager.current_conversation:
                    self.conversation_manager.create_new_conversation(user_input)

                # Ajouter le message utilisateur
                self.conversation_manager.add_message("user", user_input)
                self.refresh_display()

                # Obtenir la réponse
                with self.ui.show_processing():
                    response_content, tools_used, sources = self.send_message_to_gpt(
                        user_input
                    )

                # Ajouter la réponse de l'assistant
                self.conversation_manager.add_message(
                    "assistant", response_content, tools_used, sources
                )
                self.refresh_display()

                # Sauvegarder la conversation si activé
                if config.auto_save:
                    self.conversation_manager.save_conversation()

            except KeyboardInterrupt:
                self.ui.print_warning(
                    "\nInterruption détectée. Tapez /quit pour quitter proprement."
                )
            except Exception as e:
                self.ui.print_error(f"Erreur inattendue: {str(e)}")


def main():
    """Point d'entrée de l'application"""
    app = VerbiageChat()
    app.run()


if __name__ == "__main__":
    main()
