#!/usr/bin/env python3
"""
Verbiage - Chat GPT avec outils en terminal
Application principale (version simplifiée)
"""

import sys
import requests

from verbiage.agents import AgentManager
from verbiage.config import config
from verbiage.conversation import ConversationManager
from verbiage.ui import VerbiageUI
from verbiage.api_client import send_with_openrouter

# Nouveaux imports
from verbiage.command_handlers import (
    handle_quit, handle_clear, handle_new, handle_list,
    handle_load, handle_undo, handle_delete, handle_edit,
    handle_help, handle_agents, handle_agent, handle_create_agent,
    handle_raw, handle_config, handle_unknown
)


class VerbiageChat:
    """Application principale de chat avec OpenRouter"""

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
        self.ui.print_info("💡 Ctrl+E pour ouvrir l'éditeur")
        # historique
        self.ui.display_conversation_history(
            self.conversation_manager.current_conversation
        )

    def __init__(self):
        self.ui = VerbiageUI()
        self.conversation_manager = ConversationManager(config.conversations_dir)
        self.agent_manager = AgentManager(config.agents_dir, config)

        # Validation de la configuration
        is_valid, errors = config.validate()
        if not is_valid:
            self.ui.print_error("Erreur de configuration:")
            for error in errors:
                self.ui.print_info(f"  - {error}")
            sys.exit(1)

        # Initialiser le client HTTP
        self.client_session = requests.Session()
        self.debug = config.debug_mode
        self.config = config

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
            "/config": handle_config,
        }

    def handle_command(self, command: str) -> bool:
        command = command.lower().strip()
        cmd = command.split()[0]
        handler = self.cmd_handlers.get(cmd, handle_unknown)
        return handler(self, command)

    def _send_message(self, message: str, web_search: bool = False):
        """Factorisation de l'envoi d'un message."""
        if not self.conversation_manager.current_conversation:
            self.conversation_manager.create_new_conversation(message)

        self.conversation_manager.add_message("user", message)
        self.refresh_display()

        with self.ui.show_processing():
            response_content, tools_used, sources = send_with_openrouter(
                self.agent_manager,
                self.conversation_manager,
                message,
                self.client_session,
                web_search
            )

        self.conversation_manager.add_message(
            "assistant", response_content, tools_used, sources
        )
        self.refresh_display()

        if config.auto_save:
            self.conversation_manager.save_conversation()

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

                user_input = self.ui.get_user_input(
                    conv_id,
                    current_conversation=self.conversation_manager.current_conversation
                )

                if not user_input:
                    continue

                # Gérer les commandes
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                    continue

                # Envoi normal sans web
                self._send_message(user_input, web_search=False)

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
